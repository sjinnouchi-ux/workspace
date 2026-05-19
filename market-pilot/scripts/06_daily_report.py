#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
06_daily_report.py - 毎日07:00 / 22:30 に実行
買いシグナル状況 + 保有株チェックを統合してLINE通知
"""

import gspread
import yfinance as yf
import urllib.request
import json
import re
import pytz
from datetime import datetime

# ─── 設定 ───────────────────────────────────────
LINE_TOKEN     = "cWY02EZBaaUow+9kDUrlxrQJfBOqnyh1qINdu5ALMRwSJEfy0NY2V1rXl++j+sF41Y1uGrqRDT263RydAi5oAzfns+B4EcDjJC47uOz0rkwmpjOW4m42v0wfsivtZjZ4fNYXyyzXOjRfdM2OQy2+xQdB04t89/1O/w1cDnyilFU="
SPREADSHEET_ID = "1Jt-vKUHDmLo8Qf6aSZlBnvG5uBtpcr6gtk9ZgLjycQ4"
JST            = pytz.timezone("Asia/Tokyo")
PROFIT_TH      = 12.0   # 利確ライン（%）
RSI_SELL_TH    = 70     # 売却RSIしきい値
BB_PERIOD      = 20
BB_STD         = 2.0
# ────────────────────────────────────────────────

def connect_ss():
    client = gspread.oauth()
    return client.open_by_key(SPREADSHEET_ID)

def load_settings(ss):
    sh   = ss.worksheet("設定")
    data = sh.get_all_values()
    s    = {}
    for row in data[1:]:
        if len(row) >= 2 and row[0]:
            s[row[0]] = row[1]
    return {
        'tickers':    [t.strip() for t in s.get('ティッカー', 'QQQ,GLD').split(',')],
        'rsi_period': int(s.get('RSI期間', 14)),
        'rsi_th':     float(s.get('RSIしきい値', 40)),
        'ma_s':       int(s.get('短期MA', 5)),
        'ma_m':       int(s.get('中期MA', 20)),
    }

def _v(x):
    try:
        return float(x.iloc[-1]) if hasattr(x, 'iloc') else float(x)
    except Exception:
        return float(x)

def calc_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    loss  = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
    rs    = gain / loss.replace(0, 1e-10)
    return _v(100 - 100 / (1 + rs))

def calc_bb_upper(series, period=20, std_mult=2.0):
    sma = series.rolling(period).mean()
    std = series.rolling(period).std()
    return _v(sma + std_mult * std)

def get_current_rate():
    try:
        fx = yf.download("USDJPY=X", period="3d", interval="1d",
                         progress=False, auto_adjust=True)
        return _v(fx['Close'])
    except Exception:
        return None

def check_buy_signal(ticker, s):
    """買いシグナルの現状チェック（常に状況を返す）"""
    df = yf.download(ticker, period="120d", interval="1d",
                     progress=False, auto_adjust=True)
    if df is None or df.empty:
        return None

    if hasattr(df.columns, 'levels'):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

    close    = df['Close'].squeeze()
    rsi      = calc_rsi(close, s['rsi_period'])
    ma_s     = _v(close.rolling(s['ma_s']).mean())
    ma_m     = _v(close.rolling(s['ma_m']).mean())
    price    = _v(close)

    rsi_sig  = rsi < s['rsi_th']
    gc_sig   = (ma_s > ma_m)

    rsi_distance = rsi - s['rsi_th']   # 負なら既にシグナル、正なら残り

    return {
        'ticker':       ticker,
        'price':        round(price, 2),
        'rsi':          round(rsi, 1),
        'rsi_th':       s['rsi_th'],
        'rsi_distance': round(rsi_distance, 1),
        'rsi_sig':      rsi_sig,
        'ma_s':         round(ma_s, 2),
        'ma_m':         round(ma_m, 2),
        'gc_sig':       gc_sig,
        'any_signal':   rsi_sig or gc_sig,
    }

def get_holdings(ss):
    """売買ログから保有中の銘柄を取得"""
    sh   = ss.worksheet("売買ログ")
    rows = sh.get_all_values()
    holdings = []
    for row in rows[1:]:
        if len(row) < 9:
            continue
        buy_date  = row[1].strip()
        sell_date = row[8].strip()
        if not buy_date or sell_date:
            continue
        ticker_raw = row[2].strip()
        ticker = ticker_raw.split('/')[0].strip() if '/' in ticker_raw else ticker_raw
        shares_m  = re.search(r'[\d.]+', row[4].strip())
        shares    = float(shares_m.group()) if shares_m else 1.0
        price_m   = re.search(r'[\d.]+', row[5].strip())
        buy_price = float(price_m.group()) if price_m else 0.0
        rate_m    = re.search(r'[\d.]+', row[6].strip())
        buy_rate  = float(rate_m.group()) if rate_m else 150.0
        holdings.append({
            'ticker':    ticker,
            'shares':    shares,
            'buy_price': buy_price,
            'buy_rate':  buy_rate,
            'account':   row[3].strip(),
        })
    return holdings

def check_holding(h, current_rate):
    """保有株の現状チェック"""
    ticker = h['ticker']
    df = yf.download(ticker, period="90d", interval="1d",
                     progress=False, auto_adjust=True)
    if df is None or df.empty:
        return None

    close     = df['Close'].squeeze()
    cur_price = _v(close)
    rsi       = calc_rsi(close)
    bb_upper  = calc_bb_upper(close, BB_PERIOD, BB_STD)

    rate      = current_rate if current_rate else h['buy_rate']
    pnl_pct   = (cur_price / h['buy_price'] - 1) * 100 if h['buy_price'] > 0 else 0
    pnl_jpy   = cur_price * rate * h['shares'] - h['buy_price'] * h['buy_rate'] * h['shares']

    bb_touch   = cur_price >= bb_upper * 0.99
    sig_profit = pnl_pct >= PROFIT_TH
    sig_rsi    = rsi >= RSI_SELL_TH
    sig_strong = sig_rsi and bb_touch

    signals = []
    if sig_profit:
        signals.append(f"利確ライン達成（+{pnl_pct:.1f}%）")
    if sig_strong:
        signals.append(f"RSI過熱+BB上限タッチ（RSI={rsi:.1f}）")
    elif sig_rsi:
        signals.append(f"RSI過熱（{rsi:.1f}）")

    return {
        'ticker':      ticker,
        'account':     h['account'],
        'shares':      h['shares'],
        'buy_price':   h['buy_price'],
        'cur_price':   cur_price,
        'pnl_pct':     pnl_pct,
        'pnl_jpy':     pnl_jpy,
        'rsi':         rsi,
        'bb_upper':    bb_upper,
        'bb_touch':    bb_touch,
        'signals':     signals,
        'should_sell': len(signals) > 0,
    }

def build_message(buy_results, hold_results, today_str, time_str, cur_rate):
    lines = [f"【相場チェック {today_str} {time_str}】\n"]

    lines.append("━ 買いシグナル状況 ━━━━━━━━━━")
    for r in buy_results:
        if r is None:
            continue
        lines.append(f"📊 {r['ticker']}  ${r['price']}")
        if r['rsi_sig']:
            lines.append(f"  RSI: {r['rsi']} ✅ 押し目シグナル発生中！")
        else:
            lines.append(f"  RSI: {r['rsi']} → 買いまであと{r['rsi_distance']:.1f}pt（しきい値{r['rsi_th']:.0f}）")
        gc_mark = "✅ GC" if r['gc_sig'] else "GC待ち"
        lines.append(f"  MA短期 ${r['ma_s']} vs MA中期 ${r['ma_m']}  {gc_mark}")
        if r['any_signal']:
            lines.append("  → 🔔 買いシグナル中")
            if time_str >= "22:00":
                lines.append("  ⚡ アクション：成行で即購入")
        else:
            lines.append("  → シグナルなし")
        lines.append("")

    if hold_results:
        lines.append("━ 保有株 ━━━━━━━━━━━━━━━")
        for r in hold_results:
            if r is None:
                continue
            pct_sign = "+" if r['pnl_pct'] >= 0 else ""
            j_sign   = "+" if r['pnl_jpy'] >= 0 else "-"
            lines.append(f"📦 {r['ticker']} {r['shares']:.0f}株（{r['account']}）")
            lines.append(f"  ${r['buy_price']:.2f}→${r['cur_price']:.2f} | {pct_sign}{r['pnl_pct']:.2f}%  {j_sign}¥{abs(r['pnl_jpy']):,.0f}")
            bb_note = " ⚠️BB上限タッチ" if r['bb_touch'] else ""
            lines.append(f"  RSI:{r['rsi']:.1f} | BB上限:${r['bb_upper']:.2f}{bb_note}")
            if r['should_sell']:
                lines.append("  📋 判定:【売却検討】")
                for s in r['signals']:
                    lines.append(f"    理由:{s}")
            else:
                remain = PROFIT_TH - r['pnl_pct']
                target = r['buy_price'] * (1 + PROFIT_TH / 100)
                lines.append(f"  📋 判定:【保有継続】利確まであと{remain:.2f}%（目標${target:.2f}）")
            lines.append("")
    else:
        lines.append("━ 保有株 ━━━━━━━━━━━━━━━")
        lines.append("現在保有なし")
        lines.append("")

    if cur_rate:
        lines.append(f"USD/JPY: {cur_rate:.2f}")

    return "\n".join(lines)

def send_line(message):
    body = json.dumps({"messages": [{"type": "text", "text": message}]}).encode()
    req  = urllib.request.Request(
        "https://api.line.me/v2/bot/message/broadcast",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_TOKEN}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as res:
        return res.status

def main():
    now      = datetime.now(JST)
    today_str = now.strftime("%Y/%m/%d")
    time_str  = now.strftime("%H:%M")
    print(f"[{today_str} {time_str}] 06_daily_report.py 起動")

    ss = connect_ss()
    s  = load_settings(ss)
    print(f"  対象ティッカー: {s['tickers']}")

    cur_rate = get_current_rate()
    if cur_rate:
        print(f"  USD/JPY: {cur_rate:.2f}")

    buy_results = []
    for ticker in s['tickers']:
        print(f"  買いシグナルチェック: {ticker} ...")
        r = check_buy_signal(ticker, s)
        if r:
            sig = "🔔 シグナルあり" if r['any_signal'] else "シグナルなし"
            print(f"    {ticker}: {sig} | RSI={r['rsi']} | ${r['price']}")
        buy_results.append(r)

    holdings = get_holdings(ss)
    hold_results = []
    if holdings:
        print(f"  保有株: {len(holdings)}件")
        for h in holdings:
            print(f"  保有チェック: {h['ticker']} ...")
            r = check_holding(h, cur_rate)
            if r:
                status = "🔴 売却シグナル" if r['should_sell'] else "✅ 保有継続"
                print(f"    {h['ticker']}: {status} | ${r['cur_price']:.2f} | RSI={r['rsi']:.1f} | {r['pnl_pct']:+.2f}%")
            hold_results.append(r)
    else:
        print("  保有株なし")

    msg    = build_message(buy_results, hold_results, today_str, time_str, cur_rate)
    status = send_line(msg)
    print(f"  LINE送信ステータス: {status}")
    print("完了")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
07_scan.py - Phase2: 多銘柄スキャン
銘柄リストシートの有効銘柄を並列スキャンし、シグナルのみLINE通知
"""

import gspread
import yfinance as yf
import urllib.request
import json
import re
import pytz
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─── 設定 ───────────────────────────────────────
LINE_TOKEN     = "cWY02EZBaaUow+9kDUrlxrQJfBOqnyh1qINdu5ALMRwSJEfy0NY2V1rXl++j+sF41Y1uGrqRDT263RydAi5oAzfns+B4EcDjJC47uOz0rkwmpjOW4m42v0wfsivtZjZ4fNYXyyzXOjRfdM2OQy2+xQdB04t89/1O/w1cDnyilFU="
SPREADSHEET_ID = "1Jt-vKUHDmLo8Qf6aSZlBnvG5uBtpcr6gtk9ZgLjycQ4"
JST            = pytz.timezone("Asia/Tokyo")
PROFIT_TH      = 12.0
RSI_SELL_TH    = 70
BB_PERIOD      = 20
BB_STD         = 2.0
MAX_WORKERS    = 8  # 並列ダウンロード数
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
        'rsi_period': int(s.get('RSI期間', 14)),
        'rsi_th':     float(s.get('RSIしきい値', 40)),
        'ma_s':       int(s.get('短期MA', 5)),
        'ma_m':       int(s.get('中期MA', 20)),
    }

def load_tickers(ss):
    """銘柄リストシートから有効銘柄を取得。シートがなければ設定シートにフォールバック"""
    try:
        sh   = ss.worksheet("銘柄リスト")
        rows = sh.get_all_values()
        tickers = [row[0].strip() for row in rows[1:] if len(row) >= 3 and row[0].strip() and row[2].strip() == '✓']
        return tickers if tickers else ['QQQ', 'GLD']
    except gspread.WorksheetNotFound:
        sh   = ss.worksheet("設定")
        data = sh.get_all_values()
        for row in data[1:]:
            if row[0] == 'ティッカー':
                return [t.strip() for t in row[1].split(',')]
        return ['QQQ', 'GLD']

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
    """1銘柄の買いシグナルチェック"""
    try:
        df = yf.download(ticker, period="120d", interval="1d",
                         progress=False, auto_adjust=True)
        if df is None or df.empty:
            return None

        if hasattr(df.columns, 'levels'):
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

        close = df['Close'].squeeze()
        rsi   = calc_rsi(close, s['rsi_period'])
        ma_s  = _v(close.rolling(s['ma_s']).mean())
        ma_m  = _v(close.rolling(s['ma_m']).mean())
        price = _v(close)

        rsi_sig = rsi < s['rsi_th']
        gc_sig  = ma_s > ma_m

        return {
            'ticker':       ticker,
            'price':        round(price, 2),
            'rsi':          round(rsi, 1),
            'rsi_th':       s['rsi_th'],
            'rsi_distance': round(rsi - s['rsi_th'], 1),
            'rsi_sig':      rsi_sig,
            'ma_s':         round(ma_s, 2),
            'ma_m':         round(ma_m, 2),
            'gc_sig':       gc_sig,
            'any_signal':   rsi_sig or gc_sig,
        }
    except Exception as e:
        print(f"  [{ticker}] エラー: {e}")
        return None

def scan_tickers_parallel(tickers, s):
    """全銘柄を並列スキャンし、元の順序で返す"""
    results = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_ticker = {executor.submit(check_buy_signal, t, s): t for t in tickers}
        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                results[ticker] = future.result()
            except Exception as e:
                print(f"  [{ticker}] 並列処理エラー: {e}")
                results[ticker] = None
    return [results.get(t) for t in tickers]

def get_holdings(ss):
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
        ticker    = ticker_raw.split('/')[0].strip() if '/' in ticker_raw else ticker_raw
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
    ticker = h['ticker']
    try:
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
    except Exception as e:
        print(f"  [{ticker}] 保有チェックエラー: {e}")
        return None

def build_message(buy_results, hold_results, today_str, time_str, cur_rate, total_count):
    signal_results = [r for r in buy_results if r and r['any_signal']]
    lines = [f"【スキャン {today_str} {time_str}】\n"]

    if signal_results:
        lines.append(f"🔔 シグナル銘柄（{len(signal_results)}件）━━━━━━━━")
        for r in signal_results:
            lines.append(f"📊 {r['ticker']}  ${r['price']}")
            if r['rsi_sig']:
                lines.append(f"  RSI: {r['rsi']} ✅ 押し目")
            if r['gc_sig']:
                lines.append(f"  MA${r['ma_s']} > MA${r['ma_m']} ✅ GC")
            if time_str >= "22:00":
                lines.append("  ⚡ アクション：成行購入検討")
            lines.append("")
    else:
        lines.append(f"📊 シグナルなし（{total_count}銘柄スキャン済）")
        lines.append("")

    lines.append(f"スキャン済：{total_count}銘柄")
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
            bb_note = " ⚠️BB上限" if r['bb_touch'] else ""
            lines.append(f"  RSI:{r['rsi']:.1f} | BB上限:${r['bb_upper']:.2f}{bb_note}")
            if r['should_sell']:
                lines.append("  📋【売却検討】")
                for sig in r['signals']:
                    lines.append(f"    理由:{sig}")
            else:
                remain = PROFIT_TH - r['pnl_pct']
                target = r['buy_price'] * (1 + PROFIT_TH / 100)
                lines.append(f"  📋【保有継続】利確まであと{remain:.2f}%（目標${target:.2f}）")
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
    now       = datetime.now(JST)
    today_str = now.strftime("%Y/%m/%d")
    time_str  = now.strftime("%H:%M")
    print(f"[{today_str} {time_str}] 07_scan.py 起動")

    ss      = connect_ss()
    s       = load_settings(ss)
    tickers = load_tickers(ss)
    print(f"  スキャン対象: {len(tickers)}銘柄 {tickers}")

    cur_rate = get_current_rate()
    if cur_rate:
        print(f"  USD/JPY: {cur_rate:.2f}")

    print(f"  並列スキャン開始（MAX {MAX_WORKERS}ワーカー）...")
    buy_results  = scan_tickers_parallel(tickers, s)
    signal_count = sum(1 for r in buy_results if r and r['any_signal'])
    print(f"  スキャン完了: {len(tickers)}銘柄 / シグナル{signal_count}件")

    holdings     = get_holdings(ss)
    hold_results = []
    if holdings:
        print(f"  保有株: {len(holdings)}件")
        for h in holdings:
            hold_results.append(check_holding(h, cur_rate))
    else:
        print("  保有株なし")

    msg    = build_message(buy_results, hold_results, today_str, time_str, cur_rate, len(tickers))
    status = send_line(msg)
    print(f"  LINE送信: {status}")
    print("完了")

if __name__ == "__main__":
    main()

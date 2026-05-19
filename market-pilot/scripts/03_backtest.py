#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
03_backtest.py - バックテスト実行スクリプト
使い方: python3 03_backtest.py VOO
"""

import sys
import gspread
import yfinance as yf
import pandas as pd
import pytz
from datetime import datetime, timedelta

SPREADSHEET_ID = "1Jt-vKUHDmLo8Qf6aSZlBnvG5uBtpcr6gtk9ZgLjycQ4"
JST = pytz.timezone("Asia/Tokyo")

def connect_ss():
    gc = gspread.oauth()
    return gc.open_by_key(SPREADSHEET_ID)

def load_rules(ss):
    sh = ss.worksheet("ルール管理")
    rules = {}
    for row in sh.get_all_values():
        if len(row) >= 2 and row[0] and row[1]:
            rules[row[0]] = row[1]
    period_map = {"1ヶ月": 30, "3ヶ月": 90, "6ヶ月": 180, "1年": 365}
    period_str = rules.get("シミュレーション期間", "1年")
    return {
        "cut_loss":   abs(float(rules.get("損切りライン（%）", -4))) / 100,
        "profit":     float(rules.get("利確ライン（%）", 12)) / 100,
        "investment": float(rules.get("1回の投資額（万円）", 20)) * 10000,
        "rsi_th":     float(rules.get("RSI閾値（これ以下で押し目）", 50)),
        "ma_s":       int(rules.get("短期MA（日）", 5)),
        "ma_m":       int(rules.get("中期MA（日）", 20)),
        "ma_l":       int(rules.get("長期MA（日）", 50)),
        "period_days": period_map.get(period_str, 365),
        "period_str": period_str,
        "rate":       float(rules.get("想定為替レート（円/USD）", 160)),
        "fee_rate":   float(rules.get("手数料率（%）", 0.22)) / 100,
    }

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
    return 100 - 100 / (1 + gain / loss.replace(0, 1e-10))

def fetch_and_calc(ticker, period_days, ma_s, ma_m, ma_l):
    extra = max(ma_l * 2, 100)
    df = yf.download(ticker, period=f"{period_days + extra}d", interval="1d",
                     progress=False, auto_adjust=True)
    if df is None or df.empty:
        return None
    if hasattr(df.columns, "levels"):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df.reset_index()
    df["MA5"]   = df["Close"].rolling(ma_s).mean()
    df["MA20"]  = df["Close"].rolling(ma_m).mean()
    df["MA50"]  = df["Close"].rolling(ma_l).mean()
    df["RSI14"] = calc_rsi(df["Close"])
    df["前日比(%)"] = df["Close"].pct_change() * 100
    df["MA20比(%)"] = (df["Close"] / df["MA20"] - 1) * 100
    return df

def run_backtest(df, rules, sim_start):
    sim = df[df["Date"] >= pd.Timestamp(sim_start)].copy().reset_index(drop=True)
    trades, holding, buy_price, buy_date, no = [], False, None, None, 1

    i = 0
    while i < len(sim):
        row = sim.iloc[i]
        if not holding:
            if pd.notna(row["RSI14"]) and row["RSI14"] <= rules["rsi_th"]:
                if i + 1 < len(sim):
                    nxt = sim.iloc[i + 1]
                    buy_price = float(nxt["Open"])
                    buy_date  = nxt["Date"]
                    holding   = True
                    i += 1
                    continue
        else:
            close     = float(row["Close"])
            pnl_ratio = close / buy_price - 1
            if pnl_ratio >= rules["profit"]:
                sell_price = round(buy_price * (1 + rules["profit"]), 2)
                reason = "利確"
            elif pnl_ratio <= -rules["cut_loss"]:
                sell_price = round(buy_price * (1 - rules["cut_loss"]), 2)
                reason = "損切り"
            elif i == len(sim) - 1:
                sell_price = round(close, 2)
                reason = "期間終了"
            else:
                i += 1
                continue

            ratio    = sell_price / buy_price
            pnl_jpy  = round(rules["investment"] * (ratio - 1)
                             - rules["investment"] * rules["fee_rate"]
                             - rules["investment"] * ratio * rules["fee_rate"])
            trades.append({
                "No":         no,
                "買付日":      buy_date.strftime("%Y/%m/%d"),
                "買付価格(USD)": round(buy_price, 2),
                "売却日":      row["Date"].strftime("%Y/%m/%d"),
                "売却価格(USD)": sell_price,
                "売却理由":    reason,
                "損益(円)":    pnl_jpy,
                "損益率(%)":  f"{(ratio - 1) * 100:.2f}%",
            })
            no += 1
            holding, buy_price, buy_date = False, None, None
        i += 1
    return trades

def write_chart_sheet(ss, ticker, df, rules, sim_start):
    name = f"チャートデータ_{ticker}"
    try:
        sh = ss.worksheet(name)
        sh.clear()
    except gspread.WorksheetNotFound:
        sh = ss.add_worksheet(title=name, rows=600, cols=14)

    def fmt(v, d=2):
        return "" if pd.isna(v) else round(float(v), d)

    sim = df[df["Date"] >= pd.Timestamp(sim_start)]
    rows = [["日付","Open","High","Low","Close","Volume",
             "MA5","MA20","MA50","RSI14","押し目シグナル","前日比(%)","MA20比(%)"]]
    for _, r in sim.iterrows():
        signal = "●買いシグナル" if pd.notna(r["RSI14"]) and r["RSI14"] <= rules["rsi_th"] else ""
        rows.append([
            r["Date"].strftime("%Y/%m/%d"),
            fmt(r["Open"]), fmt(r["High"]), fmt(r["Low"]), fmt(r["Close"]),
            int(r["Volume"]) if pd.notna(r["Volume"]) else "",
            fmt(r["MA5"]), fmt(r["MA20"]), fmt(r["MA50"]),
            fmt(r["RSI14"]), signal,
            fmt(r["前日比(%)"]), fmt(r["MA20比(%)"]),
        ])
    sh.update(rows, value_input_option="USER_ENTERED")
    print(f"  {name}: {len(rows)-1}行 書き込み完了")

def write_backtest_sheet(ss, ticker, trades, rules, now_str):
    name = f"バックテスト結果_{ticker}"
    try:
        sh = ss.worksheet(name)
        sh.clear()
    except gspread.WorksheetNotFound:
        sh = ss.add_worksheet(title=name, rows=100, cols=10)

    wins   = [t for t in trades if t["損益(円)"] > 0]
    losses = [t for t in trades if t["損益(円)"] <= 0]
    total  = sum(t["損益(円)"] for t in trades)
    avg    = round(total / len(trades)) if trades else 0
    mx     = max((t["損益(円)"] for t in trades), default=0)
    mn     = min((t["損益(円)"] for t in trades), default=0)
    wr     = f"{len(wins)/len(trades)*100:.1f}%" if trades else "0.0%"

    pnl_str = f"¥{total:,}" if total < 0 else f"＋¥{total:,}"
    rows = [
        [f"■ バックテスト実行情報 [{ticker}]"],
        ["実行日時", now_str],
        ["銘柄", ticker],
        ["シミュレーション期間", rules["period_str"]],
        ["損切りライン", f"-{rules['cut_loss']*100:.1f}%"],
        ["利確ライン", f"＋{rules['profit']*100:.1f}%"],
        ["RSI閾値", f"{rules['rsi_th']:.0f}以下"],
        ["1回投資額", f"¥{int(rules['investment']):,}"],
        ["想定為替レート", f"{rules['rate']:.0f}円/USD"],
        [],
        ["■ バックテスト結果サマリー"],
        ["総取引数", f"{len(trades)}回"],
        ["勝ち / 負け", f"{len(wins)}勝 / {len(losses)}敗"],
        ["勝率", wr],
        ["総損益", pnl_str],
        ["平均損益（1取引）", f"¥{avg:,}"],
        ["最大利益（1取引）", f"¥{mx:,}"],
        ["最大損失（1取引）", f"¥{mn:,}"],
        ["最大ドローダウン", f"-{rules['cut_loss']*100:.1f}%"],
        [],
        ["■ 取引詳細ログ"],
        ["No","買付日","買付価格(USD)","売却日","売却価格(USD)","売却理由","損益(円)","損益率(%)"],
    ]
    for t in trades:
        rows.append([t["No"], t["買付日"], t["買付価格(USD)"],
                     t["売却日"], t["売却価格(USD)"], t["売却理由"],
                     t["損益(円)"], t["損益率(%)"]])
    sh.update(rows, value_input_option="RAW")
    print(f"  {name}: {len(trades)}件 書き込み完了")

def main(ticker):
    now     = datetime.now(JST)
    now_str = now.strftime("%Y/%m/%d %H:%M")
    print(f"[{now_str}] {ticker} バックテスト開始")

    ss    = connect_ss()
    rules = load_rules(ss)
    print(f"  設定: 利確+{rules['profit']*100:.0f}% / 損切り-{rules['cut_loss']*100:.0f}% / RSI≤{rules['rsi_th']:.0f} / {rules['period_str']}")

    df = fetch_and_calc(ticker, rules["period_days"], rules["ma_s"], rules["ma_m"], rules["ma_l"])
    if df is None:
        print(f"  エラー: {ticker} データ取得失敗")
        return

    sim_start = (now - timedelta(days=rules["period_days"])).date()
    print(f"  期間: {sim_start} ～ {now.date()}")

    write_chart_sheet(ss, ticker, df, rules, sim_start)

    trades = run_backtest(df, rules, sim_start)
    print(f"  取引: {len(trades)}件")

    write_backtest_sheet(ss, ticker, trades, rules, now_str)
    print("完了")

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "VOO"
    main(ticker)

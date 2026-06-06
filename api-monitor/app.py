"""API Monitor - Streamlit entry point.

Run on Windows:
    streamlit run app.py
"""

from __future__ import annotations

from dotenv import load_dotenv

import streamlit as st

import db
import monitor
import settings


def main() -> None:
    load_dotenv()
    db.init_db()

    st.set_page_config(
        page_title="API Monitor",
        page_icon=":bar_chart:",
        layout="wide",
    )

    st.title("API Monitor")
    st.caption("OpenAI / Anthropic / Google のAPI利用料・トークン・呼び出し履歴を確認するWindows向けダッシュボード")

    tab_monitor, tab_settings = st.tabs(["モニター", "設定"])

    with tab_monitor:
        monitor.render()

    with tab_settings:
        settings.render()


if __name__ == "__main__":
    main()

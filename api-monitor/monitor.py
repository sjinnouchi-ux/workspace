"""Monitor tab — summary metrics, charts and call log.

Phase 1 ships a minimum-viable view that already reads from SQLite.
Charts will be polished in Phase 3 (implementation_plan.md).
"""

from __future__ import annotations

import streamlit as st

import db


def render() -> None:
    st.subheader("今月のサマリー")

    summary = db.summary_current_month()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("今月の費用 (USD)", f"${summary['total_cost_usd']:.2f}")
    c2.metric("総トークン数",      f"{summary['total_tokens']:,}")
    c3.metric("APIコール数",       f"{summary['total_calls']:,}")
    c4.metric("最多モデル",        summary["top_model"] or "—")

    st.divider()

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("日別費用推移（サービス別）")
        daily = db.daily_cost_by_service()
        if daily.empty:
            st.info("まだAPI呼び出しの記録がありません。`api_clients` 経由で呼び出すと自動でログされます。")
        else:
            pivot = daily.pivot(index="date", columns="service", values="cost").fillna(0)
            st.line_chart(pivot)

    with col_right:
        st.subheader("サービス別費用比率（今月）")
        share = db.service_cost_share()
        if share.empty:
            st.info("データなし")
        else:
            st.bar_chart(share.set_index("service"))

    st.divider()

    st.subheader("直近のAPIコール履歴（最新50件）")
    logs = db.fetch_call_logs(limit=50)
    if logs.empty:
        st.info("記録なし")
    else:
        st.dataframe(
            logs[
                [
                    "timestamp", "service", "model", "project", "purpose",
                    "input_tokens", "output_tokens", "cost_usd",
                    "response_ms", "status",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

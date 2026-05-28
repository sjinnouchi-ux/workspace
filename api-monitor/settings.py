"""Settings tab — API keys and project/purpose customization.

Phase 1 ships a minimum-viable UI that already persists to SQLite.
Phase 4 (this revision) adds one-click copy via ``st.code`` whose
header carries Streamlit's built-in clipboard icon.
"""

from __future__ import annotations

import os

import streamlit as st

import db
from api_clients import SUPPORTED_SERVICES, MODEL_PRICING


SERVICE_LABELS = {
    "openai":    "OpenAI",
    "anthropic": "Anthropic (Claude)",
    "google":    "Google (Gemini)",
}

ENV_KEY_NAMES = {
    "openai":    "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google":    "GOOGLE_API_KEY",
}


def _mask(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 10:
        return "*" * len(key)
    return f"{key[:6]}…{key[-4:]}"


def _render_key_block(service: str, shown: str) -> None:
    """Render the masked display + copy controls for a single service."""
    show_key      = f"show_{service}"
    copy_open_key = f"copy_open_{service}"
    st.session_state.setdefault(copy_open_key, False)

    show = st.toggle("キーを表示", key=show_key)
    st.text_input(
        "現在のキー",
        value=(shown if show else _mask(shown)),
        key=f"display_{service}",
        disabled=True,
    )

    if not shown:
        st.caption("まだキーが登録されていません。下のフォームから登録してください。")
        return

    btn_label = "閉じる" if st.session_state[copy_open_key] else "📋 コピー用に表示"
    if st.button(btn_label, key=f"copybtn_{service}"):
        st.session_state[copy_open_key] = not st.session_state[copy_open_key]
        st.rerun()

    if st.session_state[copy_open_key]:
        # ``st.code`` shows a copy-to-clipboard icon in the top-right corner.
        st.code(shown, language=None, wrap_lines=True)
        st.caption("右上のコピーアイコンをクリックするとクリップボードへコピーされます。")


def render() -> None:
    st.subheader("APIキー管理")

    keys = {row["service"]: row for row in db.list_api_keys()}

    for service in SUPPORTED_SERVICES:
        with st.expander(SERVICE_LABELS[service], expanded=False):
            current   = keys.get(service, {}).get("api_key", "")
            env_value = os.environ.get(ENV_KEY_NAMES[service], "")
            shown     = current or env_value

            _render_key_block(service, shown)

            st.divider()

            new_key = st.text_input(
                "新しいキーを登録 / 上書き",
                key=f"new_{service}",
                type="password",
            )
            cols = st.columns(2)
            if cols[0].button("保存", key=f"save_{service}"):
                if new_key.strip():
                    db.upsert_api_key(service, new_key.strip())
                    st.success("保存しました。再読み込みで反映されます。")
                else:
                    st.warning("空のキーは保存しません。")
            if cols[1].button("削除", key=f"del_{service}"):
                db.delete_api_key(service)
                # Reset the copy panel so the deleted key disappears immediately.
                st.session_state[f"copy_open_{service}"] = False
                st.success("削除しました。")

    st.divider()

    st.subheader("API用途カスタマイズ")
    st.caption("プロジェクト名・使用モデル・用途メモを自由に紐付けます。")

    with st.form("setting_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
        service = c1.selectbox("サービス", SUPPORTED_SERVICES, format_func=lambda s: SERVICE_LABELS[s])
        models  = sorted({m for (svc, m) in MODEL_PRICING.keys() if svc == service})
        model   = c2.selectbox("モデル", models if models else ["custom"])
        project = c3.text_input("プロジェクト名")
        purpose = c4.text_input("用途メモ")
        if st.form_submit_button("登録 / 更新"):
            if project.strip():
                db.upsert_setting(service, model, project.strip(), purpose.strip() or None)
                st.success("保存しました。")
            else:
                st.warning("プロジェクト名は必須です。")

    rows = db.list_settings()
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("まだ登録された用途はありません。")

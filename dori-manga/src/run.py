"""
どり看護師 漫画自動化パイプライン
メインエントリーポイント

使い方:
  python src/run.py init     # 初回実行（PDFを読み込んで案①を生成）
  python src/run.py revise   # 修正実行（修正依頼を反映して最終案を生成）
"""

import sys
import os
import time

from dotenv import load_dotenv
import anthropic
from googleapiclient.discovery import build

# 自作モジュール
sys.path.insert(0, os.path.dirname(__file__))
from drive import get_pdf_files, download_pdf_as_bytes, build_drive_service
from pdf_reader import extract_pdf_info
from manga_gen import generate_panel_concepts, revise_panel
from sheets import (
    build_sheets_client, build_oauth_credentials, get_or_create_sheet,
    get_existing_titles, append_init_row,
    get_rows_with_revision_notes, update_final_panel
)

# .envを読み込む
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))


def get_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        print(f"[ERROR] 環境変数 {key} が設定されていません。.envファイルを確認してください。")
        sys.exit(1)
    return val


def build_drive_service_oauth(credentials_path: str, token_path: str):
    """OAuth2認証でGoogle Drive APIサービスを構築する"""
    creds = build_oauth_credentials(credentials_path, token_path)
    return build("drive", "v3", credentials=creds)


# ===== initモード =====
def run_init():
    print("=" * 50)
    print("【initモード】PDFを読み込んでコマ案①を生成します")
    print("=" * 50)

    # 設定取得
    anthropic_key     = get_env("ANTHROPIC_API_KEY")
    folder_id         = get_env("GOOGLE_DRIVE_FOLDER_ID")
    sheets_id         = get_env("GOOGLE_SHEETS_ID")
    credentials_path  = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    token_path        = os.getenv("GOOGLE_TOKEN_PATH", "token.json")
    sheet_name        = os.getenv("SHEET_NAME", "どり漫画管理")

    # クライアント初期化
    print("\n[1/5] クライアントを初期化中...")
    print("  ※ 初回実行時はブラウザが開きます。Googleアカウントで認証してください。")
    claude    = anthropic.Anthropic(api_key=anthropic_key)
    drive_svc = build_drive_service_oauth(credentials_path, token_path)
    gc        = build_sheets_client(credentials_path, token_path)
    ws        = get_or_create_sheet(gc, sheets_id, sheet_name)

    # PDF一覧取得
    print("\n[2/5] Googleドライブからよりついたファイル一覧を取得中...")
    pdf_files = get_pdf_files(drive_svc, folder_id)
    print(f"  → {len(pdf_files)}件のPDFが見つかりました")
    if not pdf_files:
        print("  PDFが見つかりませんでした。フォルダIDを確認してください。")
        return

    # 既存タイトル取得（重複スキップ用）
    existing = get_existing_titles(ws)
    print(f"  → 既存登録済み: {len(existing)}件")

    # 各PDFを処理
    print("\n[3/5] PDFを解析してコマ案を生成中...")
    success, skipped, error = 0, 0, 0

    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_name = pdf_file["name"]
        pdf_id   = pdf_file["id"]
        print(f"\n  [{i}/{len(pdf_files)}] {pdf_name}")

        try:
            # PDF取得
            print("    - PDFをダウンロード中...")
            pdf_bytes = download_pdf_as_bytes(drive_svc, pdf_id)

            # タイトル・要約抽出
            print("    - Claude Visionで解析中...")
            info = extract_pdf_info(claude, pdf_bytes)
            title   = info["title"]
            summary = info["summary"]
            print(f"    - タイトル: {title}")

            # 重複チェック
            if title in existing:
                print(f"    - スキップ（既に登録済み）")
                skipped += 1
                continue

            # 4コマ案生成
            print("    - 4コマ案を生成中...")
            panels = generate_panel_concepts(claude, title, summary)

            # Sheetsに書き込み
            print("    - Google Sheetsに書き込み中...")
            append_init_row(ws, {
                "title":    title,
                "summary":  summary,
                "panel1":   panels["panel1"],
                "panel2":   panels["panel2"],
                "panel3":   panels["panel3"],
                "panel4":   panels["panel4"],
                "post_text": panels["post_text"],
            })
            existing.add(title)
            success += 1
            print(f"    ✅ 完了")

            # レート制限対策
            time.sleep(2)

        except Exception as e:
            print(f"    ❌ エラー: {e}")
            error += 1

    print(f"\n[完了] 成功: {success}件 / スキップ: {skipped}件 / エラー: {error}件")


# ===== reviseモード =====
def run_revise():
    print("=" * 50)
    print("【reviseモード】修正依頼を反映して最終案を生成します")
    print("=" * 50)

    # 設定取得
    anthropic_key    = get_env("ANTHROPIC_API_KEY")
    sheets_id        = get_env("GOOGLE_SHEETS_ID")
    credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    token_path       = os.getenv("GOOGLE_TOKEN_PATH", "token.json")
    sheet_name       = os.getenv("SHEET_NAME", "どり漫画管理")

    # クライアント初期化
    print("\n[1/3] クライアントを初期化中...")
    claude = anthropic.Anthropic(api_key=anthropic_key)
    gc     = build_sheets_client(credentials_path, token_path)
    ws     = get_or_create_sheet(gc, sheets_id, sheet_name)

    # 修正依頼が入っている行を取得
    print("\n[2/3] 修正依頼が入っている行を検索中...")
    rows = get_rows_with_revision_notes(ws)
    print(f"  → {len(rows)}行が対象")
    if not rows:
        print("  修正依頼が入っている行が見つかりませんでした。")
        print("  D/G/J/M列に修正依頼を入力してから再実行してください。")
        return

    # 修正案生成
    print("\n[3/3] 修正案を生成中...")
    success, error = 0, 0

    for row_data in rows:
        row_idx = row_data["row_index"]
        title   = row_data["title"]
        print(f"\n  行{row_idx}: {title}")

        for panel_num, revision in row_data["revisions"].items():
            print(f"    - {panel_num}コマ目の修正案を生成中...")
            try:
                revised = revise_panel(
                    client=claude,
                    title=title,
                    panel_number=panel_num,
                    original_concept=revision["draft"],
                    revision_request=revision["note"]
                )
                update_final_panel(ws, row_idx, panel_num, revised)
                print(f"    ✅ {panel_num}コマ目 完了")
                success += 1
                time.sleep(1)
            except Exception as e:
                print(f"    ❌ {panel_num}コマ目 エラー: {e}")
                error += 1

    print(f"\n[完了] 成功: {success}件 / エラー: {error}件")


# ===== メイン =====
def main():
    if len(sys.argv) < 2:
        print("使い方:")
        print("  python src/run.py init    # 初回実行（PDFを読み込んでコマ案①を生成）")
        print("  python src/run.py revise  # 修正実行（修正依頼を反映して最終案を生成）")
        sys.exit(1)

    mode = sys.argv[1].lower()
    if mode == "init":
        run_init()
    elif mode == "revise":
        run_revise()
    else:
        print(f"[ERROR] 不明なモード: {mode}（init / revise のどちらかを指定してください）")
        sys.exit(1)


if __name__ == "__main__":
    main()

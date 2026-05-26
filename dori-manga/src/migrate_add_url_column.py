"""
既存スプレッドシートへの移行スクリプト

【役割】
  すでに書き込み済みのスプレッドシートに対して以下を実行します：
  1. B列（PDF URL）を挿入（既存のB列以降を1列右シフト）
  2. 既存5件の行に PDF URL を書き込み
  3. GoogleドライブのPDFファイル名に「（済）」を付与

【実行方法】
  cd dori-manga
  python src/migrate_add_url_column.py

【注意】
  一度だけ実行してください。二回目以降は列がずれます。
  実行前にスプレッドシートをバックアップすることを推奨します。
"""

import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import gspread

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
TOKEN_PATH       = os.getenv("GOOGLE_TOKEN_PATH", "token.json")
SHEETS_ID        = os.getenv("GOOGLE_SHEETS_ID", "")
SHEET_NAME       = os.getenv("SHEET_NAME", "どり漫画管理")

# 既存5件のタイトルとPDF情報のマッピング
PDF_MAP = {
    "酸素マスク": {
        "pdf_id":  "1LoLLfMK6v0Uv_0sQ29oUXLgHjXTPR-xk",
        "pdf_url": "https://drive.google.com/file/d/1LoLLfMK6v0Uv_0sQ29oUXLgHjXTPR-xk/view",
    },
    "酸素療法の毒": {
        "pdf_id":  "1uh3fzhxFFNLa7rDo4BWdJTrwL87A_Uzr",
        "pdf_url": "https://drive.google.com/file/d/1uh3fzhxFFNLa7rDo4BWdJTrwL87A_Uzr/view",
    },
    "人工呼吸器アラーム": {
        "pdf_id":  "1phW5TFNjdZKzRRAS0weUsZ23l2HbSTOL",
        "pdf_url": "https://drive.google.com/file/d/1phW5TFNjdZKzRRAS0weUsZ23l2HbSTOL/view",
    },
    "胸水の見方": {
        "pdf_id":  "1gC6QnuWYZ6XpHUVh-8uuIjxIH7tW8qrb",
        "pdf_url": "https://drive.google.com/file/d/1gC6QnuWYZ6XpHUVh-8uuIjxIH7tW8qrb/view",
    },
    "P波の見つけ方": {
        "pdf_id":  "1hug0AYwah2K3FPVQS59K-ZfJIBzCW3E4",
        "pdf_url": "https://drive.google.com/file/d/1hug0AYwah2K3FPVQS59K-ZfJIBzCW3E4/view",
    },
}


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return creds


def main():
    print("=" * 60)
    print("  どり漫画管理 — B列（PDF URL）追加マイグレーション")
    print("=" * 60)

    if not SHEETS_ID:
        print("[ERROR] .env に GOOGLE_SHEETS_ID が設定されていません。")
        import sys; sys.exit(1)

    # 認証
    print("\n[1/4] Google認証中...")
    creds = get_credentials()
    gc = gspread.authorize(creds)
    sheets_service = build("sheets", "v4", credentials=creds)
    drive_service  = build("drive",  "v3", credentials=creds)
    print("  ✅ 認証完了")

    # シートを開く
    print("\n[2/4] スプレッドシートに接続中...")
    spreadsheet = gc.open_by_key(SHEETS_ID)
    ws = spreadsheet.worksheet(SHEET_NAME)
    sheet_grid_id = spreadsheet.fetch_sheet_metadata()["sheets"][0]["properties"]["sheetId"]
    print(f"  ✅ 接続完了 (sheetId={sheet_grid_id})")

    # B列（index=1）に空列を挿入
    print("\n[3/4] B列を挿入中（既存列を右シフト）...")
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=SHEETS_ID,
        body={"requests": [{
            "insertDimension": {
                "range": {
                    "sheetId": sheet_grid_id,
                    "dimension": "COLUMNS",
                    "startIndex": 1,  # B列
                    "endIndex": 2,
                },
                "inheritFromBefore": False,
            }
        }]},
    ).execute()
    print("  ✅ B列挿入完了")

    # B1にヘッダーを書く
    ws.update_cell(1, 2, "PDF URL")
    print("  ✅ ヘッダー「PDF URL」を B1 に書き込み")

    # 既存データの各行を検索してPDF URLを書き込み
    print("\n[4/4] 既存行にPDF URLを書き込み＋Driveリネーム...")
    all_titles = ws.col_values(1)  # A列のタイトル一覧
    wrote, renamed = 0, 0

    for row_idx, title in enumerate(all_titles):
        title = title.strip()
        if title not in PDF_MAP:
            continue
        info = PDF_MAP[title]
        row_number = row_idx + 1  # 1始まり

        # PDF URLをB列に書き込み
        ws.update_cell(row_number, 2, info["pdf_url"])
        print(f"  ✅ URL書き込み ({row_number}行目): {title}")
        wrote += 1

        # Driveリネーム
        pdf_id = info["pdf_id"]
        try:
            meta = drive_service.files().get(fileId=pdf_id, fields="name").execute()
            current_name = meta.get("name", "")
            if current_name.startswith("（済）"):
                print(f"  ⏭  すでに（済）: {current_name}")
            else:
                new_name = "（済）" + current_name
                drive_service.files().update(
                    fileId=pdf_id,
                    body={"name": new_name},
                ).execute()
                print(f"  ✅ リネーム完了: {current_name} → {new_name}")
                renamed += 1
        except Exception as e:
            print(f"  [WARN] リネーム失敗 (id={pdf_id}): {e}")

    print(f"\n✅ マイグレーション完了:")
    print(f"  URL書き込み {wrote}件")
    print(f"  Driveリネーム {renamed}件")
    print(f"\nスプレッドシート: https://docs.google.com/spreadsheets/d/{SHEETS_ID}/edit")


if __name__ == "__main__":
    main()

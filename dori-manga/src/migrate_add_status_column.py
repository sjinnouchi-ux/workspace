"""
スプレッドシートに「完了」ドロップダウン列と「画像格納フォルダ」列を追加するスクリプト

【実行後の列構成】
  A: 完了（プルダウン）   ← 今回新規追加
  B: タイトル            ← 旧A
  C: PDF URL             ← 旧B
  D: 内容要約            ← 旧C
  E〜G: 1コマ目_案①/修正依頼/最終案
  H〜J: 2コマ目_案①/修正依頼/最終案
  K〜M: 3コマ目_案①/修正依頼/最終案
  N〜P: 4コマ目_案①/修正依頼/最終案
  Q: Instagram投稿文章案 ← 旧P
  R: 画像格納フォルダ    ← 今回新規追加

【書式設定】
  - A列セル: "完了" のみ選択できるドロップダウン
  - 条件付き書式: A列に "完了" が入力された行全体を薄灰色で塗りつぶし

【実行方法】
  cd dori-manga
  python src/migrate_add_status_column.py

【注意】
  一度だけ実行してください。二回目以降は列がずれます。
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

MAX_ROW = 1000  # バリデーション・条件付き書式の適用行数


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
    print("=" * 65)
    print("  どり漫画管理 — 完了列・画像格納フォルダ列 追加マイグレーション")
    print("=" * 65)

    if not SHEETS_ID:
        print("[ERROR] .env に GOOGLE_SHEETS_ID が設定されていません。")
        import sys; sys.exit(1)

    # 認証
    print("\n[1/6] Google認証中...")
    creds = get_credentials()
    gc = gspread.authorize(creds)
    sheets_service = build("sheets", "v4", credentials=creds)
    print("  ✅ 認証完了")

    # シートを開く
    print("\n[2/6] スプレッドシートに接続中...")
    spreadsheet = gc.open_by_key(SHEETS_ID)
    ws = spreadsheet.worksheet(SHEET_NAME)
    sheet_grid_id = spreadsheet.fetch_sheet_metadata()["sheets"][0]["properties"]["sheetId"]
    print(f"  ✅ 接続完了 (sheetId={sheet_grid_id})")

    # A列（index=0）に新規列を挿入
    print("\n[3/6] A列を挿入中（既存列を右シフト）...")
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=SHEETS_ID,
        body={"requests": [{
            "insertDimension": {
                "range": {
                    "sheetId": sheet_grid_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 1,
                },
                "inheritFromBefore": False,
            }
        }]},
    ).execute()
    print("  ✅ A列挿入完了")

    # A1ヘッダーと R1「画像格納フォルダ」ヘッダー
    ws.update_cell(1, 1, "完了")
    ws.update_cell(1, 18, "画像格納フォルダ")
    print("  ✅ A1 ← 「完了」, R1 ← 「画像格納フォルダ」 を書き込み")

    # ドロップダウン（データ検証）を A2:A1000 に設定
    print("\n[4/6] ドロップダウン（完了）を A列に設定中...")
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=SHEETS_ID,
        body={"requests": [{
            "setDataValidation": {
                "range": {
                    "sheetId": sheet_grid_id,
                    "startRowIndex": 1,        # 2行目（0始まり）
                    "endRowIndex": MAX_ROW,
                    "startColumnIndex": 0,     # A列
                    "endColumnIndex": 1,
                },
                "rule": {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [{"userEnteredValue": "完了"}],
                    },
                    "showCustomUi": True,
                    "strict": False,
                },
            }
        }]},
    ).execute()
    print("  ✅ ドロップダウン設定完了")

    # 条件付き書式：A列が「完了」の行全体を薄灰色に
    print("\n[5/6] 条件付き書式（完了→薄灰色）を設定中...")
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=SHEETS_ID,
        body={"requests": [{
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": sheet_grid_id,
                        "startRowIndex": 1,
                        "endRowIndex": MAX_ROW,
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "CUSTOM_FORMULA",
                            "values": [{"userEnteredValue": '=$A2="完了"'}],
                        },
                        "format": {
                            "backgroundColor": {
                                "red": 0.85,
                                "green": 0.85,
                                "blue": 0.85,
                            }
                        },
                    },
                },
                "index": 0,
            }
        }]},
    ).execute()
    print("  ✅ 条件付き書式設定完了")

    # A列の列幅を調整（完了列は狭く）
    print("\n[6/6] 列幅を調整中...")
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=SHEETS_ID,
        body={"requests": [
            # A列（完了）: 80px
            {"updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_grid_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 1,
                },
                "properties": {"pixelSize": 80},
                "fields": "pixelSize",
            }},
            # R列（画像格納フォルダ）: 250px
            {"updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_grid_id,
                    "dimension": "COLUMNS",
                    "startIndex": 17,
                    "endIndex": 18,
                },
                "properties": {"pixelSize": 250},
                "fields": "pixelSize",
            }},
        ]},
    ).execute()
    print("  ✅ 列幅調整完了")

    print("\n" + "=" * 65)
    print("  ✅ マイグレーション完了！")
    print("=" * 65)
    print(f"\n【確認】スプレッドシートを開いて以下を確認してください：")
    print(f"  1. A列に「完了」ドロップダウンが表示される")
    print(f"  2. A列に「完了」を選択すると行全体が薄灰色になる")
    print(f"  3. R列に「画像格納フォルダ」ヘッダーがある")
    print(f"\nスプレッドシート: https://docs.google.com/spreadsheets/d/{SHEETS_ID}/edit\n")


if __name__ == "__main__":
    main()

"""
どり看護師 漫画管理スプレッドシート セットアップスクリプト

【実行方法】
  cd dori-manga
  python src/setup_sheets.py

【初回実行時】
  ブラウザが自動で開きます。s.jinnouchi@yumekango.com でログインして「許可」をクリック。
  認証後 token.json が自動生成され、次回以降はブラウザ不要。

【実行後】
  スプレッドシートIDが表示されます。そのIDを .env の GOOGLE_SHEETS_ID に貼り付けてください。
"""

import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
TOKEN_PATH       = os.getenv("GOOGLE_TOKEN_PATH", "token.json")
SHEET_NAME       = os.getenv("SHEET_NAME", "どり漫画管理")

HEADER_ROW = [
    "タイトル",
    "内容要約",
    "1コマ目_案①", "1コマ目_修正依頼", "1コマ目_最終案",
    "2コマ目_案①", "2コマ目_修正依頼", "2コマ目_最終案",
    "3コマ目_案①", "3コマ目_修正依頼", "3コマ目_最終案",
    "4コマ目_案①", "4コマ目_修正依頼", "4コマ目_最終案",
    "Instagram投稿文章案",
]


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
    print("=" * 55)
    print("  どり看護師 漫画管理スプレッドシート セットアップ")
    print("=" * 55)

    # 認証
    print("\n[1/3] Google認証中...")
    print("  ※ 初回実行時はブラウザが開きます。Googleアカウントで認証してください。")
    creds = get_credentials()
    print("  ✅ 認証完了")

    # スプレッドシート作成
    print("\n[2/3] スプレッドシートを作成中...")
    service = build("sheets", "v4", credentials=creds)
    spreadsheet = service.spreadsheets().create(body={
        "properties": {"title": "どり看護師_漫画管理"},
        "sheets": [{"properties": {"title": SHEET_NAME}}],
    }).execute()

    sheet_id = spreadsheet["spreadsheetId"]
    sheet_grid_id = spreadsheet["sheets"][0]["properties"]["sheetId"]
    print(f"  ✅ 作成完了")
    print(f"  → スプレッドシートID: {sheet_id}")
    print(f"  → URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")

    # ヘッダー書き込み
    print("\n[3/3] ヘッダーを設定中...")
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=f"{SHEET_NAME}!A1",
        valueInputOption="RAW",
        body={"values": [HEADER_ROW]},
    ).execute()

    # ヘッダーを太字・水色背景で装飾
    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={"requests": [{
            "repeatCell": {
                "range": {
                    "sheetId": sheet_grid_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.68, "green": 0.85, "blue": 1.0
                        },
                        "textFormat": {"bold": True},
                        "wrapStrategy": "WRAP",
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,wrapStrategy)",
            }
        }]},
    ).execute()

    # 列幅を調整（A列:タイトル、B列:要約を広く）
    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={"requests": [
            {"updateDimensionProperties": {
                "range": {"sheetId": sheet_grid_id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1},
                "properties": {"pixelSize": 180},
                "fields": "pixelSize",
            }},
            {"updateDimensionProperties": {
                "range": {"sheetId": sheet_grid_id, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2},
                "properties": {"pixelSize": 250},
                "fields": "pixelSize",
            }},
            {"updateDimensionProperties": {
                "range": {"sheetId": sheet_grid_id, "dimension": "COLUMNS", "startIndex": 2, "endIndex": 15},
                "properties": {"pixelSize": 220},
                "fields": "pixelSize",
            }},
        ]},
    ).execute()

    print("  ✅ ヘッダー設定完了")

    print("\n" + "=" * 55)
    print("  ✅ セットアップ完了！")
    print("=" * 55)
    print(f"\n【重要】.env ファイルに以下を追記してください:")
    print(f"\n  GOOGLE_SHEETS_ID={sheet_id}\n")
    print(f"スプレッドシートURL:")
    print(f"  https://docs.google.com/spreadsheets/d/{sheet_id}/edit\n")


if __name__ == "__main__":
    main()

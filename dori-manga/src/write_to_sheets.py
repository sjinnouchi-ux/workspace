"""
Cowork生成コンテンツをスプレッドシートに書き込むスクリプト

【役割】
  CoworkがPDFを読み込んで生成した4コマ案をJSONで渡すと、
  スプレッドシートに追記します。AnthropicのAPIキーは不要です。
  書き込み完了後、GoogleドライブのPDFファイル名を「（済）」で始まる名前にリネームします。

【実行方法】
  cd dori-manga
  python src/write_to_sheets.py output.json

【JSONフォーマット（Coworkが出力）】
  {
    "title":    "タイトル（10文字以内）",
    "pdf_url":  "https://drive.google.com/file/d/<ID>/view",
    "pdf_id":   "<GoogleドライブのファイルID>",
    "summary":  "内容の要約",
    "panel1":   "1コマ目の案",
    "panel2":   "2コマ目の案",
    "panel3":   "3コマ目の案",
    "panel4":   "4コマ目の案（→まとめへの誘導含む）",
    "post_text":"Instagram投稿文章案（絵文字可・200文字）"
  }

  または複数まとめて配列で渡すことも可:
  [
    { "title": "...", ... },
    { "title": "...", ... }
  ]
"""

import sys
import os
import json
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

# カラムインデックス（1始まり）
# A列に「完了」ドロップダウンを追加後の構成（18列）
COL = {
    "status":   1,   # A: 完了（ドロップダウン）
    "title":    2,   # B: タイトル
    "pdf_url":  3,   # C: PDF URL
    "summary":  4,   # D: 内容要約
    "p1_draft": 5,   # E: 1コマ目_案①
    "p1_note":  6,   # F: 1コマ目_修正依頼
    "p1_final": 7,   # G: 1コマ目_最終案
    "p2_draft": 8,   # H: 2コマ目_案①
    "p2_note":  9,   # I: 2コマ目_修正依頼
    "p2_final": 10,  # J: 2コマ目_最終案
    "p3_draft": 11,  # K: 3コマ目_案①
    "p3_note":  12,  # L: 3コマ目_修正依頼
    "p3_final": 13,  # M: 3コマ目_最終案
    "p4_draft": 14,  # N: 4コマ目_案①
    "p4_note":  15,  # O: 4コマ目_修正依頼
    "p4_final": 16,  # P: 4コマ目_最終案
    "post_text":17,  # Q: Instagram投稿文章案
    "folder":   18,  # R: 画像格納フォルダ
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


def rename_drive_file(drive_service, file_id: str, prefix: str = "（済）") -> str:
    """GoogleドライブのファイルにPREFIXを付けてリネームする。
    すでにPREFIXで始まっている場合はスキップ。
    Returns: 'renamed' | 'skipped' | 'error'
    """
    try:
        meta = drive_service.files().get(fileId=file_id, fields="name").execute()
        current_name = meta.get("name", "")
        if current_name.startswith(prefix):
            return "skipped"
        new_name = prefix + current_name
        drive_service.files().update(
            fileId=file_id,
            body={"name": new_name},
        ).execute()
        return "renamed"
    except Exception as e:
        print(f"    [WARN] Driveリネーム失敗 (id={file_id}): {e}")
        return "error"


def write_row(ws: gspread.Worksheet, data: dict, existing_titles: set) -> str:
    """1件のコマ案をスプレッドシートに追記する。重複はスキップ。"""
    title = data.get("title", "").strip()
    if not title:
        return "skip_no_title"
    if title in existing_titles:
        return "skip_duplicate"

    row = [""] * 18
    # A列（完了）は空欄のまま（ユーザーが手動でドロップダウン選択）
    row[COL["title"] - 1]     = title
    row[COL["pdf_url"] - 1]   = data.get("pdf_url", "")
    row[COL["summary"] - 1]   = data.get("summary", "")
    row[COL["p1_draft"] - 1]  = data.get("panel1", "")
    row[COL["p2_draft"] - 1]  = data.get("panel2", "")
    row[COL["p3_draft"] - 1]  = data.get("panel3", "")
    row[COL["p4_draft"] - 1]  = data.get("panel4", "")
    row[COL["post_text"] - 1] = data.get("post_text", "")
    row[COL["folder"] - 1]    = data.get("folder", "")  # R: 画像格納フォルダURL
    ws.append_row(row)
    return "ok"


def main():
    if len(sys.argv) < 2:
        print("使い方: python src/write_to_sheets.py <JSONファイルパス>")
        print("例:     python src/write_to_sheets.py output.json")
        sys.exit(1)

    json_path = sys.argv[1]
    if not os.path.exists(json_path):
        print(f"[ERROR] ファイルが見つかりません: {json_path}")
        sys.exit(1)

    if not SHEETS_ID:
        print("[ERROR] .env に GOOGLE_SHEETS_ID が設定されていません。")
        print("  setup_sheets.py を先に実行してください。")
        sys.exit(1)

    # JSONを読み込む
    with open(json_path, encoding="utf-8") as f:
        raw = json.load(f)
    items = raw if isinstance(raw, list) else [raw]
    print(f"  → {len(items)}件のコマ案を読み込みました")

    # 認証
    print("\n[1/4] Google認証中...")
    creds = get_credentials()
    gc = gspread.authorize(creds)
    drive_service = build("drive", "v3", credentials=creds)
    print("  ✅ 認証完了")

    # シートを開く
    print("\n[2/4] スプレッドシートに接続中...")
    spreadsheet = gc.open_by_key(SHEETS_ID)
    ws = spreadsheet.worksheet(SHEET_NAME)
    existing_titles = set(ws.col_values(COL["title"])[1:])  # ヘッダー除く
    print(f"  ✅ 接続完了（既存: {len(existing_titles)}件）")

    # 書き込み
    print("\n[3/4] 書き込み中...")
    ok, skipped = 0, 0
    written_items = []
    for item in items:
        title = item.get("title", "(タイトルなし)")
        result = write_row(ws, item, existing_titles)
        if result == "ok":
            existing_titles.add(item["title"])
            print(f"  ✅ {title}")
            ok += 1
            written_items.append(item)
        else:
            reason = "重複" if result == "skip_duplicate" else "タイトルなし"
            print(f"  ⏭ スキップ ({reason}): {title}")
            skipped += 1

    # Driveリネーム
    print("\n[4/4] GoogleドライブのPDFをリネーム中...")
    renamed, rename_skipped = 0, 0
    for item in written_items:
        pdf_id = item.get("pdf_id", "").strip()
        title  = item.get("title", "(タイトルなし)")
        if not pdf_id:
            print(f"  ⏭ pdf_idなし（リネームスキップ）: {title}")
            rename_skipped += 1
            continue
        result = rename_drive_file(drive_service, pdf_id)
        if result == "renamed":
            print(f"  ✅ （済）リネーム完了: {title}")
            renamed += 1
        elif result == "skipped":
            print(f"  ⏭ すでに（済）: {title}")
            rename_skipped += 1
        else:
            rename_skipped += 1

    print(f"\n✅ 完了:")
    print(f"  書き込み {ok}件 / スキップ {skipped}件")
    print(f"  リネーム {renamed}件 / スキップ {rename_skipped}件")
    print(f"スプレッドシート: https://docs.google.com/spreadsheets/d/{SHEETS_ID}/edit")


if __name__ == "__main__":
    main()

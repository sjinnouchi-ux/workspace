"""
Google Sheets操作モジュール
漫画管理スプレッドシートの読み書き

認証方式: OAuth2 デスクトップアプリ（QQQプロジェクトと共通）
  - credentials.json: Google Cloud Console からダウンロードしたOAuth2クライアント認証情報
  - token.json: 初回認証後に自動生成されるアクセストークン（2回目以降はブラウザ不要）
"""

import os
import gspread
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


# カラムインデックス定義（1始まり）
COL = {
    "title":    1,   # A: タイトル
    "summary":  2,   # B: 要約
    "p1_draft": 3,   # C: 1コマ目_案①
    "p1_note":  4,   # D: 1コマ目_修正依頼
    "p1_final": 5,   # E: 1コマ目_修正案
    "p2_draft": 6,   # F: 2コマ目_案①
    "p2_note":  7,   # G: 2コマ目_修正依頼
    "p2_final": 8,   # H: 2コマ目_修正案
    "p3_draft": 9,   # I: 3コマ目_案①
    "p3_note":  10,  # J: 3コマ目_修正依頼
    "p3_final": 11,  # K: 3コマ目_修正案
    "p4_draft": 12,  # L: 4コマ目_案①
    "p4_note":  13,  # M: 4コマ目_修正依頼
    "p4_final": 14,  # N: 4コマ目_修正案
    "post_text":15,  # O: Instagram投稿文章案
}

HEADER_ROW = [
    "タイトル", "内容要約",
    "1コマ目_案①", "1コマ目_修正依頼", "1コマ目_修正案",
    "2コマ目_案①", "2コマ目_修正依頼", "2コマ目_修正案",
    "3コマ目_案①", "3コマ目_修正依頼", "3コマ目_修正案",
    "4コマ目_案①", "4コマ目_修正依頼", "4コマ目_修正案",
    "Instagram投稿文章案"
]


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def build_oauth_credentials(
    credentials_path: str = "credentials.json",
    token_path: str = "token.json"
) -> Credentials:
    """
    OAuth2 ユーザー認証情報を構築する（QQQプロジェクトと同じ方式）。

    初回: ブラウザが開いてGoogleアカウントで認証 → token.json が自動生成
    2回目以降: token.json を読み込んで自動更新（ブラウザ不要）
    """
    creds = None

    # 既存トークンを読み込む
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # トークンが無効または期限切れの場合は再認証
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # トークンを保存
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return creds


def build_sheets_client(
    credentials_path: str = "credentials.json",
    token_path: str = "token.json"
) -> gspread.Client:
    """gspreadクライアントを構築する（OAuth2認証）"""
    creds = build_oauth_credentials(credentials_path, token_path)
    return gspread.authorize(creds)


def get_or_create_sheet(gc: gspread.Client, sheet_id: str, sheet_name: str) -> gspread.Worksheet:
    """
    スプレッドシートを開き、指定シートを取得（なければ作成）
    """
    spreadsheet = gc.open_by_key(sheet_id)
    try:
        ws = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=sheet_name, rows=500, cols=20)
        ws.append_row(HEADER_ROW)
        # ヘッダー行を太字・背景色で装飾
        ws.format("A1:O1", {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 1.0}
        })
    return ws


def get_existing_titles(ws: gspread.Worksheet) -> set[str]:
    """既に登録済みのタイトル一覧を返す（重複登録防止）"""
    titles = ws.col_values(COL["title"])
    return set(titles[1:])  # ヘッダー除く


def append_init_row(ws: gspread.Worksheet, data: dict) -> None:
    """
    initモード用：新規行を追加する

    data keys: title, summary, panel1, panel2, panel3, panel4, post_text
    """
    row = [""] * 15
    row[COL["title"] - 1]    = data["title"]
    row[COL["summary"] - 1]  = data["summary"]
    row[COL["p1_draft"] - 1] = data["panel1"]
    row[COL["p2_draft"] - 1] = data["panel2"]
    row[COL["p3_draft"] - 1] = data["panel3"]
    row[COL["p4_draft"] - 1] = data["panel4"]
    row[COL["post_text"] - 1] = data["post_text"]
    ws.append_row(row)


def get_rows_with_revision_notes(ws: gspread.Worksheet) -> list[dict]:
    """
    reviseモード用：修正依頼（D/G/J/M列）が入っているが最終案（E/H/K/N列）が空の行を返す

    Returns:
        [{"row_index": 2, "title": "...", "revisions": {1: "修正依頼", ...}}, ...]
    """
    all_rows = ws.get_all_values()
    targets = []
    for i, row in enumerate(all_rows[1:], start=2):  # ヘッダースキップ、1始まり行番号

        def val(col_key):
            idx = COL[col_key] - 1
            return row[idx] if idx < len(row) else ""

        revisions = {}
        for panel_num, (draft_key, note_key, final_key) in enumerate([
            ("p1_draft", "p1_note", "p1_final"),
            ("p2_draft", "p2_note", "p2_final"),
            ("p3_draft", "p3_note", "p3_final"),
            ("p4_draft", "p4_note", "p4_final"),
        ], start=1):
            note = val(note_key)
            final = val(final_key)
            if note and not final:
                revisions[panel_num] = {
                    "note": note,
                    "draft": val(draft_key)
                }

        if revisions:
            targets.append({
                "row_index": i,
                "title": val("title"),
                "revisions": revisions
            })

    return targets


def update_final_panel(ws: gspread.Worksheet, row_index: int, panel_number: int, text: str) -> None:
    """
    reviseモード用：指定行の最終案列を更新する
    """
    final_keys = {1: "p1_final", 2: "p2_final", 3: "p3_final", 4: "p4_final"}
    col_index = COL[final_keys[panel_number]]
    ws.update_cell(row_index, col_index, text)

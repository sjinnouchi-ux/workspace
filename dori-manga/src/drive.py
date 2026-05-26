"""
Google Drive操作モジュール
PDFファイルの一覧取得とダウンロード
"""

import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


def get_pdf_files(service, folder_id: str) -> list[dict]:
    """
    指定フォルダ内のPDFファイル一覧を取得する

    Returns:
        [{"id": "...", "name": "..."}, ...]
    """
    results = []
    page_token = None

    while True:
        query = f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"
        response = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, createdTime)",
            orderBy="createdTime",
            pageToken=page_token
        ).execute()

        results.extend(response.get("files", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return results


def download_pdf_as_bytes(service, file_id: str) -> bytes:
    """
    指定ファイルIDのPDFをバイト列としてダウンロードする
    """
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buffer.getvalue()


def build_drive_service(credentials):
    """Google Drive APIサービスを構築する"""
    return build("drive", "v3", credentials=credentials)

"""
PDF解析モジュール
画像ベースのPDFをClaude Vision APIで解析し、タイトルと要約を抽出する
"""

import base64
import anthropic


def extract_pdf_info(client: anthropic.Anthropic, pdf_bytes: bytes) -> dict:
    """
    Claude Vision APIでPDFを解析し、タイトルと要約を返す

    Returns:
        {"title": "酸素マスク", "summary": "酸素マスクの適応と..."}
    """
    pdf_b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": """このPDFはInstagram看護師向け学習コンテンツです。
以下の2点を抽出してください。

1. タイトル（PDF1ページ目の見出しテーマ、10文字以内）
2. 要約（内容を3〜5行で簡潔にまとめたもの）

以下のJSON形式で返してください：
{
  "title": "タイトルここ",
  "summary": "要約ここ"
}

JSONのみ返してください（説明文不要）。"""
                    }
                ],
            }
        ],
    )

    import json
    text = message.content[0].text.strip()
    # コードブロックを除去
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())

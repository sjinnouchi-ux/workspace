"""
漫画コマ案生成モジュール
PDFの内容を元に、どり看護師の4コマ導入漫画のコマ案と投稿文章を生成する
"""

import json
import anthropic


# ===== キャラクター・スタイル設定 =====
STYLE_GUIDE = """
【登場キャラクター】
・どり看護師：ピンクのウサギ、聴診器を装着。落ち着いていて、たまにクスッとさせる一言を言う。
・看護師：ポニーテールの女性。真面目で一生懸命。よく驚く。

【漫画スタイル】
・手描き風の白黒漫画（どりちゃんのみピンク）
・舞台は医療現場（ICU・病棟・外来など）
・クスッと笑えるユーモアを入れる
・吹き出しのセリフは短くリズムよく
・擬音語（ピピピピ！ざわ…など）を効果的に使う
"""

# ===== 4コマ構成パターン =====
PANEL_PATTERN = """
【4コマの構成パターン】
1コマ目: 日常シーン導入。深夜や日中の医療現場。看護師とどりちゃんが登場。読者が共感できる「あるある」状況。
2コマ目: 問題発生・ドラマティックな転換。そのPDFテーマが「問題」として現れる瞬間。アラームや急変など。
3コマ目: 看護師が戸惑い・疑問を持つ。「え？なんで？」「どうすれば？」という読者の疑問を代弁する。
4コマ目: どりちゃんが解説を予告。「〇〇について一緒に確認しよう！」のような一言 + 「→〇〇まとめへ」の誘導テキスト。
"""


def generate_panel_concepts(
    client: anthropic.Anthropic,
    title: str,
    summary: str
) -> dict:
    """
    PDFのタイトルと要約から4コマのコマ案を生成する

    Returns:
        {
            "panel1": "【場所】深夜のICU\n【どり】...\n【看護師】...\n【状況】...",
            "panel2": ...,
            "panel3": ...,
            "panel4": ...,
            "post_text": "Instagram投稿文章"
        }
    """
    prompt = f"""
あなたはInstagram看護師向けコンテンツ「どり看護師」の漫画ディレクターです。

{STYLE_GUIDE}

{PANEL_PATTERN}

以下の学習コンテンツを元に、4コマ導入漫画のコマ案を作成してください。

【テーマ】{title}
【内容要約】
{summary}

各コマについて以下の形式で記述してください：
- 場所・状況の説明
- どりちゃんのセリフや様子（あれば）
- 看護師のセリフや様子
- 擬音語や効果音（あれば）

また、Instagram投稿用の文章も作成してください（絵文字使用可、200文字程度）。

以下のJSON形式で返してください：
{{
  "panel1": "コマ1の内容説明",
  "panel2": "コマ2の内容説明",
  "panel3": "コマ3の内容説明",
  "panel4": "コマ4の内容説明（→〇〇まとめへ の誘導テキスト含む）",
  "post_text": "Instagram投稿文章"
}}

JSONのみ返してください（説明文不要）。
"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    text = message.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def revise_panel(
    client: anthropic.Anthropic,
    title: str,
    panel_number: int,
    original_concept: str,
    revision_request: str
) -> str:
    """
    修正依頼を元にコマ案を修正する

    Returns:
        修正後のコマ案テキスト
    """
    prompt = f"""
あなたはInstagram看護師向けコンテンツ「どり看護師」の漫画ディレクターです。

{STYLE_GUIDE}

テーマ「{title}」の{panel_number}コマ目について、以下の案を修正してください。

【元のコマ案】
{original_concept}

【修正依頼】
{revision_request}

修正後のコマ案のみを返してください（説明文不要）。
"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text.strip()

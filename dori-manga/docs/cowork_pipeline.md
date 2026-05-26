# どり看護師 漫画化パイプライン — 設計書

作成日：2026-05-23  
プロジェクト：dori-manga（GitHub: sjinnouchi-ux-workspace）

---

## 1. システム概要・フロー

**Cowork（Claude）中心の設計**です。AnthropicのAPIキーは不要。

```
【initフロー：コマ案の初回生成】

陣内さん → CoworkにPDFのGoogleドライブURLを貼る
         ↓
Cowork → PDFを画像認識（Vision）で読み込み
         ↓
Cowork → どり看護師スタイルの4コマ案＋Instagram投稿文を生成
         ↓
Cowork → output.json を出力
         ↓
ターミナル → python src/write_to_sheets.py output.json
         ↓
スプレッドシートに自動書き込み（C/F/I/L/O列）

---

【reviseフロー：修正対応】

陣内さん → スプレッドシートのD/G/J/M列に修正依頼を記入
         ↓
陣内さん → CoworkにスプレッドシートURLと「修正してください」を伝える
         ↓
Cowork → スプレッドシートを読み込み、修正依頼のある行を検出
         ↓
Cowork → 修正案を生成 → revised_output.json を出力
         ↓
ターミナル → python src/write_to_sheets.py revised_output.json
         ↓
スプレッドシートのE/H/K/N列に最終案を書き込み
```

---

## 2. スプレッドシート構造

**シート名：** どり漫画管理

| 列 | カラム名 | 役割 | 担当 |
|----|---------|------|------|
| A | タイトル | PDFのテーマ（10文字以内） | Cowork |
| B | 内容要約 | PDFの内容要約（3〜5行） | Cowork |
| C | 1コマ目_案① | 1コマ目の初期案 | Cowork |
| D | 1コマ目_修正依頼 | 修正指示 | 陣内さん |
| E | 1コマ目_最終案 | 修正反映後の案 | Cowork |
| F | 2コマ目_案① | 2コマ目の初期案 | Cowork |
| G | 2コマ目_修正依頼 | 修正指示 | 陣内さん |
| H | 2コマ目_最終案 | 修正反映後の案 | Cowork |
| I | 3コマ目_案① | 3コマ目の初期案 | Cowork |
| J | 3コマ目_修正依頼 | 修正指示 | 陣内さん |
| K | 3コマ目_最終案 | 修正反映後の案 | Cowork |
| L | 4コマ目_案① | 4コマ目の初期案 | Cowork |
| M | 4コマ目_修正依頼 | 修正指示 | 陣内さん |
| N | 4コマ目_最終案 | 修正反映後の案 | Cowork |
| O | Instagram投稿文章案 | 投稿用テキスト（絵文字可・200文字） | Cowork |

---

## 3. 4コマ構成パターン

### キャラクター設定
- **どり看護師**：ピンクのウサギ、聴診器を装着。落ち着いていて、たまにクスッとさせる一言。
- **看護師**：ポニーテールの女性。真面目で一生懸命。よく驚く。

### スタイル
- 手描き風の白黒漫画（どりちゃんのみピンク）
- 舞台：医療現場（ICU・病棟・外来など）
- クスッと笑えるユーモア
- 吹き出しのセリフは短くリズムよく
- 擬音語（ピピピピ！ざわ…など）を効果的に使う

### コマ構成
| コマ | 内容 |
|------|------|
| 1コマ目 | 日常シーン導入。深夜や日中の医療現場。読者が共感できる「あるある」状況。 |
| 2コマ目 | 問題発生。そのPDFテーマが「問題」として現れる瞬間。アラームや急変など。 |
| 3コマ目 | 看護師が戸惑い・疑問。「え？なんで？」という読者の疑問を代弁。 |
| 4コマ目 | どりちゃんが解説を予告。「〇〇について一緒に確認しよう！→〇〇まとめへ」 |

---

## 4. Coworkへの指示プロンプト（initモード）

以下のテキストをCoworkに貼り付けて使用する：

```
以下のGoogleドライブのPDFを読み込んで、どり看護師の4コマ漫画案を生成してください。

【PDFのURL】
（ここにGoogleドライブのPDF共有URLを貼る）

【キャラクター設定】
・どり看護師：ピンクのウサギ、聴診器を装着。落ち着いていて、たまにクスッとさせる一言を言う。
・看護師：ポニーテールの女性。真面目で一生懸命。よく驚く。

【4コマ構成】
1コマ目: 日常シーン導入（医療現場のあるある）
2コマ目: 問題発生（PDFテーマの問題がアラームや急変で現れる）
3コマ目: 看護師が戸惑い・疑問（「え？なんで？」）
4コマ目: どりちゃんが解説予告（「→〇〇まとめへ」の誘導含む）

【出力形式】
以下のJSONのみ出力してください（説明文不要）：
{
  "title": "タイトル（10文字以内）",
  "summary": "内容要約（3〜5行）",
  "panel1": "1コマ目の詳細（場所・どりのセリフ・看護師のセリフ・擬音）",
  "panel2": "2コマ目の詳細",
  "panel3": "3コマ目の詳細",
  "panel4": "4コマ目の詳細（→まとめへの誘導含む）",
  "post_text": "Instagram投稿文章（絵文字可・200文字程度）"
}
```

---

## 5. ファイル構成

```
dori-manga/
├── CLAUDE.md                      # プロジェクト概要
├── .env                           # 環境変数（Gitに含めない）
├── .gitignore                     # credentials.json等を除外
├── credentials.json               # OAuth2認証情報（Gitに含めない）
├── token.json                     # 認証トークン・自動生成（Gitに含めない）
├── requirements.txt               # Pythonライブラリ
├── docs/
│   ├── cowork_pipeline.md         # このファイル（設計書）
│   ├── concept.md                 # キャラクター・世界観設定
│   ├── episode_list.md            # エピソード管理
│   └── work_log.md                # 作業ログ
└── src/
    ├── setup_sheets.py            # スプレッドシート初回セットアップ
    └── write_to_sheets.py         # Cowork生成コンテンツをSheetsに書き込み
```

---

## 6. Pythonスクリプト全文

### src/setup_sheets.py

スプレッドシートを新規作成し、ヘッダーを設定する初回セットアップスクリプト。

**実行方法：**
```bash
cd dori-manga
pip install -r requirements.txt
python src/setup_sheets.py
```

**処理内容：**
1. OAuth2認証（初回のみブラウザが開く）
2. 「どり看護師_漫画管理」スプレッドシートを新規作成
3. 「どり漫画管理」シートにヘッダー行を設定（太字・水色背景）
4. 列幅を最適化
5. スプレッドシートIDを出力 → `.env` の `GOOGLE_SHEETS_ID` に設定

---

### src/write_to_sheets.py

CoworkがJSON形式で出力したコマ案をスプレッドシートに追記するスクリプト。

**実行方法：**
```bash
python src/write_to_sheets.py output.json
```

**JSONフォーマット（1件）：**
```json
{
  "title": "酸素マスク",
  "summary": "酸素マスクの適応と流量設定について...",
  "panel1": "【場所】深夜のICU\n【どり】zzz...\n【看護師】当直中...",
  "panel2": "【状況】アラーム鳴動\n【擬音】ピピピピ！\n【看護師】え！？",
  "panel3": "【看護師】なんでアラームが...？\n【どり】起動",
  "panel4": "【どり】酸素マスクについて一緒に確認しよう！\n→酸素マスクまとめへ",
  "post_text": "💉 深夜のICUでアラームが！\nどり看護師と一緒に酸素マスクを学ぼう📚\n..."
}
```

**複数件まとめて書き込む場合（配列形式）：**
```json
[
  { "title": "酸素マスク", ... },
  { "title": "気管吸引", ... }
]
```

---

## 7. 環境変数（.env）

```env
# Google OAuth2認証（QQQプロジェクト共通）
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.json

# スプレッドシート（setup_sheets.py実行後に設定）
GOOGLE_SHEETS_ID=（ここにスプレッドシートIDを貼る）
SHEET_NAME=どり漫画管理
```

> ⚠️ `credentials.json` / `token.json` / `.env` は `.gitignore` で除外済み。GitHubにアップしないこと。

---

## 8. 必要ライブラリ（requirements.txt）

```
gspread
google-auth
google-auth-oauthlib
google-api-python-client
python-dotenv
```

インストール：
```bash
pip install -r requirements.txt
```

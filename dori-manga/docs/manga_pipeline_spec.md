# 漫画自動化パイプライン 仕様書

## 概要

Instagram学習コンテンツ（PDF）を元に、どり看護師の「4コマ導入漫画」のコマ案を
Claude APIで自動生成し、Google Sheetsで管理するCLIパイプライン。

---

## ディレクトリ構成

```
dori-manga/
├── docs/
│   └── manga_pipeline_spec.md   # このファイル
├── src/
│   ├── run.py          # メインCLI（実行エントリーポイント）
│   ├── pdf_reader.py   # PDF解析（Claude Vision API）
│   ├── manga_gen.py    # 漫画コマ案生成（Claude API）
│   ├── sheets.py       # Google Sheets読み書き
│   └── drive.py        # Google Drive PDFリスト取得
└── .env.example        # 環境変数テンプレート
```

---

## Google Sheetsのカラム定義

| 列 | 内容 | 入力者 |
|----|------|--------|
| A | タイトル（PDF1枚目のタイトル） | Claude（自動） |
| B | 内容の要約（3〜5行） | Claude（自動） |
| C | 1コマ目_Claude案① | Claude（自動） |
| D | 1コマ目_修正依頼 | 人間（手動） |
| E | 1コマ目_Claude修正案 | Claude（自動） |
| F | 2コマ目_Claude案① | Claude（自動） |
| G | 2コマ目_修正依頼 | 人間（手動） |
| H | 2コマ目_Claude修正案 | Claude（自動） |
| I | 3コマ目_Claude案① | Claude（自動） |
| J | 3コマ目_修正依頼 | 人間（手動） |
| K | 3コマ目_Claude修正案 | Claude（自動） |
| L | 4コマ目_Claude案① | Claude（自動） |
| M | 4コマ目_修正依頼 | 人間（手動） |
| N | 4コマ目_Claude修正案 | Claude（自動） |
| O | Instagram投稿文章案 | Claude（自動） |

---

## 4コマの構成パターン（参考例より）

参考例：「痙攣対応」の4コマ導入
- コマ1: 深夜のICU。看護師が記録作業中、どりちゃんも傍らで疲弊気味。日常シーン。
- コマ2: ピピピピ！患者のアラームが鳴り、痙攣発生。「え！？痙攣？」と看護師が驚く。
- コマ3: どりちゃん「来たか…」と冷静に構える。
- コマ4: どりちゃん「痙攣対応、順番で覚えると大丈夫だよ！まずは応援要請と気道確保！」
         →「痙攣対応まとめへ」

### 各コマの役割

| コマ | 役割 | ポイント |
|------|------|---------|
| 1コマ目 | 日常導入・場面設定 | 読者が共感できる「あるある」シーン |
| 2コマ目 | 問題発生・ドラマティックな転換 | そのPDFテーマが「問題」として現れる瞬間 |
| 3コマ目 | 戸惑い・疑問 | 読者の「わかる…」「え？なんで？」を引き出す |
| 4コマ目 | どりちゃんが解説へ案内 | 「〇〇まとめへ→」で本編コンテンツへブリッジ |

---

## 登場キャラクター（スクリプトのプロンプト指示用）

| キャラ | 特徴 |
|--------|------|
| どり看護師 | ピンクのウサギ、聴診器装着。落ち着いていてたまにクスッとする発言をする |
| 看護師 | ポニーテールの女性。真面目で一生懸命。よく驚く |

---

## スクリプトの実行方法

### 事前準備

1. 依存ライブラリのインストール
```bash
pip install anthropic google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client gspread python-dotenv
```

2. `.env`ファイルの設定（`.env.example`をコピー）
```bash
cp .env.example .env
# .envを編集して各値を設定
```

3. Google Service Accountの設定
   - Google Cloud Consoleでサービスアカウントを作成
   - Google Drive API と Google Sheets API を有効化
   - 認証JSONをダウンロードして`credentials.json`として保存
   - 対象のGoogleシートとGoogleドライブフォルダにサービスアカウントのメールアドレスを共有

### モード1: 初回実行（PDFを読み込んで案①を生成）

```bash
cd dori-manga
python src/run.py init
```

処理内容：
- 指定のGoogleドライブフォルダ内のPDFを全件取得
- 各PDFをClaude Vision APIで解析（タイトル・要約抽出）
- 4コマ分のコマ案と投稿文章案を生成
- Google SheetsのA/B/C/F/I/L/O列に書き込み

### モード2: 修正実行（修正依頼を反映して最終案を生成）

```bash
cd dori-manga
python src/run.py revise
```

処理内容：
- Google SheetsのD/G/J/M列（修正依頼）が入力済みの行を検索
- 元のコマ案 + 修正依頼をClaude APIに渡して修正案を生成
- E/H/K/N列に最終案を書き込み

---

## 環境変数一覧

| 変数名 | 内容 |
|--------|------|
| `ANTHROPIC_API_KEY` | Anthropic APIキー |
| `GOOGLE_DRIVE_FOLDER_ID` | PDFが格納されているGoogleドライブのフォルダID |
| `GOOGLE_SHEETS_ID` | 管理用GoogleスプレッドシートのID |
| `GOOGLE_CREDENTIALS_PATH` | サービスアカウントJSONファイルのパス（デフォルト: `credentials.json`） |
| `SHEET_NAME` | シート名（デフォルト: `どり漫画管理`） |

---

## 処理フロー図

```
[initモード]
Googleドライブ
  └─ PDFリスト取得
       └─ 各PDF
            ├─ Claude Vision API → タイトル・要約抽出
            ├─ Claude API → 4コマ案生成（C/F/I/L列）
            └─ Claude API → Instagram投稿文案生成（O列）
                 └─ Google Sheetsに書き込み

[reviseモード]
Google Sheets
  └─ D/G/J/M列に修正依頼が入った行を検索
       └─ 各行
            └─ Claude API（元案 + 修正依頼） → 修正案生成（E/H/K/N列）
                 └─ Google Sheetsに書き込み
```

---

## 更新履歴

| 日付 | 更新内容 |
|------|----------|
| 2026-05-22 | 初版作成 |

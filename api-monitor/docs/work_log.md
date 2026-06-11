# APIモニター 作業ログ

---

## 2026-05-28｜プロジェクト初期化

### 背景

- KアラートプロジェクトでOpenAI APIを使い始めたことを契機に、API利用費用の可視化ニーズが発生
- 将来的にOpenAI・Anthropic・Googleの3社を使い分ける想定のため、一元管理ダッシュボードを構築する
- Streamlit（Python）＋SQLiteで構築し、ローカルMacで起動する方針に決定

### 対応内容

- `api-monitor/` プロジェクトをGitHubに作成
- `README.md` にプロジェクト概要・構成・セットアップ手順を記載
- `AGENTS.md` にAIエージェント向けの作業ガイドラインを記載
- `docs/implementation_plan.md` にPhase1〜5の実装計画を記載
- `docs/work_log.md`（本ファイル）を作成

### 設計決定事項

- **データ保存**：SQLite（`data/api_log.db`）。外部サービス不要でシンプルに管理
- **APIキー管理**：`.env` + `python-dotenv`。GAS Script Propertiesとは分離
- **画面構成**：モニタータブ（可視化）＋設定タブ（APIキー・用途管理）の2タブ構成
- **対応3社**：OpenAI・Anthropic・Google を初回から同時接続
- **コーディングモデル**：Claude Opus 4.7 を使用（コーディング性能が最高水準）

---

## 2026-05-28｜Phase 1〜2 実装完了（Claude Desktop / Cowork）

### 対応内容

#### Phase 1（土台）

- `requirements.txt` — streamlit / openai / anthropic / google-generativeai / python-dotenv / pandas / plotly
- `.env.example` — 3社APIキーのテンプレート
- `api-monitor/.gitignore` — `data/` `*.db` `.venv/` 等を追加除外（rootの`.env`除外と併用）
- `db.py` — SQLite層を実装
  - テーブル：`api_call_logs` / `api_keys` / `api_settings`
  - 関数：`init_db`, `insert_call_log`, `fetch_call_logs`, `summary_current_month`,
    `daily_cost_by_service`, `service_cost_share`,
    `upsert_api_key`, `get_api_key`, `list_api_keys`, `delete_api_key`,
    `upsert_setting`, `list_settings`, `delete_setting`
  - DBパスは `API_MONITOR_DB_PATH` で上書き可能。デフォルトは `data/api_log.db`
- `app.py` — Streamlitエントリーポイント。タブ切り替えのみ
- `monitor.py` — モニタータブのMVP（指標カード・日別費用折れ線・サービス別棒・最新50件履歴）
- `settings.py` — 設定タブのMVP（APIキー管理 / 用途カスタマイズフォーム）

#### Phase 2（3社APIクライアント）

- `api_clients/__init__.py` — 共通インターフェース定義
  - `Usage` / `CallResult` (TypedDict)
  - `MODEL_PRICING` 表（USD/1Mトークン、入力・出力別）
  - `calc_cost(service, model, input_tokens, output_tokens) -> float`
- `api_clients/openai_client.py` — `call()` → `chat.completions.create`
  - `usage.prompt_tokens` / `usage.completion_tokens` 取得
- `api_clients/claude_client.py` — `call()` → `messages.create`
  - `usage.input_tokens` / `usage.output_tokens` 取得
- `api_clients/gemini_client.py` — `call()` → `GenerativeModel.generate_content`
  - `usage_metadata.prompt_token_count` / `usage_metadata.candidates_token_count` 取得
- いずれもエラー時も `api_call_logs` に `status='error'` で記録（失敗の見える化）
- APIキー解決順：DB登録キー → `.env` の環境変数

### 設計上の決定

- API呼び出しは **DB側で `service`, `model`, `input/output_tokens`, `cost_usd`, `response_ms` まで自動記録** する設計に統一
- `MODEL_PRICING` に料金単価を集約。Phase 5で公式単価と照合して更新
- 未登録モデルが来ても `cost_usd=0.0` でログは残す（後追いで補正可能にする）
- Streamlitのcaching/secretsは使わず、`db.get_api_key()` と `.env` のみで完結
- pyenv `3.13.3` を前提に `--break-system-packages` でインストール

### 動作確認手順

1. CLI側で `git pull`
2. `pip install -r api-monitor/requirements.txt --break-system-packages`
3. `cp api-monitor/.env.example api-monitor/.env` してAPIキー記入
4. `cd api-monitor && python3 db.py` でDB初期化（`data/api_log.db` 生成）
5. `streamlit run app.py` → `http://localhost:8501` を開く

---

## 2026-05-28｜Phase 4 部分実装：APIキーのワンクリックコピー

### 方針変更

- 陣内さんの判断で **Phase 3（plotly化）はスキップ**。Streamlit標準グラフのままで十分
- Phase 4 のうち **APIキーのワンクリックコピー** から優先実装

### 対応内容

- `settings.py` を改訂（追加ライブラリ不要）
  - ヘルパー `_render_key_block(service, shown)` に分離してテスト容易に
  - `ENV_KEY_NAMES` を辞書に切り出し
  - キー登録済みのとき：**「📋 コピー用に表示」ボタン**を表示
    - クリックでセッション状態 `copy_open_{service}` をトグル
    - 表示中は `st.code(shown, language=None, wrap_lines=True)` で出力
    - `st.code` の右上に **Streamlit標準のコピーアイコン**が付き、クリックでクリップボードへ
    - もう一度ボタンを押すと閉じる（マスク状態に戻る）
  - キー未登録のとき：「まだキーが登録されていません」と案内のみ
  - キー削除時に `copy_open_{service}` をFalseに戻す（パネル残留防止）

### 実装の根拠

- `st.code` は `streamlit>=1.36` でブロック右上に **clipboard アイコン**を自動表示する
- そのため `pyperclip` / `streamlit_extras` / JS components を一切追加せず実装できる
- マスク表示・表示切替トグルは Phase 1 のままで併存

### 動作確認（陣内さん側）

```
cd ~/sjinnouchi-ux-workspace && git pull
```

を実行するだけ。Streamlitはファイル変更を自動検知して再読み込みします（左上に「Source file changed」が出たら "Rerun"）。
ブラウザの `http://localhost:8501` → 設定タブ → 各サービスのexpander → 「📋 コピー用に表示」を確認。

---

## 2026-05-28｜セッションクローズ：運用確認＆FAQ整理

### 確認済み・合意事項

- **ブラウザで `http://localhost:8501` へのログイン成功**を確認（Phase 1〜2 + Phase 4部分実装が正常稼働）
- **ワンクリックコピー機能は現仕様で完了**（追加変更なし）
- **Phase 3（plotly化）は当面実装しない**方針で確定

### データ更新タイミングの仕様（陣内さんからの質問への回答ログ）

- 自動リフレッシュ・手動更新ボタンは **実装していない**
- データは Streamlit が rerun する瞬間に必ずSQLiteから読み直される（キャッシュ無し）
- rerun が走る条件：
  - ブラウザ更新（F5 / ⌘R）
  - 任意のwidget操作（タブ切替・トグル・ボタン押下）
  - ソースファイル変更時の "Rerun" クリック
- **ブラウザ更新で完全に最新化される**（数字としては正確）
- 副作用として、ブラウザ更新はセッション状態（コピー表示パネル等）をリセットする
  - 状態を保ちたい時は「モニター⇄設定」のタブ切替でも同じ rerun が発火する
- 自動リフレッシュは現状不要と判断（追加要望時は `streamlit-autorefresh` で対応可）

### 3社のAPIキー/モデル管理の整理（FAQログ）

- **必要なキーは3社で計3つだけ**（OpenAI / Anthropic / Google それぞれ1つ）
- モデルの切り替えは **APIリクエストのパラメータ** として都度指定
  - 例：`call(prompt, model="gpt-4o-mini")` → `call(prompt, model="gpt-4o")`
- 「Opus用のキー」「Haiku用のキー」のような発行は不要
- 1つの `OPENAI_API_KEY` で同社の全モデル（GPT-4o / GPT-4o-mini / o1 等）が呼べる
- これはGASでも同じ仕組み（ScriptProperties に1キー登録すれば全モデル使える）
- 用途別の費用集計は **DBの `project` / `purpose` フィールド + 設定タブのカスタマイズ**で実現
- 厳密な分離が必要なら各社の Project Keys / Workspace / Cloud Project 機能で別キー発行も可能（今は不要）

---

## 2026-05-30｜Streamlit 非推奨API対応

### 背景

- 起動時のターミナルログに次の非推奨警告が出ていた：
  ```
  Please replace `use_container_width` with `width`.
  `use_container_width` will be removed after 2025-12-31.
  ```
- 廃止予定日 **2025-12-31 を既に約5ヶ月超過**しており（現在 2026-05-30）、次のStreamlitアップデートで完全に削除される可能性が高い

### 対応内容

- `monitor.py`：`st.dataframe(... use_container_width=True ...)` → `width="stretch"` に置換（履歴テーブル）
- `settings.py`：`st.dataframe(rows, use_container_width=True, ...)` → `width="stretch"` に置換（用途一覧テーブル）

### 動作確認

- ブラウザ更新（または `Source file changed` → Rerun）で即時反映
- 機能・見た目は完全に同等（`width="stretch"` は `use_container_width=True` の新名称）
- ターミナルの DeprecationWarning が出なくなることを確認

### 現時点のPhase進捗

| Phase | 内容 | 状態 |
|------|------|------|
| Phase 1 | 土台コード作成 | ✅ 完了 |
| Phase 2 | 3社APIクライアント実装 | ✅ 完了 |
| Phase 3 | モニタータブのplotly化 | ⏸ スキップ（標準グラフで十分） |
| Phase 4 | APIキーのワンクリックコピー | ✅ 完了 |
| Phase 4 | 用途カスタマイズの編集・削除UI | ⏳ 未着手（必要時に実装） |
| Phase 5 | Streamlit非推奨API対応 | ✅ 完了（2026-05-30） |
| Phase 5 | launchdでMac起動時自動起動 | ⏳ 未着手 |
| Phase 5 | 費用単価の最新化＆公式単価との突合 | ⏳ 未着手 |
| テスト | 実APIキーで `call()` のログ記録確認 | ⏳ 実利用と同時並行で検証 |

### 残課題（次セッション以降）

- [ ] Phase 4: 用途カスタマイズの編集・削除UI
- [ ] Phase 5: launchd でMac起動時自動起動
- [ ] Phase 5: 費用単価の最新化＆公式単価との突合
- [ ] テスト：実APIキーで1回ずつ `call()` してログ記録を確認

---

## 2026-06-11｜方針変更：3社API利用実績の同期型モニターへ拡張

### 背景

- Claude APIを利用しているが、API Monitorのモニター画面に反映されていないことを確認
- 現行設計では、`api_clients/claude_client.py` などアプリ内クライアント経由で呼び出した場合だけSQLiteへ記録される
- Codex、Claude Desktop、公式Console、別アプリなど外部経路で使ったAPI利用は自動取得されない
- ユーザー要望として、OpenAI / Gemini / Claude の3社APIを「利用したらデータが取得されるシステム」にしたいことを確認
- そのため、単なるAPIキー登録画面ではなく、各社のusage/billing情報源から利用実績を同期するモニターへ拡張する

### 切り分け結果

- 費用単価の最新化だけでは、外部経路のClaude利用が反映されない問題は解決しない
- 単価テーブルは、モデル単価が取れない場合の補助計算には必要
- ただし、provider側からcostが取得できる場合は、OpenAI / Anthropic / Google側のusage/cost値を正とする

### 追加した実装タスク

`docs/implementation_plan.md` に `Phase 6: 3社API利用実績の自動取得` を追加。

主な残タスク:

- OpenAI Admin/Usage/Costs APIからusage/costを同期
- Anthropic Usage & Cost Admin APIからusage/costを同期
- GeminiはGoogle Cloud Billing Export to BigQueryからGemini API費用を同期
- provider同期用SQLiteテーブルを追加
- 設定タブを接続設定・同期状態中心へ改修
- モニタータブでローカル呼び出しログとprovider同期データを区別表示
- 各社公式ダッシュボードとの照合を実施

### Notion更新方針

- API Monitorプロジェクトのステータスを、実装待ちまたは設計済みの残タスク状態へ更新する
- Next Actionには「3社API利用実績の自動取得Phase 6を実装」を設定する
- 未確認の数値、費用、利用量は推測で記載しない

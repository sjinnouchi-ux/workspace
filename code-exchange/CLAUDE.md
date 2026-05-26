# code-exchange 運用ルール（2026-05-26更新）

## 1. GitHub MCP連携（2026-05-26〜）

### 確定運用フロー
Cowork（Claude Desktop）はGitHub MCP経由でcode-exchangeに直接pushできる。
ローカルフォルダへの手動コピーは不要。

```
Cowork → GitHub MCP → code-exchange/exchanges/ にpush
CLI → git pull → ターミナルで実行
```

---

## 2. CLI向け出力ルール（最優先・必須）

**CLIへの作業指示は必ず一括コピペ可能な単一コードブロックで出力する。**
複数のStepに分けてコードブロックを出力しない。

### ❌ NG（分割出力）
Step1を実行してください：git pull
Step2を実行してください：python3 script.py

### ✅ OK（一括出力）
以下を一括でターミナルにペーストしてください：
```bash
cd ~/sjinnouchi-ux-workspace && git pull && \
python3 code-exchange/exchanges/YYYYMMDD-NNN.py && \
python3 code-exchange/manage.py complete YYYYMMDD-NNN
```

### ルール詳細
- `&&` でコマンドを繋ぎ、前のコマンドが成功した場合のみ次を実行する
- 確認のためにユーザーに途中結果の貼り付けを求める場合は、そこで一旦区切ってよい
- `cat` で現在の状態確認が必要な場合は、確認用コマンドを先に一括で出し、結果を受けてから次の一括コマンドを出す

---

## 3. Pythonスクリプト実行ルール

**PythonスクリプトはすべてCLI（Claude Code）で実行する。Coworkから直接実行しない。**

### 理由
- Google OAuth認証はローカル環境にのみ保存されており、CLI環境からのみ利用可能
- code-exchangeシステムでの実行履歴・ログ管理を一元化するため

### Cowork側の出力フォーマット（省略不可・毎回必須）

Coworkがスクリプトを生成した場合は、必ず以下の3点をセットでGitHubにpushする：

**① `YYYYMMDD-NNN.md`**（手順書・コード本体）
**② `YYYYMMDD-NNN.py`**（実行スクリプト）
**③ `YYYYMMDD-NNN.json`**（pendingメタデータ）

その後、Coworkのチャットに**一括コピペ用コマンドブロック**を出力する：

```bash
cd ~/sjinnouchi-ux-workspace && git pull && \
python3 code-exchange/manage.py list && \
python3 code-exchange/exchanges/YYYYMMDD-NNN.py && \
python3 code-exchange/manage.py complete YYYYMMDD-NNN
```

---

## 4. 管理コマンド（CLI側）

```bash
cd ~/sjinnouchi-ux-workspace && git pull          # 最新を取得
python3 code-exchange/manage.py list              # 実行待ち一覧
python3 code-exchange/manage.py show <id>         # 内容確認
python3 code-exchange/manage.py complete <id>     # 完了処理
```

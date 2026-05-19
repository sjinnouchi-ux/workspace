# Claude 作業記録

Claude Code CLIが実行した作業の記録です。各プロジェクトの詳細ログは各フォルダの `docs/work_log.md` を参照。

---

## 2026-05-19｜workspaceリポジトリ作成

### 背景
- Claude Desktop と CLI 間でコードをやり取りする仕組みが必要
- market-pilot単体リポジトリから複数プロジェクト管理ワークスペースへ移行

### 対応内容
- `sjinnouchi-ux/workspace` リポジトリを新規作成
- `market-pilot/` を既存リポジトリからサブフォルダとして移行
- `code-exchange/` をDesktop↔CLI間のコードやり取りフォルダとして整備
- cronのパスを新しいワークスペースパスに更新

### 構成
```
workspace/
├── README.md       ← CLI起動時に読み込む
├── CLAUDE.md       ← Claude用コンテキスト
├── claude_log.md   ← 本ファイル（Claudeの作業記録）
├── code-exchange/  ← Desktop↔CLIコードやり取り
└── market-pilot/   ← 株式分析システム
```

### 残課題
- [ ] 旧 sjinnouchi-ux/market-pilot リポジトリをGitHubでアーカイブ
- [ ] cronのパス更新確認

---

## 2026-05-19｜dori-manga プロジェクトフォルダ作成

### 背景
- どり看護師の Instagram 漫画化プロジェクトを開始
- 企画・制作・投稿スケジュールを一元管理するフォルダが必要

### 対応内容
- `dori-manga/` フォルダを新規作成
- `CLAUDE.md`：プロジェクトコンテキスト（Claude用）
- `README.md`：プロジェクト概要
- `docs/concept.md`：キャラクター・コンセプト設定
- `docs/episode_list.md`：エピソード管理リスト
- `docs/work_log.md`：作業ログ

### 構成
```
dori-manga/
├── CLAUDE.md
├── README.md
└── docs/
    ├── concept.md
    ├── episode_list.md
    └── work_log.md
```

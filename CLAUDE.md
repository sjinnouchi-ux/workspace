# Claude ワークスペースコンテキスト

## オーナー情報
- 名前：陣内 聡（株式会社ゆめ看護）
- GitHub：sjinnouchi-ux
- メール：s.jinnouchi@yumekango.com

## このリポジトリの目的
複数プロジェクトを1つのワークスペースで管理する。各プロジェクトはサブフォルダで独立している。

## プロジェクト一覧

| フォルダ | 概要 | 作業ログ |
|---------|------|---------|
| `market-pilot/` | 株式分析・LINE通知 | `market-pilot/docs/work_log.md` |
| `dori-manga/` | どり看護師Instagram漫画化 | `dori-manga/docs/work_log.md` |
| `code-exchange/` | Desktop↔CLIコード交換 | — |

## 運用ルール（重要）

**Desktop（Claude Cowork）はGitHub Web UIのみで操作する。**
- ローカルファイル書き込み（Writeツール）は使用しない
- すべてのファイル作成・編集はGitHub Web UI経由でCommitする
- CLIは起動時にこのREADMEとDesktop作業ログで最新変更を把握する

## CLI起動時の作業フロー

1. `README.md` の「Desktop作業ログ」で最新変更を確認
2. 対象プロジェクトフォルダの `CLAUDE.md` と `docs/work_log.md` を読む
3. 作業実施
4. 対象プロジェクトの `docs/work_log.md` に記録
5. `git push` まで完結させる

## Claude Desktopからのコード受け取り

`code-exchange/` フォルダを使う。詳細は `code-exchange/README.md` を参照。

```bash
# 実行待ちコード確認
python code-exchange/manage.py list

# 完成報告（JSONを削除してpush）
python code-exchange/manage.py complete <id>
```

## Git運用

- リモート: `https://github.com/sjinnouchi-ux/workspace`
- 作業後は必ず `git push` まで完結させる
- `git pull` はClaude Codeが随時実施する

## 環境

- Python: `/Users/satoshijinnouchi/.pyenv/versions/3.13.3/bin/python3`
- ローカルパス: `/Users/satoshijinnouchi/sjinnouchi-ux-workspace/`

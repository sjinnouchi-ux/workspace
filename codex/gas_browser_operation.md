# Codex GASブラウザ操作運用

## 背景

CodexからGASを操作する方法として、まず `clasp` / Apps Script API 経由を検証した。
しかし、更新系操作で Google Workspace 側の `invalid_grant / rapt_required` が発生している。

そのため、当面のGAS編集・エラー確認・デプロイはCodex内ブラウザでApps Scriptエディタを操作する。

## 現在の状態

| 項目 | 状態 |
|------|------|
| `clasp status` | 成功 |
| `clasp push` | `rapt_required` で失敗 |
| `clasp deployments` | `rapt_required` で失敗 |
| Codex内ブラウザ | 利用可能 |
| Googleログイン | ユーザー本人確認後に利用 |

## Codexで行うGAS作業

- Apps Scriptエディタを開く
- GASコードを記載・修正する
- 保存する
- 実行してエラーを確認する
- ログ・実行結果を確認する
- 必要に応じてデプロイ操作を行う

## ユーザーが担当する操作

- Googleアカウント選択
- パスワード入力
- 2段階認証
- OAuth同意
- 重要な公開・デプロイ判断の最終承認

## 基本フロー

1. Codexが対象GASプロジェクト、スプレッドシート、目的を確認する
2. CodexがApps ScriptエディタをCodex内ブラウザで開く
3. 認証が必要な場面はユーザーが本人操作する
4. Codexがコードを編集する
5. Codexが保存・実行・ログ確認を行う
6. デプロイが必要な場合は、内容を説明してから操作する
7. 結果と残課題を `codex/work_log.md` と必要に応じて `claude_log.md` に記録する

## 注意

- OAuthコード、アクセストークン、refresh token、client secretは記録しない
- ブラウザ操作はトークン消費が大きいため、コード案は可能な限りローカルで作成してからエディタへ反映する
- `clasp` が復旧した場合は、ブラウザ操作からCLI運用へ切り替える

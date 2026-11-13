# MCP・外部ツール・hostの運用境界

[共通起動手順](codex/CODEX_DESKTOP_STARTUP.md)と[PROJECTS.md](PROJECTS.md)から対象を確定し、対象repoの現行secret管理・接続契約を確認します。

## 接続を確認する境界

Apps connector、ローカルCLI/同期、local/host MCP、hosted plugin MCP、browser profile、Remote/SSH接続先は別の認証・実行境界です。ある経路の失敗を別経路の未認証へ読み替えません。

確認するのは実際に使用するsurface、host、実行user、credential owner、対象resourceと既存権限です。正しい境界で確認できない結果はINCONCLUSIVEとして扱い、別経路の失敗だけでlogout、disconnect、credential削除、OAuth/token再発行を行いません。詳細は[接続・認証境界](codex/connection-authentication-boundaries.md)。

## 秘密情報

- 値、OAuth code/token、認証JSON、cookie、.env内容をチャット・Git・生ログへ出力しない。
- Secret Manager等が正本のrepoは、その固定role/manifest、version、既存IAM、正式helperを使用する。別project/roleやローカル.envへfallbackしない。
- 認証JSONやcookieをPC間・browser間でコピーしない。業務Googleの原則と例外は起動手順および対象repoを確認する。
- アクセス拒否を理由に、未依頼の権限拡大・policy変更・認証の弱体化を行わない。

## MiniPC・Remote・Memory

Codex Desktopが唯一のオーケストレーターです。MiniPC、ノートPC、WSL2、Remote/SSHはhostごとに接続を確認します。Memory MCPの設定・内容、CLI認証、mapped drive、browser sessionを他PCと同一とは推測しません。

開発環境、Windows Memory MCP、依頼された一回限りのClaude監査は[development-environment](https://github.com/sjinnouchi-ux/development-environment)を正本とします。現役の管理MiniPC巡回と議事録workerは各repoの別運用です。

旧Shogun/WebUI/固定Ops/diagnostics/break-glass/parallel Shogunは退役済みです。旧clone/install/起動チェックリストを再実行しません。旧Shogunの.env/config/OAuthを一律バックアップ・新PCへコピーする手順も現行方針として扱いません。

## 保存・復旧

必要なsource・記録は対象GitHubへ保存し、固定commitの読戻しと未push情報の不在を確認します。秘密情報の保管・復旧は対象サービスとrepoの正式な非公開経路に従います。具体的な依頼なしにバックアップ取得、資格情報再発行、復元や外部送信を行いません。

[承認方針](codex/AGENT_APPROVAL_POLICY.md) / [Git引継ぎ](GIT_HANDOFF_PROTOCOL.md) / [責務分担](docs/workflow-design-implementation.md)

# dori-manga Secret Management

最終更新: 2026-07-09

## 方針

- 実シークレットの正本はGoogle Secret Managerまたは各サービス側secret storeとする。
- `C:\Users\irodo\.codex\.sandbox-secrets\global.env` は移行前の互換ファイルであり、新PCへコピーしない。
- `.env`、GitHub、Markdown、チャット、ログ、DB、Drive資料に秘密値を保存しない。
- 古い作業ログ内の `global.env` 記載は当時の実施記録であり、現在の参照手順ではない。

## 作業PC・AIエージェント用の横断secret

Codex、Claude Code、Shogun、別MiniPCなどの作業環境が参照する横断値は、横断管理projectのSecret Managerに台帳化する。

```text
Secret Manager project: kakeibo-liff-prod
```

dori-manga関連の横断Secret ID:

```text
PROJECT__DORI_MANGA__SUPABASE_URL
PROJECT__DORI_MANGA__SUPABASE_ANON_KEY
PROJECT__DORI_MANGA__SUPABASE_SERVICE_ROLE_KEY
GLOBAL__GOOGLE_OAUTH__CLIENT_ID
GLOBAL__GOOGLE_OAUTH__CLIENT_SECRET
GLOBAL__GOOGLE_OAUTH__REFRESH_TOKEN
```

## Cloudflare Pages Deploy

Cloudflare Pages deployでWranglerが要求するenv名と保管済みSecret ID:

```text
CLOUDFLARE_API_TOKEN  <- GLOBAL__CLOUDFLARE__API_TOKEN
CLOUDFLARE_ACCOUNT_ID <- GLOBAL__CLOUDFLARE__ACCOUNT_ID
```

2026-07-11監査時点:

- 上記2 Secret IDは `kakeibo-liff-prod` に存在し、有効versionがある。
- `dori-manga.deploy` 用manifestは存在しない。
- `codex-agent` に上記2 Secretのaccessor権限はない。
- したがって、新PCからのCloudflare Pages deployは現在 `blocked` である。

この状態で旧 `global.env` をコピーしたり、値を直接表示して回避しない。project/role manifest、必要最小限IAM、helper経由のWrangler疎通を整備してから `ready` へ変更する。

なお、`https://dori-manga-admin.pages.dev/` のlive配信とGitHub Actions `Supabase keepalive` は監査時点で正常であり、このblockerは新PCからのdeploy credential取得に限定される。

## Supabase Edge Functions

Edge Functionsの実行時secretはSupabase側のFunction secretsとして管理する。代表例:

```text
GOOGLE_OAUTH_CLIENT_ID
GOOGLE_OAUTH_CLIENT_SECRET
GOOGLE_OAUTH_REFRESH_TOKEN
```

値は `supabase secrets set` などで設定し、CLIログ、チャット、Markdown、GitHubには残さない。

## GitHub Actions

GitHub Actionsに必要な公開可能でない値は、GitHub Secretsまたは今後のWorkload Identity Federation設計に従う。Secret Managerから取得した値をworkflowログに出力しない。

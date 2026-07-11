# dori-manga Secret Management

最終更新: 2026-07-11

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

2026-07-11 consumer実装前の監査結果:

- 上記2 Secret IDは `kakeibo-liff-prod` に存在し、有効versionがある。
- `dori-manga.deploy` 用manifestは存在しない。
- `codex-agent` に上記2 Secretのaccessor権限はない。
- したがって、新PCからのCloudflare Pages deployは現在 `blocked` である。

この監査状態では、旧 `global.env` をコピーしたり、値を直接表示して回避しないことを停止条件とした。後続実装でproject/role manifest、Secret単位IAM、helper経由のPages読取疎通を整備した結果は次節に記録する。

なお、`https://dori-manga-admin.pages.dev/` のlive配信とGitHub Actions `Supabase keepalive` は監査時点で正常であり、このblockerは新PCからのdeploy credential取得に限定される。

### Current consumer path

中央helper repo:

```text
https://github.com/sjinnouchi-ux/mgmt-terminal
```

manifest:

```text
docs/security/secret-manifests/dori-manga.deploy.json
```

service account:

```text
codex-agent@kakeibo-liff-prod.iam.gserviceaccount.com
```

このmanifestはCloudflareの2項目だけを子プロセスへ渡し、Supabase service roleやGoogle OAuthを含めない。新PCでの確認とdeploy手順は `docs/cloudflare-pages-deploy.md` を正本とする。

service account impersonation、対象projectの読取、一時preview deploy、HTTP 200、deployment削除まで検証済み。production deployは実施しておらず、production URLはHTTP 200のままである。

現行tokenは有効で対象Pages projectへ到達できるが、Cloudflare側のpermission詳細はAPIから取得できなかった。専用Pages Edit tokenへrotationするまでは状態を `ready_with_rotation_pending` とし、最小権限化が完了したとは扱わない。

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

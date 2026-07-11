# dori-manga Cloudflare Pages Deploy

最終更新: 2026-07-11

## Purpose

新しいPCへ `global.env` をコピーせず、GCP Secret Managerから子プロセス限定でCloudflare Pages deploy用環境変数を渡す。

秘密値は画面、チャット、Markdown、GitHub、ログへ表示しない。

## Canonical Repositories

```text
workspace:     https://github.com/sjinnouchi-ux/workspace
secret helper: https://github.com/sjinnouchi-ux/mgmt-terminal
```

両repoの既定branchをfetchし、作業開始commitを確定してから使う。

## Preconditions

- `gcloud auth list` で `s.jinnouchi@yumekango.com` を確認済み。
- `workspace` と `mgmt-terminal` を別々のローカル作業場へclone済み。
- `workspace` の対象変更はcommit済みで、deploy対象commitを記録できる。
- `mgmt-terminal` の `dori-manga.deploy` manifestが `PrintPlan` で解決できる。

PowerShell例では、現在地を `workspace` repo rootとする。

```powershell
$workspaceRepo = (Get-Location).Path
$mgmtRepo = (Resolve-Path '..\mgmt-terminal').Path
```

実際のclone場所が異なる場合は `$mgmtRepo` だけを変更する。絶対パスをGitHubの作業ログへ記録しない。

## Safe Preflight

manifestは値を取得せずに確認する。

```powershell
& "$mgmtRepo\tools\with-project-secrets.ps1" `
  -Project dori-manga `
  -Role deploy `
  -PrintPlan
```

次に、値を表示せず対象Pages projectへの読取だけを確認する。

```powershell
& "$mgmtRepo\tools\with-project-secrets.ps1" `
  -Project dori-manga `
  -Role deploy `
  -Executable powershell `
  -ArgumentList @(
    '-NoProfile',
    '-ExecutionPolicy', 'Bypass',
    '-File', "$mgmtRepo\tools\test-cloudflare-pages-access.ps1",
    '-ProjectName', 'dori-manga-admin'
  )
```

Expected:

```text
cloudflare_pages_access=ok
project=dori-manga-admin
production_branch=main
```

Token、Account IDの値は出力しない。

## Deploy

deployは利用者の明示指示がある場合だけ実行する。

```powershell
Push-Location $workspaceRepo
try {
  & "$mgmtRepo\tools\with-project-secrets.ps1" `
    -Project dori-manga `
    -Role deploy `
    -CommandLine 'npx wrangler pages deploy dori-manga/webapp --project-name dori-manga-admin --branch main'
} finally {
  Pop-Location
}
```

完了後は、deploy元commit、Cloudflare deployment URL、production HTTP結果だけを `dori-manga/docs/work_log.md` へ記録する。

## Security Boundary

- manifestが渡すのは `CLOUDFLARE_API_TOKEN` と `CLOUDFLARE_ACCOUNT_ID` だけ。
- Supabase service role、Google OAuth、他projectの資格情報は読み込まない。
- 現行Cloudflare Tokenは有効で対象projectへ到達できるが、permission詳細をAPIから確認できない。
- 専用のCloudflare Pages Edit tokenへrotationするまでは `ready_with_rotation_pending` とする。
- `AllowCurrentAccountFallback` は通常運用で使わない。

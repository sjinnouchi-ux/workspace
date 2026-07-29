# Git Handoff Protocol

## Purpose

この文書は、Claude、Codex、Fableなどの実行環境がGitHubを境界として作業を安全に引き継ぐための共通契約です。プロジェクト固有の`AGENTS.md`、`CLAUDE.md`、branch/PR規則、秘密管理規則が本書より厳しい場合は、プロジェクト固有規則を優先します。

## Canonical Boundary

- canonical repositoryとGitHub上の既定ブランチをオンライン正本とする。
- 添付ファイル、チャット本文、ローカルファイル、未push commit、未push branchは、GitHub上の監査証拠ではない。
- GitHub connector、GitHub API、別のエージェントは、ローカルcommitや未push branchを参照できない。
- Claude、Codex、Fableなどによるcross-agent review、監査、外部環境変更へ進む前に、作業branchをpushし、既定ブランチをbaseとするdraft PRを作成する。
- 「commit済み」と「GitHubから監査可能」は別の状態である。local HEADとremote branchの完全SHAが一致し、PRから変更を確認できる状態だけをGitHub境界での引き継ぎ可能状態とする。

## Start-of-Task Record

mutationの前に、次を確認して記録する。

- canonical repository
- repository rootの絶対パス
- 実行環境（Windows、WSL、Codex sandboxなど）
- sanitized origin URL
- current branch
- local HEADの完全40桁SHA
- `git status --porcelain=v2 --branch --untracked-files=all`
- upstream branch
- `remote.origin.fetch`の全値
- originの既定ブランチ
- `origin/<default-branch>`の完全SHA（既定ブランチが`main`なら`origin/main`）
- local HEADと`origin/<default-branch>`のahead/behind

remote URLはcredentialを含む可能性がある。生の値をチャット、Markdown、ログへ出力せず、プロセス内でcredential混入を判定し、sanitized後の値だけを表示する。credential入りURLを検出した場合は、その値を再掲せず停止する。

## Repository Root And `cwd`

現在ディレクトリやツールの`workdir`指定だけからrepository rootを推測しない。mutationの直前に、確認済み絶対パスを使って次を実行する。

```text
git -C <exact-path> rev-parse --show-toplevel
```

- 出力を正規化し、意図した絶対パスと一致することを確認する。不一致なら停止する。
- `git rev-parse --show-toplevel`が失敗した場所ではGit操作を続けない。
- 以後のGit操作は、確認済み絶対パスを使った`git -C <exact-path> ...`を優先する。
- Windows cloneをWSL側の検索だけで不存在と判定しない。WSL cloneもWindows側の検索だけで不存在と判定しない。
- ツールが指定した`workdir`を無視またはfallbackする可能性を考慮し、実際のtop-levelを毎回検証する。

## PowerShell Audit Example

次の例はWindows-native Gitで実行する。`$Repo`を対象cloneの確認済み絶対パスへ置き換える。sanitized前の`$OriginRaw`は出力しない。

```powershell
$Repo = 'C:\path\to\repo'
$ExpectedTop = [System.IO.Path]::GetFullPath($Repo).TrimEnd('\')
$ActualTop = (git -C $Repo rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Not a Git repository.' }
$ActualTop = [System.IO.Path]::GetFullPath($ActualTop).TrimEnd('\')
if (-not $ActualTop.Equals(
    $ExpectedTop,
    [System.StringComparison]::OrdinalIgnoreCase
)) {
    throw 'Repository top-level mismatch.'
}

$OriginRaw = (git -C $Repo remote get-url origin).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Cannot read origin.' }

if ($OriginRaw -match '^https?://') {
    $OriginUri = [System.Uri]$OriginRaw
    if (
        -not [string]::IsNullOrEmpty($OriginUri.UserInfo) -or
        -not [string]::IsNullOrEmpty($OriginUri.Query) -or
        -not [string]::IsNullOrEmpty($OriginUri.Fragment)
    ) {
        throw 'Credential-bearing or non-canonical origin detected.'
    }
    $Port = if ($OriginUri.IsDefaultPort) { '' } else { ":$($OriginUri.Port)" }
    $SanitizedOrigin = '{0}://{1}{2}{3}' -f (
        $OriginUri.Scheme,
        $OriginUri.Host,
        $Port,
        $OriginUri.AbsolutePath
    )
} elseif ($OriginRaw -match '^ssh://') {
    $OriginUri = [System.Uri]$OriginRaw
    if ($OriginUri.UserInfo -match ':') {
        throw 'Credential-bearing SSH origin detected.'
    }
    $Port = if ($OriginUri.IsDefaultPort) { '' } else { ":$($OriginUri.Port)" }
    $SanitizedOrigin = 'ssh://{0}{1}{2}' -f (
        $OriginUri.Host,
        $Port,
        $OriginUri.AbsolutePath
    )
} elseif ($OriginRaw -match '^(?:[^@\s]+@)?([^:\s]+):(.+)$') {
    $SanitizedOrigin = '{0}:{1}' -f $Matches[1], $Matches[2]
} else {
    throw 'Unsupported origin URL format.'
}

$Branch = (git -C $Repo branch --show-current).Trim()
if ([string]::IsNullOrWhiteSpace($Branch)) { throw 'Detached HEAD.' }
$Head = (git -C $Repo rev-parse HEAD).Trim()
if ($Head -notmatch '^[0-9a-f]{40}$') { throw 'HEAD is not a full 40-character SHA.' }
$Status = git -C $Repo status --porcelain=v2 --branch --untracked-files=all
$UpstreamOutput = git -C $Repo rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>$null
$Upstream = if ($LASTEXITCODE -eq 0) { $UpstreamOutput.Trim() } else { '<none>' }
$FetchRefspec = @(git -C $Repo config --get-all remote.origin.fetch)
if ($LASTEXITCODE -ne 0 -or $FetchRefspec.Count -eq 0) {
    throw 'remote.origin.fetch is not configured.'
}

$RemoteHead = @(git -C $Repo ls-remote --symref origin HEAD)
$DefaultRefLine = $RemoteHead |
    Where-Object { $_ -match '^ref:\s+refs/heads/\S+\s+HEAD$' } |
    Select-Object -First 1
if (-not $DefaultRefLine) { throw 'Cannot determine origin default branch.' }
$DefaultBranch = (($DefaultRefLine -split '\s+')[1] -replace '^refs/heads/', '')
$RemoteDefaultRef = "refs/remotes/origin/$DefaultBranch"

git -C $Repo fetch origin "$DefaultBranch`:$RemoteDefaultRef"
if ($LASTEXITCODE -ne 0) { throw 'Cannot update the default branch.' }
$BaseSha = (git -C $Repo rev-parse $RemoteDefaultRef).Trim()
if ($BaseSha -notmatch '^[0-9a-f]{40}$') { throw 'Base is not a full 40-character SHA.' }
$Behind, $Ahead = (
    (git -C $Repo rev-list --left-right --count "$RemoteDefaultRef...HEAD").Trim() -split '\s+'
)

[pscustomobject]@{
    RepositoryRoot = $ActualTop
    Environment = 'Windows-native Git'
    SanitizedOrigin = $SanitizedOrigin
    Branch = $Branch
    LocalHead = $Head
    Status = $Status
    Upstream = $Upstream
    FetchRefspec = $FetchRefspec
    DefaultBranch = $DefaultBranch
    BaseSha = $BaseSha
    Ahead = [int]$Ahead
    Behind = [int]$Behind
}
```

## WSL Bash Audit Example

次の例はWSL-native Gitで実行する。`repo`をWSL内の対象cloneの確認済み絶対パスへ置き換える。sanitized前の`origin_raw`は出力しない。

```bash
repo='/absolute/path/to/repo'
expected_top=$(cd "$repo" && pwd -P) || exit 1
actual_top=$(git -C "$repo" rev-parse --show-toplevel) || exit 1
actual_top=$(cd "$actual_top" && pwd -P) || exit 1
if [ "$actual_top" != "$expected_top" ]; then
  echo 'Repository top-level mismatch.' >&2
  exit 1
fi

origin_raw=$(git -C "$repo" remote get-url origin) || exit 1
case "$origin_raw" in
  http://*|https://*)
    authority=${origin_raw#*://}
    authority=${authority%%/*}
    case "$authority" in
      *@*)
        echo 'Credential-bearing origin detected.' >&2
        exit 1
        ;;
    esac
    case "$origin_raw" in
      *'?'*|*'#'*)
        echo 'Non-canonical origin detected.' >&2
        exit 1
        ;;
    esac
    sanitized_origin=$origin_raw
    ;;
  ssh://*)
    ssh_path=${origin_raw#ssh://}
    ssh_authority=${ssh_path%%/*}
    case "$ssh_authority" in
      *@*)
        ssh_userinfo=${ssh_authority%@*}
        case "$ssh_userinfo" in
          *:*)
            echo 'Credential-bearing SSH origin detected.' >&2
            exit 1
            ;;
        esac
        ;;
    esac
    sanitized_origin="ssh://${ssh_path#*@}"
    ;;
  *@*:*)
    sanitized_origin=${origin_raw#*@}
    ;;
  *)
    echo 'Unsupported origin URL format.' >&2
    exit 1
    ;;
esac

branch=$(git -C "$repo" branch --show-current) || exit 1
if [ -z "$branch" ]; then
  echo 'Detached HEAD.' >&2
  exit 1
fi
head_sha=$(git -C "$repo" rev-parse HEAD) || exit 1
if ! [[ "$head_sha" =~ ^[0-9a-f]{40}$ ]]; then
  echo 'HEAD is not a full 40-character SHA.' >&2
  exit 1
fi
status=$(git -C "$repo" status --porcelain=v2 --branch --untracked-files=all) || exit 1
if ! upstream=$(git -C "$repo" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null); then
  upstream='<none>'
fi
fetch_refspec=$(git -C "$repo" config --get-all remote.origin.fetch) || exit 1

default_ref=$(
  git -C "$repo" ls-remote --symref origin HEAD |
    awk '$1 == "ref:" && $3 == "HEAD" { print $2; exit }'
) || exit 1
if [ -z "$default_ref" ]; then
  echo 'Cannot determine origin default branch.' >&2
  exit 1
fi
default_branch=${default_ref#refs/heads/}
remote_default_ref="refs/remotes/origin/$default_branch"

git -C "$repo" fetch origin "$default_branch:$remote_default_ref" || exit 1
base_sha=$(git -C "$repo" rev-parse "$remote_default_ref") || exit 1
if ! [[ "$base_sha" =~ ^[0-9a-f]{40}$ ]]; then
  echo 'Base is not a full 40-character SHA.' >&2
  exit 1
fi
read -r behind ahead <<EOF
$(git -C "$repo" rev-list --left-right --count "$remote_default_ref...HEAD")
EOF

printf '%s\n' \
  "repository_root=$actual_top" \
  'environment=WSL-native Git' \
  "sanitized_origin=$sanitized_origin" \
  "branch=$branch" \
  "local_head=$head_sha" \
  "upstream=$upstream" \
  "default_branch=$default_branch" \
  "base_sha=$base_sha" \
  "ahead=$ahead" \
  "behind=$behind"
printf '%s\n' 'status:' "$status" 'fetch_refspec:' "$fetch_refspec"
```

## Windows And WSL Separation

- Windows側cloneはWindows-native Gitで操作する。
- WSL側cloneはWSL-native Gitで操作する。
- 原則として同じworking treeをWindows GitとWSL Gitの両方から操作しない。
- 改行規則はrepoの`.gitattributes`を正本とする。共通文書から`core.autocrlf`を一律変更しない。
- `.gitattributes`がない場合は、既存ファイル、既存Git設定、CI環境を調査し、導入の要否を別タスクで判断する。

## Fetch Refspec

`git config --get-all remote.origin.fetch`の全値を確認する。

- branch限定refspecが`refs/heads/main`を含まない場合、通常の`git fetch origin`だけで`origin/main`が更新されると仮定しない。
- main-only refspecなら`main`は更新対象だが、他branchを取得しない制約を記録する。
- `main`を明示取得する必要がある場合は、次を実行する。

  ```text
  git -C <exact-path> fetch origin main:refs/remotes/origin/main
  ```

- 新規cloneでは、理由がない限り通常の全branch refspecを使用する。

  ```text
  +refs/heads/*:refs/remotes/origin/*
  ```

- 既存cloneのrefspecを恒久変更する場合は、変更前後の全値と変更理由を作業ログへ記録する。

## Remote Branch Verification

push後はremote branchをGit transportから照合する。

```text
git -C <exact-path> ls-remote --heads origin <branch>
```

- 返されたremote branchの完全SHAとlocal HEADの完全SHAを一致確認する。
- remote branchがない、複数候補になる、またはSHAが不一致なら停止する。push漏れ、別remote、force push、別branchを疑う。
- private repoのcommit実在確認は、認証済みGitHub APIまたはconnectorでも行う。
- private repoに対する未認証URLのHTTP `200`応答をcommit実在の成功条件にしない。

## Cross-Agent Handoff Gate

review、Fable監査、外部環境変更の前に、次を順番に満たす。

1. `git -C <exact-path> cat-file -t <sha>`が`commit`を返す。
2. `git status --porcelain=v2 --branch --untracked-files=all`でtracked、staged、unstaged、untracked状態を確認する。
3. commit後のworking treeがcleanであることを確認する。
4. 作業branchをoriginへpushする。
5. local HEADと`git ls-remote --heads origin <branch>`の完全SHAが一致することを確認する。
6. GitHub上の既定ブランチをbaseとするdraft PRを作成する。
7. PR head repositoryが、同一repo branchまたは承認済みforkなど、想定したpublishing modelと一致することを確認する。
8. PRのFiles changedで必須文書、migration、コードが存在し、不要ファイルが混在しないことを確認する。
9. 最新の既定ブランチを明示取得し、local HEADのahead/behindを再確認する。
10. project固有のscope checkerと必要テストを実行する。
11. PR番号、URL、head完全SHA、base完全SHA、検証結果をGitHub上の作業ログまたはPR本文へ記録する。
12. 完了時に、未コミット、未push、ローカル専用の必要情報がないことを確認する。

Gateを満たす前の状態は`local-only`または`handoff-blocked`として報告し、監査可能なGitHub状態と表現しない。

## `safe.directory`

- `safe.directory=*`は禁止する。
- 不要なglobal `safe.directory`登録は禁止する。
- `dubious ownership`が発生した場合は、cloneの所有者、実行ユーザー、Windows/WSL境界を確認する。
- 所有者不一致が意図した隔離境界によるものだと確認でき、対象repoを操作する必要がある場合は、確認済み絶対パスに対するコマンド単位指定を優先する。

PowerShell:

```powershell
git -c "safe.directory=$Repo" -C $Repo status --porcelain=v2 --branch --untracked-files=all
```

WSL bash:

```bash
git -c "safe.directory=$repo" -C "$repo" status --porcelain=v2 --branch --untracked-files=all
```

スペースを含むパスは、各shellの規則に従って必ず引用する。

## Stop Conditions

次のいずれかに該当する場合は、同名フォルダ、別clone、別branchを推測で採用せず停止する。

- canonical repoを確定できない。
- repository rootを確定できない。
- 実際のtop-levelが指定パスと異なる。
- HEAD commitが存在しない、または`git cat-file -t <sha>`が`commit`を返さない。
- untracked作業しか存在せず、引き継ぐcommitを特定できない。
- sanitizedしたremote URLがcanonical repoと一致しない。
- branchまたはcommitの所在が複数候補になる。
- 既定ブランチまたは`main`を最新化できない。
- local/remote SHAが一致しない。
- push失敗理由が不明である。
- PR head repositoryが想定したpublishing modelと異なる。
- credential入りremote URLを検出した。

## Secret And Path Handling

- token、OAuthコード、認証JSON、`.env`、Secret値を表示、保存、commitしない。
- credential入りremote URLを表示しない。検出時は値を再掲せず、種類と停止理由だけを報告する。
- ローカル絶対パスは、必要なチャットまたは限定された引き継ぎには記載できるが、GitHub上の共通文書へ個人固有値として固定しない。
- shell履歴、PR本文、作業ログへ秘密値を含むコマンドや出力を貼らない。

## Standard Handoff Template

次のMarkdownをコピーし、各`<...>`を実測値へ置き換える。`Local repo root`の個人固有値はチャットまたは限定された引き継ぎだけに記載し、GitHubへcommitしない。

```markdown
## Git handoff

- Canonical repo: <owner/repository URL>
- Local repo root (private/chat handoff only): <absolute path>
- Environment: <Windows | WSL | Codex sandbox | other>
- Branch: <branch>
- Local HEAD full SHA: <40-character SHA>
- Remote HEAD full SHA: <40-character SHA>
- Base branch / SHA: <default branch> / <40-character SHA>
- Ahead / behind: <ahead> / <behind>
- Fetch refspec: <all remote.origin.fetch values>
- Worktree status: <clean | exact tracked/staged/unstaged/untracked summary>
- Required files verified: <paths checked in the PR>
- Tests / scope checks: <commands and results>
- PR number / URL / draft state: <number> / <URL> / <draft or ready>
- External mutations performed: <none or bounded list>
- Remaining blockers: <none or bounded list>
```

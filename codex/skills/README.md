# Codex共有スキル

複数PCで同じCodexスキルを利用するためのGit正本です。各スキルのディレクトリには、実体の`SKILL.md`、必要なライセンス、取得元を固定する`SOURCE.md`を置きます。

## 収録スキル

| Skill | 用途 | Source |
|---|---|---|
| `frontend-design` | 個別の題材に根差した、意図的で特徴的なフロントエンドデザイン | Anthropic `anthropics/skills` |

## インストール

Codexのsystem skill installerを使い、GitHub上の正本から各PCへ導入します。

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo sjinnouchi-ux/workspace --path codex/skills/frontend-design
```

導入先は通常`$env:USERPROFILE\.codex\skills\frontend-design`です。同名ディレクトリが既にある場合、installerは上書きせず停止します。

## 更新

1. 配布元のcommit SHAを固定する。
2. 配布元のファイルを改変せず更新する。
3. 各スキルの`SOURCE.md`にcommit SHAとSHA-256を記録する。
4. ライセンス、差分、Codexでの認識を検証してからGitHubへ反映する。

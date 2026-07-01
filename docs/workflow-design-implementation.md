# 設計フェーズと実装フェーズの分担

Shogun運用における「設計 = Claude割当エージェント」「実装 = Codex割当足軽」の分担を明文化する。

「Shogun = 設計」ではない。Shogunはシステム名であり、実際の役割は `config/settings.yaml` のCLI割当で決まる。

## エージェント / CLI / フェーズ

| 役割 | 主なフェーズ | CLI割当 |
|---|---|---|
| 将軍 | 命令受領・委譲 | Claude |
| 家老 | タスク分配・報告集約 | Claude |
| 軍師 | レビュー・設計検証 | Claude |
| 設計足軽 | 要件定義・仕様整理 | Claude |
| 実装足軽 | 実装・検証・デプロイ | Codex |

実際の割当はShogunの `config/settings.yaml` を正とする。この表は方針の明文化である。

## Claude / 設計側の責務

- 要件定義、仕様整理、設計判断を行う。
- 判断を各プロジェクトの `DESIGN_LOG.md` に時系列で追記する。
- 現在有効な仕様は `docs/requirements/` または `docs/specs/` に清書する。
- Codexへの実装指示を明記する。
- 実装済みかどうかを推測で書かない。

## Codex / 実装側の責務

- 実装、検証、デプロイを行う。
- 結果を各プロジェクトの `IMPLEMENTATION_LOG.md` に時系列で追記する。
- 設計と食い違った点、実装できなかった点は `Questions Back To Design` に書き戻す。

## ログと正本

- Shogunランタイムの `queue/*.yaml`、`dashboard.md`、`reports/*` は揮発的であり、恒久正本にしない。
- `DESIGN_LOG.md` と `IMPLEMENTATION_LOG.md` は恒久正本として追記する。
- LOGは経緯、`docs/requirements/` と `docs/specs/` は現在有効な仕様。
- 同じ内容をLOGとspecに二重記載しない。

## 仕様変更時の流れ

1. Claudeが `DESIGN_LOG.md` に変更判断を追記する。
2. Claudeが必要に応じて `docs/requirements/` または `docs/specs/` を更新する。
3. ClaudeがCodexへの実装指示を書く。
4. Codexが実装し、`IMPLEMENTATION_LOG.md` に記録する。
5. 食い違いがあればCodexが設計側へ戻す。

## Codexへの実装指示テンプレート

```md
### Implementation Request For Codex

- Project / project ID:
- Working Directory:
- 背景 / 目的:
- やること（Scope）:
- やらないこと（Out of Scope）:
- 想定変更ファイル / パス（Affected Files）:
- 受け入れ条件（Acceptance Criteria）:
- 検証方法（Verification）:
- 切り戻し手順（Rollback）:
- 参照（References）:
```

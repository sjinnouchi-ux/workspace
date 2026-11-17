# タスク終了時の一時作業場整理（2026-11-17）

看護守HPでは調査用のクローン3件をごみ箱に移した後、クローンの外に作った補助スクリプトが残った。新しいタスクでは補助ファイルを最初からタスク専用フォルダにまとめ、必要なものを保存したうえで同じタスクの中で整理する。[事例と実機検証](https://github.com/sjinnouchi-ux/development-environment/blob/ce811ab63c37ffb850aafa5bcd680eee63f5d2c7/docs/reports/2026-11-17-kango-temp-clone-cleanup.md)

既存・新規プロジェクトへの配布元は、各PCのグローバル指示が参照するGitHub mainの[共通起動手順](CODEX_DESKTOP_STARTUP.md#local-work-policy)。workspaceのAGENTS.md、共通カスタム指示の配布文面、作業端末のグローバルAGENTS.mdから同じ手順を参照する。別PCへの適用には、そのPCが共通起動手順を読み込むことが前提となる。

文書変更の検証対象は、ローカル不要、単独クローン、複数クローンと補助ファイル、保存未完了の各場合の終了手順と報告例、参照先、作業端末のグローバル指示との対応。過去の実機検証を参照し、今回のためにクローンは作成していない。

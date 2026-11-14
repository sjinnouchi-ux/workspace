# 旧家計簿Worker/GASの取扱い

このディレクトリと配下は **Legacy / Frozen（2026-11-14）** の保存参照用です。上位のAGENTSと共通起動手順を維持し、[README.md](README.md)を先に読んでください。

- 現行家計簿のCanonical Entryは `sjinnouchi-ux/kakeibo-liff`。このフォルダを新規開発・通常配備・本番rollbackの正本として使わない。
- ここにある旧Worker/GASやwrangler設定を実行・配備・再公開しない。現行と同じWorker名を指定する設定を含む。
- 既存source・設定・過去作業ログを保持する。過去patchや未完checkboxを、現在の適用・復旧・token再発行の指示に読み替えない。
- 旧LIFF・token/Secret/IAM・Worker version・Cloud Run旧revision/rollback版・Sheets/DBを凍結整理の名目で変更/削除しない。
- 履歴の読取り・証拠照合・凍結案内/記録の保守は可能。新しい具体的な変更・再開指示がある場合は、まず現行repo mainのAGENTS/Primary Docsと実際の状態を確認し、共通承認方針に従ってその指示範囲で進める。
- 秘密値、OAuth code、token、認証JSON、.env内容を記録しない。過去の `global.env` 運用を現在の資格情報源として復活させない。

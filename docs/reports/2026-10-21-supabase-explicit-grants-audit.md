# Supabase public schema明示GRANT変更の横断監査（2026-10-21）

## 結論と適用範囲

[Supabase公式告知](https://supabase.com/changelog/45329-breaking-change-tables-not-exposed-to-data-and-graphql-api-automatically)の2026-10-30変更は、新規publicテーブルの自動権限付与停止。既存テーブルの権限を取り消す変更ではない。新規テーブル、preview、新規環境、db resetでの再構築が確認対象。RLSとテーブル権限は別で、service_roleもテーブル権限が必要。直接Postgres接続への影響とData APIへの影響を混同しない。

現役でコード・migrationを確認できた系統では、この変更による確定的な権限不足を発見しなかった。market-pilotのみ再構築時の不足を再現したが、利用者は再開せず削除を指定した。全本番DBの実ACL・全API経路を照合した監査ではなく、税理士系統の詳細確認も未完了のため「全プロジェクトで影響ゼロ」とは判定しない。

## プロジェクト別結果

| Canonical repo / 系統 | 確認結果・問題になる条件 |
|---|---|
| mgmt-terminal | 69 migration再生成功。public 89 relation中service_role SELECT可能18件はapp/store.pyの直接アクセスallowlistと一致。残る71件はFinance/Wholesale/Credentials等のRPC専用・非公開領域で、権限なしを欠陥としない。新規migrationも明示GRANTが必要。 |
| kakeibo-liff / personal-business | 管理ターミナルFinance等を利用する系統。独立したpublicテーブル権限不足は検出せず。間接依存は上記と同じ。 |
| k-alert-production 相談DB | 7 migration、13テーブル、service_role SELECT 13件を確認。anon/authenticatedは0件。過去migrationにALTER DEFAULT PRIVILEGESがあり再生時は将来権限を復活させるため、今後の新規テーブルが自動公開される前提は避ける。 |
| k-alert-production 申込DB | 別系統8 migration、6テーブルの再生成功。申込・決済・代理店フォーム・dashboard変更テーブルの明示GRANTを確認。相談DBだけの検証で代用していない。 |
| meeting-minutes-system | 48 migration再生成功。public 40 relationにはテストbootstrapのkeepalive_ping 1件を含む。authenticated SELECT 35件、service_role 5件。members/agent等の非公開4テーブルはRPC経由。webの直接GET対象mm_meetings/mm_case_archivesに明示権限あり。private schemaとmm_agentの既存RPC権限を維持する。 |
| sharoushi-office-ai | 採用済みkeepaliveはテーブルを読まず定数と時刻を返す関数で、anon EXECUTE明示。業務基盤はGAS/Sheets。今後Supabaseへ業務テーブルを追加する際は別途GRANTが必要。Worker実行成功の未確認事項は今回変更とは別。 |
| zeirishi-office-dx | 休止中。Primary Docsではreceipt_poc/receipt_workflow等の独自schemaとpublic RPC。指定業務アカウントの実ログイン確認を満たしていないため詳細コード・本番ACL監査は未実施。安全判定を留保し、再開もしない。 |
| market-pilot | 6 migration・public 14テーブルにGRANTなし。新規環境でservice_roleのtickers SELECTが拒否されることを再現。table権限だけ追加するとautomation_controlsのbigserial sequenceでINSERT拒否を再現。optional-table検出が権限エラーを「migrationなし」と扱う点も障害の隠蔽要因。利用者指定により修正・再開せず退役。 |
| enza | 企画文書段階。将来Supabase採用時のschema設計に明示GRANTを含める。現在の実行障害としては扱わない。 |
| supabase-db-templates | 現在はREADME主体の空の参照repo。旧templateの存在を推測して修正しない。 |
| suumo-project / suumo-analysis-test | 現行分析はTurso。今回のpublic Data API変更の直接対象を検出せず。 |
| taiwan-outreach / keieisha-rouki-shindan / kango-mamori-studio-requests / yumekango-business-management | STUDIO、GAS/Sheets、業務文書等の現行資料で今回対象の直接DB実装を検出せず。 |
| development-environment / workspace | 運用・台帳。旧runtimeを再開しない。文書中のSupabase参照を稼働アプリと数えない。 |

## 再現検証

Windows上でタスク専用cloneを作り、既存本番DBへ接続せず、ネットワークなし・ポート公開なし・volume mountなしの使い捨てPostgresを使用。publicのanon/authenticated/service_role向けdefault table/sequence grantsを除去してからmigrationを順番に再生し、has_table_privilege/has_sequence_privilegeでrole別ACLを収集した。各migration自身によるdefault privilege変更は尊重している。単なる文字列GRANT検索だけでなくmarket-pilotのSET ROLEによる拒否を確認した。

| repo | 検証対象main SHA | migration数 | 結果 |
|---|---|---:|---|
| mgmt-terminal | 954acd14019b79e6fce3ec9b9845c70e3b6151fb | 69 | 再生成功 |
| k-alert-production | 36db3ee96459504e0be77ce6c5e0d8ca2424ed7a | 7 + 8 | 両DB再生成功 |
| meeting-minutes-system | a388648ce78fb13acd27d59fe8a03f894018d809 | 48 | 再生成功 |
| market-pilot | 7f81ff0c0866ded01f1ff50e61df2faebb0dbe7d | 6 | 再生成功・アクセス拒否を再現 |

前3系統とmarketはghcr.io/supabase/postgres:17.6.1.158を使用（meetingのみrepoのlocal fixtureに合わせpostgres:17-alpine）。meetingのkeepaliveはfixture由来であり本番再作成の保証ではない。起動待ちの一時serverを拾う初回probe失敗はTCP readinessへ修正して再実行済みで、プロジェクト障害とは数えていない。全5 replayのsuccess/cleaned=trueを確認。自作検証containerのみ削除し、既存containerには触れていない。

追加確認したsource: kakeibo-liff b99d5bb301c19d56e670d0d00aabf30fd3464c52、sharoushi-office-ai 65612c8ffe5b9bbbcc18563fc49ebcc995b08885、workspace c82d52189932645c0252d3f21699fb999bb82c02。全対象のCanonical Entry、既定branch、AGENTS、Primary Docsを先にオンライン確認した。管理ターミナル所定のChrome本人確認とサブブラウザ3画面接続も実施済み。秘密値・本番業務明細は記録しない。

## 残る確認・将来の実装条件

- 税理士系統の指定アカウント確認後の詳細監査。本番ACL driftと全Data API呼出の実行テストは今回範囲では未確認。
- 今後publicテーブルを追加するmigrationは用途別roleへ必要操作のみGRANTし、必要なsequenceも確認する。RLS policyだけ追加して完了にしない。
- 新規環境/reset/previewで同じmigrationを再生し、呼出roleで読み書きを確認する。既存環境で動くことだけでは再作成の証明にならない。
- 非公開RPC専用のFinance/Wholesale/Credentials等へ一括GRANTしない。権限エラーをテーブル不存在や空データとして隠さない。

本変更は監査文書のみ。アプリ・schema・権限・本番配備は変更せず、成功済みの再生検証を再利用し、重いアプリ全体テストは実施しない。

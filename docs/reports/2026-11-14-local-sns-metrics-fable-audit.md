# Fable 5.2: ローカルSNS日次集計の立ち上げ前調査監査

- Date: 2026-11-14 (JST)
- Model: `claude-fable-5-2`
- Exact audited commit: `6439a9d3a9b51e8278273565d45f1317b1cc3ee5`
- Repository: `sjinnouchi-ux/workspace`
- PR: https://github.com/sjinnouchi-ux/workspace/pull/80
- Controller: development-environment `c654afb2d27599a7803d8a5dd5a63aef6a089d42`
- Receipt: completed / exit_code 0 / nonempty audit_text
- One-shot; read-only Read/Glob/Grep; no retry; no fallback.
- 実アカウント取得の検証ではなく、固定資料の論理・根拠範囲の監査。

## Auditor response

# 監査結果(commit 6439a9d、read-only、資料の論理と証拠範囲のみ)

CriticalとImportantの指摘はなく、Minorが3件です。実取得とWeb再調査は行っていないため、公式資料の内容そのものの正否は判定していません。

## Critical
None

## Important
None

## Minor

**M1. Instagramのフォロワー総数とアカウント日別リーチは、Codex側の出典表に対応行がない**
- 箇所: spec 取得可否表(`docs/proposals/2026-11-14-local-sns-metrics-feasibility.md:39-40`)の「Userのfollowers_count」「Account Insightsの日別値」。
- 証拠: `docs/reports/2026-11-14-local-sns-metrics-sources.md:7-9` のInstagram行は、Insights guide、Media Insights、Media referenceの3件だけです。IGUserとAccount Insightsの参照は、Work初回回答(`...work-initial.md:38-39,46`)の引用にしかありません。specは構成候補を「Work初回回答と公式資料をCodexが照合」と見出しに掲げており、この2指標は照合の裏付けが追えません。
- 影響: 表現は「候補」「未検証」なので過剰な断定ではなく、追跡性の欠落にとどまります。
- 最小修正: sources表にIGUserとAccount Insightsの2行を追加します。未照合なら、spec該当セルに「Work引用のみ、Codex未照合」と付記します。

**M2. 重複防止キーがrun単位で、最小候補BのCSV再取込みを覆っていない**
- 箇所: spec `:53`「同一runの同一対象・同一定義・同一期間を一意にし、再実行で重複させない」。
- 証拠: 再実行や再取込みは通常別のrun_idになるため、run内の一意性では同じ公式ファイルの二重取込みを防げません。spec自身が `:65` でCSV再取込みを確認対象に挙げています。Work初回案にあったファイルハッシュと `imports`(`work-initial.md:148,151,161`)は、specのDB候補に引き継がれていません。
- 補足: SQLiteのUNIQUE制約はNULL同士を別値として扱います。累計スナップショットで `provider_period_start/end` がNULLになる系列は、制約だけでは一意になりません。`post_id` 側は「キーを分ける」で対処済みです。
- 最小修正: `:53` に「CSV取込みはファイル識別(ハッシュ等)で再取込みを判定する。期間がNULLの系列の一意条件は実装時に定める」の一文を追加します。テーブルの新設は不要です。

**M3. Accounts APIの記述が、出典側の確認水準の限定を引き継いでいない**
- 箇所: spec `:31`「Accounts APIはPersonal Accountも公式説明の対象だが、専用の申請・審査・権限が必要」。
- 証拠: sources `:15` は確認方法を「公式の検索表示本文で」と限定しています。これが公式ページ本文の直接読取りでないなら、specの言い切りは証拠より一段強くなります。文言からはどちらか判別できません。
- 影響: 適格性と指標は「未確認」と明記されているため、結論には影響しません。
- 最小修正: spec `:31` に「(公式の検索表示本文による確認。本文精読と適格性は未確認)」を付記します。直接読取り済みなら、sources側の表現を直します。

## 質問別の判定

1. **Instagramの条件付き見込みと、TikTokのAPI/CSV/画面の区別**: 過剰な断定や抜けはありません(M1の追跡性を除く)。
   - Instagramは「条件付きで有力」「権限・設定・認可・実取得は未検証」にとどまっています(spec `:39,45`)。
   - Work更新回答の「条件が整っています」は、冒頭注記(`work-update.md:5`)で採用範囲が限定されています。
   - 投稿Insightsがlifetime値であること、広告込み系列を分けること、Storiesを別扱いにすることも反映済みです(sources `:8`、spec `:33`)。
   - TikTokは画面閲覧、公式出力、APIを別々に判定しています(spec `:9,31,63`)。

2. **Display API制約の拡張と、閲覧可能の誤認**: どちらもありません。
   - 私的アプリの審査制約はDisplay APIに限定され、Accounts APIは「別途確認」です(spec `:27,31`)。sources `:14` は拡張しないと明記しています。
   - 「画面で見える数値が必ず出力されるとは推定しない」(spec `:63`)とあり、CSVの出力可否と列は未確認の扱いです。
   - Business Suiteを現在のアカウントで使えるとも推定していません(`work-initial.md:5`)。
   - 企業用への変更も前提にしていません。

3. **DB案**: 目的に合っています(M2を除く)。
   - 初期値は開始日の観測とし、それ以前の差分は計算しません。
   - 累計スナップショット、provider提供の期間値、観測間の純増減を分けています。
   - 累計リーチの差分を「当日のリーチ」と呼ばず、投稿リーチを合算しません。
   - 欠測は後日値で埋めず、均等配分もせず、0と区別します。
   - 取得時刻はUTC、providerの期間とタイムゾーン、source、API版、定義版を保持します(spec `:19-21,52-54`)。

4. **採用判断の保留と次の手順**: 根拠相応です。
   - Display APIにreachとfavoritesがないこと(sources `:11`)が保留の根拠になっています。
   - Accounts APIの適格性と、現在のアカウントの公式出力がともに未確認であることも、保留と整合します。
   - 実列確認は追加費用、審査、種別変更を伴わない最小の次手で、spec `:45,61-66` と一致します。
   - 新たな審査義務、ビジネス化、課金、追加インフラは導入されていません。

## Verdict
**条件付き可(Minorのみ)。** 調査案は証拠の範囲内で結論を限定しており、立ち上げ判断の材料として使えます。M1〜M3はいずれも文言または出典表の1〜2行で解消でき、判断を止める指摘ではありません。

## Codex assessment and follow-up

監査の範囲と結論に同意し、Minor 3点の最小修正を採用した。

- M1: IGUserのfollowers_countとAccount Insightsのreach/dayを公式本文で直接確認し、出典表に追加した。実アカウント検証は未実施のまま。
- M2: CSVはファイル識別と取込対象によりrunをまたいで再取込み判定し、期間NULLの累計系列も重複判定可能な条件を実装時に定めると補足した。SQLiteの公式UNIQUE仕様も照合した。今回DBは作成しない。
- M3: Accounts APIの説明は公式の検索表示本文による確認であり、直接本文の精読と当人の適格性・指標は未確認だとspecにも明記した。

本レポートと補足は監査後のCodex文書変更であり、上記exact commitの監査結果を最終headの再監査済みと読み替えない。監査は一回のみ。UTF-8、差分、相対リンク、GitHubへの同期を確認する。文書のみのためアプリ/DBの重いテストは対象外。実取得・無人運転・完全自動化の実証は未実施。

Post-run read-only check: audit-owned controller/child process count 0; effective temp directory codex-claude-audit-subject-* count 0. WSL全体の停止や無関係process/ファイルの削除は行っていない。

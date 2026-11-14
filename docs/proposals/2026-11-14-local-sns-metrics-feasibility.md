# ローカルSNS日次集計の立ち上げ前調査

状態: Work調査とFable 5.2監査完了。軽微な指摘3点をCodexが補足。その後、利用者指定でTikTokの実画面と公式CSVを追加確認した。新規プロジェクト作成・実装は未承認、未実施。

## 現在の対象と推奨経路（2026-11-14追記）

利用者はTikTokの数字のDB格納を不要と指定した。以後のDB集計対象はInstagramのみ。TikTokの記録は調査履歴として保持し、DB設計・自動取得の対象に含めない。既存DBや収集ジョブはそもそも作成しておらず、削除・停止操作はない。

Instagramは対象プロアカウントを正規に認可する公式APIを第一候補にする。Media InsightsにFeed/Reelsのviews、saved、reach、likesがある。投稿形式・広告込みの範囲・API版を固定し、初期値から日次スナップショットを保存する案。認証マークの有無とAPIの認可は別であり、今回のアカウントでのAPI取得はまだ検証していない。

| 別PC/別アカウントの意味 | 再生数 | 保存数 | 現在の判断 |
|---|---|---|---|
| Windows/Google等が別アカウントのPCから、対象Instagramの正規API認可を使う | 対応メディアでAPI取得候補 | savedをAPI取得候補 | PCの違いより、対象Instagramへの認可が重要。ブラウザのInstagramログインを毎日常駐させる構成は必須ではない。資格情報は正規の保存方法で対象PCに準備し、セッション/cookieのコピーで共有しない。 |
| 管理権限のない一般の別Instagramアカウントで公開投稿を見る | 画面に公開表示される範囲なら読取り候補。今回HTMLでは未検証。 | 公開HTMLから取得できる前提にしない | 保存ボタンや自分の保存状態は、投稿が保存された総数ではない。公開再生数と所有者向けInsightsの定義を混ぜない。 |
| 対象本人または正式な管理権限でブラウザのInsightsを開く | 表示されれば画面読取り候補 | 表示されれば画面読取り候補 | このアカウントのPC版Insights/HTML読取りは未検証。画面読取りとAPI利用可否は別。HTMLに常に必要値が含まれることや安定した無人取得を保証しない。 |

公式根拠: [Insights guide](https://developers.facebook.com/documentation/instagram-platform/insights)、[Media Insights](https://developers.facebook.com/documentation/instagram-platform/reference/instagram-media/insights)、[Media reference](https://developers.facebook.com/documentation/instagram-platform/reference/instagram-media)、[Instagram Login](https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login)。確認日2026-11-14。

Media referenceのsaved_countは所有者または承認済みcollaborator向け・Facebook Login限定で、Business Discovery等には提供されない。これはInsightsのsavedとは経路を区別する。Business Discoveryの公開view_countは広告等を含み得るため、自分のInsights viewsと同一系列にしない。これらのAPI仕様を根拠に、管理権限のない閲覧者向けHTMLから保存総数を集める案は採用しない。

次の最小調査は、Instagramプロの正規管理者・アプリ設定・必要権限・対象Feed/Reelsでの公式API適合性の確認。現時点ではAPI作成/認可、権限付与、PC設定、HTML収集プログラム、DBは実装しない。新規プロジェクトの立ち上げは引き続き行わない。

## 初期調査で利用者が指定した前提（現在は上記のInstagramのみへ縮小）

- 自身が運用するInstagramとTikTokを対象に、Windows PCで日次集計しDBへ保存する環境を検討する。
- 両SNSとも認証マークなし。利用者確認: Instagramはプロアカウント、TikTokは企業用ではない。Instagramのクリエイター/ビジネスの内訳は未確認。開発者アプリの審査、API権限、企業確認は別条件であり、認証マークの有無から推定しない。
- 利用者は現在TikTokのインサイトを閲覧できている。企業用ではないことを分析画面がない根拠にしない。画面閲覧、公式ファイル出力、自動API取得は別々に判定する。
- 過去データの取得・復元は不要。収集開始日の初期値から今後の毎日の値を記録する。
- 希望指標: アカウントのフォロワー数、アカウント/投稿のリーチ、各投稿の投稿日時、各投稿の再生数・いいね数・保存数。
- ChatGPT Workの標準モデルで案を調査し、Codexへ回収後にFable 5.2 (`claude-fable-5-2`) で一回限りのread-only監査を行う。
- 旧dori-mangaを復元しない。新規repo、PROJECTS登録、API認可・権限変更、定期ジョブ、有料契約、プログラム導入はこの調査では実施しない。追加調査では利用者がTikTokへログインし、正規のインサイト閲覧と公式CSVのサンプル出力を許可した。

## 判定の境界

公式資料の仕様確認と、実アカウントでの取得成功は別とする。追加調査でTikTok本人ログイン後の公式CSV出力は確認したが、API呼出し・無人取得・DB格納は未実施である。取得可否は経路ごと・指標ごとに条件分けし、全指標の完全自動取得を約束しない。

毎日の記録は、原則として定時に取得した累計値のスナップショットとする。隣接する観測の差分は純増減であり、日付ごとの発生件数と同一ではない。取り消し・削除・遅延・再集計の影響を受ける。特に累計ユニークリーチの差分を「当日のリーチ」と呼ばない。アカウントのリーチを投稿別リーチの合計で作らない。

開始日の観測前の差分は計算しない。電源OFFなどで欠測した日の累計値を後日値で埋めない。欠測をまたぐ差分は観測間隔分として表示し、1日分に均等配分しない。公式の期間別集計が別途取得できる場合のみ、対象期間を維持して別系列に保存する。

## 初期の構成比較（TikTok除外前の履歴）

| 案 | 構成 | 評価 |
|---|---|---|
| A | 公式API → Python → SQLite → CSV出力 | Instagramは有力。TikTok Display APIは個人専用アプリの本番審査制約があり、この用途での自作API取得を標準経路にしない。Accounts APIの条件は別途確認。 |
| B | API取得＋公式管理画面CSVの取込み → SQLite | APIにない項目を、CSVの実列・対象期間を確認して補完できる候補。CSVダウンロードが手動なら完全自動とは呼ばない。 |
| C | 管理画面の通常操作を自動化 → SQLite | UI変更、ログイン/MFA、画面ロック、規約、数値の丸めへの依存が大きい。非公開API・認証回避を使わず、実現性は別途確認する。 |

最小候補はB。Instagramは公式Insightsを優先し、TikTokは現在のインサイトから出力できる項目を公式CSVで取り込む候補とする。追加調査で一部の実列を確認したが、保存相当数・投稿別リーチはCSVに含まれず、全希望指標と全投稿の網羅性、元タイムゾーン、無人取得は未検証。この段階では毎日の収集成功や全指標取得を保証しない。手動ダウンロードが必要ならDB取込みのみ自動であり、SNS取得は半自動と明記する。Accounts APIはPersonal Accountも公式説明の対象だが、専用の申請・審査・権限が必要とされる（この点は公式の検索表示本文による確認。直接本文の精読と当人の適格性・対応指標は未確認）。企業用への変更を当然の前提にしない。すべての希望指標の自動化が必要なら、開始前の可否判定条件に含める。

Instagramの最小対象はFeed/Reels。Storiesは取得できる期間が短いため、希望がある場合に収集頻度を別途検討する。再生/表示、投稿単位/アカウント単位、広告込みの有無も明示する。

## 今回の条件での取得可否

下表は[実アカウント公式CSV確認](../reports/2026-11-14-tiktok-official-export-check.md)を反映した現在の判定。Total ViewersをInstagram reachと同一の定義だとは断定しない。

| 指標 | Instagramプロ | TikTok企業用ではない・インサイト閲覧可能 |
|---|---|---|
| フォロワー総数 | Userのfollowers_countが候補。権限・設定・認可・実取得は未検証。 | Display APIに仕様はあるが私的アプリの本番審査制約あり。現在の公式出力の総数列、またはAccounts APIの条件を確認。 |
| アカウントリーチ | Account Insightsの日別値が候補。元期間・タイムゾーンを保持。 | Reach名の列はないが、日別Total Viewers等を公式CSVで出力確認。別の元指標名として扱い、同一定義と推定しない。 |
| 投稿ID・投稿日時 | Media IDとtimestampが候補。 | Content.csvのVideo linkとPost timeを出力確認。リンクから安定IDを扱う方法、時刻/期間の意味は実装前に確認。 |
| 投稿別再生/いいね | Media Insightsのviews/likesが候補。投稿形式と定義を固定。 | Content.csvにTotal views/Total likesを出力確認。サンプル15投稿であり、全投稿網羅・日次無人取得は未実証。 |
| 投稿別リーチ/保存相当 | Media Insightsのreach/savedが候補。 | 投稿詳細の総視聴者数/ブックマーク数は画面表示あり。確認した公式CSVに該当列なし、専用出力口は未確認。Accounts APIは利用適格性・指標の確認が残る。 |

WindowsのDB保存と日次実行は通常の構成で実現可能。Instagramの日次API取得は条件付きで有力。初期調査ではTikTokの保存相当数・リーチを含む無人取得が未実証だったが、現在はTikTokのDB格納を対象から外したため、その不足をInstagramの検討条件には含めない。

## DBとローカル実行の候補

- `accounts`: platform、account_id、アカウント種別の確認状態。投稿IDとアカウントIDは文字列で扱う。
- `posts`: platform、account_id、post_id、published_at_utc、投稿形式、削除/非公開等の取得状態。
- `collection_runs`: run_id、scheduled_for_utc、started_at_utc、finished_at_utc、結果、失敗分類。生の認証レスポンスは保存しない。
- `metric_observations`: run_id、platform、account_id、post_id（アカウント指標はnull）、metric_name、value（未取得はnull）、status、observed_at_utc、provider_period_start/end、provider_timezone、source、API_version、metric_definition_version。投稿指標とアカウント指標のキーを分ける。
- 累計/期間値、Instagramのみ/広告込み/Facebook込み、推定値等の意味が異なるものは別系列とする。同一runの同一対象・同一定義・同一期間を一意にする。CSV再取込みはrun_idをまたいでファイル識別（ハッシュ等）と取込対象を照合し、同じファイルを二重計上しない。期間がNULLの累計系列も重複判定できるキー/条件を実装時に定める。SQLiteのUNIQUEはNULL同士を区別するため、NULLを含む複合キーだけで重複防止できると推定しない。欠測・未対応・権限不足・取得失敗を0と区別する。
- JSTは利用者表示/スケジュールの日付。取得時刻はUTC。providerの集計期間は保持し、日付ラベルだけをJSTに変えてJST集計と誤表示しない。
- Windows Task Schedulerから日次実行し、遅延実行・二重起動防止を検討する。スリープ復帰は端末の対応状況を実測し、電源OFF中の実行を保証しない。常時記録が必須ならPCの稼働条件を利用者が判断する。
- 資格情報はWindows Credential Manager/DPAPI等を候補として、将来の実装repo規則に従って決める。APIごとに有効期限・refresh条件を確認し、失効時は取得失敗を明示する。SNSのパスワードをDBへ保存しない。
- 実指標DB、資格情報、API生レスポンス、認証ログをGitへ保存しない。バックアップはSQLiteのbackup API等で整合するコピーを作り、必要な保存先と復元方法を決める。稼働中のDBファイルだけを単純コピーしない。

## 立ち上げ判断前に必要な確認

1. 利用者確認済みの種別を前提に、Instagramプロの内訳と所有/管理権限を確認する。認証マークの購入、TikTokの企業用への変更を前提にしない。
2. 指標をアカウント/投稿、累計/期間値、対象投稿形式ごとに固定する。
3. API経路の審査・権限・利用目的適合性、TikTok Accounts APIの利用条件、現在閲覧できるTikTokインサイトから出力できる公式CSVの実際の列を確認する。画面で見える数値が必ず出力されるとは推定しない。
4. 将来の取得検証では少数投稿でID・投稿日時・数値・定義を画面と比較し、API遅延や丸めによる差を記録する。
5. 初期値・翌日値、欠測、認証失効、二重実行、保存数の取り消し、CSV再取込み、バックアップ復元を対象に絞って確認する。
6. 希望指標すべての取得経路と、自動/手動・未対応の境界を提示した後に、利用者が新規プロジェクト立ち上げを判断する。

## 調査の出典・進行

- 公式資料の確認結果は[出典と確認境界](../reports/2026-11-14-local-sns-metrics-sources.md)を参照。
- [現在のTikTokの公式出力確認](../reports/2026-11-14-tiktok-official-export-check.md)で実際のCSV3種の列を記録した。原本・実数値はGitへ保存せず、プロジェクト作成・実装は行っていない。
- Workの[初回回答](../reports/2026-11-14-local-sns-metrics-work-initial.md)と[追加前提を反映した更新結論](../reports/2026-11-14-local-sns-metrics-work-update.md)を回収済み。Instagramプロ・TikTok非企業用でインサイト閲覧可能・両方認証マークなし・過去分不要という全追加前提を反映したWork最終更新も同文書へ保存した。
- [Fable 5.2監査](../reports/2026-11-14-local-sns-metrics-fable-audit.md)はcommit `6439a9d3a9b51e8278273565d45f1317b1cc3ee5`で一回実施し、正常完了。Critical/Importantなし、Minor 3点。出典追加、CSV再取込み/NULLキー、Accounts API確認水準の限定をCodexが補足した。補足後の再監査は実施しない。
- 新規プロジェクトを作らず、共通workspaceに立ち上げ前の調査記録だけを保存する。台帳・稼働システム・認証設定は変更しない。

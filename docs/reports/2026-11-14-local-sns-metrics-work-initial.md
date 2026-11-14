# ChatGPT Workから回収した初回調査回答

回収日: 2026-11-14。Workチャット: SNS指標取得調査報告。標準モデル。本文のリンクを保持し、表示専用の引用マーカーだけを除去した。

この回答はアカウント種別の追加確認前のもの。現在の前提はInstagramプロ、TikTok企業用ではない・インサイト閲覧可能、両方認証マークなし、過去分不要、開始日から毎日DB記録である。種別未確認という本文の記述は採用しない。[現時点の調査案](../proposals/2026-11-14-local-sns-metrics-feasibility.md)を優先する。TikTok Business Suiteを現在のPersonal Accountで使えるとの確認はなく、現在のインサイトと同一と推定しない。

以下は外部モデルの参考回答であり、Codexの実アカウント検証やFable監査の完了証拠ではない。

---

**推薦は「Instagramは公式APIを優先、TikTokは公式エクスポートを起点にする併用構成」です。** 収集開始日に初期スナップショットを保存し、以後の観測値をSQLiteへ追記します。ただし、現段階で両SNSの全指標を毎日無人取得できるとは確定できません。特にTikTokのリーチ・保存相当指標は、利用可能な管理画面とAPIの追加条件を確認する必要があります。

以下は**2026年11月14日確認**の公式資料に基づく調査結果です。追加の前提に従い、過去データの復元は対象から外しています。プロジェクト・リポジトリ作成、実装、インストール、SNS認証、定期ジョブ作成は行っていません。

**1．認証マークと利用条件は別です**

| 区分 | 意味 | 今回の判定 |
|---|---|---|
| プロフィールの認証マーク | アカウントの認証表示 | 両SNSともなし。これだけで通常の分析機能やAPIが利用不可になるわけではない |
| Instagramのプロアカウント | BusinessまたはCreatorというアカウント種別 | **未確認**。今回のInstagram API経路では必要 |
| TikTokのPersonal／Business Account | TikTok上のアカウント種別 | **未確認**。Business Suiteなどの利用条件に関係する |
| 開発者アプリ審査・権限承認 | 作成したアプリの目的、製品、取得権限の承認 | **未確認**。プロフィール認証とは別 |
| Meta Business Verification | 開発者側などの事業者確認 | **未確認**。必要性は選ぶアクセスレベル・手続きによる |
| TikTok Verified Business Account／Business Centerの確認 | TikTokの事業者・資産管理上の確認 | **未確認**。プロフィールの認証マークと同一視しない |

Instagramは、自分が所有・管理するプロアカウントをアプリのDashboardへ追加した場合、公式資料上はStandard Accessの対象です。他者のプロアカウントへ提供する場合はAdvanced Accessとなります。したがって「自分用でも必ず第三者提供向け審査が必要」「認証マークが必要」とは判断しません。一方、本人の所有・管理権限や実際のアプリ設定はまだ確認できていません。

根拠：[Meta：Instagram Platform insights](https://developers.facebook.com/documentation/instagram-platform/insights)、[Instagram Login概要](https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login)。確認日：2026-11-14。

**2．Instagramの取得可否**

表の「条件付き」は、公式に取得経路は存在するものの、今回のアカウントで使えることは未確認、という意味です。

Instagram Login経路では、基本情報用の`instagram_business_basic`、Insights用の`instagram_business_manage_insights`と本人の認可が必要です。Facebookページの連携は不要です。Facebook Login経路では、連携ページと`instagram_basic`、`instagram_manage_insights`、`pages_read_engagement`などが必要になり、資産管理の状態によって追加権限があります。プロフィールの認証マークは、これらの前提条件として記載されていません。

| 対象 | 指標 | 公式APIの経路・判定 | 保存する単位・制限 |
|---|---|---|---|
| アカウント | フォロワー総数 | **条件付き**：Userオブジェクトの`followers_count` | 取得時点の総人数を毎日保存。Insightsの`follower_count`と同じ意味だと扱わない |
| アカウント | リーチ | **条件付き**：Account Insightsの`reach` | 日別のユニーク到達アカウント数。推定値。`period=day`等、対応する指定を使用 |
| 投稿 | 投稿日時 | **条件付き**：Mediaの`timestamp` | UTCの作成日時を保存し、JSTへ変換。公開・予約投稿などの表示との対応は初回検証 |
| 投稿 | リーチ | **条件付き**：Media Insightsの`reach` | 投稿単位の累計ユニーク到達数を観測。アカウントリーチと別管理 |
| 投稿 | 再生数 | **条件付き**：Media Insightsの`views` | Reelsの再生指標を保存。静止画等の表示指標と同じ名称だけで統合しない |
| 投稿 | いいね数 | **条件付き**：Media Insightsの`likes`等 | 投稿単位の現在値・累計値を観測。取得フィールドと集計範囲を固定 |
| 投稿 | 保存数 | **条件付き**：Media Insightsの`saved` | Feed／Reelsの投稿単位。誰が保存したか、どのコレクションへ入れたかを取得する機能ではない |

フィールドの根拠：[IGUser](https://developers.facebook.com/docs/graph-api/reference/shadow-ig-user)、[Media Reference](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/v21.0/)、[Account Insights](https://developers.facebook.com/documentation/instagram-platform/api-reference/instagram-user/insights)、[Media Insights](https://developers.facebook.com/documentation/instagram-platform/reference/instagram-media/insights)。確認日：2026-11-14。

運用上は次の区別が必要です。

- **投稿Insightsは原則`lifetime`の値**です。毎日取得しても、それ自体が「その日に発生した件数」になるわけではありません。
- アカウントの日別リーチは、その日の到達人数です。投稿の累計リーチの差分とは別物です。
- 広告・ブースト・Facebookへのクロスポストを含む`total_views`などは別定義です。通常の`views`と混ぜず、今回どちらを使うか固定します。
- カルーセルは親投稿単位で扱います。子画像ごとのInsightsは対象にしません。
- Storiesには24時間の取得制限があるため、**最小案はFeed／Reelsに限定**します。Storiesも必要なら、日1回収集とは別設計が必要です。
- Insightsには最大48時間の遅延があり、空データが返る場合があります。空を0へ変換しません。

管理画面ではMeta Business SuiteにInstagramのInsightsがあり、閲覧権限が必要です。ただし、**今回取得できたMeta公式資料からは、要求した全項目のCSV列・日別粒度・出力条件まで確定できませんでした**。したがってCSVは補助候補であり、「保存数も含め必ずCSVで取れる」とはしません。画面に表示されることと、CSVへ出力できることも分けて検証します。

根拠：[Meta Business SuiteのInsights概要](https://www.facebook.com/business/help/4185855074991336)。確認日：2026-11-14。

**3．TikTokの取得可否**

TikTok Display APIには必要な基本フィールドがありますが、**本人専用ローカルアプリの本番利用には重大な障壁があります**。公式App Review Guidelinesは、私的・個人利用向けアプリを認めないと明記しています。Login Kit・API製品の承認やscopeの認可も必要です。

したがって、次の表は「技術仕様として存在するフィールド」と「今回採用できる経路」を分けています。認証マークがないことが主な障壁ではありません。

根拠：[App Review Guidelines](https://developers.tiktok.com/docs/en/app-review-guidelines)、[Display API Get Started](https://developers.tiktok.com/docs/en/display-api-get-started)。確認日：2026-11-14。

| 対象 | 指標 | Display API | 公式管理画面・追加APIによる経路 |
|---|---|---|---|
| アカウント | フォロワー総数 | **仕様確認済み・利用は条件付き**：`follower_count`、`user.info.stats` | Business SuiteにFollowersデータのダウンロードあり。ただし総数／新規増加の列、日別粒度は実ファイル確認が必要 |
| アカウント | リーチ | **取得不可：Display APIに該当フィールドなし** | Business Suite OverviewにReachのダウンロードあり。Business Accountと閲覧権限が必要。今回の利用可否・日別列は未確認 |
| 投稿 | 投稿日時 | **仕様確認済み・利用は条件付き**：`create_time` | Studio／Business Suiteの出力に含まれるかは未確認 |
| 投稿 | リーチ | **取得不可：Display APIに該当フィールドなし** | Accounts APIが公式候補。追加申請・承認・アカウント認可が必要。今回使える指標・粒度は未確認 |
| 投稿 | 再生数 | **仕様確認済み・利用は条件付き**：`view_count` | 公式分析画面・エクスポートが候補。要求する投稿別列の出力は実ファイル確認が必要 |
| 投稿 | いいね数 | **仕様確認済み・利用は条件付き**：`like_count` | 同上 |
| 投稿 | 保存相当数 | **取得不可：Display APIに該当フィールドなし** | Favoritesが候補。CSVへの出力は未確認。別製品の公式APIに存在しても、今回の利用権限を意味しない |

Display APIの動画一覧は**公開動画**が対象で、ページングして取得します。返る再生数・いいね数は取得時点の値であり、投稿後の毎日分を返す時系列APIではありません。

根拠：[Get User Info](https://developers.tiktok.com/docs/en/tiktok-api-v2-get-user-info)、[Video Object](https://developers.tiktok.com/docs/en/tiktok-api-v2-video-object)、[List Videos](https://developers.tiktok.com/docs/en/tiktok-api-v2-video-list)。確認日：2026-11-14。

TikTok Business AccountのWeb Business Suiteは、OverviewでReach・Engagement・Followers等をダウンロードでき、期間は直近7・28・60日またはカスタム期間と案内しています。ただし、この案内だけでは**投稿別の日別保存数まで出力できるとは確定しません**。ファイル形式、各列、集計タイムゾーンも確認対象です。

根拠：[About Web Business Suite](https://ads.tiktok.com/resources/help/article/navigate-web-business-suite)。確認日：2026-11-14。

追加APIは次の扱いにします。

| 経路 | 今回の扱い |
|---|---|
| Accounts API／API for Business | **追加条件付き候補**。公式にはBusiness・Personal Account活動の管理・分析を案内。ただし2026年3月20日以降、対象scopeを含む新規申請・権限追加には専用申請が必要。Business Accountに変更するだけで利用可能にはならない |
| TikTok OneのMedia Insights | `favorites`等は存在するが、**TikTok One向けの別経路**。一般の本人用集計へそのまま使えるとはしない |
| Research API | 研究資格・個別申請・承認が必要。今回の自己運用SNS分析の標準経路には採用しない |
| 広告レポートAPI | 広告の集計用。通常投稿全体のリーチ・再生を取得する代替として扱わない |

根拠：[Accounts API概要](https://business-api.tiktok.com/portal/docs/accounts-api-overview/v1.3)、[Accounts API案内](https://business-api.tiktok.com/gateway/docs/index?doc_id=1737565048641538&language=ENGLISH)、[TikTok One Media Insights](https://business-api.tiktok.com/portal/docs/get-authorized-tto-media-insights/v1.3)、[Research API資格](https://developers.tiktok.com/products/research-api/)。確認日：2026-11-14。

なお、TikTokの**Favoritesは投稿へのお気に入り追加数**です。利用者自身のお気に入り一覧、コレクションへの分類、端末への動画ダウンロード件数とは区別します。DBでもInstagramの`saved`とは別の指標定義にします。

**4．収集開始日からの記録方法**

初日は、取得できたアカウント指標と各投稿の現在値を「初期スナップショット」として保存します。既存投稿が10万再生なら、初日の値は10万です。これを初日の日次再生数にはしません。

翌日以降は、次の3種類を分けて保存します。

| データ | 意味 |
|---|---|
| 観測スナップショット | その取得時刻にAPI・画面・公式ファイルが返した値 |
| プラットフォーム提供の日別値 | SNS側が指定日の指標として集計した値 |
| スナップショット間の差分 | 2回の観測の間に見えた純増減 |

**累計値の差分は日次活動の真値ではありません。** いいね・保存の取り消し、投稿削除、無効反応の除去、再集計、反映遅延を含み、負になる場合もあります。マイナス値を0へ丸めません。

また、累計リーチが100→120になっても、その日のリーチが20とは限りません。既に到達した人が再び閲覧しても、累計ユニーク人数には増えないためです。アカウントの期間リーチも、投稿リーチの合計では求めません。

未取得値は`NULL`とし、`not_supported`、`permission_denied`、`temporarily_unavailable`、`missed_run`などの理由を残します。**正式に返った0だけを0として保存**します。

**5．構成案の比較と推薦**

| 比較項目 | A：公式API優先 | B：API＋公式エクスポート | C：管理画面の操作自動化 |
|---|---|---|---|
| 規約・利用条件 | 承認された用途・権限内で利用 | API条件＋公式出力機能を利用 | 画面アクセス権だけで自動収集許可があるとは判断できない |
| 取得範囲 | Instagramは有力。TikTokは権限と用途審査が障壁 | APIにない項目を出力ファイルで補える可能性 | 画面に出る項目に限る。丸め表示・非表示にも弱い |
| 安定性 | 比較的高い。バージョン変更対応は必要 | 比較的高い。CSV列変更への対応が必要 | 低い。画面・文言・配置変更に影響される |
| ログイン・MFA | 初回認可、失効時の再認可 | 出力操作時に本人のログインが必要な場合あり | セッション切れ、MFA、CAPTCHAで止まりやすい |
| 保守負担 | 中 | 低〜中 | 高 |
| 導入手間 | アプリ設定・権限確認が必要 | ファイル確認から小さく開始できる | 見かけより大きい。例外処理が増える |
| 費用 | ローカル実行費・開発保守費。今回、課金必須とは確認していない | 同左。手動出力の作業時間が残る | 自作でも保守時間が大きい。有料RPAは任意 |
| 今回の推薦 | Instagram部分に採用候補 | **全体の推薦** | 標準案にはしない |

Cについて、今回の日本アカウントに適用される規約・許可を十分確認できていないため、無人画面収集を許可済みとは扱いません。公式Developer Termsが認めるAPI自動利用と、通常画面を自動操作して収集する行為は分けます。

根拠：[TikTok Developer Terms](https://www.tiktok.com/legal/page/global/tik-tok-developer-terms-of-service/en)。確認日：2026-11-14。

**実現可能な最小案は、まず公式ファイルの取り込み・DB集計を自動化し、条件確認後にInstagram APIを加える構成です。** TikTokのダウンロードは当初手動でも構いません。その場合「毎日のDB集計」は自動化できますが、「毎日のSNS取得」は半自動です。ファイルに投稿別の保存数がなければ、その指標は欠測のまま残します。

TikTokまで無人取得する案は、Accounts API等の適格性・承認・必要指標を確認できた場合の追加段階とします。

**6．Windowsローカル構成の具体案**

構成は**Python＋SQLite＋CSV出力**で十分です。Excel形式が必要なら`.xlsx`出力を追加します。AIモデルを毎日の数値集計に使う必要はありません。

| テーブル | 主キー・主要項目 |
|---|---|
| `accounts` | 主キー：`platform, account_id`。アプリID／ID名前空間、表示名、種別、確認済み権限 |
| `posts` | 主キー：`platform, account_id, post_id`。投稿日時UTC、投稿種別、URL、初回発見時刻、公開状態 |
| `metric_definitions` | `metric_definition_id`。元フィールド名、対象、単位、累計／日別、organic／paid／combined、推定値か、定義バージョン |
| `sources` | `source_id`。API製品・バージョン・endpoint、または公式CSV種別、ファイルハッシュ |
| `observations` | `observation_id`。アカウント／投稿参照、`observed_at_utc`、指標定義、ソース、値、状態、対象期間、元タイムゾーン |
| `collection_runs` | `run_id`。予定時刻、実行時刻、終了状態、エラー、取得件数、再試行回数 |
| `imports` | `import_id`。ファイルハッシュ、生成日時、取り込み日時、列定義、対象アカウント・期間 |

`observations`は、対象・指標・ソース・対象期間・観測時刻等で重複防止します。アカウント指標には投稿IDを入れず、対象種別を明示します。TikTokの`open_id`はアプリ単位なので、アプリの違うIDを同一IDとして扱いません。

時刻と運用は次の設計を推薦します。

- **UTCを原本、JSTを表示・集計用**にします。`observed_at`と`published_at`を分離し、`observed_date_jst`を生成します。元データの日別集計がJSTか不明なら、単に日付をJSTへ貼り替えません。
- **将来の実行案**は毎日JST 09:00。現在値の観測と、提供される日別値の再取得を分けます。日別値は遅延対策として直近数日を再取得し、改訂履歴を残します。累計スナップショットを過去日付に書き戻しません。
- Windows Task Schedulerの`StartWhenAvailable`で実行漏れ後の再開、`WakeToRun`で対応するスリープ解除を設定できます。ただし完全な電源OFF中の定時観測はできません。再開時は実際の取得時刻で1件保存し、欠けた日の値を捏造しません。
- API側に対象日の値が残っている場合だけ、欠測を日別値で補完します。それ以外は「前回から今回までの複数日差分」です。
- CSV取り込みはファイルハッシュで二重取り込みを防止。取得・認証エラーと、正常な0件を区別します。

根拠：[Microsoft StartWhenAvailable](https://learn.microsoft.com/en-us/windows/win32/taskschd/tasksettings-startwhenavailable)、[WakeToRun](https://learn.microsoft.com/en-us/windows/win32/taskschd/tasksettings-waketorun)。確認日：2026-11-14。

API制限・資格情報は以下の扱いです。

- HTTP 429等には指数バックオフと上限付き再試行。認証・権限エラーは連続再試行せず、ローカルで要対応と表示します。
- TikTok Display APIの既定制限は対象3endpointそれぞれ毎分600リクエストですが、別製品へ流用しません。投稿一覧はページング完了まで確認します。
- トークン期限は固定値を埋め込まず、`expires_in`等から管理します。TikTokの公式資料には期限の異なる記載があるため、採用経路の最新仕様と実レスポンスを優先します。更新後のrefresh tokenも置換します。[Manage OAuth Access Tokens](https://developers.tiktok.com/docs/en/oauth-user-access-token-management)、確認日：2026-11-14。
- トークン・secretはWindows Credential ManagerまたはDPAPIで保護し、SQLite・CSV・ログへ平文保存しません。タスク実行ユーザーと資格情報の復号可能なユーザーを合わせます。[Microsoft資格情報管理](https://learn.microsoft.com/en-us/windows/win32/SecBP/handling-passwords)、確認日：2026-11-14。
- 出力には値だけでなく、観測時刻・対象期間・指標定義・ソース・欠測理由を付けます。投稿IDはExcelで丸められないよう文字列扱いにします。
- SQLiteは整合性を保てるバックアップ方式を使い、原本ファイルとともに別ドライブへ世代保存。復元確認を行います。**実指標データ、CSV、DB、資格情報はGitHubへ保存しません。**

**7．段階的な検証と合格条件**

以下は今後着手する場合の手順で、今回は実行していません。

| 段階 | 確認すること | 合格条件 |
|---|---|---|
| ① アカウント条件 | Instagramの種別、TikTokの種別、本人の管理権限、既存API利用の有無 | 対象アカウントと所有・管理関係が特定できる |
| ② 公式出力の確認 | 各SNSのサンプル出力、フォロワー・リーチ・投稿ID・日時・再生・いいね・保存相当の列 | 各列の対象・単位・集計期間が分かる。不足列を一覧化できる |
| ③ API適格性 | Instagram Standard Accessの条件、TikTokの利用目的・製品・申請条件 | 許可された経路が説明できる。使えないAPIを前提にしない |
| ④ 初期スナップショット | 新旧の投稿、Reels、カルーセル等で画面・出力・APIを比較 | IDで対応付けでき、差異を日時・定義・広告等で説明できる |
| ⑤ 継続記録 | 7日程度の観測、再実行、通信断、スリープ、空値、認証失敗 | 重複なし、欠測はNULL、負の差分保持、再開時刻を正しく記録 |
| ⑥ 無人化判定 | 取得からDB保存・出力・バックアップまでの連続運転 | 自動化できた指標と手動工程が明確。必要指標の欠落を隠さない |

利用者に最初に確認する事項は、次の3点で十分です。

1. **InstagramはBusiness／Creator／個人のどれか。TikTokはPersonal／Businessのどれか。**
2. **両方とも本人が所有・管理し、分析画面を閲覧できるか。**
3. **既存の公式エクスポートや承認済みAPI接続があるか。ある場合、どの列が出るか。**

認証マークの追加取得や、アカウント種別変更、有料契約を先に行う必要があるとは判断していません。

**最終判断として、Instagramは条件を満たせば、今後のフォロワー総数・日別アカウントリーチ・投稿日時・投稿別リーチ／再生／いいね／保存の継続記録を公式API中心で組める見込みがあります。TikTokは、Display APIだけではリーチ・保存相当数が不足し、本人専用アプリの本番審査にも制約があります。公式エクスポートの実列を確認し、必要ならAccounts APIの追加条件を評価する順序が妥当です。**

両SNSとも、収集開始日の初期値から記録を積み上げます。毎日の累計観測は可能性がありますが、**全投稿の「その日に発生した再生・いいね・保存・リーチ」をすべて正確に無人取得できる、という約束はできません。**

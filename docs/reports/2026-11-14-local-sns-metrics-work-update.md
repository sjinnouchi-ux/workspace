# ChatGPT Work: アカウント種別反映後の更新結論

回収日: 2026-11-14。Workチャット「SNS指標取得調査報告」。本文のURLを保持し表示用引用マーカーのみ除去。直後の利用者追加確認は「TikTokのインサイトは閲覧できる」。画面閲覧可能という事実を含む現在の前提は[調査案](../proposals/2026-11-14-local-sns-metrics-feasibility.md)を優先する。

この外部モデル回答の『Instagramは条件が整っている』はAPI取得成功を示さない。本人管理権限、アプリ設定、認可、実取得は未検証であり、Codexの採用判断は条件付き見込みに限定する。

---

**結論は、Instagramは公式APIによる日次記録を進められる条件が整っています。一方、現在のTikTok個人アカウントで「保存数・リーチまで完全自動取得できる」とは確認できません。** この2項目の完全自動取得を必須条件にするなら、現時点では実装開始の判断は保留です。

認証マークがないことと、API利用権限・アプリ審査は別問題です。以下は公式資料を**2026年11月14日**に確認した結果です。

| 対象・指標 | 今回の前提での結論 |
|---|---|
| Instagram：フォロワー総数 | プロアカウントなので公式APIの対象。本人の管理権限・アプリ設定・必要な認可が成立すれば毎日取得可能 |
| Instagram：アカウントリーチ | 公式Insights APIで日別取得が可能。推定値・反映遅延を含む |
| Instagram：投稿日時、投稿別リーチ・再生・いいね・保存 | Feed／Reelsを中心に公式APIで取得可能。投稿指標は原則累計値を毎日観測する構成 |
| TikTok：フォロワー総数 | Display APIに`follower_count`が存在。ただしアプリ承認と`user.info.stats`の認可が必要。今回の本人専用ローカル用途で利用できるとは未確定 |
| TikTok：投稿日時・再生・いいね | Display APIに`create_time`・`view_count`・`like_count`が存在。公開動画が対象。同じく利用承認が条件 |
| **TikTok：アカウント／投稿リーチ** | **Display APIでは取得不可。現在の個人アカウントで使える、承認済みの無人取得経路は未確認** |
| **TikTok：保存相当数（Favorites）** | **Display APIでは取得不可。現在の個人アカウントでの完全自動取得は確認できない** |

Instagramの条件・指標：[Meta Insights](https://developers.facebook.com/documentation/instagram-platform/insights)、[Account Insights](https://developers.facebook.com/documentation/instagram-platform/api-reference/instagram-user/insights)、[Media Insights](https://developers.facebook.com/documentation/instagram-platform/reference/instagram-media/insights)。
TikTokのフィールド：[User Info](https://developers.tiktok.com/docs/en/tiktok-api-v2-get-user-info)、[Video Object](https://developers.tiktok.com/docs/en/tiktok-api-v2-video-object)。

**TikTok個人アカウントを維持する場合は、次のように分けます。**

| 経路 | アカウント種別変更 | 追加条件と今回の評価 |
|---|---|---|
| TikTok Studioなどの公式分析画面・公式出力 | 変更を前提にしない | 現在のアカウントで表示・出力できる項目を確認する候補。保存相当数・投稿別リーチが必要な粒度で出力されるかは未確認。手動ダウンロード＋DBへの自動取り込みなら半自動 |
| Display API | Businessへの変更が必須とはされていない | アプリ・製品・scopeの承認と本人認可が必要。さらに公式審査基準は私的・個人利用向けアプリを認めておらず、今回の本人専用ローカル集計には障壁がある。保存数・リーチは承認されても取得できない |
| Accounts API | **変更必須とは断定しない** | 公式資料にはPersonal Accountも対象とする案内がある。ただし別のアクセス申請・審査・アカウント認可が必要。承認後に使える指標・権限まで確認する必要がある |
| Web Business Suite | Business Accountが条件 | 現在の個人アカウント向けの標準案には含めない。変更しても全投稿の保存数・リーチの無人取得が保証されるわけではない |
| 管理画面の操作自動化 | 種別変更とは別問題 | 自動収集の許可・安定性が確認できていないため、完全自動化を成立させる代替案として採用しない |

根拠：[TikTok App Review Guidelines](https://developers.tiktok.com/docs/en/app-review-guidelines)、[Accounts API案内](https://business-api.tiktok.com/gateway/docs/index?doc_id=1737565048641538&language=ENGLISH)、[Web Business Suite](https://ads.tiktok.com/resources/help/article/navigate-web-business-suite)。確認日：2026-11-14。

**今回の推薦構成は、InstagramのAPI取得と、TikTokの公式出力取り込みを分けたPython＋SQLiteです。** TikTokのアカウント種別変更は前提にしません。Accounts APIは、個人アカウントのままで必要指標を取得できる承認条件が確認できた場合だけ追加候補とします。

記録は収集開始日の初期スナップショットから始めます。UTCの観測時刻・JST日付・投稿ID・指標定義・取得元を保存し、未取得は`NULL`にします。投稿累計値の差分は、取り消し・再集計・遅延を含む**観測間の純増減**として扱います。特に累計リーチの差分を「その日のリーチ」とは呼びません。

したがって、最終的な判断は次のとおりです。

- **Instagram：必要な認可・設定を確認後、今後の日次自動記録を組める見込みがある。**
- **TikTok個人アカウント：公式出力を使った半自動集計は候補。APIによる取得は別途条件確認が必要。**
- **TikTokの保存数・リーチ：現在の条件のままで完全自動取得できるとは言えない。Accounts API等の承認と指標対応を確認するまでは、必須要件を満たしたと判定しない。**

今回は調査のみで、実装・SNS認証・プロジェクト立ち上げは行っていません。

## インサイト閲覧可能という最終追加前提を反映したWork回答

前提を更新します。**TikTokは非企業用アカウントで、現在インサイトを閲覧できています。分析を見るためのビジネス化は不要です。** Instagramはプロアカウント、両方とも認証マークなし、記録は収集開始日からとします。

| 項目 | 更新した判定 |
|---|---|
| TikTok Studio等のインサイト閲覧 | **確認済み**：利用者が現在閲覧できている |
| TikTokの公式ファイル出力 | **未確認**：現在のアカウントでダウンロードできるか、投稿ID・日時・再生・いいね・Favorites・リーチが実際に出力されるかは、画面閲覧とは別に確認が必要 |
| TikTok Display API | フォロワー数・投稿日時・再生数・いいね数のフィールドはある。ただし本人専用アプリの審査条件が障壁。**リーチ・Favoritesは取得対象にない** |
| TikTok Accounts API | 個人アカウントも対象になり得るが、別申請・審査・認可が必要。**ビジネス化を当然の前提にしない**。今回の利用可否と必要指標の対応は未確認 |
| Instagram公式API | プロアカウントなので対象。管理権限・アプリ設定・認可が成立すれば、要求指標の日次記録が可能な見込み |

公式根拠の確認日：**2026-11-14**。[TikTok Video Object](https://developers.tiktok.com/docs/en/tiktok-api-v2-video-object)、[審査基準](https://developers.tiktok.com/docs/en/app-review-guidelines)、[Accounts API](https://business-api.tiktok.com/gateway/docs/index?doc_id=1737565048641538&language=ENGLISH)、[Instagram Insights](https://developers.facebook.com/documentation/instagram-platform/insights)。

**更新結論：InstagramはAPI中心、TikTokは現在使えているインサイトの公式出力を確認するところから始める併用案が妥当です。** 出力できれば取り込み・DB集計は自動化できますが、手動ダウンロードが残れば半自動です。**TikTokの保存相当数・リーチを毎日完全自動取得できることは、まだ確認できていません。**

開始日の値を初期スナップショットとして保存し、以後の累計値と差分を分けます。未取得は0にせず、累計差分は日次活動の真値として扱いません。実装・認証・プロジェクト作成は行っていません。

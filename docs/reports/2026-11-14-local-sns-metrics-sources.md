# ローカルSNS集計: 公式資料の確認境界

確認日: 2026-11-14（JST）。Codexによる公開資料の読取り。実アカウントでは未検証。以下は短い要約であり、公式本文の転載ではない。

| 公式出典 | 確認した仕様と限界 |
|---|---|
| [Instagram Insights guide](https://developers.facebook.com/documentation/instagram-platform/insights) | プロアカウントが対象。Instagram Login経路は `instagram_business_basic` と `instagram_business_manage_insights`。自ら所有/管理しApp Dashboardに追加したアカウントにはStandard Accessの経路が示される。他者のアカウント向けはAdvanced Access。認証バッジが必要という条件はこの資料にない。実際のアプリ/アカウントの適合性は未確認。 |
| [Instagram Media Insights](https://developers.facebook.com/documentation/instagram-platform/reference/instagram-media/insights) | Feed/Reelsの `reach`、`likes`、`saved`、`views` が掲載される。投稿種別で対応指標が違う。responseのperiod説明ではlifetime固定であり、汎用parameter一覧にdayがあるだけでは投稿別日次履歴取得の根拠にしない。広告/Facebook込みのtotal系列を通常系列と混ぜない。 |
| [Instagram Media reference](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/v21.0/) | 投稿日時timestampがある。閲覧時の本文は現行v27.0を表示した。プロアカウント所有メディアが対象。saved_count等のobject fieldはFacebook Login限定等の条件があり、Insightsのsavedと経路を混同しない。実装時は採用API版を固定する。 |
| [TikTok Get User Info](https://developers.tiktok.com/docs/en/tiktok-api-v2-get-user-info) | follower_countはuser.info.stats。認証マークのis_verifiedは別フィールド。認証マークなしという情報だけでAPI取得可否は決まらない。 |
| [TikTok Video Object](https://developers.tiktok.com/docs/en/tiktok-api-v2-video-object) | create_time、like_count、view_countを確認。Display APIのこのobjectにはreachやfavorites/savedはない。API for Businessの別仕様にある指標と混ぜない。 |
| [TikTok Query Videos](https://developers.tiktok.com/docs/en/tiktok-api-v2-video-query) | video.list scope、本人所有の動画を対象とする照会、1リクエスト20IDまで。過去累計の期間別履歴を返す仕様ではなく、今後の観測値の更新に使う候補。 |
| [TikTok Display API Get Started](https://developers.tiktok.com/docs/en/display-api-get-started) | 開発者登録、Login Kit/TikTok API製品の承認、scope、ユーザー認可が必要。公開プロフィール表示が想定される製品であり、ローカル分析専用アプリとしての審査適合性を実装前に確認する。 |
| [TikTok App Review Guidelines](https://developers.tiktok.com/docs/en/app-review-guidelines) | Description節は私的・個人利用向けアプリを認めないと規定する。この用途の自作Display APIアプリが本番承認される前提を置かない。API for BusinessのAccounts APIとは別製品の条件であり、この禁止をAccounts API全般へ拡張しない。 |
| [TikTok Accounts API overview](https://business-api.tiktok.com/portal/docs/accounts-api-overview/v1.3) / [Accounts API案内](https://business-api.tiktok.com/gateway/docs/index?doc_id=1737565048641538&language=ENGLISH) | 公式の検索表示本文で、Personal/Business Account活動のプログラム管理、ブランド/creator所有アカウントの分析という用途と、2026-03-20以降の対象新規申請・scope追加に専用Access Application Formが必要であることを確認。General Personal AccountはBusiness Suiteへの入口を持たず、Advanced AccessはTikTok for Business等との連携による追加段階と説明される。プロフィールの認証マークとは別。この利用者が承認されるか、必要な保存/リーチ指標が得られるかは未確認。 |
| [TikTok Web Business Suite](https://ads.tiktok.com/resources/help/article/navigate-web-business-suite?lang=en) | 管理画面の分析機能がある。対象アカウントでCSVが出るか、投稿別保存/リーチが含まれるか、日付が何を意味するかは実ファイルで未確認。 |
| [Microsoft TaskSettings](https://learn.microsoft.com/en-us/windows/win32/taskschd/tasksettings) | StartWhenAvailableとWakeToRunの設定がある。遅延起動は当時の累計値を復元しない。PC固有の復帰/電源/ネットワーク条件は実測対象。 |

## Codexによる暫定結論

認証マークなし・過去分不要という条件は、今後のスナップショット記録という設計と両立する。Windows側のDB保存と日次実行は通常のローカル構成で候補にできる。難所はDB自体ではなく、両SNSの対象アカウントで希望指標を正式に取得できる経路である。

利用者確認でInstagramはプロ、TikTokは企業用ではないがインサイトを閲覧できる。Instagramは権限等が合えば希望指標の多くを取得できる公式経路がある。TikTok通常Display APIだけで保存数とリーチを満たす根拠はなく、私的アプリの本番審査制約もある。現在閲覧できるインサイトの公式出力の可否・実列、またはAccounts APIの適合確認が必要。現時点の提案は条件付きの実現可能性であり、全指標完全自動の実証ではない。

## 保存・監査の準備

- Workspace main基準: `00c978297e1e34ae90f7325acd277702d48c39e8`。
- Development-environment controller基準: `c654afb2d27599a7803d8a5dd5a63aef6a089d42`。初回確認からの差分は他タスクの文書のみで、監査契約・runner変更なし。
- 対象は立ち上げ前の一般化した設計資料のみ。SNSアカウントID、実指標、認証値、ブラウザ履歴、生診断は記録しない。
- 新規プロジェクト/repoの立ち上げ、台帳更新、SNS認可、実データ取得、ジョブ登録は実施していない。
- 文書のみのためアプリ/DBの重いテストは不要。差分、UTF-8、リンク/参照、秘密情報がないこと、GitHubからの読戻しを検証する。

# 現在のTikTokアカウントの公式出力確認

確認日: 2026-11-14（JST）。アプリ内ブラウザで利用者がログインした対象アカウントと、ログイン後のTikTok Studioを確認した。企業用への切替、認証マーク追加、API認可、プロジェクト作成、実装、DB登録、定期化は行っていない。

## 結果

| 対象 | 画面での閲覧 | 今回確認した公式CSV |
|---|---|---|
| 投稿別の保存相当数 | 投稿詳細の概要でブックマークアイコンと数値が表示された。 | 保存数、Saves、Favorites等の列はなかった。 |
| 投稿別の総視聴者数 | 投稿詳細の視聴者タブで表示された。 | コンテンツCSVに投稿別総視聴者数/Reach列はなかった。投稿詳細の概要・視聴者・エンゲージメントを確認した範囲で、専用のダウンロード機能は見つからなかった。 |
| アカウントの日別総視聴者数 | アカウントの視聴者タブで表示された。 | Viewers.csvにDate、Total Viewers、New Viewers、Returning Viewersが出力された。 |
| 投稿別再生数・いいね数・投稿日 | コンテンツ/投稿詳細で閲覧できた。 | Content.csvにTotal views、Total likes、Post time、Video link等が出力された。 |

画面では「総視聴者数」と表示され、投稿詳細の説明は投稿を見た視聴者について新規と戻ってきた視聴者を含める内容だった。今回はReachという名前の列や、Instagram reachと完全に同一であるという定義までは確認していない。Total Viewersを「リーチ」と無条件で改名せず、元指標名で保持する。

したがって、アカウント日別の総視聴者数は公式CSVで取り出せる。一方、今回確認した公式CSVだけでは、投稿別の保存相当数と投稿別リーチ/総視聴者数の継続記録を満たせない。画面にある数値をファイルでも出せるとは判断しない。他の製品/APIや未確認の出力手段も含めた全面的な取得不可とは断定しない。

## 実際に出力して確認した列

いずれもTikTok Studioの「データをダウンロード」からCSVを選び、ZIPをダウンロードして内部CSVの列を確認した。XLSXも選択肢として表示されたが、XLSX本体は今回検証していない。

| 画面/内部ファイル | 実列（原表記） | サンプル範囲 |
|---|---|---|
| 概要 / Overview.csv | Date, Video Views, Profile Views, Likes, Comments, Shares | 画面既定の直近7日、7行。保存/Reach/総視聴者数の列なし。 |
| コンテンツ / Content.csv | Time, Video title, Video link, Post time, Total likes, Total comments, Total shares, Total views | 15行、15種類の空欄でないVideo link、Post timeあり。画面は「あなたのトップ投稿」であり、全投稿の完全一覧だとは保証しない。Time列の意味、期間と累計の境界、元タイムゾーンは別途確認が必要。 |
| 視聴者 / Viewers.csv | Date, Total Viewers, New Viewers, Returning Viewers | 画面既定の直近7日、7行。投稿IDやVideo linkはなく、アカウント全体の日別系列である。 |

過去分のDB埋戻しは目的にせず、出力機能と列の検証に必要な既定期間の少量サンプルだけを確認した。CSVの値・投稿本文・個別の投稿ID・視聴者属性・認証情報はこの公開記録へ転載していない。原本ZIPはブラウザの通常Downloadsに保持し、Gitの作業場へコピーしていない。

## 確認した正規画面

- TikTokの本人プロフィールから、通常メニューのTikTok Studioへ進んだ。
- [概要](https://www.tiktok.com/tiktokstudio/analytics)
- [コンテンツ](https://www.tiktok.com/tiktokstudio/analytics/content)
- [視聴者](https://www.tiktok.com/tiktokstudio/analytics/viewers)
- 既存投稿1件の「データを表示」から、概要・視聴者・エンゲージメントを確認した。対象の実ID/実数値は公開記録に載せない。

## 構成案への影響と残条件

- InstagramのAPI候補とTikTok公式ファイルの取込みを分ける案は維持する。ただしTikTokの今回の出力では、保存相当数と投稿別リーチは欠ける。必須指標をすべて満たしたとは扱わない。
- 日別アカウントTotal Viewersは記録候補にできる。投稿別再生/いいね等は出力対象投稿と集計期間の確認が残る。毎日取り込んでも全投稿が含まれる保証は今回得ていない。
- 保存相当数・投稿別総視聴者数を今後必須とする場合、正式に利用できる別経路の確認が残る。画面の数値の自動読取りは別の規約/運用調査であり、今回その可否を検証・実装していない。
- API/無人ダウンロード、PC停止時の運転、CSVの自動取込み、DB、バックアップは未構築。新規プロジェクトは未作成。
- これは前回Fable監査後の利用者指定による実画面・実CSV確認の追記であり、再監査は行っていない。

## Gitと検証

Canonical areaは既存のworkspace共通調査、[draft PR80](https://github.com/sjinnouchi-ux/workspace/pull/80)を継続する。default main `00c978297e1e34ae90f7325acd277702d48c39e8`、開始時branch head `be87cede427830d402eff4838f0b04924e20e6ec`、upstream同SHA、default比ahead3/behind0、全branch refspec、credential-free origin、Windows-native Git、開始時cleanを確認した。

CSVの実列・構造確認、UTF-8、文書差分と参照、秘密値や実指標をGitへ持ち込んでいないこと、push後のGitHub読戻しを検証する。アプリ/DB変更がないため重いテストは不要。前回の作業場削除拒否を維持し、別経路で削除を再試行しない。

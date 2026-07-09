# dori-manga

どり看護師の Instagram 漫画化プロジェクト。

[@dori_nurse](https://www.instagram.com/dori_nurse/)（約5万フォロワー）向けの漫画コンテンツを
定期配信し、エンゲージメント向上・お守り販売への導線強化を目指す。

## ドキュメント

| ファイル | 内容 |
|----------|------|
| `docs/concept.md` | キャラクター・世界観・コンセプト設定 |
| `docs/episode_list.md` | エピソード管理リスト |
| `docs/supabase/supabase-db-design.md` | 画像生成評価DBの設計 |
| `docs/supabase/chatgpt-db-instruction.md` | ChatGPT向けDB連携・画像評価指示 |
| `docs/secret-management.md` | Secret Managerによる秘密値管理方針 |
| `docs/work_log.md` | 作業ログ |

## GAS

| ファイル | 内容 |
|----------|------|
| `gas/create_manga_folders.gs` | Google Driveフォルダ作成 |
| `gas/supabase-import/dori-manga-import.gs` | スプレッドシートからSupabaseへ画像評価を登録 |

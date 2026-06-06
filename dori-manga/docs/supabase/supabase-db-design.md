# Supabase DB 設計ドキュメント

**プロジェクト名**: dori-manga  
**Organization**: Yumekango  
**用途**: ChatGPT Image2.0 で生成した漫画画像のOK/NG評価を蓄積し、次回プロンプト改善に活かす「画像生成学習DB」  
**最終更新**: 2026-05-28

---

## テーブル一覧

| テーブル名 | 役割 | 種別 |
|---|---|---|
| `characters` | キャラクター情報（プロンプト付き） | マスター |
| `prompt_templates` | 再利用プロンプトテンプレート | マスター |
| `manga_episodes` | 1投稿分（4コマ1セット） | 漫画管理 |
| `manga_panels` | 1コマごとの設計情報 | 漫画管理 |
| `generation_attempts` | 1回の画像生成ごとの試行履歴 | **中心テーブル** |
| `prompt_lessons` | 次回プロンプト改善ルール | 学習 |

---

## テーブル詳細

### 1. characters

キャラクターのプロンプト情報を管理する。`base_prompt` と `negative_prompt` をそのままChatGPTへ貼り付けて使う。

| カラム名 | 型 | 説明 |
|---|---|---|
| `id` | uuid (PK) | 自動採番 |
| `name` | text NOT NULL | どり看護師 / 看護師（ポニーテール） |
| `base_prompt` | text | 生成に使う基本プロンプト全文 |
| `negative_prompt` | text | 除外指示（ネガティブプロンプト） |
| `reference_image_url` | text | 参考画像のURL |
| `is_active` | boolean | 使用中かどうか（default: true） |
| `created_at` | timestamptz | 作成日時 |

**登録済みデータ**:
- `どり看護師` — ピンクのうさぎナースキャラクター
- `看護師（ポニーテール）` — 人間の女性看護師

---

### 2. prompt_templates

シーンや構図ごとの汎用プロンプトテンプレート。`{expression}` `{action}` などの変数を含む。

| カラム名 | 型 | 説明 |
|---|---|---|
| `id` | uuid (PK) | 自動採番 |
| `name` | text NOT NULL | テンプレート名（例: どり看護師_標準コマ） |
| `template_text` | text NOT NULL | プロンプト本文（変数含む） |
| `negative_prompt` | text | 除外指示 |
| `is_active` | boolean | 使用中かどうか（default: true） |
| `created_at` | timestamptz | 作成日時 |

**登録済みデータ**:
- `どり看護師_標準コマ` — 1キャラ構図
- `2キャラ構図` — どり看護師＋看護師の2人構図

---

### 3. manga_episodes

Instagram投稿1本分（4コマ漫画1セット）を管理する。

| カラム名 | 型 | 説明 |
|---|---|---|
| `id` | uuid (PK) | 自動採番 |
| `title` | text NOT NULL | エピソードタイトル |
| `theme` | text | テーマ（例: 採血, 夜勤, 患者対応） |
| `status` | text | 制作状態（下記参照） |
| `created_at` | timestamptz | 作成日時 |

**status の値**:
| 値 | 意味 |
|---|---|
| `draft` | 下書き（default） |
| `in_progress` | 制作中 |
| `completed` | 完成 |
| `posted` | 投稿済み |

---

### 4. manga_panels

1コマごとの設計情報。採用した画像を `selected_attempt_id` で参照する。

| カラム名 | 型 | 説明 |
|---|---|---|
| `id` | uuid (PK) | 自動採番 |
| `episode_id` | uuid (FK → manga_episodes) | 所属エピソード |
| `panel_number` | integer NOT NULL | コマ番号（1〜4） |
| `scene_text` | text | コマの内容説明 |
| `target_prompt` | text | このコマの目標プロンプト |
| `selected_attempt_id` | uuid (FK → generation_attempts) | 採用した試行のID |
| `status` | text | 制作状態（下記参照） |
| `created_at` | timestamptz | 作成日時 |

**status の値**:
| 値 | 意味 |
|---|---|
| `draft` | 下書き（default） |
| `generating` | 生成中 |
| `selected` | 採用画像決定済み |
| `rejected` | 没 |
| `completed` | 完了 |

---

### 5. generation_attempts（中心テーブル）

**1回の画像生成 = 1行**。Google Drive情報・評価・ChatGPT評価JSONをまとめて保存する。

| カラム名 | 型 | 説明 |
|---|---|---|
| `id` | uuid (PK) | 自動採番 |
| `panel_id` | uuid (FK → manga_panels) | 対象コマ |
| `attempt_number` | integer | 試行回数（1回目, 2回目…） |
| `image_url` | text | Google Drive 共有URL |
| `drive_file_id` | text | Google Drive ファイルID（GAS/Python連携用） |
| `file_name` | text | ファイル名（例: ep1_panel2_attempt3.png） |
| `folder_status` | text | Driveの保存フォルダ（OK/NG/CLOSE/PENDING） |
| `result_status` | text NOT NULL | DB上の評価結果（OK/NG/CLOSE/PENDING） |
| `final_generation_prompt` | text | 実際に使ったプロンプト全文 |
| `evaluation_summary` | text | 評価の一言まとめ |
| `evaluation_json` | jsonb | ChatGPTが出力した評価JSON（下記参照） |
| `created_at` | timestamptz | 作成日時（default: now()） |

**result_status / folder_status の値**:
| 値 | 意味 |
|---|---|
| `OK` | 採用 |
| `NG` | 没 |
| `CLOSE` | 惜しい（次回参考） |
| `PENDING` | 評価待ち（default） |

---

### 6. prompt_lessons

`evaluation_json` から手動または自動で抽出した、次回プロンプト改善ルール。

| カラム名 | 型 | 説明 |
|---|---|---|
| `id` | uuid (PK) | 自動採番 |
| `source_attempt_id` | uuid (FK → generation_attempts) | 学習元の試行ID |
| `lesson_text` | text NOT NULL | 改善ルール本文 |
| `is_active` | boolean | 有効/無効（default: true） |
| `created_at` | timestamptz | 作成日時 |

**例**:
> 「どり看護師の目は必ず `small black dot eyes, no eye highlights` と明記する」

---

## テーブル関係（FK）

```
manga_episodes
  └─ 1:N ─ manga_panels
               └─ 1:N ─ generation_attempts
                             └─ 1:N ─ prompt_lessons
manga_panels.selected_attempt_id ──→ generation_attempts（採用画像の逆参照）
```

---

## evaluation_json フォーマット

画像生成後にユーザーがOK/NG/CLOSEを判断し、ChatGPTに出力させるJSON。
このJSONをそのまま `generation_attempts.evaluation_json` に保存する。

```json
{
  "result": "NG",
  "image_features": [
    "うさぎの目が大きい",
    "耳の内側が青くない",
    "背景に薄いグラデーションがある"
  ],
  "good_points": [
    "構図は自然",
    "看護師との距離感は良い"
  ],
  "ng_reason": "どり看護師の固定特徴（小さい黒目・light blue inner ears）と異なる",
  "next_prompt_hint": "small black dot eyes, no eye highlights, light blue inner ears を強調する",
  "reuse_possible": false
}
```

### フィールド定義

| フィールド | 型 | 説明 |
|---|---|---|
| `result` | string | OK / NG / CLOSE / PENDING |
| `image_features` | string[] | 画像の特徴（良し悪し問わず） |
| `good_points` | string[] | 良かった点 |
| `ng_reason` | string \| null | NGの理由（NGの場合必須） |
| `next_prompt_hint` | string \| null | 次回プロンプトへの改善ヒント |
| `reuse_possible` | boolean | CLOSEの場合に次回の参考として使えるか |

---

## DB登録用JSONフォーマット（ChatGPTへの出力依頼用）

画像生成後にChatGPTへ渡すプロンプトで、以下のJSONを出力させる。
GASがこのJSONを読み取り、`generation_attempts` へ1行登録する。

```json
{
  "attempt_number": 3,
  "result_status": "NG",
  "final_generation_prompt": "A cute pink bunny nurse, small black dot eyes, light blue inner ears...",
  "evaluation_summary": "目の形とキャラクター一致性に問題あり",
  "evaluation_json": {
    "result": "NG",
    "image_features": ["うさぎの目が大きい", "耳の内側が青くない"],
    "good_points": ["構図は自然"],
    "ng_reason": "どり看護師の固定特徴と異なる",
    "next_prompt_hint": "small black dot eyes, no eye highlights, light blue inner ears を強調",
    "reuse_possible": false
  },
  "prompt_lesson_candidates": [
    "どり看護師の目は必ず small black dot eyes, no eye highlights と明記する",
    "内耳は light blue inner ears を必ず追加する"
  ]
}
```

> `episode_title` / `panel_number` / `file_name` はオプション（省略可）。省略時はスプレッドシートB4の値・Driveファイル名を使用。

---

## 運用ワークフロー（GASベース・現行）

```
1. ChatGPT Image2.0 でコマ画像を生成
2. ユーザーが OK / NG / CLOSE を判断
3. ChatGPT に評価JSONの出力を依頼 → DB登録用JSONを取得
4. スプレッドシート「画像格納」シートに入力
   - B2: 画像のGoogle Drive URL
   - B4: panel_number（コマ番号・必ず数値で入力）
   - B5〜B7: OK/NG/CLOSE フォルダURL
   - B8: OK / NG / CLOSE を選択
   - B9: ChatGPTが出力したJSON を貼り付け
5. 「🩺 どり漫画DB」メニュー → 「▶ DBにインポート実行」を押す
6. 確認ダイアログで内容を確認してYESを押す
7. GASが自動処理：
   - manga_episodes を title で検索 → なければ自動作成（draft）
   - manga_panels を episode_id + panel_number で検索 → なければ自動作成
   - generation_attempts に1行INSERT
   - prompt_lesson_candidates を prompt_lessons に複数INSERT
   - Google Drive の画像を OK/NG/CLOSE フォルダへ移動
   - B9をクリア（二重登録防止）
8. 次回生成時に prompt_lessons を参照してプロンプト改善
```

### 運用上の注意

| 項目 | ルール |
|------|--------|
| `episode_title` | JSONに含めなくてもOK（省略時は `(未設定)` でエピソード自動作成） |
| `panel_number` | JSONに含めなくてもOK。その場合はB4セルの値を使用。**必ず数値で入力すること** |
| `file_name` | JSONに含めなくてもOK（省略時はDriveの実ファイル名を使用） |
| `service_role`キー | GASのスクリプトプロパティに格納。チャット・ファイルへの記載禁止 |

---

## Supabase接続情報

| 項目 | 値 |
|------|-----|
| プロジェクトURL | https://supabase.com/dashboard/project/vdntqwtywxyjxelycavx |
| REST API URL | https://vdntqwtywxyjxelycavx.supabase.co |
| Publishable（anon）キー | sb_publishable_b8a4K90d5R6S5RZReLa-HA_G6nNwKKW |
| Table Editor | https://supabase.com/dashboard/project/vdntqwtywxyjxelycavx/editor |

```env
SUPABASE_URL=https://vdntqwtywxyjxelycavx.supabase.co
SUPABASE_ANON_KEY=sb_publishable_b8a4K90d5R6S5RZReLa-HA_G6nNwKKW
SUPABASE_SERVICE_ROLE_KEY=（GASスクリプトプロパティに設定済み・ここには記載しない）
```

> ⚠️ `service_role key` はRLSをバイパスするため、GASスクリプトプロパティにのみ格納。このファイルやチャットへの記載禁止。

---

## Python 登録サンプル

```python
from supabase import create_client
import os, json

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

def register_attempt(data: dict):
    """DB登録用JSONを generation_attempts へ1行登録する"""
    row = {
        "panel_id":                 data.get("panel_id"),          # UUIDは事前に取得
        "attempt_number":           data.get("attempt_number"),
        "image_url":                data.get("image_url"),
        "drive_file_id":            data.get("drive_file_id"),
        "file_name":                data.get("file_name"),
        "folder_status":            data.get("folder_status"),
        "result_status":            data.get("result_status"),
        "final_generation_prompt":  data.get("final_generation_prompt"),
        "evaluation_summary":       data.get("evaluation_summary"),
        "evaluation_json":          data.get("evaluation_json"),    # dict のまま渡す
    }
    result = supabase.table("generation_attempts").insert(row).execute()
    return result
```

---

## DB登録用JSON 実例（2026-05-28 初回OK確認済み）

attempt_number 6・WBC/CRP解説コマ・OK判定での実際の登録JSON。

```json
{
  "attempt_number": 6,
  "result_status": "OK",
  "final_generation_prompt": "Create a clean soft pastel manga comic style medical illustration in a single vertical 3:4 panel with a thick black border. Scene: nurse station. Use a simple, uncluttered background with large blank white space, minimal objects, and focus on characters. On the left, place a young female nurse in simple black-and-white manga line art with light brown pencil-textured hair, worried and confused expression, sweat marks, and a hand near her chin. She is holding one sheet of paper. On the paper, write only the Japanese text 「検査データ」 and do not include detailed lab values on the paper. Above the nurse, place a speech bubble with exactly: 「まだ見てなかった…\nCRPまだ正常…？」. Around the nurse's head, add confusion text exactly: 「WBC？」 and 「CRP？」 with small question marks and a worried blue face icon. On the right, place Dori nurse: a cute pink bunny character with white belly, white muzzle, black dot eyes with no highlights, blue inner ears, round chubby silhouette, purple stethoscope, and yellow medical notebook. Dori has a cheerful, expressive, gentle teaching face similar to the provided reference, with a small open smiling mouth and one finger raised. Above Dori, place a speech bubble with exactly: 「WBCは\n\"先に\"上がることが\n多いんだ」. Between/above Dori and the nurse, include a simple educational graph titled 「炎症マーカーの推移イメージ」 showing WBC rising earlier than CRP. Use a pink WBC curve that rises first and a blue CRP curve that rises later. Label the axes with 「高」 at the top, 「低」 at the bottom, and 「時間経過」 on the horizontal axis. Add a small label 「WBCが先行」 above the graph. Keep all Japanese text clean and readable. Maintain rough pencil texture, simple line art, reduced visual clutter, and pastel coloring only for Dori, graph, and small accents.",
  "evaluation_summary": "構図・内容OK",
  "evaluation_json": {
    "result": "OK",
    "image_features": [
      "ナースステーションの1コマ漫画",
      "看護師が検査データ用紙を持つ",
      "頭周囲にWBC？CRP？の混乱演出",
      "どり看護師がWBC先行を説明",
      "WBCとCRPの推移グラフあり"
    ],
    "good_points": [
      "指定セリフが概ね反映されている",
      "用紙の文字が検査データのみでシンプル",
      "どりの表情が明るく教育的",
      "WBC先行のグラフが視覚的に分かりやすい"
    ],
    "ng_reason": null,
    "next_prompt_hint": null,
    "reuse_possible": true
  },
  "prompt_lesson_candidates": [
    "検査用紙には詳細数値を書かせず「検査データ」のみを明記すると画面が整理される",
    "WBCとCRPの説明では、右側に小さな推移グラフを配置すると教育漫画として分かりやすい",
    "どり看護師は参考画像のように黒点目・小さな開口笑顔・指差しポーズにすると表情が豊かになる"
  ]
}
```

> `episode_title` と `panel_number` はJSONに含めず、B4セルで管理する運用に変更（2026-05-28）。

---

## 検証ログ

| 日付 | 内容 | 結果 |
|------|------|------|
| 2026-05-27 | GASスクリプト初回実装・GitHubにPush | ✅ |
| 2026-05-27 | `Header:null` エラー → SUPABASE_SERVICE_ROLE_KEY 未設定が原因 | ✅ 修正 |
| 2026-05-27 | `Cannot read properties of undefined (reading 'id')` → manga_panelsにレコードなし | ✅ 自動作成ロジック追加 |
| 2026-05-27 | `PGRST204 description column not found` → manga_panelsにdescriptionカラム不存在 | ✅ 削除 |
| 2026-05-27 | 画像移動がDB書き込み前に実行されていた | ✅ 実行順序修正 |
| 2026-05-28 | `22P02 invalid input syntax for type integer` → panel_numberに文字列が入っていた | ✅ オペレーション変更（B4に数値のみ入力） |
| 2026-05-28 | normalizeLessonText追加 → prompt_lesson_candidatesの型ブレ（object混入）を吸収 | ✅ |
| 2026-05-28 | attempt_number 6・WBC/CRP解説コマ・OK判定で初回インポート成功確認 | ✅ |

---

*このドキュメントは Supabase dori-manga プロジェクトのDB設計図です。*  
*漫画プロジェクト以外への転用時は、`manga_episodes` / `manga_panels` をプロジェクト用途に合わせて置き換えてください。*

# GA4設定作業ログ — kango-mamori.com

**作業日**: 2026年5月24日
**担当**: 陣内 聡（株式会社ゆめ看護）
**対象サイト**: https://kango-mamori.com/
**CMS**: STUDIO Design
**使用Googleアカウント**: s.jinnouchi@yumekango.com

---

## 作業概要

kango-mamori.comにGoogle Analytics 4（GA4）を新規設定し、STUDIOに連携。あわせてSNS流入のトラッキング方法（UTMパラメータ）を整備した。

---

## 1. GA4アカウント・プロパティ作成

### 作成手順（5ステップウィザード）

| ステップ | 内容 | 設定値 |
|----------|------|--------|
| Step 1 | アカウントの作成 | アカウント名：`株式会社ゆめ看護` |
| Step 2 | プロパティの作成 | プロパティ名：`kango-mamori.com` / タイムゾーン：日本 / 通貨：日本円（JPY） |
| Step 3 | お店やサービスの詳細 | 業種：その他 / ビジネス規模：小規模 |
| Step 4 | ビジネス目標 | ブランド認知度の向上 を選択 |
| Step 5 | データの収集 | プラットフォーム：ウェブ |

### 作成されたGA4リソース

| 項目 | 値 |
|------|----|
| **GAアカウント名** | 株式会社ゆめ看護 |
| **プロパティ名** | kango-mamori.com |
| **タイムゾーン** | 日本（Asia/Tokyo） |
| **通貨** | 日本円（JPY） |
| **データストリーム名** | 看護のお守り |
| **ストリームURL** | https://kango-mamori.com |
| **ストリームID** | 14935330073 |
| **測定ID（Measurement ID）** | **G-JGYQG5T6NM** |

---

## 2. STUDIOへのGA4連携

### 手順

1. STUDIO Design（https://app.studio.design/）にログイン
2. kango-mamoriプロジェクトを開く
3. エディタ画面 → 左上「/S」ロゴ → **アナリティクス** をクリック
4. ダッシュボードにリダイレクトされる → **ホーム** → **Apps** タブを開く
5. 「Google Analytics」カードを選択
6. 測定ID欄に `G-JGYQG5T6NM` を入力 → 保存
7. 緑色で測定IDが表示されれば連携完了

### 確認ポイント

- STUDIOのAppsページに `G-JGYQG5T6NM` が緑色で表示されていること
- GA4管理画面のデータストリームで「ウェブサイトへのタグ設定の確認」が通ること（反映まで24〜48時間かかる場合あり）

---

## 3. SNS流入トラッキング（UTMパラメータ）

### 概要

GA4は一部のSNSからの流入を自動検出するが、Instagram・TikTok・LINEなどは精度が低い。UTMパラメータ付きURLを投稿リンクに使うことで、SNS別の流入数を正確に計測できる。

### UTMパラメータの構成

```
https://kango-mamori.com?utm_source={SNS名}&utm_medium=social&utm_campaign={キャンペーン名}
```

### SNS別URL例（キャンペーン：台湾展開）

| SNS | URL |
|-----|-----|
| Instagram | `https://kango-mamori.com?utm_source=instagram&utm_medium=social&utm_campaign=taiwan_outreach` |
| TikTok | `https://kango-mamori.com?utm_source=tiktok&utm_medium=social&utm_campaign=taiwan_outreach` |
| Facebook | `https://kango-mamori.com?utm_source=facebook&utm_medium=social&utm_campaign=taiwan_outreach` |
| LINE | `https://kango-mamori.com?utm_source=line&utm_medium=social&utm_campaign=taiwan_outreach` |
| X (Twitter) | `https://kango-mamori.com?utm_source=x&utm_medium=social&utm_campaign=taiwan_outreach` |

### 用意したキャンペーン名

| キャンペーン名（utm_campaign） | 用途 |
|-------------------------------|------|
| `taiwan_outreach` | 台湾展開関連の投稿 |
| `fukushima_hachimangu` | 福島八幡宮関連の投稿 |
| `kango_kokushi` | 看護師国試関連の投稿 |
| `general` | 一般投稿 |

### GA4での確認場所

GA4管理画面 → **レポート** → **集客** → **トラフィック獲得**
「セッションの参照元 / メディア」で `instagram / social`、`tiktok / social` 等が表示される。

---

## 4. 今後の運用フロー

```
SNS投稿時
  ↓
UTMリンクジェネレーターでページ・SNS・キャンペーンを選択
  ↓
生成されたURLをコピー → 投稿のリンク欄に貼り付け
  ↓
GA4「トラフィック獲得」レポートで流入数を確認（翌日以降）
```

---

## 5. 関連リンク

| 用途 | URL |
|------|-----|
| GA4管理画面 | https://analytics.google.com/ |
| STUDIO Design | https://app.studio.design/ |
| kango-mamori.com | https://kango-mamori.com/ |

---

## 備考・注意事項

- GA4の設定はすべて `s.jinnouchi@yumekango.com` アカウントで実施
- データ反映には最大48時間かかる場合がある
- UTMパラメータはSNSのbioリンクや各投稿のリンク欄に使用する（本文中URLは短縮URLサービスを経由するためUTMが消える場合がある点に注意）
- STUDIOのGA4連携は自動でタグをページ全体に挿入するため、手動でのタグ埋め込みは不要

---

*記録者: Claude (Cowork) / 作業日: 2026-05-24*

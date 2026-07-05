# AI経営実装度診断WEBアプリ 実装設計書（ロジック仕様書）

> 本ファイルは診断ロジック・質問・選択肢・判定・結果文言を定義する正本（人間参照用）です。
> 実装用の機械可読な正本は `config.seed.json` を参照してください（本ファイルの内容から生成済み）。

## 1. 目的

本アプリは、営業マンが経営者にその場で入力してもらうことを想定した、簡易的な「経営とAIに関する診断WEBアプリ」である。

目的は、商品パッケージや無料相談予約へ誘導することではない。診断結果をきっかけに、営業マンがその場で経営者と会話し、自然に次の提案・クロージングへ進めることを目的とする。

本診断の中心テーマは以下である。

> AIを知っているかではなく、会社としてAIを管理・実装できる状態にあるかを診断する。

特に、AI活用が進んでいるかどうかは、単なるツール利用状況ではなく、AI管理者・AI推進役・AI窓口の有無と役割の明確さで判断する。

## 2. 診断で扱う範囲

含める内容：社長自身のAI利用状況／社長が使っているAIの種類／AIエージェント利用状況／LLM・API利用状況／現場・社員のAI利用状況／AI管理者・AI推進役・社内窓口の有無／AI管理者の役割の明確さ／従業員全体へのAI知見の広がり／外部専門家のAI対応状況。

含めない内容：画像生成AI／NotebookLM等の個別ツール／議事録AI・動画生成AI・SNS投稿AI等のツール診断／経営戦略・事業計画のコンサル／売上・採用・価格戦略への提言／セキュリティ診断としての判定／「情報漏洩リスクが高い」等の断定的結果表示。

除外理由：本診断は経営コンサルではなくAIアーキテクト的な実装・管理体制の診断。セキュリティリスクは質問回答だけでは精度高く判定できないため、結果として「セキュリティ不安タイプ」は設けない。

## 3. 画面構成（全体フロー）

1ページ目 トップページ（会社名=必須／業種=任意／注意書き／開始ボタン）→ 2ページ目 従業員数選択（ボタン形式）→ 3ページ目以降 診断質問（3〜4択ボタン、回答で分岐）→ 結果表示 4ステップ（①経営者の声 ②現在の状態 ③このまま進むと起きやすいこと ④最初に決めるべきこと）。

## 4. トップページ仕様

タイトル：AI経営実装度診断
サブタイトル：最大10問・3分ほどで、会社としてAIを管理・実装できる状態にあるかを確認する簡易診断です。
保険文言（必須）：本診断は、経営とAI活用に関する自社ノウハウをもとにした簡易診断です。結果はあくまで参考情報であり、個別の状況により異なります。

入力項目：会社名（必須・テキスト・空欄では開始不可）／業種（任意）。
入力させない：氏名・役職・メール・電話・無料相談予約・面談希望日。

## 5. 2ページ目：従業員数選択

質問文：御社の従業員規模を教えてください。

| value | ラベル | 判定上の扱い |
|---|---|---|
| employee_1_9 | 1〜9人 | 小規模。社長自身の管理でも成立しやすい |
| employee_10_29 | 10〜29人 | 社内窓口があると望ましい |
| employee_30_99 | 30〜99人 | AI管理者の必要度が上がる |
| employee_100_200 | 100〜200人 | AI管理者なしでは現場展開が難しい |
| employee_201_plus | 201人以上 | 想定外規模。ただし診断は継続可能 |

従業員規模だけで結果を確定させない。ただし30人以上の場合はAI管理者・AI窓口の重要性を強く評価する。30人以上で、現場利用があるにもかかわらずAI管理者が弱い場合はC判定に寄せる。

## 6. 診断質問設計（すべて3〜4択ボタン）

### Q1. 社長自身のAI利用状況
質問：社長ご自身は、AIをどの程度使っていますか？
- ceo_none ほとんど使っていない（ceo_level=0）
- ceo_light ChatGPT、Gemini、Claudeなどをたまに使う（ceo_level=1）
- ceo_daily ChatGPT、Gemini、Claudeなどを日常的に使っている（ceo_level=2）
- ceo_agent Codex、Cowork、Claude CodeなどのAIエージェントも使っている（ceo_level=3）
分岐：ceo_none→Q4。それ以外→Q2。

### Q2. 社長がよく使うAIの種類（Q1でAI利用ありのとき表示）
質問：社長ご自身がよく使うAIは、どれに近いですか？
- ceo_tool_chat ChatGPT、Gemini、ClaudeなどのチャットAIが中心（ceo_tool_level=1）
- ceo_tool_agent Codex、Cowork、Claude CodeなどのAIエージェントが中心（ceo_tool_level=3）
- ceo_tool_api LLM/APIを使った業務システムや自動化（ceo_tool_level=4）
- ceo_tool_mix 複数を使い分けている（ceo_tool_level=3）
- ceo_tool_unknown 分からない（担当者に聞かないと不明）（ceo_tool_level=0）
分岐：ceo_tool_chat→Q3。ceo_tool_agent/ceo_tool_api/ceo_tool_mix→Q3B。
ceo_tool_unknown→Q4。

### Q3. AIエージェント利用状況（Q2でチャットAI中心のとき表示）
質問：AIエージェントは使っていますか？
補足：ここでいうAIエージェントとは、単に回答するだけでなく、調査・資料作成・コード作成・ファイル編集などの作業を任せられるAIを指します。
- agent_none まだ使っていない（agent_level=0）
- agent_trial 試したことはあるが、業務には入っていない（agent_level=1）
- agent_work Codex、Cowork、Claude Codeなどを業務で使っている（agent_level=3）
- agent_api LLM/APIをシステムや業務フローに組み込んでいる（agent_level=4）
分岐：agent_none/agent_trial→Q4。agent_work/agent_api→Q3B。

### Q3B. LLM/API利用状況
質問：LLM/APIを使った業務システム化は進んでいますか？
- api_none API利用はしていない（api_level=0）
- api_trial 試験的に使っている、または外部に相談している（api_level=1）
- api_partial 社内業務の一部にAPIを組み込んでいる（api_level=3）
- api_multi 複数業務でLLM/APIを使い、運用までしている（api_level=4）
分岐：回答後Q4へ。

### Q4. 現場・社員のAI利用状況（全員表示）
質問：現場や社員の方は、AIをどの程度使っていますか？
- field_none ほとんど使っていない、または把握していない（field_level=0）
- field_chat ChatGPT、Gemini、Claudeなどを一部社員が使っている（field_level=1）
- field_agent Codex、Cowork、Claude CodeなどのAIエージェントやサブスクを使っている（field_level=3）
- field_api 社内システムや業務フローにLLM/APIが組み込まれている（field_level=4）
分岐：回答後Q5へ。

### Q5. AI管理者・AI推進役・社内窓口（全員表示）
質問：AIを管理する役割は、社内外で決まっていますか？
- admin_none まだ決まっていない、または社長が都度判断している（admin_level=0）
- admin_internal_ops 総務・管理部門など社内で担当者がいる（admin_level=1）
- admin_internal_it IT担当・システム開発担当など社内で担当者がいる（admin_level=2）
- admin_external 外部委託先が担当している（相談している）（admin_level=1）
- admin_agent_manager AIエージェントマネージャーのような管理役を置いている（admin_level=3）
分岐：admin_external→Q5B。E候補に該当ならQ6・Q7を表示。該当しなければ結果判定へ。

### Q5B. 外部委託先への依存度（Q5で外部委託先を選んだとき表示）
質問：委託先とのAIに関する関係は、どれに近いですか？
- vendor_full_ai A1：あらゆるAIに関する内容を全面的に委託（admin_role_level=0 / knowledge_spread_level=0）
- vendor_ad_hoc_dev A2：AIを含めたシステム開発などで都度都度の委託（admin_role_level=1 / knowledge_spread_level=1）
- vendor_full_internalize A3：全面を委託しているが内製を進めたい（admin_role_level=1 / knowledge_spread_level=0）
- vendor_unknown A4：詳細は分からない（admin_role_level=0 / knowledge_spread_level=0）
分岐：A1/A3/A4は、結果上は社内AI人材の育成が次の焦点になる方向へ寄せ、専用の結果ページ「社内のAI人材の教育を進めていくことを検討していませんか？」を表示する。A2は外部活用をしながら社内窓口を整える方向へ寄せる。

## 7. D/E判定用の追加質問

DとEの間には明確な壁を設ける。Eは最高評価のため安易に出さない。

### 7.1 Q6/Q7を表示する条件（e_candidate）
admin_level >= 1 かつ 以下のいずれか：
ceo_level>=3／ceo_tool_level>=3／agent_level>=3／api_level>=1／field_level>=3／（従業員30人以上 かつ admin_level>=2）。

### Q6. AI管理者の役割の明確さ
質問：AI管理者・AI推進役の役割は、現在どの状態に近いですか？
- role_unclear AIに詳しい人や相談先はいるが、正式な役割はまだ決まっていない（admin_role_level=0）
- role_window 社内窓口は決まっており、社員からの相談やツール選定を受けている（admin_role_level=1）
- role_decision AIエージェント、LLM/API、外部委託、従量課金の扱いまで判断できる担当者がいる（admin_role_level=3）
- role_lead AI管理者が、現場導入・社員教育・外部専門家との連携まで主導している（admin_role_level=4）

### Q7. AI知見の広がり
質問：AI活用の知見は、社内外にどこまで広がっていますか？
- spread_personal 一部の詳しい人や社長に知見が偏っている（knowledge_spread_level=0）
- spread_department 特定部署ではAI活用が進んでいるが、全社的な教育はこれから（knowledge_spread_level=1）
- spread_company 従業員全体のAI理解を高める取り組みを始めている（knowledge_spread_level=3）
- spread_external 社労士・税理士・ITベンダーなど外部専門家のAI対応まで確認しながら進めている（knowledge_spread_level=4）

## 8. 結果分類（5本）

ユーザー画面では「〇〇タイプ」表記を使わず、問いかけ形式の見出しで表示する。

- A 様子見・保留フェーズ：AIについて、不確定なことが多くて様子見になっていませんか？
- B 社長先行・現場未展開フェーズ：社長ご自身はAIを使い始めている一方で、会社全体にはまだ広がっていませんか？
- C 現場利用あり・AI管理者不在フェーズ：社員がAIを使い始めているのに、誰が管理するかが曖昧になっていませんか？
- D AI窓口あり・現場実装準備フェーズ：AIの窓口が見えてきています。AIによる一部業務自動化の整備を進める段階ではありませんか？
- E 最高評価・先進フェーズ：最もAI導入が進んだ経営をされています。社外や市場が追いついていないことが、数少ないリスクではありませんか？

評価ニュアンス：A/B/Cは断定否定を避ける。DとEは必ず褒める。Eは「社外・市場が追いついていない」ことをリスクに置く。

## 9. 結果判定ロジック

点数合計型ではなくフロー型・優先判定型。最重要は「AI管理者の有無」。

優先順位：①E条件 ②現場利用あり×AI管理者弱い→C ③AI窓口・管理者候補あり×AI利用あり→D ④社長はAI利用×現場未展開→B ⑤それ以外→A。

擬似コード：
```
employee_size_level = convertEmployeeSize(employee_size)
  // employee_1_9=0, employee_10_29=1, employee_30_99=2, employee_100_200=3, employee_201_plus=4

ceo_active   = ceo_level >= 1
field_active = field_level >= 1

advanced_ai_usage = (ceo_level>=3 or ceo_tool_level>=3 or agent_level>=3 or api_level>=3 or field_level>=3)

admin_weak = (admin_level==0 or (employee_size_level>=2 and admin_level<=1))

result_E = (advanced_ai_usage and admin_level>=2 and admin_role_level>=3 and knowledge_spread_level>=3)

if result_E:                                                         result="E"
else if field_active and admin_weak:                                 result="C"
else if (admin_level>=1 or admin_role_level>=1) and (ceo_active or field_active): result="D"
else if ceo_active and not field_active:                             result="B"
else:                                                                result="A"
```

注：e_candidate の api しきい値は >=1（緩い）、advanced_ai_usage は >=3（厳しい）。両者は意図的に異なる。

## 10. 結果表示仕様

結果は1画面に全部出さず4ステップ（声→現在の状態→起きやすいこと→最初に決めるべきこと）。
商品誘導はしない：推奨プラン・月額金額・無料相談ボタン・面談予約ボタン・問い合わせフォーム・メール取得フォームを表示しない。営業マンがその場で会話を引き取る前提。

## 11. 結果本文サンプル（初期値・A〜E 各4枚）

実際の文章はスプレッドシートから差し替え可能にする。初期値の全文は `config.seed.json` の `result_steps`（21行）に格納済み。各結果の基本構成は「10=声／20=現在の状態／30=起きやすいこと／40=最初に決めるべきこと」。外部委託先A1/A3/A4の場合のみ、25=社内AI人材育成ページを追加表示する。

## 12〜16. スプレッドシート連携・API設計

Googleスプレッドシートで、診断回答の保存・質問文/選択肢の管理・結果文言の管理・診断バージョン管理を行う。反映方式は案A（GASをAPI化）：GET /config で質問・選択肢・結果文言を返し、POST /submit で回答を保存する。

推奨シート：app_config / questions / choices / results / result_steps / submissions。
運用確認用に、回答valueを日本語ラベルへ展開した `submission_answer_labels` シートを併用する。
submissions の列は timestamp, submission_id, diagnosis_version, company_name, industry, employee_size, q1..q7_value（外部委託先依存度の q5b_value を含む）, 各内部計算値, advanced_ai_usage, result_code, result_headline, result_phase, raw_payload_json（＋任意 device_type, user_agent）。

## 17. 実装時の注意点

避ける表現：御社は遅れています／リテラシーが低いです／危険です／専門家を入れないと失敗します。
使う表現：可能性があります／自然な状態です／次に整理する段階です／かなり前向きな状態です／最もAI導入が進んだ経営をされています。
DとEは必ず褒める。Eは安売りしない（エージェントまたはLLM/API利用あり＋AI管理者あり＋役割が高レベルで明確＋社員教育または外部専門家対応まで視野、が揃った場合のみ）。

## 18. 最終的な診断思想

本診断が見るべきものは「会社としてAIを現場に広げるための管理者・窓口・役割があるか」。最終判定で重視するのは、社長がAIを使っているか／現場でAIが使われているか／エージェント・LLM/APIまで利用しているか／AI管理者・窓口がいるか／役割が明確か／従業員全体や外部専門家までAI対応が広がっているか。

営業マンが結果画面を見せたうえで、次の会話につなげることを目指す：「社長、この診断結果を見る限り、AIを入れるかどうかより、まず御社では誰がAIを管理して、どの業務から現場に広げるかを決める段階だと思います。」

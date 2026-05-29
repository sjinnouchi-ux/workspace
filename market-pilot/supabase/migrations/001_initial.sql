-- ============================================================
-- market-pilot  Supabase Migration 001  : Stage A 記録基盤
-- 6 tables: tickers / strategy_rules / market_snapshots /
--           signals / run_logs / notifications
-- 設計: master_design_v2.md §5.1, §9（堅牢性・データ品質要件）準拠
-- ============================================================

-- 拡張（UUID 生成用）
create extension if not exists "pgcrypto";

-- ------------------------------------------------------------
-- 1. tickers : 銘柄マスタ（8シンボル）
-- ------------------------------------------------------------
create table if not exists tickers (
    id           bigint generated always as identity primary key,
    symbol       text        not null unique,           -- 例: QQQ, BTC-USD
    name         text        not null,                  -- 表示名
    asset_class  text        not null,                  -- 'etf' | 'crypto'
    sector       text,                                  -- 例: technology, energy
    is_active    boolean     not null default true,
    note         text,
    created_at   timestamptz not null default now()
);

comment on table tickers is '監視対象銘柄のマスタ';

-- ------------------------------------------------------------
-- 2. strategy_rules : 戦略定義・パラメータ
--    §9.4 初期は全戦略 status='RESEARCH'
-- ------------------------------------------------------------
create table if not exists strategy_rules (
    id            bigint generated always as identity primary key,
    code          text        not null unique,          -- 例: dual_momentum
    name          text        not null,                 -- 表示名
    description   text,
    params        jsonb       not null default '{}'::jsonb,  -- 戦略パラメータ
    status        text        not null default 'RESEARCH'
        check (status in ('RESEARCH','PAPER','MICRO_AUTO','MANUAL_APPROVAL','SUSPENDED','RETIRED')),
    automation_level smallint not null default 0
        check (automation_level between 0 and 4),
    notify_line   boolean     not null default true,    -- RESEARCH でも通知可（§9.4）
    is_active     boolean     not null default true,
    created_at    timestamptz not null default now(),
    updated_at    timestamptz not null default now()
);

comment on table strategy_rules is '戦略の定義・パラメータ・ステータス';

-- ------------------------------------------------------------
-- 3. market_snapshots : 日次の価格・指標スナップショット
-- ------------------------------------------------------------
create table if not exists market_snapshots (
    id            bigint generated always as identity primary key,
    ticker_id     bigint      not null references tickers(id) on delete cascade,
    as_of         date        not null,                 -- 対象日
    price         numeric,                              -- 終値（INVALID 時 null 可）
    prev_close    numeric,                              -- 前日終値
    change_pct    numeric,                              -- 前日比(%)
    rsi           numeric,                              -- RSI(14)
    ma5           numeric,
    ma20          numeric,
    ma50          numeric,
    bb_upper      numeric,                              -- ボリンジャー上限
    volatility    numeric,                              -- 実現ボラ
    is_valid      boolean     not null default true,    -- §9.2 異常値ガード結果
    raw           jsonb       not null default '{}'::jsonb, -- 取得生データ/補助値
    created_at    timestamptz not null default now(),
    unique (ticker_id, as_of)
);

comment on table market_snapshots is '日次の価格・テクニカル指標スナップショット';
create index if not exists idx_snapshots_asof on market_snapshots (as_of);

-- ------------------------------------------------------------
-- 4. signals : 生成シグナル（理由付き）
--    §9.1 理由を必ず保存 / §9.2 INVALID も1行として残す
-- ------------------------------------------------------------
create table if not exists signals (
    id            bigint generated always as identity primary key,
    ticker_id     bigint      not null references tickers(id) on delete cascade,
    strategy_id   bigint      references strategy_rules(id) on delete set null,
    snapshot_id   bigint      references market_snapshots(id) on delete set null,
    as_of         date        not null,
    signal_type   text        not null
        check (signal_type in ('BUY','SELL','HOLD','INVALID')),
    reason_text   text        not null,                 -- §9.1 人間可読の根拠
    reason_detail jsonb       not null default '{}'::jsonb, -- §9.1 条件名・閾値・実測値
    created_at    timestamptz not null default now()
);

comment on table signals is '生成シグナル。BUY/SELL/HOLD/INVALID を理由付きで保存（§9.1/§9.2）';
create index if not exists idx_signals_asof on signals (as_of);
create index if not exists idx_signals_type on signals (signal_type);

-- ------------------------------------------------------------
-- 5. run_logs : 実行ログ（§9.3 厚めに保存）
--    全体サマリ1行 + 銘柄/戦略別の明細を level で区別
-- ------------------------------------------------------------
create table if not exists run_logs (
    id            bigint generated always as identity primary key,
    run_id        uuid        not null default gen_random_uuid(), -- 1実行を束ねるID
    job_name      text        not null,                 -- 例: daily_report
    level         text        not null default 'summary'
        check (level in ('summary','ticker','strategy')),
    ticker_id     bigint      references tickers(id) on delete set null,
    strategy_id   bigint      references strategy_rules(id) on delete set null,
    status        text        not null
        check (status in ('success','partial','failed','skipped')),
    message       text,                                 -- 概要
    error_text    text,                                 -- §9.3 エラー本文
    detail        jsonb       not null default '{}'::jsonb,
    started_at    timestamptz,
    finished_at   timestamptz not null default now()
);

comment on table run_logs is '実行ログ。run_id で1実行を束ね、銘柄/戦略別の部分失敗を可視化（§9.3）';
create index if not exists idx_runlogs_runid on run_logs (run_id);
create index if not exists idx_runlogs_job on run_logs (job_name, finished_at);

-- ------------------------------------------------------------
-- 6. notifications : 通知履歴（LINE 送信記録）
-- ------------------------------------------------------------
create table if not exists notifications (
    id            bigint generated always as identity primary key,
    run_id        uuid,                                 -- 関連実行（任意）
    channel       text        not null default 'line'
        check (channel in ('line')),
    kind          text        not null default 'daily'
        check (kind in ('daily','monthly','alert')),
    body          text        not null,                 -- 送信本文
    status        text        not null default 'sent'
        check (status in ('sent','failed','skipped')),
    error_text    text,
    created_at    timestamptz not null default now()
);

comment on table notifications is 'LINE 通知の送信履歴';
create index if not exists idx_notifications_created on notifications (created_at);

-- ============================================================
-- 初期データ：8シンボル（§2 ユニバース）
-- ============================================================
insert into tickers (symbol, name, asset_class, sector) values
    ('QQQ',     'Invesco QQQ Trust',          'etf',    'technology'),
    ('XLE',     'Energy Select Sector SPDR',  'etf',    'energy'),
    ('XLV',     'Health Care Select Sector',  'etf',    'healthcare'),
    ('XLF',     'Financial Select Sector',    'etf',    'financials'),
    ('GLD',     'SPDR Gold Shares',           'etf',    'commodity_gold'),
    ('TLT',     'iShares 20+ Year Treasury',  'etf',    'bond_long'),
    ('BTC-USD', 'Bitcoin USD',                'crypto', 'crypto'),
    ('ETH-USD', 'Ethereum USD',               'crypto', 'crypto')
on conflict (symbol) do nothing;

-- ============================================================
-- 初期データ：戦略7種（§4 / §9.4 全て RESEARCH・通知可）
-- ============================================================
insert into strategy_rules (code, name, description, status, automation_level, notify_line) values
    ('dual_momentum',  'Dual Momentum',           '絶対+相対モメンタムで資産選択',      'RESEARCH', 0, true),
    ('tsmom',          'Time-Series Momentum',    '時系列モメンタム（トレンド追随）',    'RESEARCH', 0, true),
    ('ma_cross_adx',   'MA Cross + ADX Filter',   '移動平均クロスをADXでフィルター',     'RESEARCH', 0, true),
    ('vol_target',     'Volatility Targeting',    '目標ボラに合わせ建玉調整',           'RESEARCH', 0, true),
    ('inverse_vol',    'Inverse-Vol (Risk Parity)','ボラ逆数で資産配分',               'RESEARCH', 0, true),
    ('regime_detect',  'Regime Detection',        'リスクオン/オフ判定',               'RESEARCH', 0, true),
    ('corr_break',     'Correlation Break',       '通常相関からの乖離を検知',           'RESEARCH', 0, true)
on conflict (code) do nothing;

-- ============================================================
-- 完了
-- ============================================================

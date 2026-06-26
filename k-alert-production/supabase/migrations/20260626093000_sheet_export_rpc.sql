drop function if exists public.export_reports_for_sheet(date, date, text, text, integer);
drop function if exists public.export_report_companies_for_sheet(integer);

create or replace function public.export_reports_for_sheet(
  p_start_date date default null,
  p_end_date date default null,
  p_company_name text default '全社',
  p_status text default 'すべて',
  p_limit integer default 500
)
returns table (
  "受付日時" text,
  case_code text,
  "企業名" text,
  "名前" text,
  "いつ" text,
  "どこで" text,
  "誰が" text,
  "誰に" text,
  "内容要約" text,
  "相談希望" text,
  "状態" text,
  "LINE userId" text,
  report_id uuid,
  case_id uuid,
  "提出日時" timestamptz,
  "更新日時" timestamptz,
  "メモ" text,
  "内部フラグ" text
)
language sql
security definer
set search_path = public
as $$
  select
    to_char(coalesce(r.submitted_at, r.created_at) at time zone 'Asia/Tokyo', 'YYYY-MM-DD HH24:MI') as "受付日時",
    coalesce(c.case_code, '') as case_code,
    coalesce((r.body::jsonb) ->> 'company_name', '') as "企業名",
    coalesce(nullif((r.body::jsonb) ->> 'reporter_name', ''), '匿名') as "名前",
    coalesce((r.body::jsonb) ->> 'when_text', '') as "いつ",
    coalesce((r.body::jsonb) ->> 'where_text', '') as "どこで",
    coalesce((r.body::jsonb) ->> 'who_text', '') as "誰が",
    coalesce((r.body::jsonb) ->> 'to_whom_text', '') as "誰に",
    coalesce((r.body::jsonb) ->> 'what_how_text', '') as "内容要約",
    coalesce((r.body::jsonb) ->> 'consultation_request', '') as "相談希望",
    case c.status
      when 'open' then '未連絡'
      when 'collecting' then '未連絡'
      when 'waiting_investigator' then '要確認'
      when 'in_consultation' then '調査中'
      when 'completed' then '提出済'
      when 'closed' then '完了'
      else coalesce(c.status, '')
    end as "状態",
    coalesce(lu.line_user_id, '') as "LINE userId",
    r.id as report_id,
    r.case_id,
    r.submitted_at as "提出日時",
    r.updated_at as "更新日時",
    coalesce((r.body::jsonb) ->> 'free_text', '') as "メモ",
    case when ((r.body::jsonb) ->> 'demo') = 'true' then 'demo' else '' end as "内部フラグ"
  from public.reports r
  left join public.cases c on c.id = r.case_id
  left join public.line_users lu on lu.id = c.line_user_id
  where r.report_type = 'anonymous_report'
    and r.deleted_at is null
    and (p_start_date is null or coalesce(r.submitted_at, r.created_at)::date >= p_start_date)
    and (p_end_date is null or coalesce(r.submitted_at, r.created_at)::date <= p_end_date)
    and (p_company_name = '全社' or coalesce((r.body::jsonb) ->> 'company_name', '') = p_company_name)
    and (
      p_status = 'すべて'
      or case c.status
        when 'open' then '未連絡'
        when 'collecting' then '未連絡'
        when 'waiting_investigator' then '要確認'
        when 'in_consultation' then '調査中'
        when 'completed' then '提出済'
        when 'closed' then '完了'
        else coalesce(c.status, '')
      end = p_status
    )
  order by coalesce(r.submitted_at, r.created_at) desc
  limit least(greatest(coalesce(p_limit, 500), 1), 1000);
$$;

create or replace function public.export_report_companies_for_sheet(
  p_limit integer default 500
)
returns table ("企業名" text)
language sql
security definer
set search_path = public
as $$
  select candidates."企業名"
  from (
    select 0 as sort_order, '全社'::text as "企業名"
    union
    select
      1 as sort_order,
      coalesce((r.body::jsonb ->> 'company_name'), '') as "企業名"
    from public.reports r
    where r.report_type = 'anonymous_report'
      and r.deleted_at is null
      and coalesce((r.body::jsonb ->> 'company_name'), '') <> ''
  ) candidates
  group by candidates.sort_order, candidates."企業名"
  order by candidates.sort_order, candidates."企業名"
  limit least(greatest(coalesce(p_limit, 500), 1), 1000);
$$;

grant execute on function public.export_reports_for_sheet(date, date, text, text, integer) to anon;
grant execute on function public.export_report_companies_for_sheet(integer) to anon;

notify pgrst, 'reload schema';

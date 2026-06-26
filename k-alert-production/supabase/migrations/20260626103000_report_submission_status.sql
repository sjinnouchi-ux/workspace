alter table public.reports
  add column if not exists submission_status text not null default 'unsubmitted',
  add column if not exists submitted_to_company_at timestamptz;

alter table public.reports
  drop constraint if exists reports_submission_status_check;

alter table public.reports
  add constraint reports_submission_status_check
  check (submission_status in ('unsubmitted', 'submitted'));

update public.reports
set submission_status = 'unsubmitted'
where submission_status is null
   or submission_status not in ('unsubmitted', 'submitted');

drop function if exists public.export_reports_for_sheet(date, date, text, text, integer);

create or replace function public.export_reports_for_sheet(
  p_start_date date default null,
  p_end_date date default null,
  p_company_name text default '全社',
  p_status text default 'すべて',
  p_limit integer default 500
)
returns table (
  "提出状態" text,
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
    case coalesce(r.submission_status, 'unsubmitted')
      when 'submitted' then '提出済'
      else '未提出'
    end as "提出状態",
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
      or case coalesce(r.submission_status, 'unsubmitted')
        when 'submitted' then '提出済'
        else '未提出'
      end = p_status
    )
  order by coalesce(r.submitted_at, r.created_at) desc
  limit least(greatest(coalesce(p_limit, 500), 1), 1000);
$$;

drop function if exists public.update_report_submission_status(uuid, text, text);

create or replace function public.update_report_submission_status(
  p_report_id uuid,
  p_submission_status text,
  p_source text default 'google_sheet'
)
returns table (
  report_id uuid,
  "提出状態" text,
  updated_at timestamptz
)
language plpgsql
security definer
set search_path = public
as $$
declare
  next_status text;
begin
  next_status := case p_submission_status
    when '提出済' then 'submitted'
    when 'submitted' then 'submitted'
    when '未提出' then 'unsubmitted'
    when 'unsubmitted' then 'unsubmitted'
    else null
  end;

  if p_report_id is null or next_status is null then
    raise exception 'invalid report submission status update';
  end if;

  update public.reports
  set submission_status = next_status,
      submitted_to_company_at = case
        when next_status = 'submitted' then coalesce(submitted_to_company_at, now())
        else null
      end,
      updated_at = now()
  where id = p_report_id
    and report_type = 'anonymous_report'
    and deleted_at is null;

  if not found then
    raise exception 'report not found';
  end if;

  return query
  select
    r.id,
    case r.submission_status when 'submitted' then '提出済' else '未提出' end,
    r.updated_at
  from public.reports r
  where r.id = p_report_id;
end;
$$;

grant execute on function public.export_reports_for_sheet(date, date, text, text, integer) to anon;
grant execute on function public.update_report_submission_status(uuid, text, text) to anon;

notify pgrst, 'reload schema';

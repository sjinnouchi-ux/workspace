create table if not exists public.system_heartbeats (
  name text primary key,
  last_seen_at timestamptz not null default now(),
  source text not null default 'gas',
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.system_heartbeats enable row level security;

drop function if exists public.touch_system_heartbeat(text, text);

create or replace function public.touch_system_heartbeat(
  p_name text default 'k_alert_sheet_gas',
  p_source text default 'gas'
)
returns table (
  heartbeat_name text,
  last_seen_at timestamptz
)
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.system_heartbeats as heartbeats (
    name,
    last_seen_at,
    source,
    details,
    updated_at
  )
  values (
    coalesce(nullif(p_name, ''), 'k_alert_sheet_gas'),
    now(),
    coalesce(nullif(p_source, ''), 'gas'),
    jsonb_build_object('purpose', 'supabase_free_plan_keepalive'),
    now()
  )
  on conflict (name) do update
    set last_seen_at = excluded.last_seen_at,
        source = excluded.source,
        details = excluded.details,
        updated_at = excluded.updated_at;

  return query
  select heartbeats.name::text, heartbeats.last_seen_at
  from public.system_heartbeats heartbeats
  where heartbeats.name = coalesce(nullif(p_name, ''), 'k_alert_sheet_gas');
end;
$$;

grant execute on function public.touch_system_heartbeat(text, text) to anon;

notify pgrst, 'reload schema';

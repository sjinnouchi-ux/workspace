-- K Alert production initial schema.
-- Secrets must not be stored in this database schema or migration history.

create extension if not exists "pgcrypto";

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table public.line_users (
  id uuid primary key default gen_random_uuid(),
  line_user_id text not null unique,
  display_name text,
  picture_url text,
  is_active boolean not null default true,
  first_seen_at timestamptz,
  last_seen_at timestamptz,
  deleted_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.investigators (
  id uuid primary key default gen_random_uuid(),
  line_user_id uuid not null unique references public.line_users(id),
  name text not null,
  chatwork_room_id text,
  chatwork_account_id text,
  is_active boolean not null default true,
  notes text,
  deleted_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.cases (
  id uuid primary key default gen_random_uuid(),
  case_code text not null unique,
  line_user_id uuid not null references public.line_users(id),
  route_type text not null default 'undecided',
  status text not null default 'open',
  ai_summary text,
  category text,
  urgency text not null default 'unknown',
  completed_at timestamptz,
  deleted_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint cases_route_type_check check (
    route_type in ('undecided', 'anonymous_report', 'investigator_consultation')
  ),
  constraint cases_status_check check (
    status in ('open', 'collecting', 'waiting_investigator', 'in_consultation', 'completed', 'closed')
  ),
  constraint cases_urgency_check check (
    urgency in ('high', 'medium', 'low', 'unknown')
  )
);

create table public.webhook_events (
  id uuid primary key default gen_random_uuid(),
  webhook_event_id text not null unique,
  line_user_id uuid references public.line_users(id),
  event_type text,
  raw_payload jsonb not null,
  processed_at timestamptz,
  created_at timestamptz not null default now()
);

create table public.messages (
  id uuid primary key default gen_random_uuid(),
  case_id uuid references public.cases(id),
  webhook_event_id text references public.webhook_events(webhook_event_id),
  sender_type text not null,
  sender_line_user_id uuid references public.line_users(id),
  channel text not null,
  body text,
  message_type text,
  raw_payload jsonb,
  created_at timestamptz not null default now(),
  constraint messages_sender_type_check check (
    sender_type in ('user', 'ai', 'investigator', 'system')
  ),
  constraint messages_channel_check check (
    channel in ('line', 'system', 'chatwork', 'admin')
  )
);

create table public.ai_extractions (
  id uuid primary key default gen_random_uuid(),
  case_id uuid not null references public.cases(id),
  when_text text,
  where_text text,
  who_text text,
  to_whom_text text,
  what_text text,
  how_text text,
  urgency text,
  notes text,
  model text,
  prompt_version text,
  created_at timestamptz not null default now(),
  constraint ai_extractions_urgency_check check (
    urgency is null or urgency in ('high', 'medium', 'low', 'unknown')
  )
);

create table public.investigator_sessions (
  id uuid primary key default gen_random_uuid(),
  case_id uuid not null references public.cases(id),
  investigator_id uuid not null references public.investigators(id),
  status text not null default 'active',
  start_keyword text,
  end_keyword text,
  started_at timestamptz not null default now(),
  ended_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint investigator_sessions_status_check check (
    status in ('active', 'ended', 'cancelled')
  )
);

create table public.chatwork_notifications (
  id uuid primary key default gen_random_uuid(),
  case_id uuid not null references public.cases(id),
  investigator_id uuid references public.investigators(id),
  room_id text not null,
  message_body text not null,
  chatwork_message_id text,
  status text not null default 'pending',
  error_message text,
  sent_at timestamptz,
  created_at timestamptz not null default now(),
  constraint chatwork_notifications_status_check check (
    status in ('pending', 'sent', 'failed')
  )
);

create table public.ai_response_rules (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  trigger_type text not null,
  trigger_text text,
  instruction text not null,
  priority integer not null default 100,
  active boolean not null default false,
  approved_by text,
  approved_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.rule_reviews (
  id uuid primary key default gen_random_uuid(),
  reviewed_period_start timestamptz,
  reviewed_period_end timestamptz,
  summary text,
  proposed_rules jsonb,
  status text not null default 'draft',
  created_by text,
  created_at timestamptz not null default now(),
  constraint rule_reviews_status_check check (
    status in ('draft', 'approved', 'rejected', 'applied')
  )
);

create table public.reports (
  id uuid primary key default gen_random_uuid(),
  case_id uuid not null references public.cases(id),
  report_type text not null,
  status text not null default 'draft',
  body text,
  storage_url text,
  submitted_at timestamptz,
  deleted_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint reports_report_type_check check (
    report_type in ('anonymous_report', 'consultation_report')
  ),
  constraint reports_status_check check (
    status in ('draft', 'reviewed', 'submitted', 'archived')
  )
);

create table public.audit_logs (
  id uuid primary key default gen_random_uuid(),
  actor_type text not null,
  actor_id uuid,
  action text not null,
  target_table text,
  target_id uuid,
  metadata jsonb,
  created_at timestamptz not null default now()
);

create index line_users_line_user_id_idx on public.line_users(line_user_id);
create index cases_line_user_id_idx on public.cases(line_user_id);
create index cases_status_idx on public.cases(status);
create index cases_case_code_idx on public.cases(case_code);
create index messages_case_id_created_at_idx on public.messages(case_id, created_at);
create index messages_webhook_event_id_idx on public.messages(webhook_event_id);
create index webhook_events_webhook_event_id_idx on public.webhook_events(webhook_event_id);
create index investigator_sessions_case_id_idx on public.investigator_sessions(case_id);
create unique index investigator_sessions_one_active_per_investigator_idx
  on public.investigator_sessions(investigator_id)
  where status = 'active';
create index ai_response_rules_active_trigger_type_idx
  on public.ai_response_rules(active, trigger_type);
create index chatwork_notifications_case_id_idx on public.chatwork_notifications(case_id);

create trigger line_users_set_updated_at
before update on public.line_users
for each row execute function public.set_updated_at();

create trigger investigators_set_updated_at
before update on public.investigators
for each row execute function public.set_updated_at();

create trigger cases_set_updated_at
before update on public.cases
for each row execute function public.set_updated_at();

create trigger investigator_sessions_set_updated_at
before update on public.investigator_sessions
for each row execute function public.set_updated_at();

create trigger ai_response_rules_set_updated_at
before update on public.ai_response_rules
for each row execute function public.set_updated_at();

create trigger reports_set_updated_at
before update on public.reports
for each row execute function public.set_updated_at();

alter table public.line_users enable row level security;
alter table public.investigators enable row level security;
alter table public.cases enable row level security;
alter table public.webhook_events enable row level security;
alter table public.messages enable row level security;
alter table public.ai_extractions enable row level security;
alter table public.investigator_sessions enable row level security;
alter table public.chatwork_notifications enable row level security;
alter table public.ai_response_rules enable row level security;
alter table public.rule_reviews enable row level security;
alter table public.reports enable row level security;
alter table public.audit_logs enable row level security;


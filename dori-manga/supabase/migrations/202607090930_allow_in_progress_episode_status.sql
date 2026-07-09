alter table public.manga_episodes
  drop constraint if exists manga_episodes_status_check;

alter table public.manga_episodes
  add constraint manga_episodes_status_check
  check (
    status is null
    or status in (
      '完成',
      '制作中',
      '未完成',
      '不採用',
      'completed',
      'in_progress',
      'draft',
      'rejected'
    )
  );

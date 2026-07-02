-- ============================================================
-- 【参考保管用・適用禁止】
-- dori-manga: 画像評価インポートRPC v1
-- 現在Supabaseに適用されているのは v2（folder_status削除・
-- theme/scene_text対応・authenticated実行許可）。
-- v2の本文はSupabaseのmigration履歴
-- `import_generation_attempt_rpc_v2` を参照のこと。
-- ============================================================

create or replace function public.import_generation_attempt(payload jsonb)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_title          text := coalesce(nullif(trim(payload->>'episode_title'), ''), '(未設定)');
  v_panel_number   int;
  v_attempt_number int;
  v_status         text := upper(trim(payload->>'result_status'));
  v_episode_id     uuid;
  v_panel_id       uuid;
  v_attempt_id     uuid;
  v_existing_id    uuid;
  v_lesson         jsonb;
  v_lesson_text    text;
  v_lessons_count  int := 0;
begin
  begin
    v_panel_number   := (payload->>'panel_number')::int;
    v_attempt_number := (payload->>'attempt_number')::int;
  exception when others then
    raise exception 'panel_number / attempt_number は数値で指定してください: %',
      payload->>'panel_number';
  end;

  if v_status not in ('OK','NG','CLOSE','PENDING') then
    raise exception 'result_status が不正です: %', v_status;
  end if;
  if coalesce(trim(payload->>'final_generation_prompt'), '') = '' then
    raise exception 'final_generation_prompt が空です';
  end if;
  if coalesce(trim(payload->>'evaluation_summary'), '') = '' then
    raise exception 'evaluation_summary が空です';
  end if;
  if jsonb_typeof(payload->'evaluation_json') is distinct from 'object' then
    raise exception 'evaluation_json はオブジェクト形式で指定してください';
  end if;

  select id into v_episode_id
    from manga_episodes where title = v_title limit 1;
  if v_episode_id is null then
    insert into manga_episodes (title, status)
      values (v_title, 'draft')
      returning id into v_episode_id;
  end if;

  select id into v_panel_id
    from manga_panels
    where episode_id = v_episode_id and panel_number = v_panel_number
    limit 1;
  if v_panel_id is null then
    insert into manga_panels (episode_id, panel_number)
      values (v_episode_id, v_panel_number)
      returning id into v_panel_id;
  end if;

  select id into v_existing_id
    from generation_attempts
    where panel_id = v_panel_id and attempt_number = v_attempt_number
    limit 1;
  if v_existing_id is not null then
    return jsonb_build_object(
      'status', 'duplicate',
      'message', '同じコマ・試行回数のレコードが既に存在します（何も変更していません）',
      'attempt_id', v_existing_id,
      'episode_id', v_episode_id,
      'panel_id', v_panel_id
    );
  end if;

  insert into generation_attempts (
    panel_id, attempt_number, image_url, drive_file_id, file_name,
    folder_status, result_status,
    final_generation_prompt, evaluation_summary, evaluation_json
  ) values (
    v_panel_id, v_attempt_number,
    payload->>'image_url', payload->>'drive_file_id', payload->>'file_name',
    v_status, v_status,
    payload->>'final_generation_prompt',
    payload->>'evaluation_summary',
    payload->'evaluation_json'
  ) returning id into v_attempt_id;

  for v_lesson in
    select * from jsonb_array_elements(
      coalesce(nullif(payload->'prompt_lesson_candidates', 'null'::jsonb), '[]'::jsonb))
  loop
    v_lesson_text := case jsonb_typeof(v_lesson)
      when 'string' then v_lesson #>> '{}'
      when 'object' then coalesce(
        v_lesson->>'lesson_text', v_lesson->>'text',
        v_lesson->>'rule', v_lesson->>'content',
        v_lesson::text)
      else v_lesson::text
    end;
    if coalesce(trim(v_lesson_text), '') <> '' then
      insert into prompt_lessons (source_attempt_id, lesson_text, is_active)
        values (v_attempt_id, trim(v_lesson_text), true);
      v_lessons_count := v_lessons_count + 1;
    end if;
  end loop;

  return jsonb_build_object(
    'status', 'ok',
    'attempt_id', v_attempt_id,
    'episode_id', v_episode_id,
    'panel_id', v_panel_id,
    'lessons_inserted', v_lessons_count
  );
end;
$$;

revoke execute on function public.import_generation_attempt(jsonb) from public, anon, authenticated;
grant  execute on function public.import_generation_attempt(jsonb) to service_role;

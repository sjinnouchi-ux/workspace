import { AppError } from "./errors.ts";

export type SupabaseEnv = {
  url: string;
  anonKey: string;
  authHeader: string;
};

type AppSettingRow = {
  key: string;
  value?: string | null;
};

type EpisodeRow = {
  id: string;
  title: string;
  drive_folder_id?: string | null;
  drive_folder_url?: string | null;
};

export function getSupabaseEnv(req: Request): SupabaseEnv {
  const url = Deno.env.get("SUPABASE_URL");
  const anonKey = Deno.env.get("SUPABASE_ANON_KEY");
  const authHeader = req.headers.get("Authorization") ?? "";

  if (!url || !anonKey) {
    throw new AppError(
      "Supabaseの環境変数が設定されていません。",
      500,
      "supabase_env_missing",
    );
  }
  if (!authHeader.startsWith("Bearer ")) {
    throw new AppError(
      "ログイン情報を確認できません。再ログインしてください。",
      401,
      "authorization_required",
    );
  }
  return { url, anonKey, authHeader };
}

export async function supabaseRequest<T>(
  env: SupabaseEnv,
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const extraHeaders = headersToRecord(init.headers);
  const res = await fetch(`${env.url}/rest/v1/${path}`, {
    ...init,
    headers: {
      apikey: env.anonKey,
      Authorization: env.authHeader,
      "Content-Type": "application/json",
      ...extraHeaders,
    },
  });

  const text = await res.text();
  if (!res.ok) {
    throw new AppError(
      `Supabaseへのアクセスに失敗しました。権限またはデータ状態を確認してください。HTTP ${res.status}`,
      res.status === 401 || res.status === 403 ? 403 : 500,
      "supabase_request_failed",
    );
  }
  if (!text) return undefined as T;
  return JSON.parse(text) as T;
}

export async function getDriveRootFolderId(env: SupabaseEnv): Promise<string> {
  const keyRows = await supabaseRequest<AppSettingRow[]>(
    env,
    "app_settings?select=key,value&key=eq.drive_root_folder_id&limit=1",
  );
  const id = keyRows[0]?.value?.trim();
  if (id) return id;

  const urlRows = await supabaseRequest<AppSettingRow[]>(
    env,
    "app_settings?select=key,value&key=eq.drive_root_folder_url&limit=1",
  );
  const url = urlRows[0]?.value?.trim();
  const fromUrl = url ? extractDriveFolderId(url) : null;
  if (fromUrl) return fromUrl;

  throw new AppError(
    "Drive親フォルダが未設定です。管理タブで親フォルダIDまたはURLを保存してください。",
    400,
    "drive_root_missing",
  );
}

export async function getEpisode(
  env: SupabaseEnv,
  episodeId: string,
): Promise<EpisodeRow> {
  const rows = await supabaseRequest<EpisodeRow[]>(
    env,
    `manga_episodes?select=id,title,drive_folder_id,drive_folder_url&id=eq.${encodeURIComponent(episodeId)}&limit=1`,
  );
  const episode = rows[0];
  if (!episode) {
    throw new AppError(
      "対象の作品が見つかりません。画面を更新してから再度お試しください。",
      404,
      "episode_not_found",
    );
  }
  return episode;
}

export async function updateEpisodeDriveFolder(
  env: SupabaseEnv,
  episodeId: string,
  folderId: string,
  folderUrl: string,
): Promise<void> {
  await supabaseRequest(
    env,
    `manga_episodes?id=eq.${encodeURIComponent(episodeId)}`,
    {
      method: "PATCH",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify({
        drive_folder_id: folderId,
        drive_folder_url: folderUrl,
      }),
    },
  );
}

function extractDriveFolderId(url: string): string | null {
  const match = url.match(/\/folders\/([a-zA-Z0-9_-]+)/) ??
    url.match(/[?&]id=([a-zA-Z0-9_-]+)/);
  return match?.[1] ?? null;
}

function headersToRecord(headers: HeadersInit | undefined): Record<string, string> {
  if (!headers) return {};
  if (headers instanceof Headers) {
    return Object.fromEntries(headers.entries());
  }
  if (Array.isArray(headers)) {
    return Object.fromEntries(headers);
  }
  return Object.fromEntries(
    Object.entries(headers as Record<string, string>).map(([key, value]) => [
      key,
      String(value),
    ]),
  );
}

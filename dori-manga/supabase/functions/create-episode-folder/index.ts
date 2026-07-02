import { handleOptions, jsonResponse } from "../_shared/cors.ts";
import { errorBody, errorStatus, AppError } from "../_shared/errors.ts";
import {
  getDriveRootFolderId,
  getEpisode,
  getSupabaseEnv,
  updateEpisodeDriveFolder,
} from "../_shared/supabase.ts";
import {
  driveWebViewUrl,
  ensureChildFolder,
  getDriveAccessToken,
} from "../_shared/google_drive.ts";

const SUBFOLDERS = ["OK", "NG", "CLOSE", "完成"];

Deno.serve(async (req) => {
  const options = handleOptions(req);
  if (options) return options;

  try {
    if (req.method !== "POST") {
      throw new AppError("POSTで呼び出してください。", 405, "method_not_allowed");
    }

    const { episode_id, title } = await readPayload(req);
    const supabaseEnv = getSupabaseEnv(req);
    const [episode, rootFolderId, accessToken] = await Promise.all([
      getEpisode(supabaseEnv, episode_id),
      getDriveRootFolderId(supabaseEnv),
      getDriveAccessToken(),
    ]);

    const folderTitle = title || episode.title;
    const episodeFolder = await ensureChildFolder(
      accessToken,
      rootFolderId,
      folderTitle,
    );
    const subfolders = [];

    for (const name of SUBFOLDERS) {
      const result = await ensureChildFolder(
        accessToken,
        episodeFolder.folder.id,
        name,
      );
      subfolders.push({
        name,
        folder_id: result.folder.id,
        reused: result.reused,
      });
    }

    const folderUrl = episodeFolder.folder.webViewLink ??
      driveWebViewUrl(episodeFolder.folder.id);
    await updateEpisodeDriveFolder(
      supabaseEnv,
      episode_id,
      episodeFolder.folder.id,
      folderUrl,
    );

    return jsonResponse({
      status: "ok",
      folder_id: episodeFolder.folder.id,
      folder_url: folderUrl,
      reused: episodeFolder.reused,
      subfolders,
    });
  } catch (error) {
    return jsonResponse(errorBody(error), errorStatus(error));
  }
});

async function readPayload(req: Request): Promise<{
  episode_id: string;
  title: string;
}> {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    throw new AppError("JSONを読み取れませんでした。", 400, "invalid_json");
  }

  const payload = body as { episode_id?: unknown; title?: unknown };
  const episodeId = typeof payload.episode_id === "string"
    ? payload.episode_id.trim()
    : "";
  const title = typeof payload.title === "string" ? payload.title.trim() : "";

  if (!episodeId) {
    throw new AppError("作品IDが指定されていません。", 400, "episode_id_required");
  }
  if (!title) {
    throw new AppError("タイトルが指定されていません。", 400, "title_required");
  }
  return { episode_id: episodeId, title };
}

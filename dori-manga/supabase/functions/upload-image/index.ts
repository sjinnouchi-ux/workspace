import { handleOptions, jsonResponse } from "../_shared/cors.ts";
import { errorBody, errorStatus, AppError } from "../_shared/errors.ts";
import { getEpisode, getSupabaseEnv } from "../_shared/supabase.ts";
import {
  findChildFolder,
  getDriveAccessToken,
  uploadFile,
} from "../_shared/google_drive.ts";

const ALLOWED_STATUS = new Set(["OK", "NG", "CLOSE"]);
const MAX_IMAGE_BYTES = 10 * 1024 * 1024;

Deno.serve(async (req) => {
  const options = handleOptions(req);
  if (options) return options;

  try {
    if (req.method !== "POST") {
      throw new AppError("POSTで呼び出してください。", 405, "method_not_allowed");
    }

    const payload = await readPayload(req);
    const supabaseEnv = getSupabaseEnv(req);
    const [episode, accessToken] = await Promise.all([
      getEpisode(supabaseEnv, payload.episode_id),
      getDriveAccessToken(),
    ]);

    if (!episode.drive_folder_id) {
      throw new AppError(
        "作品フォルダが未作成です。先にフォルダ作成を実行してください。",
        400,
        "episode_folder_missing",
      );
    }

    const statusFolder = await findChildFolder(
      accessToken,
      episode.drive_folder_id,
      payload.result_status,
    );
    if (!statusFolder) {
      throw new AppError(
        `Drive内に判定フォルダ「${payload.result_status}」が見つかりません。作品フォルダ構成を確認してください。`,
        404,
        "status_folder_missing",
      );
    }

    const file = await uploadFile(
      accessToken,
      statusFolder.id,
      payload.file_name,
      payload.content_type,
      payload.bytes,
    );

    return jsonResponse({
      status: "ok",
      file_id: file.id,
      web_view_link: file.webViewLink ?? null,
    });
  } catch (error) {
    return jsonResponse(errorBody(error), errorStatus(error));
  }
});

async function readPayload(req: Request): Promise<{
  episode_id: string;
  result_status: "OK" | "NG" | "CLOSE";
  file_name: string;
  content_type: string;
  bytes: Uint8Array;
}> {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    throw new AppError("JSONを読み取れませんでした。", 400, "invalid_json");
  }

  const payload = body as {
    episode_id?: unknown;
    result_status?: unknown;
    file_name?: unknown;
    content_base64?: unknown;
    content_type?: unknown;
  };

  const episodeId = typeof payload.episode_id === "string"
    ? payload.episode_id.trim()
    : "";
  const resultStatus = typeof payload.result_status === "string"
    ? payload.result_status.trim().toUpperCase()
    : "";
  const fileName = typeof payload.file_name === "string"
    ? payload.file_name.trim()
    : "";
  const contentBase64 = typeof payload.content_base64 === "string"
    ? payload.content_base64.trim()
    : "";
  const contentType = typeof payload.content_type === "string" &&
      payload.content_type.trim()
    ? payload.content_type.trim()
    : guessContentType(fileName);

  if (!episodeId) {
    throw new AppError("作品IDが指定されていません。", 400, "episode_id_required");
  }
  if (!ALLOWED_STATUS.has(resultStatus)) {
    throw new AppError(
      "判定はOK/NG/CLOSEのいずれかを指定してください。",
      400,
      "invalid_result_status",
    );
  }
  if (!fileName) {
    throw new AppError("ファイル名が指定されていません。", 400, "file_name_required");
  }
  if (!contentBase64) {
    throw new AppError("画像データが指定されていません。", 400, "content_required");
  }

  const bytes = decodeBase64(contentBase64);
  if (bytes.byteLength > MAX_IMAGE_BYTES) {
    throw new AppError(
      "画像サイズが10MBを超えています。画像を圧縮してから再度お試しください。",
      413,
      "image_too_large",
    );
  }

  return {
    episode_id: episodeId,
    result_status: resultStatus as "OK" | "NG" | "CLOSE",
    file_name: fileName,
    content_type: contentType,
    bytes,
  };
}

function decodeBase64(value: string): Uint8Array {
  try {
    const normalized = value.includes(",") ? value.split(",").pop() ?? "" : value;
    const binary = atob(normalized);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i += 1) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  } catch {
    throw new AppError(
      "画像データのBase64形式が不正です。",
      400,
      "invalid_base64",
    );
  }
}

function guessContentType(fileName: string): string {
  const lower = fileName.toLowerCase();
  if (lower.endsWith(".png")) return "image/png";
  if (lower.endsWith(".jpg") || lower.endsWith(".jpeg")) return "image/jpeg";
  if (lower.endsWith(".webp")) return "image/webp";
  if (lower.endsWith(".gif")) return "image/gif";
  return "application/octet-stream";
}

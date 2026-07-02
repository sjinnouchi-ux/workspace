import { AppError } from "./errors.ts";

const DRIVE_API = "https://www.googleapis.com/drive/v3";
const DRIVE_UPLOAD_API = "https://www.googleapis.com/upload/drive/v3";
const TOKEN_URL = "https://oauth2.googleapis.com/token";
const FOLDER_MIME_TYPE = "application/vnd.google-apps.folder";

type DriveFile = {
  id: string;
  name?: string;
  mimeType?: string;
  webViewLink?: string;
};

type DriveListResponse = {
  files?: DriveFile[];
};

type OAuthTokenResponse = {
  access_token?: string;
  error?: string;
  error_description?: string;
};

export function driveWebViewUrl(fileId: string): string {
  return `https://drive.google.com/drive/folders/${fileId}`;
}

export async function getDriveAccessToken(): Promise<string> {
  const clientId = Deno.env.get("GOOGLE_OAUTH_CLIENT_ID");
  const clientSecret = Deno.env.get("GOOGLE_OAUTH_CLIENT_SECRET");
  const refreshToken = Deno.env.get("GOOGLE_OAUTH_REFRESH_TOKEN");

  if (!clientId || !clientSecret || !refreshToken) {
    throw new AppError(
      "Google OAuth認証情報が未設定です。Supabase secretsを確認してください。",
      500,
      "google_oauth_missing",
    );
  }

  const tokenRes = await fetch(TOKEN_URL, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refreshToken,
      grant_type: "refresh_token",
    }),
  });

  const tokenJson = await tokenRes.json() as OAuthTokenResponse;
  if (!tokenRes.ok) {
    if (tokenJson.error === "invalid_grant") {
      throw new AppError(
        "Google OAuthのrefresh tokenが失効しています。初回同意フローをやり直してSupabase secretsを更新してください。",
        502,
        "google_oauth_invalid_grant",
      );
    }
    throw new AppError(
      "Google Drive認証に失敗しました。OAuthクライアントID、シークレット、refresh tokenを確認してください。",
      502,
      "google_auth_failed",
    );
  }

  if (!tokenJson.access_token) {
    throw new AppError(
      "Google Drive認証トークンを取得できませんでした。",
      502,
      "google_token_missing",
    );
  }
  return tokenJson.access_token;
}

export async function findChildFolder(
  accessToken: string,
  parentId: string,
  name: string,
): Promise<DriveFile | null> {
  const query = [
    `'${escapeDriveQuery(parentId)}' in parents`,
    `name = '${escapeDriveQuery(name)}'`,
    `mimeType = '${FOLDER_MIME_TYPE}'`,
    "trashed = false",
  ].join(" and ");

  const url = `${DRIVE_API}/files?${new URLSearchParams({
    q: query,
    fields: "files(id,name,mimeType,webViewLink)",
    pageSize: "1",
    supportsAllDrives: "true",
    includeItemsFromAllDrives: "true",
  })}`;
  const data = await driveRequest<DriveListResponse>(accessToken, url);
  return data.files?.[0] ?? null;
}

export async function createFolder(
  accessToken: string,
  parentId: string,
  name: string,
): Promise<DriveFile> {
  return await driveRequest<DriveFile>(
    accessToken,
    `${DRIVE_API}/files?fields=id,name,mimeType,webViewLink&supportsAllDrives=true`,
    {
      method: "POST",
      body: JSON.stringify({
        name,
        mimeType: FOLDER_MIME_TYPE,
        parents: [parentId],
      }),
    },
  );
}

export async function ensureChildFolder(
  accessToken: string,
  parentId: string,
  name: string,
): Promise<{ folder: DriveFile; reused: boolean }> {
  const existing = await findChildFolder(accessToken, parentId, name);
  if (existing) return { folder: existing, reused: true };

  const created = await createFolder(accessToken, parentId, name);
  return { folder: created, reused: false };
}

export async function uploadFile(
  accessToken: string,
  parentId: string,
  fileName: string,
  contentType: string,
  bytes: Uint8Array,
): Promise<DriveFile> {
  const boundary = `dori_manga_${crypto.randomUUID()}`;
  const metadata = {
    name: fileName,
    parents: [parentId],
  };
  const body = buildMultipartBody(boundary, metadata, contentType, bytes);
  const multipartBody = body.buffer.slice(
    body.byteOffset,
    body.byteOffset + body.byteLength,
  ) as ArrayBuffer;

  return await driveRequest<DriveFile>(
    accessToken,
    `${DRIVE_UPLOAD_API}/files?uploadType=multipart&fields=id,name,webViewLink`,
    {
      method: "POST",
      headers: {
        "Content-Type": `multipart/related; boundary=${boundary}`,
      },
      body: multipartBody,
    },
  );
}

async function driveRequest<T>(
  accessToken: string,
  url: string,
  init: RequestInit = {},
): Promise<T> {
  const extraHeaders = headersToRecord(init.headers);
  const res = await fetch(url, {
    ...init,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
      ...extraHeaders,
    },
  });

  const text = await res.text();
  if (!res.ok) {
    throw classifyDriveError(res.status, text);
  }
  if (!text) return undefined as T;
  return JSON.parse(text) as T;
}

function classifyDriveError(status: number, text: string): AppError {
  const lower = text.toLowerCase();
  if (lower.includes("invalid_grant")) {
    return new AppError(
      "Google OAuthのrefresh tokenが失効しています。初回同意フローをやり直してSupabase secretsを更新してください。",
      502,
      "drive_oauth_invalid_grant",
    );
  }
  if (status === 401) {
    return new AppError(
      "Google Drive認証に失敗しました。OAuth認証情報を確認してください。",
      502,
      "drive_auth_failed",
    );
  }
  if (status === 403) {
    return new AppError(
      "Google Driveの権限が不足しています。認証したGoogleユーザーが親フォルダにアクセスできるか確認してください。",
      403,
      "drive_permission_denied",
    );
  }
  if (status === 404) {
    return new AppError(
      "Google Driveの対象フォルダが見つかりません。親フォルダIDまたは作品フォルダIDを確認してください。",
      404,
      "drive_folder_not_found",
    );
  }
  if (status === 400) {
    return new AppError(
      "Google Drive APIへのリクエスト形式が不正です。フォルダIDやファイル名を確認してください。",
      400,
      "drive_bad_request",
    );
  }
  return new AppError(
    `Google Drive APIでエラーが発生しました。HTTP ${status}`,
    502,
    "drive_api_error",
  );
}

function buildMultipartBody(
  boundary: string,
  metadata: Record<string, unknown>,
  contentType: string,
  bytes: Uint8Array,
): Uint8Array {
  const encoder = new TextEncoder();
  const start = encoder.encode(
    `--${boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n` +
      `${JSON.stringify(metadata)}\r\n` +
      `--${boundary}\r\nContent-Type: ${contentType}\r\n\r\n`,
  );
  const end = encoder.encode(`\r\n--${boundary}--`);
  const body = new Uint8Array(start.length + bytes.length + end.length);
  body.set(start, 0);
  body.set(bytes, start.length);
  body.set(end, start.length + bytes.length);
  return body;
}

function escapeDriveQuery(value: string): string {
  return value.replace(/\\/g, "\\\\").replace(/'/g, "\\'");
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

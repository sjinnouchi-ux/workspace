export class AppError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(message: string, status = 400, code = "bad_request") {
    super(message);
    this.name = "AppError";
    this.status = status;
    this.code = code;
  }
}

export function errorBody(error: unknown): {
  status: "error";
  code: string;
  message: string;
} {
  if (error instanceof AppError) {
    return { status: "error", code: error.code, message: error.message };
  }
  return {
    status: "error",
    code: "internal_error",
    message: "サーバー処理中に予期しないエラーが発生しました。",
  };
}

export function errorStatus(error: unknown): number {
  return error instanceof AppError ? error.status : 500;
}

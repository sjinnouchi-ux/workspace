export interface Env {
  FASTAPI_ORIGIN_URL?: string;
  FORWARD_PATH?: string;
  ACK_WHEN_ORIGIN_MISSING?: string;
  LIFF_ID?: string;
  LIFF_REPORT_API_KEY?: string;
}

const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
};
const REPORT_COMPLETION_NO_CONSULTATION_MESSAGE =
  "🛡️ Kアラートからのメッセージ 🛡️\n\n通報を受付ました。内容は匿名で企業に報告書を提出しますのでご安心ください。";
const REPORT_COMPLETION_WITH_CONSULTATION_MESSAGE =
  "🛡️ Kアラートからのメッセージ 🛡️\n\n通報を受付ました。内容は匿名で企業に報告書を提出しますのでご安心ください。\n\n調査官より、改めてチャットでご連絡しますのでご不安な点があればご相談ください。";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/health") {
      return json({ ok: true, service: "k-alert-production-webhook" });
    }

    if (request.method === "GET" && url.pathname === "/report") {
      return html(buildReportFormHtml(env.LIFF_ID || ""));
    }

    if (request.method === "POST" && url.pathname === "/api/report") {
      return submitReport(request, env);
    }

    if (request.method !== "POST") {
      return json({ ok: false, error: "method_not_allowed" }, 405);
    }

    const forwardPath = env.FORWARD_PATH || "/webhooks/line";
    if (url.pathname !== forwardPath) {
      return json({ ok: false, error: "not_found" }, 404);
    }

    return forwardToFastApi(request, env, forwardPath);
  },
};

async function submitReport(request: Request, env: Env): Promise<Response> {
  if (!env.FASTAPI_ORIGIN_URL) {
    return json({ ok: false, error: "origin_not_configured" }, 503);
  }
  if (!env.LIFF_REPORT_API_KEY) {
    return json({ ok: false, error: "liff_report_api_key_not_configured" }, 503);
  }

  const payload = await request.json().catch(() => null);
  if (!payload || typeof payload !== "object") {
    return json({ ok: false, error: "invalid_json" }, 400);
  }

  const origin = new URL(env.FASTAPI_ORIGIN_URL);
  const target = new URL("/liff/report", origin);
  const response = await fetch(target.toString(), {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-liff-report-api-key": env.LIFF_REPORT_API_KEY,
    },
    body: JSON.stringify(payload),
    redirect: "manual",
  });
  const text = await response.text();
  return new Response(text, {
    status: response.status,
    headers: JSON_HEADERS,
  });
}

async function forwardToFastApi(
  request: Request,
  env: Env,
  forwardPath: string,
): Promise<Response> {
  if (!env.FASTAPI_ORIGIN_URL) {
    if (env.ACK_WHEN_ORIGIN_MISSING === "true") {
      return json({ ok: true, mode: "ack_without_origin" });
    }
    return json({ ok: false, error: "origin_not_configured" }, 503);
  }

  const origin = new URL(env.FASTAPI_ORIGIN_URL);
  const target = new URL(forwardPath, origin);

  return fetch(target.toString(), {
    method: request.method,
    headers: request.headers,
    body: request.body,
    redirect: "manual",
  });
}

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: JSON_HEADERS,
  });
}

function html(body: string): Response {
  return new Response(body, {
    status: 200,
    headers: { "content-type": "text/html; charset=utf-8" },
  });
}

function buildReportFormHtml(liffId: string): string {
  const liffInitScript = liffId
    ? `liff.init({ liffId: "${escapeJs(liffId)}" }).catch(() => setStatus("LIFFの初期化に失敗しました。LINEから開き直してください。", true));`
    : `setStatus("フォームを表示しています。", false);`;

  return `<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Kアラート通報</title>
<script charset="utf-8" src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>
<style>
:root { color-scheme: light; --navy:#142d52; --green:#3fcf62; --bg:#f3f5f8; --text:#152033; --muted:#6b7280; --line:#dfe4ea; --danger:#b42318; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
.header { background:var(--navy); color:#ffd84a; font-weight:800; padding:14px 18px; text-align:center; }
main { padding:18px 16px calc(96px + env(safe-area-inset-bottom)); }
.panel { background:#fff; border:1px solid rgba(15,23,42,.06); border-radius:8px; box-shadow:0 8px 24px rgba(15,23,42,.08); margin-bottom:14px; padding:16px; }
.intro, .notice { color:#374151; font-size:14px; font-weight:700; line-height:1.7; }
label { color:var(--muted); display:block; font-size:13px; font-weight:800; margin-bottom:8px; }
.optional { color:#8a94a3; font-size:12px; font-weight:700; }
input:not([type="radio"]), textarea { appearance:none; background:#fff; border:1px solid var(--line); border-radius:8px; color:var(--text); font:inherit; outline:none; padding:13px 14px; width:100%; }
textarea { min-height:84px; resize:vertical; }
input:focus, textarea:focus { border-color:var(--green); box-shadow:0 0 0 3px rgba(63,207,98,.16); }
.choices { display:grid; gap:10px; grid-template-columns:1fr 1fr; }
.choice { align-items:center; border:1px solid var(--line); border-radius:8px; color:#374151; cursor:pointer; display:flex; font-weight:800; justify-content:center; min-height:52px; padding:10px; }
.choice input { accent-color:var(--green); flex:0 0 auto; height:18px; margin:0 8px 0 0; width:18px; }
.choice:has(input:checked) { border-color:var(--green); box-shadow:0 0 0 3px rgba(63,207,98,.16); color:#067647; }
.status { color:var(--muted); font-size:13px; min-height:18px; padding:2px 2px 0; }
.status.error { color:var(--danger); }
.status.success { color:#067647; }
.footer { background:rgba(255,255,255,.94); border-top:1px solid rgba(15,23,42,.08); bottom:0; left:0; padding:12px 16px calc(12px + env(safe-area-inset-bottom)); position:fixed; right:0; }
button { background:var(--green); border:0; border-radius:8px; color:#fff; font:inherit; font-weight:900; min-height:56px; width:100%; }
button:disabled { background:#a7d9b2; }
</style>
</head>
<body>
<div class="header">Kアラート通報</div>
<main>
  <form id="reportForm">
    <section class="panel intro">
      通報の内容については、所属している勤務先に対して報告書を提出します。<br>
      匿名希望の場合は名前入力は不要です。
    </section>
    <section class="panel"><label for="companyName">企業名</label><input id="companyName" name="companyName" autocomplete="organization" required></section>
    <section class="panel"><label for="reporterName">名前 <span class="optional">任意</span></label><input id="reporterName" name="reporterName" autocomplete="name"></section>
    <section class="panel"><label for="whenText">いつの事ですか？</label><div class="optional">例：2026年6月23日</div><textarea id="whenText" name="whenText" required></textarea></section>
    <section class="panel"><label for="whereText">どこで起きましたか？</label><div class="optional">例：職場の事務所で</div><textarea id="whereText" name="whereText" required></textarea></section>
    <section class="panel"><label for="whoText">だれが起こした人ですか？</label><div class="optional">例：職場の先輩の田中さん</div><textarea id="whoText" name="whoText" required></textarea></section>
    <section class="panel"><label for="toWhomText">だれに対してのことですか？</label><div class="optional">例：後輩の山田君に</div><textarea id="toWhomText" name="toWhomText" required></textarea></section>
    <section class="panel"><label for="whatHowText">なにをどのようにしていましたか</label><div class="optional">例：お金を貸してくれと強く迫っていました</div><textarea id="whatHowText" name="whatHowText" required></textarea></section>
    <section class="panel"><label for="freeText">その他 <span class="optional">任意</span></label><textarea id="freeText" name="freeText"></textarea></section>
    <section class="panel">
      <label>相談受付希望</label>
      <div class="choices">
        <label class="choice"><input type="radio" name="consultationRequest" value="希望する" required>希望する</label>
        <label class="choice"><input type="radio" name="consultationRequest" value="希望しない" required>希望しない</label>
      </div>
    </section>
    <section class="panel notice">証拠保全のため、写真・スクリーンショット・録音などがあれば削除せず保管しておいてください。</section>
    <div id="status" class="status" role="status" aria-live="polite"></div>
  </form>
</main>
<div class="footer"><button id="submitButton" form="reportForm" type="submit">送信する</button></div>
<script>
const statusEl = document.getElementById("status");
const submitButton = document.getElementById("submitButton");
const params = new URLSearchParams(location.search);
const caseCode = params.get("case_code") || "";
${liffInitScript}
document.getElementById("reportForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!caseCode) {
    setStatus("相談ケース情報が見つかりません。LINEから開き直してください。", true);
    return;
  }
  setStatus("送信中です。", false);
  submitButton.disabled = true;
  const form = new FormData(event.currentTarget);
  const payload = {
    case_code: caseCode,
    company_name: value(form, "companyName"),
    reporter_name: value(form, "reporterName"),
    when_text: value(form, "whenText"),
    where_text: value(form, "whereText"),
    who_text: value(form, "whoText"),
    to_whom_text: value(form, "toWhomText"),
    what_how_text: value(form, "whatHowText"),
    free_text: value(form, "freeText"),
    consultation_request: value(form, "consultationRequest")
  };
  try {
    const response = await fetch("/api/report", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok || data.ok !== true) throw new Error(data.detail || data.error || "送信に失敗しました。");
    await sendLineCompletionMessage(payload.consultation_request === "希望する");
    setStatus("送信しました。ご報告ありがとうございます。", false, true);
    submitButton.disabled = true;
    setTimeout(() => {
      if (window.liff && liff.isInClient()) liff.closeWindow();
    }, 1400);
  } catch (error) {
    setStatus(error.message || "送信に失敗しました。", true);
    submitButton.disabled = false;
  }
});
async function sendLineCompletionMessage(wantsConsultation) {
  if (!window.liff || !liff.isInClient()) return;
  const message = wantsConsultation
    ? ${JSON.stringify(REPORT_COMPLETION_WITH_CONSULTATION_MESSAGE)}
    : ${JSON.stringify(REPORT_COMPLETION_NO_CONSULTATION_MESSAGE)};
  try {
    await liff.sendMessages([{ type: "text", text: message }]);
  } catch (error) {
    console.warn("LIFF sendMessages failed", error);
  }
}
function value(form, name) { return String(form.get(name) || "").trim(); }
function setStatus(message, error, success) {
  statusEl.textContent = message;
  statusEl.className = "status" + (error ? " error" : "") + (success ? " success" : "");
}
</script>
</body>
</html>`;
}

function escapeJs(value: string): string {
  return value.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
}

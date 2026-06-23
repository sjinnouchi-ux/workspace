const K_ALERT_GAS_URL = "https://script.google.com/macros/s/AKfycbxm5GWC-3zcEyCNSiO7wLg5Ee4qd4c6SHKPBDLhffijuMDk4H0mRVdEwxDEThYstE2lHA/exec";
const LIFF_ID = "2010343610-N2psO7GW";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (request.method === "GET") {
      if (url.pathname === "/report") {
        return htmlResponse(buildReportFormHtml());
      }

      return jsonResponse({
        ok: true,
        service: "k-alert-worker",
        message: "K alert worker is running."
      });
    }

    if (request.method === "POST" && url.pathname === "/api/report") {
      return handleReportApi(request);
    }

    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405 });
    }

    const bodyText = await request.text();

    ctx.waitUntil(
      fetch(K_ALERT_GAS_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: bodyText,
        redirect: "follow"
      }).catch((err) => console.log("K alert GAS forward failed:", err))
    );

    return new Response("OK", { status: 200 });
  }
};

async function handleReportApi(request) {
  const payload = await request.json().catch(() => null);
  if (!payload || payload.source !== "liff_report") {
    return jsonResponse({ ok: false, error: "Invalid report payload." }, 400);
  }

  const gasResponse = await fetch(K_ALERT_GAS_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    redirect: "follow"
  });
  const text = await gasResponse.text();
  const data = safeJsonParse(text) || { ok: false, error: "Invalid GAS response." };

  if (!gasResponse.ok || data.ok !== true) {
    return jsonResponse({
      ok: false,
      error: data.error || "Report submission failed."
    }, 502);
  }

  return jsonResponse({
    ok: true,
    no: data.no
  });
}

function buildReportFormHtml() {
  return `<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Kアラート通報</title>
<script charset="utf-8" src="https://static.line-scdn.net/liff/edge/2/sdk.js"></` + `script>
<style>
:root {
  color-scheme: light;
  --navy: #142d52;
  --green: #3fcf62;
  --bg: #f3f5f8;
  --text: #152033;
  --muted: #6b7280;
  --line: #dfe4ea;
  --danger: #b42318;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.header {
  background: var(--navy);
  color: #ffd84a;
  font-weight: 700;
  padding: 14px 18px;
  text-align: center;
}
main {
  padding: 18px 16px calc(96px + env(safe-area-inset-bottom));
}
.panel {
  background: #fff;
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
  margin-bottom: 14px;
  padding: 16px;
}
.intro {
  color: #374151;
  font-size: 14px;
  line-height: 1.75;
}
.notice {
  background: #fff7ed;
  border: 1px solid #fed7aa;
  color: #9a3412;
  font-size: 13px;
  line-height: 1.7;
}
label {
  color: var(--muted);
  display: block;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 8px;
}
.optional {
  color: #8a94a3;
  font-size: 12px;
  font-weight: 600;
}
input:not([type="radio"]), textarea {
  appearance: none;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 8px;
  color: var(--text);
  font: inherit;
  outline: none;
  padding: 13px 14px;
  width: 100%;
}
textarea {
  min-height: 94px;
  resize: vertical;
}
input:focus, textarea:focus {
  border-color: var(--green);
  box-shadow: 0 0 0 3px rgba(63, 207, 98, 0.16);
}
.choices {
  display: grid;
  gap: 10px;
  grid-template-columns: 1fr 1fr;
}
.choice {
  align-items: center;
  border: 1px solid var(--line);
  border-radius: 8px;
  color: #374151;
  cursor: pointer;
  display: flex;
  font-weight: 700;
  justify-content: center;
  min-height: 52px;
  padding: 10px;
}
.choice input {
  accent-color: var(--green);
  flex: 0 0 auto;
  height: 18px;
  margin: 0 8px 0 0;
  width: 18px;
}
.choice:has(input:checked) {
  border-color: var(--green);
  box-shadow: 0 0 0 3px rgba(63, 207, 98, 0.16);
  color: #067647;
}
.status {
  color: var(--muted);
  font-size: 13px;
  min-height: 18px;
  padding: 2px 2px 0;
}
.status.error { color: var(--danger); }
.status.success { color: #067647; }
.footer {
  background: rgba(255, 255, 255, 0.94);
  border-top: 1px solid rgba(15, 23, 42, 0.08);
  bottom: 0;
  left: 0;
  padding: 12px 16px calc(12px + env(safe-area-inset-bottom));
  position: fixed;
  right: 0;
}
button {
  background: var(--green);
  border: 0;
  border-radius: 8px;
  color: #fff;
  font: inherit;
  font-weight: 800;
  min-height: 56px;
  width: 100%;
}
button:disabled {
  background: #a7d9b2;
}
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
    <section class="panel">
      <label for="companyName">企業名</label>
      <input id="companyName" name="companyName" autocomplete="organization" required>
    </section>
    <section class="panel">
      <label for="reporterName">名前 <span class="optional">任意</span></label>
      <input id="reporterName" name="reporterName" autocomplete="name">
    </section>
    <section class="panel">
      <label for="when">いつの事ですか？</label>
      <div class="optional">例：2026年6月23日</div>
      <textarea id="when" name="when" required></textarea>
    </section>
    <section class="panel">
      <label for="where">どこで起きましたか？</label>
      <div class="optional">例：職場の事務所で</div>
      <textarea id="where" name="where" required></textarea>
    </section>
    <section class="panel">
      <label for="who">だれが起こした人ですか？</label>
      <div class="optional">例：職場の先輩の田中さん</div>
      <textarea id="who" name="who" required></textarea>
    </section>
    <section class="panel">
      <label for="toWhom">だれに対してのことですか？</label>
      <div class="optional">例：後輩の山田君に</div>
      <textarea id="toWhom" name="toWhom" required></textarea>
    </section>
    <section class="panel">
      <label for="whatHow">なにをどのようにしていましたか</label>
      <div class="optional">例：お金を貸してくれと強く迫っていました</div>
      <textarea id="whatHow" name="whatHow" required></textarea>
    </section>
    <section class="panel">
      <label for="freeText">その他（自由記載） <span class="optional">任意</span></label>
      <textarea id="freeText" name="freeText"></textarea>
    </section>
    <section class="panel">
      <label>相談受付希望</label>
      <div class="choices">
        <label class="choice"><input type="radio" name="consultationRequest" value="希望する" required>希望する</label>
        <label class="choice"><input type="radio" name="consultationRequest" value="希望しない" required>希望しない</label>
      </div>
    </section>
    <section class="panel notice">
      証拠保全のため、写真・スクリーンショット・録音などがあれば削除せず保管しておいてください。
    </section>
    <div id="status" class="status" role="status" aria-live="polite"></div>
  </form>
</main>
<div class="footer">
  <button id="submitButton" form="reportForm" type="submit">送信する</button>
</div>
<script>
const statusEl = document.getElementById('status');
const submitButton = document.getElementById('submitButton');

liff.init({ liffId: '${LIFF_ID}' }).catch(() => {
  setStatus('LIFFの初期化に失敗しました。LINEから開き直してください。', true);
});

document.getElementById('reportForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  setStatus('送信中です。', false);
  submitButton.disabled = true;

  const form = event.currentTarget;
  const data = new FormData(form);
  const payload = {
    source: 'liff_report',
    report: {
      companyName: getValue(data, 'companyName'),
      reporterName: getValue(data, 'reporterName'),
      when: getValue(data, 'when'),
      where: getValue(data, 'where'),
      who: getValue(data, 'who'),
      toWhom: getValue(data, 'toWhom'),
      whatHow: getValue(data, 'whatHow'),
      freeText: getValue(data, 'freeText'),
      consultationRequest: getValue(data, 'consultationRequest')
    }
  };

  try {
    const response = await fetch('/api/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!response.ok || !result.ok) throw new Error(result.error || '送信に失敗しました。');

    form.reset();
    setStatus('送信しました。ご報告ありがとうございます。', false, true);
    setTimeout(() => {
      if (window.liff && liff.isInClient()) liff.closeWindow();
    }, 1400);
  } catch (err) {
    setStatus('送信できませんでした。時間をおいて再度お試しください。', true);
    submitButton.disabled = false;
  }
});

function getValue(data, key) {
  const value = data.get(key);
  return value === null ? '' : String(value).trim();
}

function setStatus(message, isError, isSuccess) {
  statusEl.textContent = message;
  statusEl.className = 'status' + (isError ? ' error' : '') + (isSuccess ? ' success' : '');
}
</script>
</body>
</html>`;
}

function htmlResponse(html) {
  return new Response(html, {
    status: 200,
    headers: { "Content-Type": "text/html; charset=utf-8" }
  });
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8" }
  });
}

function safeJsonParse(text) {
  try {
    return JSON.parse(text);
  } catch (_err) {
    return null;
  }
}

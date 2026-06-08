const GAS_URL = "https://script.google.com/macros/s/AKfycbx2Dw3tpCTC8PZxRwIH68d00TflY98ekTAkxv2-KY7t7EByJdcN676gUOonCg58rg_4/exec";

export default {
  async fetch(request, env, ctx) {
    if (request.method === "GET") {
      return serveGasResponse(request);
    }

    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405 });
    }

    const bodyText = await request.text();

    ctx.waitUntil(
      fetch(GAS_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: bodyText,
        redirect: "follow"
      }).catch((err) => console.log("Household GAS forward failed:", err))
    );

    return new Response("OK", { status: 200 });
  }
};

async function serveGasResponse(request) {
  const requestUrl = new URL(request.url);
  const gasUrl = new URL(GAS_URL);
  gasUrl.search = requestUrl.search;

  const gasResponse = await fetch(gasUrl.toString(), { redirect: "follow" });
  const contentType = gasResponse.headers.get("Content-Type") || "";

  if (requestUrl.searchParams.get("action") === "getCategories" || contentType.includes("application/json")) {
    return new Response(gasResponse.body, {
      status: gasResponse.status,
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "no-store"
      }
    });
  }

  let html = await gasResponse.text();
  const workerUrl = `${requestUrl.origin}${requestUrl.pathname}`;
  html = html.replace(/const GAS_URL = '.*?';/, `const GAS_URL = '${workerUrl}';`);

  return new Response(html, {
    status: gasResponse.status,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store"
    }
  });
}

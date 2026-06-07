const K_ALERT_GAS_URL = "https://script.google.com/macros/s/AKfycbxm5GWC-3zcEyCNSiO7wLg5Ee4qd4c6SHKPBDLhffijuMDk4H0mRVdEwxDEThYstE2lHA/exec";

export default {
  async fetch(request, env, ctx) {
    if (request.method === "GET") {
      return jsonResponse({
        ok: true,
        service: "k-alert-worker",
        message: "K alert worker is running."
      });
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

function jsonResponse(data) {
  return new Response(JSON.stringify(data), {
    status: 200,
    headers: { "Content-Type": "application/json; charset=utf-8" }
  });
}

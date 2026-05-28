export default {
  async fetch(request, env, ctx) {
    if (request.method === 'GET') {
      return new Response('K alert router is running.', { status: 200 });
    }

    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405 });
    }

    const bodyText = await request.text();
    const payload = safeJsonParse(bodyText);

    if (shouldTryKAlert(payload)) {
      try {
        const kAlertResponse = await forwardJson(env.K_ALERT_GAS_URL, bodyText);
        const decision = await safeResponseJson(kAlertResponse);
        if (decision && decision.handled) {
          return new Response('OK', { status: 200 });
        }
      } catch (err) {
        console.log('K alert route failed. Falling back to legacy GAS.', err);
      }
    }

    if (!env.LEGACY_GAS_URL) {
      return new Response('OK', { status: 200 });
    }

    ctx.waitUntil(forwardJson(env.LEGACY_GAS_URL, bodyText));
    return new Response('OK', { status: 200 });
  }
};

function shouldTryKAlert(payload) {
  if (!payload || !Array.isArray(payload.events)) return false;
  return payload.events.some((event) => {
    if (!event.message || event.message.type !== 'text') return false;
    const text = event.message.text.trim();
    // Follow-up messages may not include the trigger word, so text events are
    // checked by K_ALERT_GAS first. It returns handled:false for unrelated text.
    return text.length > 0;
  });
}

async function forwardJson(url, bodyText) {
  if (!url) {
    return new Response(JSON.stringify({ handled: false, reason: 'missing_url' }), { status: 200 });
  }
  return fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: bodyText
  });
}

function safeJsonParse(text) {
  try {
    return JSON.parse(text);
  } catch (_err) {
    return null;
  }
}

async function safeResponseJson(response) {
  try {
    return await response.json();
  } catch (_err) {
    return null;
  }
}

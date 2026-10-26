// Fetch wrapper: JSON in/out, CSRF header on state-changing requests, auth guard.

let csrf = null;

async function ensureCsrf() {
  if (!csrf) {
    const r = await fetch("/api/auth/csrf", { credentials: "same-origin" });
    csrf = (await r.json()).csrf;
  }
  return csrf;
}

export class ApiError extends Error {
  constructor(message, status, body) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

export async function api(path, { method = "GET", body } = {}) {
  const headers = { Accept: "application/json" };
  if (method !== "GET") {
    headers["X-CSRF-Token"] = await ensureCsrf();
    headers["Content-Type"] = "application/json";
  }
  const res = await fetch(path, {
    method,
    headers,
    credentials: "same-origin",
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  let data = {};
  try { data = await res.json(); } catch { /* empty body */ }
  if (data && data.csrf) csrf = data.csrf;
  if (!res.ok) {
    if (res.status === 401 && !location.pathname.match(/^\/(login|register)?$/)) {
      location.href = `/login?next=${encodeURIComponent(location.pathname + location.search)}`;
    }
    throw new ApiError(data.error || `Request failed (${res.status})`, res.status, data);
  }
  return data;
}

let userPromise = null;
export function requireUser() {
  if (!userPromise) userPromise = api("/api/auth/me").then((d) => d.user);
  return userPromise;
}

export async function logout() {
  await api("/api/auth/logout", { method: "POST" });
  location.href = "/";
}

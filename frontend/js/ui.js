// Shared UI: app shell, escaping, formatting, toasts, dialogs.

import { requireUser, logout } from "./api.js";

export const STATE_LABEL = {
  FOCUSED: "Focused",
  LOOKING_AWAY: "Looking away",
  LOOKING_DOWN: "Looking down",
  EYES_CLOSED: "Eyes closed",
  ABSENT: "Not detected",
};
export const DISTRACTION_STATES = ["LOOKING_AWAY", "LOOKING_DOWN", "EYES_CLOSED", "ABSENT"];

export function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

export const $ = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

const ICONS = {
  dashboard: '<path d="M3 13h8V3H3zM13 21h8V11h-8zM3 21h8v-6H3zM13 3v6h8V3z"/>',
  session: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3.5"/>',
  plan: '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
  schedule: '<rect x="3" y="4.5" width="18" height="16.5" rx="2"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/>',
  history: '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5M12 7v5l3 2"/>',
  analytics: '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
  research: '<path d="M9 3h6M10 3v6L4.5 19a1.5 1.5 0 0 0 1.3 2h12.4a1.5 1.5 0 0 0 1.3-2L14 9V3"/><path d="M7 15h10"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
  menu: '<path d="M3 6h18M3 12h18M3 18h18"/>',
  logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
};

export function icon(name) {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ""}</svg>`;
}

const NAV = [
  ["dashboard", "Dashboard", "/dashboard"],
  ["session", "Focus Session", "/session"],
  ["plan", "My Plan", "/plan"],
  ["schedule", "Schedule", "/schedule"],
  ["history", "History", "/history"],
  ["analytics", "Analytics", "/analytics"],
];

// Must match APP_VERSION in backend/version.py.
export const APP_VERSION = "1.2.0";

/** Warn when the pages are newer than the running server (e.g. after `git pull`
 * without restarting `python run.py`), which otherwise causes "Not found" errors. */
async function checkServerVersion() {
  try {
    const h = await (await fetch("/api/health", { cache: "no-store" })).json();
    if (h.version === APP_VERSION) return;
    const bar = document.createElement("div");
    bar.className = "alert warn update-banner";
    bar.setAttribute("role", "alert");
    bar.innerHTML = `<strong>Update almost done.</strong> Restart NeuroFocus to finish installing the new version,
      then reload this page.`;
    document.querySelector(".main")?.prepend(bar);
  } catch { /* server unreachable: pages show their own errors */ }
}

export async function mountShell(active) {
  checkServerVersion();
  const user = await requireUser();
  const side = $("#sidebar");
  const link = ([key, label, href]) =>
    `<a href="${href}" class="${key === active ? "active" : ""}" ${key === active ? 'aria-current="page"' : ""}>${icon(key)}${label}</a>`;
  side.innerHTML = `
    <a class="brand" href="/dashboard"><span class="brand-mark">◎</span>NeuroFocus AI</a>
    <nav class="nav" aria-label="Main">
      ${NAV.map(link).join("")}
      <div class="nav-section">Project</div>
      ${link(["research", "Research & Method", "/research"])}
      ${link(["settings", "Settings", "/settings"])}
    </nav>
    <div class="sidebar-foot">
      <div class="small"><strong>${esc(user.display_name)}</strong></div>
      <div class="tiny">${esc(user.email)}</div>
      <button class="btn ghost small" id="logoutBtn">${icon("logout")}<span>Sign out</span></button>
    </div>`;
  $("#logoutBtn").addEventListener("click", logout);
  const menu = $("#menuBtn");
  if (menu) {
    menu.innerHTML = icon("menu");
    menu.addEventListener("click", () => side.classList.toggle("open"));
  }
  return user;
}

let toastHost;
export function toast(msg, kind = "") {
  if (!toastHost) {
    toastHost = document.createElement("div");
    toastHost.className = "toast-host";
    toastHost.setAttribute("role", "status");
    document.body.append(toastHost);
  }
  const t = document.createElement("div");
  t.className = `toast ${kind}`;
  t.textContent = msg;
  toastHost.append(t);
  setTimeout(() => t.remove(), 4200);
}

export function showError(el, err) {
  el.textContent = err?.message || String(err);
  el.classList.remove("hidden");
}

export function confirmDialog(message, okLabel = "Delete") {
  return new Promise((resolve) => {
    const d = document.createElement("dialog");
    d.innerHTML = `<div class="dialog-body"><p></p></div>
      <div class="dialog-foot"><button class="btn" value="no">Cancel</button><button class="btn danger" value="yes"></button></div>`;
    d.querySelector("p").textContent = message;
    d.querySelector('[value="yes"]').textContent = okLabel;
    d.addEventListener("click", (e) => {
      if (e.target.value) { d.close(); resolve(e.target.value === "yes"); d.remove(); }
    });
    d.addEventListener("cancel", () => { resolve(false); d.remove(); });
    document.body.append(d);
    d.showModal();
  });
}

// ---------- formatting ----------
export function fmtScore(x) { return x == null ? "–" : Math.round(x).toString(); }
export function fmtDuration(sec) {
  if (sec == null) return "–";
  sec = Math.round(sec);
  const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60;
  if (h) return `${h}h ${m}m`;
  if (m) return `${m}m ${s.toString().padStart(2, "0")}s`;
  return `${s}s`;
}
export function fmtClock(sec) {
  sec = Math.max(0, Math.floor(sec));
  const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60;
  return (h ? `${h}:` : "") + `${String(m).padStart(h ? 2 : 1, "0")}:${String(s).padStart(2, "0")}`;
}
export function fmtDateTime(iso) {
  const d = new Date(iso);
  return d.toLocaleString(undefined, { weekday: "short", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
}
export function fmtTime(localIso) {
  return new Date(localIso).toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
}
// Green for strong scores; low scores stay neutral instead of a "fail" red/orange,
// so feedback informs without shaming (see docs/research).
export function scoreClass(x) {
  if (x == null) return "";
  return x >= 75 ? "s-FOCUSED" : "";
}
// Local wall-clock ISO 'YYYY-MM-DDTHH:MM' (what the schedule API stores).
export function localIso(d = new Date()) {
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;
}
export function localDate(d = new Date()) { return localIso(d).slice(0, 10); }
export const tzOffsetMin = () => -new Date().getTimezoneOffset();

// Apply the saved theme preference (per-device convenience only).
try {
  const t = localStorage.getItem("nf-theme");
  if (t) document.documentElement.dataset.theme = t;
} catch { /* storage blocked */ }

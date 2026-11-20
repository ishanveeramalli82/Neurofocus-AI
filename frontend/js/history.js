import { api } from "./api.js";
import { $, esc, mountShell, fmtDuration, fmtScore, fmtDateTime, scoreClass, toast, confirmDialog } from "./ui.js";

// Old links (/history?id=N) now open the detailed session report.
const legacyId = new URLSearchParams(location.search).get("id");
if (legacyId) location.replace(`/report?id=${encodeURIComponent(legacyId)}`);

await mountShell("history");
const PAGE = 20;
let offset = 0;

async function loadList() {
  const { sessions, total } = await api(`/api/sessions?limit=${PAGE}&offset=${offset}`);
  $("#rows").innerHTML = sessions.length ? sessions.map((s) => `
    <tr class="clickable" data-id="${s.id}">
      <td><strong>${esc(s.title)}</strong>${s.status !== "ended" ? ' <span class="badge">unfinished</span>' : ""}</td>
      <td class="small">${esc(s.subject) || "–"}</td>
      <td class="small">${fmtDateTime(s.started_at)}</td>
      <td class="small">${fmtDuration(s.total_s)}</td>
      <td class="small">${s.calibrated ? "yes" : "no"}</td>
      <td class="small">${s.distraction_count}</td>
      <td><strong class="${scoreClass(s.focus_score)}">${fmtScore(s.focus_score)}</strong></td>
      <td class="row-actions">
        <a class="btn small" href="/report?id=${s.id}">Open</a>
        ${s.status !== "ended" ? `<button class="btn small" data-finish="${s.id}">Finish</button>` : ""}
        <button class="btn small danger" data-delete="${s.id}" data-title="${esc(s.title)}">Delete</button>
      </td>
    </tr>`).join("") : '<tr><td colspan="8" class="empty">No sessions recorded yet. <a href="/session">Start one</a></td></tr>';
  $("#pageLabel").textContent = total ? `${offset + 1}–${Math.min(offset + PAGE, total)} of ${total}` : "";
  $("#prevBtn").disabled = offset === 0;
  $("#nextBtn").disabled = offset + PAGE >= total;
}

$("#rows").addEventListener("click", async (e) => {
  const del = e.target.closest("[data-delete]");
  const fin = e.target.closest("[data-finish]");
  if (del) {
    if (!(await confirmDialog(`Delete "${del.dataset.title}" and all of its data? This cannot be undone.`))) return;
    try { await api(`/api/sessions/${del.dataset.delete}`, { method: "DELETE" }); toast("Session deleted"); loadList(); }
    catch (err) { toast(err.message, "error"); }
    return;
  }
  if (fin) {
    try { await api(`/api/sessions/${fin.dataset.finish}/end`, { method: "POST", body: {} }); toast("Session finished"); loadList(); }
    catch (err) { toast(err.message, "error"); }
    return;
  }
  if (e.target.closest("a, button")) return;
  const tr = e.target.closest("tr[data-id]");
  if (tr) location.href = `/report?id=${tr.dataset.id}`;
});
$("#prevBtn").addEventListener("click", () => { offset = Math.max(0, offset - PAGE); loadList(); });
$("#nextBtn").addEventListener("click", () => { offset += PAGE; loadList(); });

if (!legacyId) loadList();

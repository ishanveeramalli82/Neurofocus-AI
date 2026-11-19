import { api } from "./api.js";
import { $, esc, mountShell, fmtDuration, fmtScore, fmtDateTime, scoreClass } from "./ui.js";

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
    </tr>`).join("") : '<tr><td colspan="7" class="empty">No sessions recorded yet. <a href="/session">Start one</a></td></tr>';
  $("#pageLabel").textContent = total ? `${offset + 1}–${Math.min(offset + PAGE, total)} of ${total}` : "";
  $("#prevBtn").disabled = offset === 0;
  $("#nextBtn").disabled = offset + PAGE >= total;
}

$("#rows").addEventListener("click", (e) => {
  const tr = e.target.closest("tr[data-id]");
  if (tr) location.href = `/report?id=${tr.dataset.id}`;
});
$("#prevBtn").addEventListener("click", () => { offset = Math.max(0, offset - PAGE); loadList(); });
$("#nextBtn").addEventListener("click", () => { offset += PAGE; loadList(); });

if (!legacyId) loadList();

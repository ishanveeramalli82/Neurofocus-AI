import { api } from "./api.js";
import { lineChart, barChart, ring, timeline } from "./charts.js";
import { $, esc, mountShell, fmtClock, fmtDuration, fmtScore, fmtDateTime, scoreClass, STATE_LABEL, toast, confirmDialog } from "./ui.js";

await mountShell("history");
const id = new URLSearchParams(location.search).get("id");
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
    </tr>`).join("") : '<tr><td colspan="7" class="empty">No sessions recorded yet.</td></tr>';
  $("#pageLabel").textContent = total ? `${offset + 1}–${Math.min(offset + PAGE, total)} of ${total}` : "";
  $("#prevBtn").disabled = offset === 0;
  $("#nextBtn").disabled = offset + PAGE >= total;
}

$("#rows").addEventListener("click", (e) => {
  const tr = e.target.closest("tr[data-id]");
  if (tr) location.href = `/history?id=${tr.dataset.id}`;
});
$("#prevBtn").addEventListener("click", () => { offset = Math.max(0, offset - PAGE); loadList(); });
$("#nextBtn").addEventListener("click", () => { offset += PAGE; loadList(); });

async function loadDetail() {
  $("#listView").classList.add("hidden");
  $("#detailView").classList.remove("hidden");
  const d = await api(`/api/sessions/${id}`);
  const s = d.session;
  ring($("#detailRing"), s.focus_score, "Focus Score");
  $("#dTitle").textContent = s.title;
  $("#dStatus").textContent = s.status;
  $("#dLen").textContent = fmtDuration(s.total_s);
  $("#dFocused").textContent = fmtDuration(s.focused_s);
  $("#dDis").textContent = s.distraction_count;
  $("#dMeta").textContent = `${fmtDateTime(s.started_at)}${s.subject ? ` · ${s.subject}` : ""} · engine v${s.engine_version}`;
  const c = s.calibration;
  $("#dCal").textContent = !c ? "Not calibrated." : c.calibrated
    ? `Calibrated (${c.quality}): away beyond ±${c.yaw_threshold.toFixed(0)}°, down beyond ${c.pitch_down_threshold.toFixed(0)}°.`
    : "Ran with population-default thresholds (no personal calibration).";
  timeline($("#dTimeline"), d.samples);
  $("#dTimeLabel").textContent = `${d.samples.length} s`;
  $("#dLegend").innerHTML = Object.entries(STATE_LABEL).map(([k, v]) => `<span><i class="dot s-${k}"></i>${v}</span>`).join("");
  const step = Math.max(1, Math.floor(d.samples.length / 300));
  lineChart($("#dLive"), d.samples.filter((_, i) => i % step === 0).map((x) => ({
    label: fmtClock(x.second), value: x.live_score,
  })));
  const br = d.distraction_breakdown;
  barChart($("#dBreakdown"), ["LOOKING_AWAY", "LOOKING_DOWN", "EYES_CLOSED", "ABSENT"].map((k) => ({
    label: STATE_LABEL[k], value: (br[k]?.seconds || 0) / 60,
    title: `${STATE_LABEL[k]}: ${br[k]?.count || 0} times, ${fmtDuration(br[k]?.seconds || 0)}`,
  })), { unit: "m" });
  $("#dTitleInput").value = s.title;
  $("#dSubjectInput").value = s.subject;
  $("#dNotes").value = s.notes;
}

$("#saveNotes").addEventListener("click", async () => {
  try {
    await api(`/api/sessions/${id}`, { method: "PATCH", body: { title: $("#dTitleInput").value, subject: $("#dSubjectInput").value, notes: $("#dNotes").value } });
    toast("Saved");
    $("#dTitle").textContent = $("#dTitleInput").value;
  } catch (e) { toast(e.message, "error"); }
});
$("#deleteBtn").addEventListener("click", async () => {
  if (!(await confirmDialog("Delete this session and all of its data? This cannot be undone."))) return;
  await api(`/api/sessions/${id}`, { method: "DELETE" });
  location.href = "/history";
});

if (id) loadDetail().catch((e) => { toast(e.message, "error"); });
else loadList();

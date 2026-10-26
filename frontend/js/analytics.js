import { api } from "./api.js";
import { lineChart, barChart } from "./charts.js";
import { $, $$, esc, mountShell, fmtScore, scoreClass, STATE_LABEL, tzOffsetMin } from "./ui.js";

await mountShell("analytics");

async function load(days) {
  const a = await api(`/api/analytics/summary?days=${days}&tz_offset_min=${tzOffsetMin()}`);
  $("#note").textContent = a.note;
  $("#tScore").textContent = fmtScore(a.totals.focus_score);
  $("#tScore").className = `value ${scoreClass(a.totals.focus_score)}`;
  $("#tFocused").textContent = `${a.totals.focused_hours.toFixed(1)} h`;
  $("#tTotal").textContent = `of ${a.totals.total_hours.toFixed(1)} h tracked`;
  $("#tSessions").textContent = a.totals.sessions;
  $("#tRate").textContent = a.totals.total_hours ? (a.totals.distractions / a.totals.total_hours).toFixed(1) : "–";
  const label = (d) => new Date(d + "T12:00").toLocaleDateString(undefined, { month: "short", day: "numeric" });
  lineChart($("#dailyScore"), a.daily.map((d) => ({ label: label(d.date), value: d.score })));
  barChart($("#dailyMin"), a.daily.map((d) => ({ label: label(d.date), value: d.focused_s / 60 })), { unit: "", alt: true });
  const hours = Array.from({ length: 24 }, (_, h) => a.by_hour.find((x) => x.hour === h));
  const first = hours.findIndex(Boolean), last = 23 - [...hours].reverse().findIndex(Boolean);
  barChart($("#byHour"), first < 0 ? [] : hours.slice(first, last + 1).map((x, i) => ({
    label: `${first + i}:00`, value: x?.score || 0,
    title: x ? `${first + i}:00 · score ${Math.round(x.score)} · ${x.sessions} sessions` : "no sessions",
  })), { yMax: 100 });
  $("#bySubject").innerHTML = a.by_subject.length ? a.by_subject.map((s) => `
    <tr><td>${esc(s.subject)}</td><td>${s.sessions}</td><td>${s.hours.toFixed(1)}</td>
    <td><strong class="${scoreClass(s.score)}">${fmtScore(s.score)}</strong></td></tr>`).join("")
    : '<tr><td colspan="4" class="empty">No sessions in this range.</td></tr>';
  const br = a.distraction_breakdown;
  barChart($("#breakdown"), ["LOOKING_AWAY", "LOOKING_DOWN", "EYES_CLOSED", "ABSENT"].map((k) => ({
    label: STATE_LABEL[k], value: (br[k]?.seconds || 0) / 60, title: `${STATE_LABEL[k]}: ${br[k]?.count || 0} episodes`,
  })), { unit: "m" });
}

$("#rangeTabs").addEventListener("click", (e) => {
  const b = e.target.closest("button");
  if (!b) return;
  $$("#rangeTabs button").forEach((x) => x.classList.toggle("active", x === b));
  load(Number(b.dataset.days));
});
load(30);

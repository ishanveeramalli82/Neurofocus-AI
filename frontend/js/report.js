import { api } from "./api.js";
import { barChart, lineChart, ring, timeline } from "./charts.js";
import { $, esc, mountShell, fmtClock, fmtDuration, fmtScore, fmtDateTime,
  STATE_LABEL, DISTRACTION_STATES, toast, confirmDialog } from "./ui.js";

await mountShell("history");
const id = new URLSearchParams(location.search).get("id");
const fmt = (x, d = 0) => (x == null ? "–" : Number(x).toFixed(d));
const kv = (label, value, sub = "") =>
  `<div><div class="label">${esc(label)}</div><div class="value">${value}</div>${sub ? `<div class="sub">${sub}</div>` : ""}</div>`;

if (!id) location.replace("/history");

let r;
try {
  r = await api(`/api/sessions/${encodeURIComponent(id)}/report`);
} catch (e) {
  $("#loadError").textContent = e.message;
  $("#loadError").classList.remove("hidden");
  throw e;
}
$("#report").classList.remove("hidden");
$("#csvBtn").href = `/api/sessions/${r.session_id}/timeline.csv`;
$("#jsonBtn").href = `/api/sessions/${r.session_id}/report?download=1`;
$("#printBtn").addEventListener("click", () => window.print());

const ov = r.overview, fp = r.focus_pattern, ds = r.distractions, cmp = r.comparison, dq = r.data_quality;

// ---------------------------------------------------------------- 1. overview
document.title = `${ov.title} · Session report · NeuroFocus AI`;
$("#rTitle").textContent = ov.title;
$("#rMeta").textContent = [fmtDateTime(ov.started_at), ov.subject, `engine v${dq.engine_version}`].filter(Boolean).join(" · ");
$("#rStatus").textContent = ov.status;
ring($("#rRing"), ov.focus_score, "Focus Score");
$("#rRank").textContent = cmp.rank ? `#${cmp.rank} of your ${cmp.rank_of} sessions` : "Your first session";
$("#rOverview").innerHTML = [
  kv("Tracked time", fmtDuration(ov.tracked_s), "camera time, excluding pauses"),
  kv("Focused", fmtDuration(ov.focused_s), `${fmt(ov.focus_score)}% of tracked time`),
  kv("Distracted", fmtDuration(ov.distracted_s)),
  kv("Distractions", ov.distraction_count, ov.distractions_per_hour != null ? `${fmt(ov.distractions_per_hour, 1)} per hour` : ""),
  kv("Longest focus streak", fmtDuration(fp.longest_focus_s)),
  kv("First distraction", fp.time_to_first_distraction_s != null ? `at ${fmtClock(fp.time_to_first_distraction_s)}` : "none"),
  kv("Started", new Date(ov.started_at).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }),
    ov.ended_at ? `ended ${new Date(ov.ended_at).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}` : ""),
  kv("Total time on page", ov.wall_clock_s != null ? fmtDuration(ov.wall_clock_s) : "–", "includes calibration and pauses"),
].join("");

// ---------------------------------------------------------------- 2. insights
$("#rInsights").innerHTML = r.insights.map((t) => `<li>${esc(t)}</li>`).join("") || "<li>No observations.</li>";

// ---------------------------------------------------------------- 3. timeline
timeline($("#rTimeline"), r.samples);
$("#rTimeLabel").textContent = `${r.samples.length} seconds recorded, one state per second`;
$("#rLegend").innerHTML = Object.entries(STATE_LABEL).map(([k, v]) => `<span><i class="dot s-${k}"></i>${v}</span>`).join("");
if (r.samples.length) {
  const first = r.samples[0].second, span = r.samples[r.samples.length - 1].second - first + 1;
  $("#rAxis").innerHTML = [0, 0.25, 0.5, 0.75, 1].map((f) => `<span>${fmtClock(f * span)}</span>`).join("");
  const step = Math.max(1, Math.floor(r.samples.length / 300));
  lineChart($("#rLive"), r.samples.filter((_, i) => i % step === 0).map((s) => ({ label: fmtClock(s.second - first), value: s.live_score })));
} else {
  $("#rLive").innerHTML = '<div class="empty">No data recorded.</div>';
}

// ---------------------------------------------------------------- 4. pattern
$("#rSegLabel").textContent = `${fp.segment_length_s / 60}-minute blocks`;
barChart($("#rSegments"), fp.segments.map((s) => ({
  label: fmtClock(s.start_s), value: s.score,
  cls: s.score >= 75 ? "st-FOCUSED" : s.score >= 50 ? "mid" : "lo",
  title: `${fmtClock(s.start_s)}–${fmtClock(s.end_s)}: score ${fmt(s.score)}`,
})), { yMax: 100 });
$("#rHalves").textContent = fp.first_half_score != null
  ? `First half: ${fmt(fp.first_half_score)} · Second half: ${fmt(fp.second_half_score)}`
  : "Halves are compared for sessions of 2 minutes or more.";
$("#rPattern").innerHTML = [
  kv("Focus streaks", fp.focus_bouts, "unbroken focused stretches"),
  kv("Longest streak", fmtDuration(fp.longest_focus_s),
    fp.longest_focus_window ? `${fmtClock(fp.longest_focus_window.start_s)}–${fmtClock(fp.longest_focus_window.end_s)}` : ""),
  kv("Average streak", fmtDuration(fp.mean_focus_bout_s)),
  kv("Median streak", fmtDuration(fp.median_focus_bout_s)),
  kv("Time to first distraction", fp.time_to_first_distraction_s != null ? fmtClock(fp.time_to_first_distraction_s) : "none"),
  kv("Best block", fp.best_segment ? fmt(fp.best_segment.score) : "–", fp.best_segment ? `${fmtClock(fp.best_segment.start_s)}–${fmtClock(fp.best_segment.end_s)}` : ""),
  kv("Lowest block", fp.worst_segment ? fmt(fp.worst_segment.score) : "–", fp.worst_segment ? `${fmtClock(fp.worst_segment.start_s)}–${fmtClock(fp.worst_segment.end_s)}` : ""),
].join("");

// ---------------------------------------------------------------- 5. states & types
const states = Object.entries(r.state_time);
barChart($("#rStateChart"), states.map(([k, v]) => ({ label: v.label, value: v.pct || 0, cls: `st-${k}`,
  title: `${v.label}: ${fmtDuration(v.seconds)} (${fmt(v.pct, 1)}%)` })), { yMax: 100, unit: "%" });
$("#rStateTable").innerHTML = states.map(([k, v]) =>
  `<tr><td><span class="table-dot bg-${k}"></span>${esc(v.label)}</td><td>${fmtDuration(v.seconds)}</td><td>${fmt(v.pct, 1)}%</td></tr>`).join("");
$("#rTypeTable").innerHTML = DISTRACTION_STATES.map((k) => {
  const b = ds.by_type[k];
  return `<tr><td><span class="table-dot bg-${k}"></span>${esc(b.label)}</td><td>${b.count}</td><td>${fmtDuration(b.total_s)}</td>
    <td>${b.mean_s != null ? fmtDuration(b.mean_s) : "–"}</td><td>${b.longest_s != null ? fmtDuration(b.longest_s) : "–"}</td>
    <td>${b.pct_of_distracted_time != null ? fmt(b.pct_of_distracted_time) + "%" : "–"}</td></tr>`;
}).join("");
barChart($("#rLengths"), [
  { label: "under 10 s", value: ds.short_under_10s },
  { label: "10–60 s", value: ds.medium_10_60s, cls: "mid" },
  { label: "over 1 min", value: ds.long_over_60s, cls: "lo" },
], { height: 160 });

// ---------------------------------------------------------------- 6. episodes
$("#rEpCount").textContent = `${ds.episodes.length} total${ds.longest ? ` · longest ${fmtDuration(ds.longest.duration_s)} (${ds.longest.label})` : ""}`;
$("#rEpisodes").innerHTML = ds.episodes.length ? ds.episodes.map((e, i) => `
  <tr><td>${i + 1}</td><td><span class="table-dot bg-${e.state}"></span>${esc(e.label)}</td>
  <td>${fmtClock(e.start_s)}</td><td>${fmtClock(e.end_s)}</td><td>${fmtDuration(e.duration_s)}</td></tr>`).join("")
  : '<tr><td colspan="5" class="empty">No distractions were detected.</td></tr>';

// ---------------------------------------------------------------- 7. comparison & plan
const bar = (name, value, mine = false) => `<div class="row"><span class="name">${esc(name)}</span>
  <div class="meter"><div class="${mine ? "mine" : ""}" data-w="${value ?? 0}"></div></div><span class="num">${fmt(value)}</span></div>`;
$("#rCompare").innerHTML = cmp.other_sessions ? [
  bar("This session", ov.focus_score, true),
  bar(`Your average (${cmp.other_sessions})`, cmp.your_average_score),
  cmp.subject_sessions ? bar(`${ov.subject} average (${cmp.subject_sessions})`, cmp.subject_average_score) : "",
  cmp.previous_session_score != null ? bar("Your previous session", cmp.previous_session_score) : "",
].join("") : '<p class="small muted">This is your first finished session, so there is nothing to compare with yet.</p>';
$("#rCompare").querySelectorAll("[data-w]").forEach((d) => { d.style.width = `${Math.min(100, Number(d.dataset.w))}%`; });
$("#rCompareKv").innerHTML = cmp.other_sessions ? [
  kv("Difference from average", cmp.your_average_score != null && ov.focus_score != null
    ? `${ov.focus_score - cmp.your_average_score >= 0 ? "+" : ""}${fmt(ov.focus_score - cmp.your_average_score)}` : "–", "points"),
  kv("Your usual length", fmtDuration(cmp.your_average_length_s)),
  kv("Rank", cmp.rank ? `#${cmp.rank} of ${cmp.rank_of}` : "–", "by Focus Score"),
].join("") : "";
$("#rPlan").innerHTML = [
  kv("Planned", ov.planned_min ? `${ov.planned_min} min` : "not set"),
  kv("Tracked", fmtDuration(ov.tracked_s)),
  kv("Plan completed", ov.plan_completion_pct != null ? `${fmt(ov.plan_completion_pct)}%` : "–"),
].join("");
const ev = ov.schedule_event;
$("#rEvent").innerHTML = ev
  ? `Linked schedule block: <strong>${esc(ev.title)}</strong> (${fmtDateTime(ev.start_at)}, ${esc(ev.kind)})${ev.completed ? " · marked done" : ""}. <a href="/schedule">Open schedule</a>`
  : "Not linked to a schedule block. You can start sessions from a study block on the Schedule page.";

// ---------------------------------------------------------------- 8. data quality
$("#rQuality").innerHTML = [
  kv("Frames analysed", dq.frames_received.toLocaleString()),
  kv("Face detected", dq.face_detected_pct != null ? `${fmt(dq.face_detected_pct, 1)}%` : "–", "of frames"),
  kv("Average frame rate", dq.average_frame_rate != null ? `${fmt(dq.average_frame_rate, 1)}/s` : "–", "target 10/s"),
  kv("Seconds recorded", dq.seconds_recorded.toLocaleString()),
  kv("Calibration", dq.calibrated ? (dq.calibration?.quality || "yes") : "not calibrated"),
  kv("Engine version", dq.engine_version),
].join("");
const c = dq.calibration;
$("#rCal").innerHTML = c ? [
  kv("Neutral head yaw", `${fmt(c.yaw0, 1)}°`, "where you face to see the screen"),
  kv("Neutral head pitch", `${fmt(c.pitch0, 1)}°`),
  kv("Looking away beyond", `±${fmt(c.yaw_threshold)}°`),
  kv("Looking down beyond", `${fmt(c.pitch_down_threshold)}°`),
  kv("Open-eye EAR", fmt(c.ear0, 3)),
  kv("Eyes closed below EAR", fmt(c.ear_closed_threshold, 3)),
].join("") : '<p class="small muted">No calibration recorded.</p>';
$("#rCalWarn").innerHTML = c?.warnings?.length ? `<div class="alert warn small">${c.warnings.map(esc).join("<br>")}</div>` : "";
const flat = (o, pre = "") => Object.entries(o).flatMap(([k, v]) =>
  v && typeof v === "object" && !Array.isArray(v) ? flat(v, `${pre}${k}.`) : [[`${pre}${k}`, Array.isArray(v) ? v.join("–") : v]]);
$("#rParams").innerHTML = flat(dq.engine_params).map(([k, v]) => `<tr><td class="mono">${esc(k)}</td><td class="mono">${esc(v)}</td></tr>`).join("");
$("#rDisclaimer").textContent = r.disclaimer;

// ---------------------------------------------------------------- 9. notes
$("#nTitle").value = ov.title;
$("#nSubject").value = ov.subject;
$("#nNotes").value = ov.notes;
$("#saveNotes").addEventListener("click", async () => {
  try {
    await api(`/api/sessions/${r.session_id}`, { method: "PATCH",
      body: { title: $("#nTitle").value, subject: $("#nSubject").value, notes: $("#nNotes").value } });
    $("#rTitle").textContent = $("#nTitle").value;
    toast("Saved");
  } catch (e) { toast(e.message, "error"); }
});
$("#deleteBtn").addEventListener("click", async () => {
  if (!(await confirmDialog("Delete this session and all of its data? This cannot be undone."))) return;
  await api(`/api/sessions/${r.session_id}`, { method: "DELETE" });
  location.href = "/history";
});

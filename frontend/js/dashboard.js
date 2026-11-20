import { api } from "./api.js";
import { lineChart } from "./charts.js";
import { $, esc, mountShell, fmtDuration, fmtScore, fmtDateTime, fmtTime, scoreClass, localDate, tzOffsetMin } from "./ui.js";

const user = await mountShell("dashboard");
const hour = new Date().getHours();
$("#greeting").textContent = `${hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening"}, ${user.display_name.split(" ")[0]}`;
$("#dateLabel").textContent = new Date().toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" });

const [week, two, overview, recent] = await Promise.all([
  api(`/api/analytics/summary?days=7&tz_offset_min=${tzOffsetMin()}`),
  api(`/api/analytics/summary?days=14&tz_offset_min=${tzOffsetMin()}`),
  api(`/api/schedule/overview?date=${localDate()}`),
  api("/api/sessions?limit=6"),
]);

const t = week.today;
$("#todayMin").textContent = `${Math.round(t.focused_min)} min`;
$("#goalMeter").firstElementChild.style.width = `${Math.min(100, (100 * t.focused_min) / t.goal_min)}%`;
$("#goalLabel").textContent = `goal ${t.goal_min} min`;
$("#weekScore").textContent = fmtScore(week.totals.focus_score);
$("#weekScore").className = `value ${scoreClass(week.totals.focus_score)}`;
$("#streak").textContent = `${week.active_days_last7} of 7`;

// Next steps: survey, then unlocking the personal plan.
const plan = await api(`/api/plan/status?tz_offset_min=${tzOffsetMin()}`);
const steps = [];
if (!user.onboarding.done) {
  steps.push(`<div class="card next-card"><h3>Tell NeuroFocus how you study</h3>
    <p class="small muted">A 2-minute survey so your breaks, block lengths and study times fit you.</p>
    <a class="btn primary small" href="/onboarding">Take the survey</a></div>`);
}
if (!plan.unlocked) {
  steps.push(`<div class="card next-card"><h3>Your personal plan: ${plan.sessions_done} of ${plan.sessions_needed} sessions</h3>
    <div class="meter"><div data-w="${(100 * plan.sessions_done) / plan.sessions_needed}"></div></div>
    <p class="small muted">Record ${plan.sessions_needed - plan.sessions_done} more session${plan.sessions_needed - plan.sessions_done === 1 ? "" : "s"} (2+ minutes each) to unlock a study plan built around how you focus.</p>
    <a class="btn small" href="/session">Start a session</a></div>`);
} else if (!plan.latest_plan) {
  steps.push(`<div class="card next-card"><h3>Your personal plan is ready to build</h3>
    <p class="small muted">Pick the days and times you can study and what you'll learn.</p>
    <a class="btn primary small" href="/plan">Build my plan</a></div>`);
}
$("#nextSteps").innerHTML = steps.join("");
$("#nextSteps").querySelectorAll("[data-w]").forEach((d) => { d.style.width = `${d.dataset.w}%`; });
$("#weekPlan").textContent = `${Math.round(overview.week.completed_study_min / 60 * 10) / 10}h`;
$("#weekPlanSub").textContent = `done of ${Math.round(overview.week.planned_study_min / 60 * 10) / 10}h planned`;

lineChart($("#trend"), two.daily.map((d) => ({
  label: new Date(d.date + "T12:00").toLocaleDateString(undefined, { month: "short", day: "numeric" }),
  value: d.score,
})));

const tl = $("#todayList");
tl.innerHTML = overview.today.length ? overview.today.map((e) => `
  <li class="k-${e.kind}"><span class="dot kdot"></span>
    <div class="grow"><div class="small"><strong>${esc(e.title)}</strong></div>
    <div class="tiny">${fmtTime(e.start_at)}–${fmtTime(e.end_at)} · ${esc(e.kind)}${e.focus ? ` · score ${fmtScore(e.focus.score)}` : ""}</div></div>
    ${e.kind === "study" && !e.completed ? `<a class="btn small" href="/session?event=${e.id}">Start</a>` : e.completed ? '<span class="badge s-FOCUSED">done</span>' : ""}
  </li>`).join("") : '<li class="empty">Nothing scheduled today. <a href="/schedule">Plan a study block</a></li>';

$("#dueList").innerHTML = overview.due_soon.length ? overview.due_soon.map((task) => `
  <li><div class="grow"><div class="small"><strong>${esc(task.title)}</strong></div>
  <div class="tiny">due ${fmtDateTime(task.due_at)}${task.subject ? ` · ${esc(task.subject)}` : ""}</div></div>
  <span class="badge prio-${task.priority}">${task.priority}</span></li>`).join("") : '<li class="empty">No deadlines in the next 7 days.</li>';

$("#recent").innerHTML = recent.sessions.length ? recent.sessions.map((s) => `
  <tr class="clickable" data-id="${s.id}"><td><strong>${esc(s.title)}</strong><div class="tiny">${esc(s.subject)}</div></td>
  <td class="small">${fmtDateTime(s.started_at)}</td><td class="small">${fmtDuration(s.total_s)}</td>
  <td><strong class="${scoreClass(s.focus_score)}">${fmtScore(s.focus_score)}</strong></td></tr>`).join("")
  : '<tr><td colspan="4" class="empty">No sessions yet. <a href="/session">Start your first one</a></td></tr>';
$("#recent").addEventListener("click", (e) => {
  const tr = e.target.closest("tr[data-id]");
  if (tr) location.href = `/report?id=${tr.dataset.id}`;
});

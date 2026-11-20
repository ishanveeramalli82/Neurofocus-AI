// Personal study plan: the student enters study times and topics; the server
// planner (backend/planner.py) builds the plan and explains every decision.
import { api } from "./api.js";
import { $, $$, esc, mountShell, localDate, tzOffsetMin, toast } from "./ui.js";

await mountShell("plan");
const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const KIND = { learn: "Learn", review: "Self-test review" };
let lastInputs = null;

// ------------------------------------------------------------- status
const st = await api(`/api/plan/status?tz_offset_min=${tzOffsetMin()}`);
if (!st.unlocked) {
  $("#locked").classList.remove("hidden");
  $("#needN").textContent = st.sessions_needed;
  $("#haveN").textContent = st.sessions_done;
  $("#lockMeter").style.width = `${(100 * st.sessions_done) / st.sessions_needed}%`;
  $("#surveyHint").classList.toggle("hidden", st.survey_done);
} else {
  $("#builder").classList.remove("hidden");
}

// ------------------------------------------------------------- availability rows
function availRow(a = { day: 0, start: "16:00", end: "18:00" }) {
  const div = document.createElement("div");
  div.className = "plan-row";
  div.innerHTML = `
    <select aria-label="Day">${DAYS.map((d, i) => `<option value="${i}" ${i === a.day ? "selected" : ""}>${d}</option>`).join("")}</select>
    <input type="time" aria-label="From" value="${esc(a.start)}">
    <span class="tiny">to</span>
    <input type="time" aria-label="Until" value="${esc(a.end)}">
    <button class="btn ghost small" type="button" aria-label="Remove">✕</button>`;
  div.querySelector("button").addEventListener("click", () => div.remove());
  $("#availRows").append(div);
}
$("#addAvail").addEventListener("click", () => availRow());
$$("[data-preset]").forEach((b) => b.addEventListener("click", () => {
  if (b.dataset.preset === "weekdays") {
    $("#availRows").innerHTML = "";
    [0, 1, 2, 3, 4].forEach((d) => availRow({ day: d, start: "16:00", end: "18:00" }));
  } else {
    [5, 6].forEach((d) => availRow({ day: d, start: "10:00", end: "12:00" }));
  }
}));

// ------------------------------------------------------------- topic rows
function topicRow(t = { subject: "", topic: "", minutes: 120, deadline: "", priority: "medium" }) {
  const div = document.createElement("div");
  div.className = "plan-row topic";
  div.innerHTML = `
    <input placeholder="Subject (e.g. Biology)" aria-label="Subject" maxlength="60" value="${esc(t.subject)}">
    <input placeholder="What you'll learn (e.g. Cell respiration)" aria-label="What you'll learn" maxlength="120" value="${esc(t.topic)}">
    <label class="tiny">Minutes needed<input type="number" min="15" max="3000" step="15" value="${t.minutes}"></label>
    <label class="tiny">Test / due date<input type="date" value="${esc(t.deadline || "")}"></label>
    <label class="tiny">Priority<select>${["high", "medium", "low"].map((p) => `<option ${p === t.priority ? "selected" : ""}>${p}</option>`).join("")}</select></label>
    <button class="btn ghost small" type="button" aria-label="Remove">✕</button>`;
  div.querySelector("button").addEventListener("click", () => div.remove());
  $("#topicRows").append(div);
}
$("#addTopic").addEventListener("click", () => topicRow());

function readInputs() {
  return {
    start_date: $("#startDate").value,
    weeks: Number($("#weeks").value),
    availability: $$("#availRows .plan-row").map((r) => {
      const [day, from, to] = r.querySelectorAll("select, input");
      return { day: Number(day.value), start: from.value, end: to.value };
    }),
    topics: $$("#topicRows .plan-row").map((r) => {
      const [subject, topic, minutes, deadline, priority] = r.querySelectorAll("input, select");
      return { subject: subject.value, topic: topic.value, minutes: Number(minutes.value),
        deadline: deadline.value || null, priority: priority.value };
    }).filter((t) => t.topic.trim()),
    tz_offset_min: tzOffsetMin(),
  };
}

function fillInputs(inp) {
  $("#availRows").innerHTML = "";
  $("#topicRows").innerHTML = "";
  inp.availability.forEach(availRow);
  inp.topics.forEach(topicRow);
  $("#weeks").value = inp.weeks;
}

// ------------------------------------------------------------- render a plan
const fmtDay = (iso) => new Date(iso + "T12:00").toLocaleDateString(undefined, { weekday: "long", month: "short", day: "numeric" });
const fmtT = (hhmm) => new Date(`2000-01-01T${hhmm}`).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
const kv = (l, v, sub = "") => `<div><div class="label">${esc(l)}</div><div class="value">${v}</div>${sub ? `<div class="sub">${esc(sub)}</div>` : ""}</div>`;

function showPlan(plan, { saved = false, created = null } = {}) {
  $("#result").classList.remove("hidden");
  const s = plan.summary, p = plan.personalization;
  $("#resultTitle").textContent = saved ? "Your current plan" : "Plan preview";
  $("#confBadge").textContent = `personalization confidence: ${plan.confidence}`;
  $("#resultKv").innerHTML = [
    kv("Study block", `${plan.block_min} min`, `then a ${plan.short_break_min}-min break`),
    kv("Long break", `${plan.long_break_min} min`, `after every ${plan.long_break_every} blocks`),
    kv("Planned", `${Math.round(s.planned_min / 6) / 10} h`, `of ${Math.round(s.available_min / 6) / 10} h you're free`),
    kv("Kept free", `${s.free_pct ?? "–"}%`, "catch-up time"),
    kv("Blocks", plan.blocks.length),
    kv("Topics", s.topics.length),
  ].join("");
  $("#warnings").innerHTML = plan.warnings.map((w) => `<div class="alert warn small">${esc(w)}</div>`).join("");
  $("#whyList").innerHTML = plan.why.map((w) => `<li>${esc(w)}</li>`).join("");
  $("#personalKv").innerHTML = [
    kv("Sessions used", p.sessions_used),
    kv("Your typical focus streak", p.personal_median_min != null ? `${p.personal_median_min.toFixed(1)} min` : "not used yet", "median of each session's median"),
    kv("Weight on your data", p.weight ? p.weight.toFixed(2) : "0", "n / (n + 4)"),
    kv("Starting block length", `${p.prior_block_min} min`, p.prior_source),
    kv("Preferred time", p.preferred_band || "none"),
  ].join("");
  $("#bandRows").innerHTML = Object.entries(p.time_bands || {}).map(([b, v]) =>
    `<tr><td>${esc(b)}</td><td>${v.sessions}</td><td>${v.mean.toFixed(0)}</td><td>${v.adjusted.toFixed(0)}</td></tr>`).join("")
    || '<tr><td colspan="4" class="empty">No sessions yet.</td></tr>';
  const byDate = {};
  for (const b of plan.blocks) (byDate[b.date] ||= []).push(b);
  $("#blockCount").textContent = `${plan.blocks.length} blocks`;
  $("#days").innerHTML = Object.keys(byDate).sort().map((d) => `
    <h3 class="report-sub">${fmtDay(d)}</h3>
    <ul class="list">${byDate[d].map((b) => `
      <li class="plan-block k-${b.kind}">
        <div class="plan-time">${fmtT(b.start)}–${fmtT(b.end)}</div>
        <div class="grow"><strong>${esc(b.topic)}</strong> <span class="badge">${KIND[b.kind]}</span>
          ${b.subject ? `<span class="tiny">${esc(b.subject)}</span>` : ""}
          <details class="tiny"><summary>Why here?</summary>${esc(b.reason)}</details></div>
      </li>`).join("")}</ul>`).join("") || '<div class="empty">No blocks could be scheduled. Add more study times.</div>';
  $("#applyBtn").classList.toggle("hidden", saved);
  $("#applyHint").textContent = saved ? `Added to your schedule ${created ? new Date(created).toLocaleDateString() : ""}. Open the Schedule page to see it.` :
    "Replaces upcoming blocks from your previous plan (finished blocks are kept).";
  $("#result").scrollIntoView({ behavior: "smooth", block: "start" });
}

async function preview() {
  $("#buildError").classList.add("hidden");
  lastInputs = readInputs();
  try {
    const r = await api("/api/plan/preview", { method: "POST", body: lastInputs });
    showPlan(r.plan);
  } catch (e) {
    $("#buildError").textContent = e.message;
    $("#buildError").classList.remove("hidden");
  }
}
$("#previewBtn").addEventListener("click", preview);
$("#editBtn").addEventListener("click", () => { $("#builder").scrollIntoView({ behavior: "smooth" }); });
$("#applyBtn").addEventListener("click", async () => {
  $("#applyBtn").disabled = true;
  try {
    const r = await api("/api/plan", { method: "POST", body: lastInputs || readInputs() });
    toast(`Added ${r.plan.blocks.length} study blocks to your schedule.`);
    showPlan(r.plan, { saved: true, created: Date.now() });
  } catch (e) { toast(e.message, "error"); }
  $("#applyBtn").disabled = false;
});

// ------------------------------------------------------------- initial state
$("#startDate").value = localDate();
if (st.unlocked) {
  const latest = await api("/api/plan/latest");
  if (latest.plan) {
    fillInputs(latest.inputs);
    showPlan(latest.plan, { saved: true, created: latest.created_at });
    $("#result").scrollIntoView({ block: "start" });
  } else {
    [0, 1, 2, 3, 4].forEach((d) => availRow({ day: d, start: "16:00", end: "18:00" }));
    topicRow();
  }
}

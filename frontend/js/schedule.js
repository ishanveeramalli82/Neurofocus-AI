import { api } from "./api.js";
import { $, $$, esc, mountShell, fmtTime, fmtDateTime, fmtScore, scoreClass, localIso, localDate, toast, confirmDialog } from "./ui.js";

const user = await mountShell("schedule");
const H0 = 6, H1 = 24, ROW = 44; // visible hours and pixel height per hour
let weekStart = mondayOf(new Date());
let view = "week";
let events = [];
let editing = null;
let planningTask = null;

function mondayOf(d) {
  const x = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  x.setDate(x.getDate() - ((x.getDay() + 6) % 7));
  return x;
}
const addDays = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };

async function load() {
  const start = localDate(weekStart);
  const end = localDate(addDays(weekStart, view === "week" ? 7 : 14));
  const [{ events: evs }, overview] = await Promise.all([
    api(`/api/schedule/events?start=${start}&end=${end}`),
    api(`/api/schedule/overview?date=${start}`),
  ]);
  events = evs;
  const endLabel = addDays(weekStart, view === "week" ? 6 : 13);
  $("#weekLabel").textContent = `${weekStart.toLocaleDateString(undefined, { month: "short", day: "numeric" })} – ${endLabel.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}`;
  view === "week" ? renderWeek() : renderAgenda();
  const w = overview.week;
  $("#weekStudy").textContent = `${(w.completed_study_min / 60).toFixed(1)} h done`;
  $("#weekStudySub").textContent = `of ${(w.planned_study_min / 60).toFixed(1)} h of study blocks planned`;
  $("#weekMeter").firstElementChild.style.width = `${w.planned_study_min ? Math.min(100, (100 * w.completed_study_min) / w.planned_study_min) : 0}%`;
  const scored = events.filter((e) => e.focus);
  $("#weekFocus").textContent = scored.length
    ? `Average Focus Score in scheduled blocks: ${fmtScore(scored.reduce((a, e) => a + e.focus.score, 0) / scored.length)}` : "";
}

// ---------------------------------------------------------------- week grid
function renderWeek() {
  const wk = $("#week");
  const todayStr = localDate();
  const days = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));
  wk.innerHTML = `<div class="week-head"><div></div>${days.map((d) =>
    `<div class="${localDate(d) === todayStr ? "today" : ""}">${d.toLocaleDateString(undefined, { weekday: "short" })} ${d.getDate()}</div>`).join("")}</div>
    <div class="hours">${Array.from({ length: H1 - H0 }, (_, i) => `<div>${i ? `${(H0 + i) % 12 || 12}${H0 + i < 12 ? "a" : "p"}` : ""}</div>`).join("")}</div>
    ${days.map((d) => `<div class="day-col ${localDate(d) === todayStr ? "today" : ""}" data-date="${localDate(d)}">${"<div class='slot'></div>".repeat(H1 - H0)}</div>`).join("")}`;
  for (const col of $$(".day-col", wk)) {
    const date = col.dataset.date;
    const dayEvents = events.filter((e) => e.start_at.slice(0, 10) <= date && e.end_at.slice(0, 10) >= date)
      .map((e) => clipToDay(e, date)).filter(Boolean);
    layoutLanes(dayEvents);
    for (const e of dayEvents) {
      const el = document.createElement("div");
      el.className = `ev k-${e.ev.kind} ${e.ev.completed ? "done" : ""}`;
      el.style.top = `${(e.startMin / 60 - H0) * ROW}px`;
      el.style.height = `${Math.max(18, ((e.endMin - e.startMin) / 60) * ROW - 2)}px`;
      el.style.left = `calc(${(100 * e.lane) / e.lanes}% + 3px)`;
      el.style.width = `calc(${100 / e.lanes}% - 6px)`;
      el.style.right = "auto";
      el.innerHTML = `<div class="ev-title">${esc(e.ev.title)}</div><div>${fmtTime(e.ev.start_at)}${e.ev.focus ? ` · ${fmtScore(e.ev.focus.score)}` : ""}</div>`;
      el.title = `${e.ev.title} (${fmtTime(e.ev.start_at)}–${fmtTime(e.ev.end_at)})`;
      el.addEventListener("click", (ev) => { ev.stopPropagation(); openEvent(e.ev); });
      col.append(el);
    }
    if (date === todayStr) {
      const now = new Date();
      const mins = now.getHours() * 60 + now.getMinutes();
      if (mins >= H0 * 60) {
        const line = document.createElement("div");
        line.className = "now-line";
        line.style.top = `${(mins / 60 - H0) * ROW}px`;
        col.append(line);
      }
    }
    col.addEventListener("click", (ev) => {
      if (ev.target.closest(".ev")) return;
      const rect = col.getBoundingClientRect();
      const mins = Math.floor((((ev.clientY - rect.top) / ROW) * 60 + H0 * 60) / 30) * 30;
      openEvent(null, date, mins);
    });
  }
}

function clipToDay(ev, date) {
  const toMin = (iso) => Number(iso.slice(11, 13)) * 60 + Number(iso.slice(14, 16));
  const startMin = ev.start_at.slice(0, 10) < date ? 0 : toMin(ev.start_at);
  const endMin = ev.end_at.slice(0, 10) > date ? 24 * 60 : toMin(ev.end_at);
  const s = Math.max(startMin, H0 * 60), e = Math.min(endMin, H1 * 60);
  return e > s ? { ev, startMin: s, endMin: e } : null;
}

function layoutLanes(items) {
  items.sort((a, b) => a.startMin - b.startMin || b.endMin - a.endMin);
  let cluster = [], clusterEnd = -1;
  const close = () => { const n = Math.max(...cluster.map((c) => c.lane)) + 1; cluster.forEach((c) => (c.lanes = n)); cluster = []; };
  for (const it of items) {
    if (it.startMin >= clusterEnd && cluster.length) close();
    const used = new Set(cluster.filter((c) => c.endMin > it.startMin).map((c) => c.lane));
    let lane = 0;
    while (used.has(lane)) lane++;
    it.lane = lane;
    cluster.push(it);
    clusterEnd = Math.max(clusterEnd, it.endMin);
  }
  if (cluster.length) close();
}

function renderAgenda() {
  const byDay = {};
  for (const e of events) (byDay[e.start_at.slice(0, 10)] ||= []).push(e);
  const keys = Object.keys(byDay).sort();
  $("#agenda").innerHTML = keys.length ? keys.map((k) => `
    <h3>${new Date(k + "T12:00").toLocaleDateString(undefined, { weekday: "long", month: "short", day: "numeric" })}</h3>
    <ul class="list">${byDay[k].map((e) => `
      <li class="k-${e.kind}" data-id="${e.id}"><i class="dot kdot"></i>
        <div class="grow"><strong class="small">${esc(e.title)}</strong>${e.completed ? ' <span class="badge s-FOCUSED">done</span>' : ""}
          <div class="tiny">${fmtTime(e.start_at)}–${fmtTime(e.end_at)} · ${e.kind}${e.subject ? ` · ${esc(e.subject)}` : ""}${e.focus ? ` · Focus ${fmtScore(e.focus.score)}` : ""}</div></div>
        <button class="btn small" data-open="${e.id}">Open</button></li>`).join("")}</ul>`).join("")
    : '<div class="empty">Nothing scheduled in the next two weeks.</div>';
}
$("#agenda").addEventListener("click", (e) => {
  const b = e.target.closest("[data-open]");
  if (b) openEvent(events.find((x) => x.id === Number(b.dataset.open)));
});

// ---------------------------------------------------------------- event dialog
const pad = (n) => String(n).padStart(2, "0");
function openEvent(ev, date, mins) {
  editing = ev;
  $("#evError").classList.add("hidden");
  $("#evDialogTitle").textContent = ev ? "Edit event" : "New event";
  $("#evTitle").value = ev?.title ?? "";
  $("#evKind").value = ev?.kind ?? "study";
  $("#evSubject").value = ev?.subject ?? "";
  $("#evNotes").value = ev?.notes ?? "";
  if (ev) {
    $("#evDate").value = ev.start_at.slice(0, 10);
    $("#evStart").value = ev.start_at.slice(11, 16);
    $("#evEnd").value = ev.end_at.slice(11, 16);
  } else {
    const m = mins ?? Math.ceil((new Date().getHours() * 60 + new Date().getMinutes()) / 30) * 30;
    const end = Math.min(m + user.settings.default_session_min, 23 * 60 + 59);
    $("#evDate").value = date ?? localDate();
    $("#evStart").value = `${pad(Math.floor(m / 60) % 24)}:${pad(m % 60)}`;
    $("#evEnd").value = `${pad(Math.floor(end / 60))}:${pad(end % 60)}`;
  }
  $("#repeatField").classList.toggle("hidden", !!ev);
  $("#evRepeat").value = "0";
  $("#evDoneWrap").classList.toggle("hidden", !ev);
  $("#evDone").checked = !!ev?.completed;
  $("#evDelete").classList.toggle("hidden", !ev);
  const startable = ev && ev.kind === "study" && !ev.completed;
  $("#evStartSession").classList.toggle("hidden", !startable);
  if (startable) $("#evStartSession").href = `/session?event=${ev.id}`;
  $("#evFocus").textContent = ev?.focus ? `Focus Score in this block: ${fmtScore(ev.focus.score)} over ${Math.round(ev.focus.seconds / 60)} min (${ev.focus.sessions} session${ev.focus.sessions > 1 ? "s" : ""}).` : "";
  $("#eventDialog").showModal();
  $("#evTitle").focus();
}

$("#evCancel").addEventListener("click", () => $("#eventDialog").close());
$("#eventForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const date = $("#evDate").value;
  let endDate = date;
  if ($("#evEnd").value <= $("#evStart").value) endDate = localDate(addDays(new Date(date + "T12:00"), 1)); // crosses midnight
  const body = {
    title: $("#evTitle").value, kind: $("#evKind").value, subject: $("#evSubject").value, notes: $("#evNotes").value,
    start_at: `${date}T${$("#evStart").value}`, end_at: `${endDate}T${$("#evEnd").value}`,
  };
  try {
    let r;
    if (editing) r = await api(`/api/schedule/events/${editing.id}`, { method: "PUT", body: { ...body, completed: $("#evDone").checked } });
    else r = await api("/api/schedule/events", { method: "POST", body: { ...body, repeat_weekly: Number($("#evRepeat").value) } });
    $("#eventDialog").close();
    if (r.conflicts?.length) toast(`Saved, but it overlaps: ${[...new Set(r.conflicts.map((c) => c.title))].join(", ")}`);
    else toast("Saved");
    load();
  } catch (err) {
    $("#evError").textContent = err.message;
    $("#evError").classList.remove("hidden");
  }
});

$("#evDelete").addEventListener("click", async () => {
  const ev = editing;
  let scope = "one";
  if (ev.recurrence_group) {
    const series = await confirmDialog("Delete this and all following events in the series? Choose Cancel to delete only this one.", "Delete series");
    scope = series ? "series" : "one";
  } else if (!(await confirmDialog(`Delete "${ev.title}"?`))) return;
  await api(`/api/schedule/events/${ev.id}?scope=${scope}`, { method: "DELETE" });
  $("#eventDialog").close();
  load();
});

// ---------------------------------------------------------------- tasks
async function loadTasks() {
  const { tasks } = await api("/api/schedule/tasks");
  const now = localIso();
  $("#tasks").innerHTML = tasks.length ? tasks.map((t) => `
    <div class="task-item ${t.done ? "done" : ""}" data-id="${t.id}">
      <input type="checkbox" data-act="toggle" ${t.done ? "checked" : ""} aria-label="Mark done">
      <div class="grow">
        <div class="task-title small"><strong>${esc(t.title)}</strong> <span class="badge prio-${t.priority}">${t.priority}</span></div>
        <div class="tiny">${t.due_at ? `<span class="${!t.done && t.due_at < now ? "s-LOOKING_AWAY" : ""}">due ${fmtDateTime(t.due_at)}</span>` : "no due date"}
          ${t.estimated_min ? ` · ~${t.estimated_min} min` : ""}${t.subject ? ` · ${esc(t.subject)}` : ""}</div>
        ${t.done ? "" : `<div class="row"><button class="btn small" data-act="plan">Auto-plan</button><button class="btn small ghost" data-act="delete">Delete</button></div>`}
      </div>
    </div>`).join("") : '<div class="empty">No tasks yet.</div>';
  window._tasks = tasks;
}

$("#taskForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("/api/schedule/tasks", { method: "POST", body: {
      title: $("#tTitle").value, subject: $("#tSubject").value, priority: $("#tPrio").value,
      due_at: $("#tDue").value || null, estimated_min: $("#tEst").value || null,
    } });
    e.target.reset();
    loadTasks();
  } catch (err) { toast(err.message, "error"); }
});

$("#tasks").addEventListener("click", async (e) => {
  const act = e.target.dataset.act;
  const item = e.target.closest(".task-item");
  if (!act || !item) return;
  const id = Number(item.dataset.id);
  const task = window._tasks.find((t) => t.id === id);
  if (act === "toggle") {
    await api(`/api/schedule/tasks/${id}`, { method: "PUT", body: { done: e.target.checked } });
    loadTasks();
  } else if (act === "delete") {
    if (await confirmDialog(`Delete task "${task.title}"?`)) { await api(`/api/schedule/tasks/${id}`, { method: "DELETE" }); loadTasks(); }
  } else if (act === "plan") {
    planningTask = task;
    $("#pEst").value = task.estimated_min || "";
    $("#pBlock").value = user.settings.default_session_min;
    $("#planInfo").textContent = `Plan "${task.title}"${task.due_at ? `, due ${fmtDateTime(task.due_at)}` : ""}.`;
    $("#planDialog").showModal();
  }
});

$("#planCancel").addEventListener("click", () => $("#planDialog").close());
$("#planForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    if (Number($("#pEst").value) !== planningTask.estimated_min) {
      await api(`/api/schedule/tasks/${planningTask.id}`, { method: "PUT", body: { estimated_min: Number($("#pEst").value) } });
      loadTasks();
    }
    const r = await api(`/api/schedule/tasks/${planningTask.id}/plan`, { method: "POST", body: {
      now: localIso(), block_min: Number($("#pBlock").value), max_per_day: Number($("#pMax").value),
      day_start: $("#pStart").value, day_end: $("#pEnd").value,
    } });
    $("#planDialog").close();
    toast(r.warning || `Planned ${r.placed_blocks} study block${r.placed_blocks === 1 ? "" : "s"}.`, r.warning ? "error" : "");
    if (r.events[0]) weekStart = mondayOf(new Date(r.events[0].start_at));
    load();
  } catch (err) { toast(err.message, "error"); }
});

// ---------------------------------------------------------------- navigation
$("#prevWeek").addEventListener("click", () => { weekStart = addDays(weekStart, -7); load(); });
$("#nextWeek").addEventListener("click", () => { weekStart = addDays(weekStart, 7); load(); });
$("#thisWeek").addEventListener("click", () => { weekStart = mondayOf(new Date()); load(); });
$("#newEventBtn").addEventListener("click", () => openEvent(null));
$("#viewTabs").addEventListener("click", (e) => {
  const b = e.target.closest("button");
  if (!b) return;
  view = b.dataset.view;
  $$("#viewTabs button").forEach((x) => x.classList.toggle("active", x === b));
  $("#weekView").classList.toggle("hidden", view !== "week");
  $("#agendaView").classList.toggle("hidden", view !== "agenda");
  load();
});

load();
loadTasks();

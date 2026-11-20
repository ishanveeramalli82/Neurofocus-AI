import { api } from "./api.js";
import { VisionTracker, FRAME_HZ } from "./vision.js";
import { ring, timeline, timeRing } from "./charts.js";
import { MiniView, miniViewSupport } from "./miniview.js";
import { $, esc, mountShell, STATE_LABEL, fmtClock, fmtScore, fmtTime, toast, showError, localDate } from "./ui.js";

const user = await mountShell("session");
const settings = user.settings;
$("#planned").value = settings.default_session_min;
if (settings.if_then_prompt) $("#ifThenField").classList.add("highlight");

let tracker = null;
let sessionId = null;
let linkedEvent = null;
let running = false, paused = false;
let buffer = [];
let samples = [];            // [{second, state}] for the local timeline
let lastState = null, episodeStart = null, alerted = false;
let t0 = 0, pausedAt = 0, pausedTotal = 0;
let sendTimer = null, clockTimer = null;
let lastFeature = null;
let mini = null;
const liveState = { state: null, live: null, session: null, distractions: 0, alert: "" };

// ---------------------------------------------------------- setup form
const today = localDate();
const params = new URLSearchParams(location.search);
try {
  const [{ events }, { sessions }] = await Promise.all([
    api(`/api/schedule/events?start=${today}&end=${today}T23:59`),
    api("/api/sessions?limit=50"),
  ]);
  for (const ev of events.filter((e) => e.kind === "study" || e.kind === "exam" || e.kind === "other")) {
    const o = document.createElement("option");
    o.value = ev.id;
    o.textContent = `${fmtTime(ev.start_at)}–${fmtTime(ev.end_at)} · ${ev.title}`;
    o.dataset.title = ev.title;
    o.dataset.subject = ev.subject;
    o.dataset.minutes = Math.round((new Date(ev.end_at) - new Date(ev.start_at)) / 60000);
    $("#eventSel").append(o);
  }
  const subjects = [...new Set(sessions.map((s) => s.subject).filter(Boolean))];
  $("#subjectList").innerHTML = subjects.map((s) => `<option value="${esc(s)}">`).join("");
  if (params.get("event")) {
    $("#eventSel").value = params.get("event");
    $("#eventSel").dispatchEvent(new Event("change"));
  }
} catch (e) { /* the form still works without these */ }

$("#eventSel").addEventListener("change", (e) => {
  const o = e.target.selectedOptions[0];
  if (o?.value) {
    if (!$("#title").value) $("#title").value = o.dataset.title;
    if (!$("#subject").value) $("#subject").value = o.dataset.subject;
    $("#planned").value = o.dataset.minutes;
  }
});
if (params.get("event")) $("#eventSel").dispatchEvent(new Event("change"));

$("#setupForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  $("#setupError").classList.add("hidden");
  $("#startBtn").disabled = true;
  try {
    const eventId = $("#eventSel").value ? Number($("#eventSel").value) : null;
    const { session } = await api("/api/sessions", {
      method: "POST",
      body: { title: $("#title").value, subject: $("#subject").value, schedule_event_id: eventId,
        planned_min: Number($("#planned").value) || null, if_then_plan: $("#ifThen").value },
    });
    sessionId = session.id;
    linkedEvent = eventId;
    $("#completeWrap").classList.toggle("hidden", !eventId);
    $("#setup").classList.add("hidden");
    $("#live").classList.remove("hidden");
    tracker = new VisionTracker($("#video"), $("#overlay"));
    await tracker.init((msg) => { $("#videoMsg").textContent = msg; $("#videoMsg").classList.toggle("hidden", !msg); });
    if ($("#doCal").checked) await runCalibration();
    else await skipCalibration();
  } catch (err) {
    console.error(err);
    tracker?.stop();
    $("#live").classList.add("hidden");
    $("#setup").classList.remove("hidden");
    const msg = err.name === "NotAllowedError" ? "Camera permission was denied. Allow camera access in your browser and try again."
      : err.name === "NotFoundError" ? "No camera was found on this device." : err.message;
    showError($("#setupError"), { message: msg });
    if (sessionId) await api(`/api/sessions/${sessionId}`, { method: "DELETE" }).catch(() => {});
    sessionId = null;
  } finally {
    $("#startBtn").disabled = false;
  }
});

// ---------------------------------------------------------- calibration
const PHASES = [
  { name: "center", title: "Look at the dot", text: "Look at the dot in the middle of your screen, as if you were reading. Keep still.", targets: [[50, 50]], each: 10 },
  { name: "corners", title: "Follow the dot", text: "Follow the dot to each corner of your screen with your eyes and head, as you naturally would.", targets: [[4, 6], [96, 6], [96, 94], [4, 94]], each: 3 },
  { name: "down", title: "Look at your desk", text: "Look down at your desk or keyboard, as if writing notes.", targets: [null], each: 4 },
];
const LEAD_IN = 1.2; // seconds to move your eyes before recording starts
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function collectPhase(phase, frames) {
  const target = $("#calTarget");
  for (const tgt of phase.targets) {
    if (tgt) {
      target.classList.remove("hidden");
      target.style.left = `${tgt[0]}%`;
      target.style.top = `${tgt[1]}%`;
    } else target.classList.add("hidden");
    await sleep(LEAD_IN * 1000);
    const start = performance.now();
    await new Promise((resolve) => {
      tracker.start((f) => {
        frames.push(f);
        const p = (performance.now() - start) / (phase.each * 1000);
        $("#calBar").style.width = `${Math.min(100, p * 100)}%`;
        if (p >= 1) { tracker.pause(); resolve(); }
      }, calT0);
    });
  }
}

let calT0 = 0;
async function runCalibration() {
  const stage = $("#calStage");
  stage.classList.remove("hidden");
  stage.classList.add("running");
  $("#calResult").classList.add("hidden");
  $("#calCancel").classList.remove("hidden");
  calT0 = performance.now();
  const phases = {};
  let cancelled = false;
  $("#calCancel").onclick = () => { cancelled = true; };
  for (const ph of PHASES) {
    $("#calTitle").textContent = ph.title;
    $("#calText").textContent = ph.text;
    $("#calBar").style.width = "0%";
    phases[ph.name] = [];
    await collectPhase(ph, phases[ph.name]);
    if (cancelled) break;
  }
  $("#calTarget").classList.add("hidden");
  stage.classList.remove("running");
  if (cancelled) { stage.classList.add("hidden"); return skipCalibration(); }
  $("#calTitle").textContent = "Checking calibration…";
  $("#calText").textContent = "";
  const res = await api(`/api/sessions/${sessionId}/calibration`, { method: "POST", body: { phases } });
  showCalResult(res, phases);
}

function calSummary(c) {
  return `Neutral head pose: yaw ${c.yaw0.toFixed(1)}°, pitch ${c.pitch0.toFixed(1)}° · ` +
    `"looking away" beyond ±${c.yaw_threshold.toFixed(0)}° · "looking down" beyond ${c.pitch_down_threshold.toFixed(0)}° · ` +
    `eyes closed below EAR ${c.ear_closed_threshold.toFixed(3)}`;
}

function showCalResult(res, phases) {
  const box = $("#calResult");
  const c = res.calibration;
  box.classList.remove("hidden");
  $("#calCancel").classList.add("hidden");
  $("#calTitle").textContent = res.ok ? "Calibration complete" : "Calibration needs another try";
  $("#calText").textContent = res.ok ? calSummary(c) : "";
  box.innerHTML = `
    ${c.warnings.length ? `<div class="alert ${res.ok ? "warn" : "error"} small">${c.warnings.map(esc).join("<br>")}</div>` : ""}
    <div class="row centered"></div>`;
  const row = box.querySelector(".row");
  const btn = (label, cls, fn) => { const b = document.createElement("button"); b.className = `btn ${cls}`; b.textContent = label; b.onclick = fn; row.append(b); };
  if (res.ok) btn("Start studying", "primary", () => { $("#calStage").classList.add("hidden"); beginTracking(c); });
  btn("Redo calibration", res.ok ? "" : "primary", () => runCalibration());
  if (!res.ok) {
    if (c.quality !== "failed") btn("Use it anyway", "", async () => {
      const r = await api(`/api/sessions/${sessionId}/calibration`, { method: "POST", body: { phases, accept_anyway: true } });
      $("#calStage").classList.add("hidden");
      beginTracking(r.calibration);
    });
    btn("Skip calibration", "ghost", () => { $("#calStage").classList.add("hidden"); skipCalibration(); });
  }
}

async function skipCalibration() {
  const r = await api(`/api/sessions/${sessionId}/calibration`, { method: "POST", body: { skip: true } });
  beginTracking(r.calibration);
}

// ---------------------------------------------------------- live tracking
const legend = Object.entries(STATE_LABEL).map(([k, v]) => `<span><i class="dot s-${k}"></i>${v}</span>`).join("");
$("#legend").innerHTML = legend;
ring($("#ringLive"), null, "Last 60 s");

function beginTracking(cal) {
  $("#calInfo").textContent = cal.calibrated
    ? `Calibrated. ${calSummary(cal)}`
    : "Running without personal calibration (population-default thresholds). Accuracy may be lower if your camera is off to the side.";
  running = true;
  t0 = performance.now();
  tracker.start(onFrame, t0);
  sendTimer = setInterval(flush, 1000);
  setupMiniView();
  setupSupports();
  clockTimer = setInterval(tick, 500);
  window.addEventListener("beforeunload", warnUnload);
}

function onFrame(f) {
  if (paused) return;
  f.t = Math.round((f.t - pausedTotal) * 1000) / 1000;
  buffer.push(f);
  lastFeature = f;
  if ($("#showSensors").checked) renderSensors(f);
}

function renderSensors(f) {
  const cell = (k, v) => `<div>${k}: ${v}</div>`;
  $("#sensorBox").innerHTML = f.face_present
    ? cell("yaw", `${f.yaw.toFixed(1)}°`) + cell("pitch", `${f.pitch.toFixed(1)}°`) + cell("EAR", f.ear.toFixed(3)) +
      cell("gaze_h", f.gaze_h.toFixed(2)) + cell("gaze_v", f.gaze_v.toFixed(2)) + cell("t", f.t.toFixed(1))
    : cell("face", "not detected") + cell("t", f.t.toFixed(1));
}

let flushing = false;
let lastFlushError = null;
async function flush() {
  if (flushing || !buffer.length || !sessionId) return;
  flushing = true;
  const batch = buffer.splice(0, 600);
  try {
    const r = await api(`/api/sessions/${sessionId}/frames`, { method: "POST", body: { frames: batch } });
    lastFlushError = null;
    $("#connAlert").classList.add("hidden");
    update(r);
  } catch (e) {
    lastFlushError = e;
    if (connectionProblem(e)) {
      $("#connAlert").textContent = SERVER_DOWN;
      $("#connAlert").classList.remove("hidden");
    }
    if (e.status >= 500 || !e.status) buffer.unshift(...batch); // network problem: retry later
    if (buffer.length > 3000) buffer.splice(0, buffer.length - 3000);
  } finally { flushing = false; }
}

function update(r) {
  const s = r.state;
  $("#statePill").innerHTML = `<span class="dot s-${s}"></span><span class="s-${s}">${STATE_LABEL[s]}</span>`;
  ring($("#ringLive"), r.live_score, "Last 60 s");
  $("#sessScore").textContent = fmtScore(r.session_score);
  $("#distractions").textContent = r.distraction_count;
  const sec = Math.floor(r.t);
  if (!samples.length || samples[samples.length - 1].second < sec) samples.push({ second: sec, state: s });
  timeline($("#liveTimeline"), samples);
  if (tracker) $("#fps").textContent = `${tracker.fps.toFixed(1)} frames/s`;

  if (s !== lastState) { episodeStart = r.t; alerted = false; lastState = s; }
  const away = s !== "FOCUSED" ? r.t - (r.current_episode?.start_t ?? episodeStart) : 0;
  const alertBox = $("#liveAlert");
  if (s !== "FOCUSED" && away >= settings.alert_after_s && settings.nudges && !nudgesMuted && !onBreak) {
    alertBox.textContent = `${STATE_LABEL[s]} for ${Math.round(away)} s. Ready to get back to it?`;
    alertBox.classList.remove("hidden");
    if (!alerted) { alerted = true; chime(); }
  } else alertBox.classList.add("hidden");
  $("#calmState").innerHTML = `<span class="dot s-${s}"></span> ${STATE_LABEL[s]}`;
  Object.assign(liveState, {
    state: s, live: r.live_score, session: r.session_score, distractions: r.distraction_count,
    alert: alertBox.classList.contains("hidden") ? "" : alertBox.textContent,
  });
  pushMini();
}

// ---------------------------------------------------------- pop-out mini view
function elapsedSeconds() {
  const now = paused ? pausedAt : performance.now();
  return (now - t0) / 1000 - pausedTotal;
}

function pushMini() {
  if (!mini?.isOpen) return;
  mini.update({ ...liveState, paused, elapsed: elapsedSeconds(), planned: Number($("#planned").value) * 60 });
}

function setupMiniView() {
  const btn = $("#popOutBtn");
  if (!miniViewSupport()) {
    btn.disabled = true;
    $("#popOutHint").textContent = "Pop-out needs Chrome or Edge.";
    return;
  }
  mini = new MiniView({
    video: $("#video"),
    onPause: () => $("#pauseBtn").click(),
    onEnd: () => $("#endBtn").click(),
    onClose: () => {
      $("#videoBox").classList.remove("popped");
      btn.textContent = "Pop out mini view";
    },
  });
  btn.addEventListener("click", async () => {
    if (mini.isOpen) { mini.close(); return; }
    try {
      await mini.open();
      $("#videoBox").classList.add("popped");
      btn.textContent = "Close mini view";
      pushMini();
    } catch (e) { toast(e.message, "error"); }
  });
}

function chime() {
  if (!settings.alert_sound) return;
  try {
    const ctx = new AudioContext();
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.frequency.value = 660;
    g.gain.setValueAtTime(0.0001, ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.15, ctx.currentTime + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.6);
    o.connect(g).connect(ctx.destination);
    o.start(); o.stop(ctx.currentTime + 0.65);
  } catch { /* audio not available */ }
}

let goalNotified = false;
function tick() {
  if (!running) return;
  const now = paused ? pausedAt : performance.now();
  const el = (now - t0) / 1000 - pausedTotal;
  $("#elapsed").textContent = fmtClock(el);
  const planned = Number($("#planned").value) * 60;
  $("#planMeter").firstElementChild.style.width = `${Math.min(100, (100 * el) / planned)}%`;
  $("#planLabel").textContent = el < planned ? `${fmtClock(planned - el)} left of ${planned / 60} min plan`
    : `Plan complete. Time for a ${settings.break_min}-minute break.`;
  if (el >= planned && !goalNotified) { goalNotified = true; toast(`You reached your ${planned / 60}-minute goal. Take a ${settings.break_min}-minute break!`); chime(); }
  $("#timeLabel").textContent = `${samples.length}s recorded`;
  supportsTick(el, planned);
  pushMini();
}

function setPaused(p) {
  if (p === paused || !running) return;
  paused = p;
  if (paused) { pausedAt = performance.now(); tracker.pause(); }
  else {
    pausedTotal += (performance.now() - pausedAt) / 1000;
    tracker.start(onFrame, t0);
  }
  $("#pauseBtn").textContent = $("#calmPause").textContent = paused ? "Resume" : "Pause";
  pushMini();
}
$("#pauseBtn").addEventListener("click", () => setPaused(!paused));

$("#privacyBlur").addEventListener("change", (e) => $("#videoBox").classList.toggle("privacy", e.target.checked));
$("#showSensors").addEventListener("change", (e) => $("#sensorBox").classList.toggle("hidden", !e.target.checked));

function warnUnload(e) { e.preventDefault(); e.returnValue = ""; }

const SERVER_DOWN = "Connection lost. Your session is saved so far. Make sure NeuroFocus is still running, "
  + "then try again.";

function connectionProblem(e) {
  return !e?.status || e.status >= 500;
}

let ending = false;
let reflection = null;
$("#endBtn").addEventListener("click", async () => {
  if (ending) return;
  ending = true;
  const btn = $("#endBtn");
  btn.disabled = true;
  btn.textContent = "Ending…";
  // Stop recording first; frames already captured stay in the buffer until sent.
  if (running) {
    running = false;
    clearInterval(sendTimer); clearInterval(clockTimer);
    mini?.close();
    tracker?.stop();
    hideSupportsUi();
    reflection = await askReflection();
  }
  try {
    while (flushing) await new Promise((res) => setTimeout(res, 100));  // let an in-flight send finish
    while (buffer.length) {
      const before = buffer.length;
      await flush();
      if (buffer.length >= before) throw lastFlushError || new Error("Could not send the last frames.");
    }
    const { session } = await api(`/api/sessions/${sessionId}/end`, {
      method: "POST",
      body: { notes: $("#notes").value, complete_event: linkedEvent && $("#completeEvent").checked,
        ...(reflection ? { reflection } : {}) },
    });
    window.removeEventListener("beforeunload", warnUnload);
    location.href = `/report?id=${session.id}`;
  } catch (e) {
    console.error(e);
    showEndError(connectionProblem(e) ? SERVER_DOWN : `Could not end the session: ${e.message}`);
    btn.disabled = false;
    btn.textContent = "Try ending again";
    ending = false;
  }
});

function showEndError(msg) {
  const box = $("#connAlert");
  box.textContent = msg;
  box.classList.remove("hidden");
  toast(msg, "error");
}

// ======================================================================
// Focus supports (switched on from the onboarding survey or Settings).
// Design basis: docs/research/ADHD friendly study app design.md
// ======================================================================
let nudgesMuted = false;
let calm = false;
let onBreak = false, breakEndsAt = 0, breakTimer = null;
let blockNo = 1, blockStartEl = 0;
let nextCheckinEl = Infinity, checkinHideTimer = null;

function setupSupports() {
  $("#liveTools").classList.remove("hidden");
  $("#calmTask").textContent = $("#title").value || "Study session";
  const ifThen = $("#ifThen").value.trim();
  for (const id of ["#calmIfThen", "#ifThenLive"]) {
    $(id).textContent = ifThen ? `Your plan: ${ifThen}` : "";
    $(id).classList.toggle("hidden", !ifThen);
  }
  $("#bigTimer").classList.toggle("hidden", !(settings.big_timer || settings.block_timer));
  if (settings.block_timer) {
    $("#blockChip").classList.remove("hidden");
  }
  if (settings.checkins) nextCheckinEl = settings.checkin_every_min * 60;
  if (!settings.nudges) { $("#muteBtn").disabled = true; $("#muteBtn").textContent = "Nudges off (Settings)"; }
  if (settings.calm_mode) setCalm(true);
}

function setCalm(on) {
  calm = on;
  document.body.classList.toggle("calm", on);
  $("#calmView").classList.toggle("hidden", !on);
  $("#calmBtn").setAttribute("aria-pressed", String(on));
  $("#calmBtn").textContent = on ? "Exit calm mode" : "Calm focus mode";
}
$("#calmBtn").addEventListener("click", () => setCalm(!calm));
$("#calmExit").addEventListener("click", () => setCalm(false));
$("#calmPause").addEventListener("click", () => setPaused(!paused));
$("#calmEnd").addEventListener("click", () => $("#endBtn").click());
$("#muteBtn").addEventListener("click", () => {
  nudgesMuted = !nudgesMuted;
  $("#muteBtn").setAttribute("aria-pressed", String(nudgesMuted));
  $("#muteBtn").textContent = nudgesMuted ? "Unmute nudges" : "Mute nudges";
  if (nudgesMuted) $("#liveAlert").classList.add("hidden");
});

function supportsTick(el, planned) {
  // Visual countdown: the current block if the block timer is on, otherwise the planned session.
  const blockLen = settings.block_min * 60;
  const remaining = settings.block_timer ? blockLen - (el - blockStartEl) : planned - el;
  const total = settings.block_timer ? blockLen : planned;
  const label = settings.block_timer ? `left in block ${blockNo}` : "left in your plan";
  if (!$("#bigTimer").classList.contains("hidden")) timeRing($("#bigTimer"), remaining, total, label);
  if (calm) timeRing($("#calmRing"), remaining, total, label);
  $("#calmSub").textContent = settings.block_timer
    ? `Block ${blockNo} · ${settings.block_min}-minute blocks with ${settings.break_min}-minute breaks`
    : `${fmtClock(el)} studied of your ${planned / 60}-minute plan`;
  if (settings.block_timer) $("#blockChip").textContent = `Block ${blockNo} · ${fmtClock(Math.max(0, remaining))} left`;
  if (settings.block_timer && !paused && !onBreak && remaining <= 0) startBreak();
  if (!paused && el >= nextCheckinEl) { showCheckin(el); nextCheckinEl = el + settings.checkin_every_min * 60; }
}

function startBreak() {
  onBreak = true;
  setPaused(true);
  chime();
  breakEndsAt = performance.now() + settings.break_min * 60000;
  $("#breakTitle").textContent = `Block ${blockNo} done. Break time!`;
  $("#breakText").textContent = "Stand up, stretch, get some water. Tracking is paused during your break.";
  $("#breakNext").textContent = "Start next block";
  $("#breakCard").classList.remove("hidden");
  const tickBreak = () => {
    const left = (breakEndsAt - performance.now()) / 1000;
    timeRing($("#breakRing"), left, settings.break_min * 60, "break left");
    if (left <= 0) {
      clearInterval(breakTimer);
      $("#breakTitle").textContent = "Ready to start again?";
      $("#breakText").textContent = `Block ${blockNo + 1} is next. Click when you're back at your desk.`;
      chime();
    }
  };
  tickBreak();
  breakTimer = setInterval(tickBreak, 500);
}
function endBreak() {
  clearInterval(breakTimer);
  $("#breakCard").classList.add("hidden");
  onBreak = false;
  blockNo++;
  setPaused(false);
  const now = performance.now();
  blockStartEl = (now - t0) / 1000 - pausedTotal;
}
$("#breakNext").addEventListener("click", endBreak);
$("#breakSkip").addEventListener("click", endBreak);

function showCheckin(el) {
  const card = $("#checkinCard");
  card.dataset.t = String(Math.round(el * 10) / 10);
  card.classList.remove("hidden");
  clearTimeout(checkinHideTimer);
  checkinHideTimer = setTimeout(() => card.classList.add("hidden"), 45000);   // never blocks work
}
$("#checkinCard").addEventListener("click", async (e) => {
  const b = e.target.closest("[data-rating]");
  if (!b) return;
  $("#checkinCard").classList.add("hidden");
  if (!b.dataset.rating) return;
  try {
    await api(`/api/sessions/${sessionId}/checkins`, { method: "POST",
      body: { t: Number($("#checkinCard").dataset.t), rating: b.dataset.rating } });
  } catch { /* a missed check-in is not worth interrupting the student */ }
});

function hideSupportsUi() {
  clearInterval(breakTimer);
  $("#breakCard").classList.add("hidden");
  $("#checkinCard").classList.add("hidden");
  setCalm(false);
}

const PULLED = [["phone", "Phone"], ["other_apps", "Other apps or websites"], ["people", "People around me"],
  ["tired", "Feeling tired"], ["thoughts", "My own thoughts"], ["hungry", "Hungry or thirsty"],
  ["noise", "Noise"], ["nothing", "Nothing really"]];
$("#feltGroup").innerHTML = ["Not at all", "A little", "Somewhat", "Mostly", "Very"].map((l, i) =>
  `<label class="chip-opt"><input type="radio" name="felt" value="${i + 1}"><span>${l}</span></label>`).join("");
$("#pulledGroup").innerHTML = PULLED.map(([v, l]) =>
  `<label class="chip-opt"><input type="checkbox" name="pulled" value="${v}"><span>${l}</span></label>`).join("");

function askReflection() {
  return new Promise((resolve) => {
    const d = $("#reflectDialog");
    const done = (val) => { d.close(); resolve(val); };
    $("#reflectSkip").onclick = () => done(null);
    d.oncancel = (e) => { e.preventDefault(); done(null); };
    $("#reflectForm").onsubmit = (e) => {
      e.preventDefault();
      const felt = document.querySelector('[name="felt"]:checked');
      done({
        felt_focus: felt ? Number(felt.value) : null,
        pulled_away: [...document.querySelectorAll('[name="pulled"]:checked')].map((i) => i.value),
        helped: $("#helped").value,
      });
    };
    d.showModal();
  });
}

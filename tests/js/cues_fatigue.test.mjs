// Unit tests for the browser-side reminder ladder and tiredness signs.
// Run with: node --test tests/js/cues_fatigue.test.mjs   (also run by pytest when Node is installed)
import { test } from "node:test";
import assert from "node:assert/strict";

globalThis.window = {};   // no audio device here: sounds become no-ops
const { RefocusLadder, AUDIO_COOLDOWN_S, MAX_SOUNDS_PER_HOUR } = await import("../../frontend/js/cues.js");
const { FatigueMonitor } = await import("../../frontend/js/fatigue.js");

const settings = (o = {}) => ({ alert_after_s: 20, alert_sound: true, cue_voice: true, cue_volume: 35, ...o });

test("ladder: visual first, then chime, then one spoken line, then silence", () => {
  const l = new RefocusLadder(() => settings());
  const fired = [];
  for (let away = 0; away <= 300; away++) { const s = l.update(away, 1000 + away, "Bio"); if (s) fired.push([away, s]); }
  assert.deepEqual(fired, [[20, 1], [40, 2], [80, 3]]);
  assert.equal(l.soundTimes.length, 1);          // 2nd sound blocked by the 150 s cooldown
});

test("sounds respect the cooldown and the hourly cap", () => {
  const l = new RefocusLadder(() => settings());
  let now = 0;
  for (let ep = 0; ep < 40; ep++) {              // 40 distraction episodes, 3 minutes apart
    for (let away = 0; away <= 50; away++) l.update(away, now + away, "x");
    l.update(0, now + 51, "x");
    now += 180;
  }
  const gaps = l.soundTimes.slice(1).map((t, i) => t - l.soundTimes[i]);
  assert.ok(gaps.every((g) => g >= AUDIO_COOLDOWN_S));
  const perHour = (t) => l.soundTimes.filter((x) => x > t - 3600 && x <= t).length;
  assert.ok(l.soundTimes.every((t) => perHour(t) <= MAX_SOUNDS_PER_HOUR));
});

test("no sound when audio is off; nothing before the alert delay", () => {
  const l = new RefocusLadder(() => settings({ alert_sound: false }));
  for (let a = 0; a < 20; a++) assert.equal(l.update(a, a, "x"), 0);
  for (let a = 20; a < 200; a++) l.update(a, a, "x");
  assert.equal(l.soundTimes.length, 0);
});

const cal = { calibrated: true, ear0: 0.3, pitch0: 0, pitch_sign: 1 };   // closed below 0.165
const frame = (t, ear, mar = 0.1, pitch = 0) => ({ t, face_present: true, ear, mar, pitch });
function run(m, from, to, fn) { let t = from; for (; t < to; t = Math.round((t + 0.1) * 10) / 10) m.addFrame(fn(t)); return t; }

test("one sign alone is not enough; two signs are", () => {
  const m = new FatigueMonitor(cal);
  // eyes closed ~30% of the time, in 0.3 s pieces (short closures)
  let t = run(m, 0, 70, (x) => frame(x, Math.round(x * 10) % 10 < 3 ? 0.1 : 0.3));
  m.check(t);
  t = run(m, t, 200, (x) => frame(x, Math.round(x * 10) % 10 < 3 ? 0.1 : 0.3));
  let r = m.check(t);
  assert.equal(r.reasons.length, 1);
  assert.equal(r.tired, false);
  // add two yawns -> two signs
  t = run(m, t, t + 2, (x) => frame(x, 0.3, 0.8)); t = run(m, t, t + 5, (x) => frame(x, 0.3));
  t = run(m, t, t + 2, (x) => frame(x, 0.3, 0.8)); t = run(m, t, t + 1, (x) => frame(x, 0.3));
  r = m.check(t);
  assert.ok(r.tired && r.reasons.some((x) => x.includes("yawned 2 times")));
});

test("normal blinking is not flagged", () => {
  const m = new FatigueMonitor(cal);
  const t = run(m, 0, 300, (x) => frame(x, Math.round(x * 10) % 40 === 0 ? 0.1 : 0.3));
  assert.equal(m.check(t).reasons.length, 0);
});

test("looking down at notes is ignored", () => {
  const m = new FatigueMonitor(cal);
  const t = run(m, 0, 300, (x) => frame(x, 0.12, 0.1, -30));   // lids low because looking down
  assert.equal(m.check(t).reasons.length, 0);
});

test("30 minutes without a break triggers on its own; break and snooze reset it", () => {
  const m = new FatigueMonitor(null);
  assert.ok(m.check(31 * 60).tired);
  m.markBreak(31 * 60);
  assert.equal(m.check(40 * 60).tired, false);
  m.snooze(70 * 60);
  assert.equal(m.check(75 * 60).tired, false);
});

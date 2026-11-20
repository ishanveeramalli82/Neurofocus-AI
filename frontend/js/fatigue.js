// Signs of tiredness from the camera features, computed in the browser.
// This is a SUGGESTION tool ("you might be tired, want a break?"), not a
// drowsiness or medical measurement: none of these signs are validated for
// students at a desk, and reading a screen itself lowers blink rate.
// It is separate from the attention engine that the science-fair experiment tests.
//
// Signs (relative to YOUR calibration where possible):
//  1. Eyes-closed share of the last 60 s (PERCLOS-style; Dinges et al. 1998), high for 2+ minutes
//  2. Long blinks (>= 0.4 s): 3 or more in the last minute (blink duration is a better
//     fatigue sign than blink rate; Schleicher et al. 2008)
//  3. Yawns: mouth wide open for >= 1.5 s, 2 or more in 10 minutes
//  4. Focus dropping: last 10 min well below the first 10 min
// Eye frames while looking down (> 20 deg below your neutral pose) are ignored:
// lowered lids when reading notes are not tiredness.
// A break is suggested when 2+ of these signs are present, or after 30 minutes
// without a break. Blink RATE is deliberately not used (it barely differs between
// screen and paper reading). Thresholds are heuristics; none are validated for
// students at a desk (docs/research/, "Gentle refocus cues and fatigue breaks").

export const FATIGUE_DEFAULTS = {
  perclosWindowS: 60,
  perclosLimit: 0.15,          // > 15% of the last minute with eyes closed...
  perclosSustainS: 120,        // ...for at least 2 minutes
  longClosureS: 0.4,
  longClosureWindowS: 60,
  longClosuresLimit: 3,
  marYawn: 0.6,                // mouth height / width
  yawnMinS: 1.5,
  yawnWindowS: 600,
  yawnsLimit: 2,
  declineMinSessionS: 20 * 60,
  declinePoints: 20,
  lookDownDeg: 20,
  signsNeeded: 2,
  noBreakS: 30 * 60,
  snoozeS: 20 * 60,
};

export class FatigueMonitor {
  /** cal: calibration from the server (uses ear0, pitch0, pitch_sign); null = defaults. */
  constructor(cal = null, opts = {}) {
    this.o = { ...FATIGUE_DEFAULTS, ...opts };
    // Stricter than the attention engine: about 0.55 x your own open-eye EAR (0.2 if uncalibrated).
    this.earClosed = cal?.calibrated ? 0.55 * cal.ear0 : 0.2;
    this.pitch0 = cal?.calibrated ? cal.pitch0 : 0;
    this.pitchSign = cal?.pitch_sign ?? 1;
    this.perclosHighSince = null;
    this.frames = [];          // {t, closed, mar}
    this.closures = [];        // end times of long closures
    this.yawns = [];           // end times of yawns
    this.closedSince = null;
    this.yawnSince = null;
    this.lastBreakT = 0;
    this.snoozedUntil = -Infinity;
  }

  addFrame(f) {
    const t = f.t;
    const down = Number.isFinite(f.pitch) && this.pitchSign * (f.pitch - this.pitch0) < -this.o.lookDownDeg;
    if (down) return;   // looking down at notes: lowered lids are not tiredness
    const closed = !!f.face_present && Number.isFinite(f.ear) && f.ear < this.earClosed;
    const mar = f.face_present && Number.isFinite(f.mar) ? f.mar : null;
    this.frames.push({ t, closed, present: !!f.face_present });
    const keep = Math.max(this.o.perclosWindowS, 10);
    while (this.frames.length && t - this.frames[0].t > keep) this.frames.shift();
    // long eye closures
    if (closed && this.closedSince == null) this.closedSince = t;
    if (!closed && this.closedSince != null) {
      if (t - this.closedSince >= this.o.longClosureS) this.closures.push(t);
      this.closedSince = null;
    }
    // yawns
    const open = mar != null && mar > this.o.marYawn;
    if (open && this.yawnSince == null) this.yawnSince = t;
    if (!open && this.yawnSince != null) {
      if (t - this.yawnSince >= this.o.yawnMinS) this.yawns.push(t);
      this.yawnSince = null;
    }
    this.closures = this.closures.filter((x) => t - x <= this.o.longClosureWindowS);
    this.yawns = this.yawns.filter((x) => t - x <= this.o.yawnWindowS);
  }

  markBreak(t) { this.lastBreakT = t; this.snoozedUntil = t + this.o.snoozeS; this.perclosHighSince = null; }
  snooze(t) { this.snoozedUntil = t + this.o.snoozeS; }

  /** samples: [{second, state}] from the engine (for the focus-decline sign).
   * Returns {tired, reasons[], signs} ; tired only when not snoozed. */
  check(t, samples = []) {
    const o = this.o, reasons = [];
    const present = this.frames.filter((f) => f.present);
    const perclos = present.length >= 20 ? present.filter((f) => f.closed).length / present.length : 0;
    if (perclos > o.perclosLimit) this.perclosHighSince ??= t; else this.perclosHighSince = null;
    if (this.perclosHighSince != null && t - this.perclosHighSince >= o.perclosSustainS) {
      reasons.push(`your eyes have been closed for ${Math.round(perclos * 100)}% of the time for a couple of minutes`);
    }
    if (this.closures.length >= o.longClosuresLimit) reasons.push(`you had ${this.closures.length} long, slow blinks in the last minute`);
    if (this.yawns.length >= o.yawnsLimit) reasons.push(`you yawned ${this.yawns.length} times in the last 10 minutes`);
    let decline = null;
    if (samples.length >= o.declineMinSessionS) {
      const pct = (arr) => (100 * arr.filter((s) => s.state === "FOCUSED").length) / Math.max(arr.length, 1);
      const first = pct(samples.slice(0, 600)), last = pct(samples.slice(-600));
      decline = first - last;
      if (decline >= o.declinePoints) reasons.push(`your focus dropped from ${Math.round(first)} to ${Math.round(last)} compared with the start`);
    }
    const signs = reasons.length;
    const sinceBreak = t - this.lastBreakT;
    const longStretch = sinceBreak >= o.noBreakS;
    if (longStretch) reasons.push(`you've studied ${Math.round(sinceBreak / 60)} minutes without a break`);
    return { tired: (signs >= o.signsNeeded || longStretch) && t >= this.snoozedUntil, reasons,
      signs: { perclos, longClosures: this.closures.length, yawns: this.yawns.length, decline, sinceBreak } };
  }
}

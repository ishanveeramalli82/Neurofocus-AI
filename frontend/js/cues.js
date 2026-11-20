// Gentle audio reminders. Designed NOT to startle (docs/research/, "Gentle refocus cues"):
//  * slow fade-in: fast rise times with loud, broadband sound drive the startle reflex
//  * soft pure (sine) tones through a low-pass filter, no noise, no harsh high beeps
//  * a FALLING two-note contour: rising pitch is heard as more urgent (Edworthy et al. 1991)
//  * quiet by default, user volume control, can be switched off (WCAG 2.2 SC 1.4.2)
//  * a short escalation ladder (visual first, then chime, then voice) that stops, with a
//    cooldown and an hourly cap, instead of a repeating alarm

let ctx = null;

/** Create/resume the audio engine. Call from a click (browsers block audio until the user interacts). */
export function unlockAudio() {
  try {
    ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
    if (ctx.state === "suspended") ctx.resume();
  } catch { ctx = null; }
}

/** Soft two-note "singing bowl" chime. volume: 0..1 (user setting, default 0.35). */
export function softChime(volume = 0.35) {
  unlockAudio();
  if (!ctx) return;
  const now = ctx.currentTime;
  const peak = 0.12 * Math.max(0, Math.min(1, volume));       // quiet even at 100%
  const filter = ctx.createBiquadFilter();
  filter.type = "lowpass";
  filter.frequency.value = 1800;
  filter.connect(ctx.destination);
  // Two falling notes (E5 then C5), each fading in over 0.5 s and out over ~1.5 s.
  [[659.3, 0], [523.3, 0.4]].forEach(([freq, delay]) => {
    const osc = ctx.createOscillator(), gain = ctx.createGain();
    osc.type = "sine";
    osc.frequency.value = freq;
    const t = now + delay;
    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.linearRampToValueAtTime(peak, t + 0.5);          // slow rise: no startle
    gain.gain.exponentialRampToValueAtTime(0.0001, t + 1.6);   // soft fade
    osc.connect(gain).connect(filter);
    osc.start(t);
    osc.stop(t + 1.7);
  });
}

/** Calm spoken reminder using the computer's built-in voices (works offline). */
export function speak(text, volume = 0.35) {
  if (!("speechSynthesis" in window)) return;
  try {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 0.92;       // slightly slower than normal speech
    u.pitch = 1.0;
    u.volume = Math.max(0.05, Math.min(1, volume * 1.6));
    const voices = window.speechSynthesis.getVoices();
    const calm = voices.find((v) => /en/i.test(v.lang) && /(female|samantha|zira|aria|jenny|google us english)/i.test(v.name))
      || voices.find((v) => /^en/i.test(v.lang));
    if (calm) u.voice = calm;
    window.speechSynthesis.speak(u);
  } catch { /* speech not available */ }
}

const FIRST = ["Hey, let's come back to {task}.", "Gentle reminder: back to {task} when you're ready.",
  "Let's pick up {task} again."];
const SECOND = ["Still there? Take a breath, then let's get back to {task}.",
  "No worries. Let's refocus on {task} together."];
const LAST = "If you need one, a short break is fine too. Otherwise, back to {task}.";
const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];

/**
 * Escalating, self-limiting reminder ladder for one distraction episode.
 * step 1 (at alert time): visual message only
 * step 2 (+20 s still away): soft chime
 * step 3 (+40 s more): one calm spoken line offering to refocus or take a break, then silence
 * Audio cooldown of 150 s between sounds and at most 8 sounds per hour, so
 * frequent drifting never turns into a stream of alarms.
 */
export const AUDIO_COOLDOWN_S = 150;
export const MAX_SOUNDS_PER_HOUR = 8;
export class RefocusLadder {
  constructor(getSettings) {
    this.getSettings = getSettings;
    this.reset();
    this.soundTimes = [];
  }

  reset() { this.step = 0; this.nextAt = null; }

  /** Call regularly with seconds distracted in the current episode (0 when focused). Returns the step fired, if any. */
  update(awaySeconds, nowSeconds, task) {
    const s = this.getSettings();
    if (awaySeconds <= 0) { this.reset(); return 0; }
    if (awaySeconds < s.alert_after_s) return 0;
    const gaps = [0, 20, 40];
    if (this.step >= 3) return 0;
    if (this.nextAt == null) this.nextAt = s.alert_after_s;
    if (awaySeconds < this.nextAt) return 0;
    this.step += 1;
    this.nextAt = awaySeconds + (gaps[this.step] ?? Infinity);
    if (this.step === 1 || !s.alert_sound) return this.step;          // step 1 is visual only
    this.soundTimes = this.soundTimes.filter((x) => nowSeconds - x < 3600);
    const last = this.soundTimes[this.soundTimes.length - 1] ?? -Infinity;
    if (nowSeconds - last < AUDIO_COOLDOWN_S || this.soundTimes.length >= MAX_SOUNDS_PER_HOUR) return this.step;
    const vol = (s.cue_volume ?? 35) / 100;
    const t = (str) => str.replaceAll("{task}", task || "your work");
    if (this.step === 2 || !s.cue_voice) softChime(vol);
    else speak(t(Math.random() < 0.5 ? LAST : pick(SECOND.concat(FIRST))), vol);
    this.soundTimes.push(nowSeconds);
    return this.step;
  }
}

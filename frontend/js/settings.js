import { api } from "./api.js";
import { softChime, speak, unlockAudio } from "./cues.js";
import { $, mountShell, toast, confirmDialog } from "./ui.js";

const user = await mountShell("settings");
const s = user.settings;
$("#name").value = user.display_name;
$("#goal").value = s.daily_goal_min;
$("#sessionLen").value = s.default_session_min;
$("#breakLen").value = s.break_min;
$("#alertAfter").value = s.alert_after_s;
$("#sound").checked = s.alert_sound;
const FLAGS = { cueVoice: "cue_voice", tiredPrompts: "tired_prompts", nudges: "nudges", blockTimer: "block_timer", calmMode: "calm_mode", bigTimer: "big_timer",
  checkins: "checkins", ifThenPrompt: "if_then_prompt" };
for (const [id, key] of Object.entries(FLAGS)) $(`#${id}`).checked = !!s[key];
$("#blockMin").value = s.block_min;
$("#cueVolume").value = s.cue_volume;
$("#testSound").addEventListener("click", () => {
  unlockAudio();
  const vol = Number($("#cueVolume").value) / 100;
  softChime(vol);
  if ($("#cueVoice").checked) setTimeout(() => speak("Hey, let's come back to your work.", vol), 2600);
});
$("#checkinEvery").value = s.checkin_every_min;
try { $("#theme").value = localStorage.getItem("nf-theme") || ""; } catch { /* storage blocked */ }

$("#profileForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("/api/account/profile", { method: "PUT", body: {
      display_name: $("#name").value,
      settings: { daily_goal_min: $("#goal").value, default_session_min: $("#sessionLen").value,
        break_min: $("#breakLen").value, alert_after_s: $("#alertAfter").value, alert_sound: $("#sound").checked,
        block_min: $("#blockMin").value, checkin_every_min: $("#checkinEvery").value, cue_volume: $("#cueVolume").value,
        ...Object.fromEntries(Object.entries(FLAGS).map(([id, key]) => [key, $(`#${id}`).checked])) },
    } });
    try { localStorage.setItem("nf-theme", $("#theme").value); } catch { /* ignore */ }
    applyTheme();
    toast("Settings saved");
  } catch (err) { toast(err.message, "error"); }
});

$("#pwForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("/api/account/password", { method: "PUT", body: { current_password: $("#curPw").value, new_password: $("#newPw").value } });
    e.target.reset();
    toast("Password updated");
  } catch (err) { toast(err.message, "error"); }
});

$("#deleteForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!(await confirmDialog("Permanently delete your account and all data?", "Delete everything"))) return;
  try {
    await api("/api/account", { method: "DELETE", body: { password: $("#delPw").value } });
    location.href = "/";
  } catch (err) { toast(err.message, "error"); }
});

function applyTheme() {
  let t = "";
  try { t = localStorage.getItem("nf-theme") || ""; } catch { /* ignore */ }
  if (t) document.documentElement.dataset.theme = t; else delete document.documentElement.dataset.theme;
}

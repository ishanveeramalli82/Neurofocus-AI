// "How do you study?" onboarding survey. Questions come from the server
// (backend/survey.py) so the wording, options and validation live in one place.
import { api, requireUser } from "./api.js";
import { $, esc, toast } from "./ui.js";

await requireUser();
const [{ questions }, profile] = await Promise.all([api("/api/profile/questions"), api("/api/profile")]);
const answers = { ...profile.answers };
const sections = [...new Set(questions.map((q) => q.section))];
let step = -1;

function progress() {
  $("#progressBar").style.width = `${step < 0 ? 0 : ((step + 1) / (sections.length + 1)) * 100}%`;
  $("#stepLabel").textContent = step < 0 ? "" : step < sections.length ? `Step ${step + 1} of ${sections.length}` : "Done";
}

function field(q) {
  const name = `q_${q.id}`;
  const why = `<div class="tiny onb-why">Why we ask: ${esc(q.why)}</div>`;
  if (q.type === "time") {
    return `<fieldset class="onb-q"><legend>${esc(q.text)}</legend>
      <input type="time" name="${name}" value="${esc(answers[q.id] || "")}" aria-label="${esc(q.text)}">${why}</fieldset>`;
  }
  const multi = q.type === "multi";
  const chosen = new Set(multi ? answers[q.id] || [] : [answers[q.id]]);
  const opts = q.options.map(([val, label]) => `
    <label class="chip-opt"><input type="${multi ? "checkbox" : "radio"}" name="${name}" value="${esc(val)}"
      ${chosen.has(val) ? "checked" : ""}><span>${esc(label)}</span></label>`).join("");
  return `<fieldset class="onb-q"><legend>${esc(q.text)}</legend>
    <div class="chip-group ${q.type === "scale" ? "scale" : ""}">${opts}</div>${why}</fieldset>`;
}

function collect() {
  for (const q of questions.filter((x) => x.section === sections[step])) {
    const name = `q_${q.id}`;
    if (q.type === "multi") answers[q.id] = [...document.querySelectorAll(`[name="${name}"]:checked`)].map((i) => i.value);
    else if (q.type === "time") answers[q.id] = document.querySelector(`[name="${name}"]`).value || null;
    else answers[q.id] = document.querySelector(`[name="${name}"]:checked`)?.value || null;
  }
}

function render() {
  progress();
  $("#sectionTitle").textContent = sections[step];
  $("#questions").innerHTML = questions.filter((q) => q.section === sections[step]).map(field).join("");
  $("#backBtn").classList.toggle("invisible", step === 0);
  $("#nextBtn").textContent = step === sections.length - 1 ? "Finish" : "Next";
  $("#questions").querySelector("input")?.focus();
}

$("#beginBtn").addEventListener("click", () => {
  step = 0;
  $("#intro").classList.add("hidden");
  $("#surveyForm").classList.remove("hidden");
  render();
});
$("#backBtn").addEventListener("click", () => { collect(); step--; render(); });
$("#surveyForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  collect();
  if (step < sections.length - 1) { step++; render(); return; }
  try {
    const clean = Object.fromEntries(Object.entries(answers).filter(([, v]) => v != null && v !== "" && !(Array.isArray(v) && !v.length)));
    const r = await api("/api/profile", { method: "PUT", body: { answers: clean } });
    step = sections.length;
    progress();
    $("#surveyForm").classList.add("hidden");
    $("#done").classList.remove("hidden");
    $("#skipBtn").classList.add("hidden");
    const supports = questions.find((q) => q.id === "supports").options.filter(([k]) => (r.answers.supports || []).includes(k));
    $("#doneText").textContent = supports.length
      ? "These focus supports are now switched on (change them any time in Settings):"
      : "No focus supports chosen. You can switch them on any time in Settings.";
    $("#doneList").innerHTML = supports.map(([, label]) => `<li>${esc(label)}</li>`).join("");
  } catch (err) {
    $("#formError").textContent = err.message;
    $("#formError").classList.remove("hidden");
  }
});
$("#skipBtn").addEventListener("click", async () => {
  await api("/api/profile/skip", { method: "POST" }).catch(() => {});
  toast("You can take the survey later from Settings.");
  location.href = "/dashboard";
});
progress();

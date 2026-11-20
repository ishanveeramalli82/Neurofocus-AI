import { api } from "./api.js";
import { $, showError } from "./ui.js";

const next = new URLSearchParams(location.search).get("next");
const dest = next && next.startsWith("/") && !next.startsWith("//") ? next : "/dashboard";

async function submit(form, path, body, goTo = dest) {
  $("#error").classList.add("hidden");
  $("#submitBtn").disabled = true;
  try {
    await api(path, { method: "POST", body });
    location.href = goTo;
  } catch (e) {
    showError($("#error"), e);
  } finally {
    $("#submitBtn").disabled = false;
  }
}

$("#loginForm")?.addEventListener("submit", (e) => {
  e.preventDefault();
  submit(e.target, "/api/auth/login", { email: $("#email").value, password: $("#password").value });
});

$("#registerForm")?.addEventListener("submit", (e) => {
  e.preventDefault();
  if (!$("#agree").checked) return showError($("#error"), { message: "Please confirm you understand NeuroFocus is not a diagnostic tool." });
  submit(e.target, "/api/auth/register", {
    display_name: $("#name").value, email: $("#email").value, password: $("#password").value,
  }, "/onboarding");  // new accounts start with the short "How do you study?" survey
});

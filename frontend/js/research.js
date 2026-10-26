import { $, esc, mountShell } from "./ui.js";

// Public page: use the app shell when signed in, otherwise a simple layout.
const status = await (await fetch("/api/auth/status", { credentials: "same-origin" })).json();
if (status.signed_in) await mountShell("research");
else {
  $("#sidebar").remove();
  $("#shell").classList.remove("shell");
  $("#publicHome").classList.remove("hidden");
}

const fmt = (x, n = 3) => (x == null || Number.isNaN(x) ? "n/a" : Number(x).toFixed(n));

const { version, params } = await (await fetch("/api/engine/params")).json();
const rows = [
  ["Engine version", version],
  ["Default 'looking away' threshold (no calibration)", `±${params.default_yaw_threshold_deg}°`],
  ["Default 'looking down' threshold (no calibration)", `${params.default_pitch_down_threshold_deg}°`],
  ["Calibrated away threshold", `widest corner look + ${params.yaw_margin_deg}°, limited to ${params.yaw_threshold_bounds.join("–")}°`],
  ["Calibrated down threshold", `lowest corner look + ${params.pitch_margin_deg}°, limited to ${params.pitch_threshold_bounds.join("–")}°`],
  ["Eyes-closed threshold", `EAR < ${params.ear_closed_ratio} × personal open-eye EAR`],
  ["Iris offset to degrees", `${params.gaze_to_deg}° per unit`],
  ["Onset times", Object.entries(params.onset_s).map(([k, v]) => `${k.replace("_", " ").toLowerCase()} ${v} s`).join(", ")],
  ["Recovery time", `${params.recovery_s} s`],
  ["Live score window", `${params.live_window_s} s`],
];
$("#paramsTable").innerHTML = rows.map(([k, v]) => `<tr><td class="small">${esc(k)}</td><td class="small mono">${esc(v)}</td></tr>`).join("");

const { runs } = await (await fetch("/api/research/runs")).json();
const official = runs.filter((r) => !r.smoke_test);
const box = $("#results");
if (!official.length) {
  box.innerHTML = `<p class="small">No official experiment run has been recorded yet. Run
    <code>python -m research.pipeline.run_experiment --config research/config/experiment_v1.json</code>
    and the results will appear here automatically.</p>`;
} else {
  box.innerHTML = official.map((r) => {
    const p = r.statistics.primary;
    const table = p ? `
      <p class="small">Primary comparison: <strong>${esc(p.comparison.treatment)}</strong> vs <strong>${esc(p.comparison.control)}</strong> on <code>${esc(p.comparison.metric)}</code>
        (${r.n_students} virtual students, ${Math.round(r.session_duration_s / 60)}-minute sessions)</p>
      <div class="table-wrap"><table>
        <thead><tr><th>Noise</th><th>Treatment</th><th>Control</th><th>Mean difference [95% CI]</th><th>p (Holm)</th><th>Effect r</th></tr></thead>
        <tbody>${Object.entries(p.by_noise).map(([lv, t]) => `<tr><td>${esc(lv)}</td><td>${fmt(t.mean_a)}</td><td>${fmt(t.mean_b)}</td>
          <td>${fmt(t.mean_diff)} [${fmt(t.ci95_mean_diff[0])}, ${fmt(t.ci95_mean_diff[1])}]</td><td>${fmt(t.p_holm, 4)}</td><td>${fmt(t.rank_biserial, 2)}</td></tr>`).join("")}</tbody>
      </table></div>` : "<p class='small'>Exploratory run (no primary hypothesis test).</p>";
    const figs = r.figures.filter((f) => !f.startsWith("confusion_behaviors")).slice(0, 8).map((f) =>
      `<a href="/research-files/${encodeURIComponent(r.run_id)}/figures/${encodeURIComponent(f)}" target="_blank" rel="noopener">${esc(f)}</a>`).join(" · ");
    return `<div class="stack"><h3>${esc(r.experiment_id)} <span class="tiny">run ${esc(r.run_id)} · engine v${esc(r.engine_version)}</span></h3>${table}
      <p class="tiny">Full report: <a href="/research-files/${encodeURIComponent(r.run_id)}/statistics_report.md" target="_blank" rel="noopener">statistics_report.md</a>${figs ? ` · Figures: ${figs}` : ""}</p></div>`;
  }).join("<hr>");
}

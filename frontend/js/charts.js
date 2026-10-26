// Small dependency-free SVG charts. Rendered at the container's pixel width
// and re-rendered on resize. Colours come from CSS classes (theme-aware).

import { esc, STATE_LABEL } from "./ui.js";

const PAD = { l: 34, r: 10, t: 10, b: 26 };
const renderers = new Map();
window.addEventListener("resize", () => renderers.forEach((fn) => fn()));

function mount(el, draw) {
  const fn = () => { el.innerHTML = draw(Math.max(el.clientWidth, 260)); };
  renderers.set(el, fn);
  fn();
}

function yTicks(max) {
  const step = max <= 10 ? 2 : max <= 50 ? 10 : max <= 100 ? 25 : Math.ceil(max / 4 / 10) * 10;
  const out = [];
  for (let v = 0; v <= max + 1e-9; v += step) out.push(v);
  return out;
}

/** points: [{label, value|null}] */
export function lineChart(el, points, { height = 220, yMax = 100, unit = "" } = {}) {
  if (!points.some((p) => p.value != null)) {
    el.innerHTML = '<div class="empty">No data yet</div>';
    renderers.delete(el);
    return;
  }
  mount(el, (W) => {
    const iw = W - PAD.l - PAD.r, ih = height - PAD.t - PAD.b;
    const x = (i) => PAD.l + (points.length === 1 ? iw / 2 : (i * iw) / (points.length - 1));
    const y = (v) => PAD.t + ih - (v / yMax) * ih;
    const grid = yTicks(yMax).map((v) =>
      `<line class="grid-line" x1="${PAD.l}" x2="${W - PAD.r}" y1="${y(v)}" y2="${y(v)}"/><text x="${PAD.l - 6}" y="${y(v) + 4}" text-anchor="end">${v}${unit}</text>`).join("");
    const every = Math.ceil(points.length / Math.max(2, Math.floor(iw / 60)));
    const xl = points.map((p, i) => (i % every === 0 || (i === points.length - 1 && i % every >= every / 2))
      ? `<text x="${x(i)}" y="${height - 6}" text-anchor="middle">${esc(p.label)}</text>` : "").join("");
    // break the line where values are missing
    let d = "", area = "", seg = [];
    const flush = () => {
      if (!seg.length) return;
      d += "M" + seg.map(([i, v]) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`).join("L");
      area += `M${x(seg[0][0])},${y(0)}L` + seg.map(([i, v]) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`).join("L") + `L${x(seg[seg.length - 1][0])},${y(0)}Z`;
      seg = [];
    };
    points.forEach((p, i) => (p.value == null ? flush() : seg.push([i, Math.min(p.value, yMax)])));
    flush();
    const dots = points.length <= 40 ? points.map((p, i) => p.value == null ? "" :
      `<circle class="pt" cx="${x(i)}" cy="${y(Math.min(p.value, yMax))}" r="3"><title>${esc(p.label)}: ${Math.round(p.value)}${unit}</title></circle>`).join("") : "";
    return `<svg class="chart" width="${W}" height="${height}" role="img">${grid}<path class="area" d="${area}"/><path class="line" d="${d}"/>${dots}${xl}</svg>`;
  });
}

/** items: [{label, value, title?}] */
export function barChart(el, items, { height = 200, yMax, unit = "", alt = false } = {}) {
  if (!items.length || !items.some((i) => i.value)) {
    el.innerHTML = '<div class="empty">No data yet</div>';
    renderers.delete(el);
    return;
  }
  const max = yMax ?? (Math.max(...items.map((i) => i.value || 0)) * 1.15 || 1);
  mount(el, (W) => {
    const iw = W - PAD.l - PAD.r, ih = height - PAD.t - PAD.b;
    const bw = iw / items.length;
    const y = (v) => PAD.t + ih - (v / max) * ih;
    const grid = yTicks(max).filter((v) => v <= max).map((v) =>
      `<line class="grid-line" x1="${PAD.l}" x2="${W - PAD.r}" y1="${y(v)}" y2="${y(v)}"/><text x="${PAD.l - 6}" y="${y(v) + 4}" text-anchor="end">${Math.round(v)}${unit}</text>`).join("");
    const every = Math.ceil(items.length / Math.max(2, Math.floor(iw / 44)));
    const bars = items.map((it, i) => {
      const v = it.value || 0, bx = PAD.l + i * bw + bw * 0.18, w = bw * 0.64;
      const label = i % every === 0 ? `<text x="${PAD.l + i * bw + bw / 2}" y="${height - 6}" text-anchor="middle">${esc(it.label)}</text>` : "";
      return `<rect class="bar ${alt ? "alt" : ""}" x="${bx}" y="${y(v)}" width="${w}" height="${Math.max(0, y(0) - y(v))}" rx="3"><title>${esc(it.title || `${it.label}: ${Math.round(v)}${unit}`)}</title></rect>${label}`;
    }).join("");
    return `<svg class="chart" width="${W}" height="${height}" role="img">${grid}${bars}</svg>`;
  });
}

/** Coloured strip of attention states. samples: [{second, state}] */
export function timeline(el, samples) {
  el.className = "timeline";
  el.innerHTML = "";
  if (!samples.length) return;
  const total = samples[samples.length - 1].second - samples[0].second + 1;
  let runStart = 0;
  for (let i = 1; i <= samples.length; i++) {
    if (i === samples.length || samples[i].state !== samples[runStart].state) {
      const end = i === samples.length ? samples[i - 1].second + 1 : samples[i].second;
      const div = document.createElement("div");
      div.className = `bg-${samples[runStart].state}`;
      div.style.width = `${(100 * (end - samples[runStart].second)) / total}%`;
      div.title = `${STATE_LABEL[samples[runStart].state]} · ${end - samples[runStart].second}s`;
      el.append(div);
      runStart = i;
    }
  }
}

/** Circular score gauge (0-100). */
export function ring(el, value, sub = "Focus Score") {
  const r = 70, c = 2 * Math.PI * r;
  const v = value == null ? 0 : Math.max(0, Math.min(100, value));
  el.innerHTML = `<svg class="ring" viewBox="0 0 170 170" role="img" aria-label="${sub} ${value == null ? "not available" : Math.round(v)}">
    <circle class="track" cx="85" cy="85" r="${r}" fill="none" stroke-width="13"/>
    <circle class="val" cx="85" cy="85" r="${r}" fill="none" stroke-width="13" stroke-linecap="round"
      stroke-dasharray="${c}" stroke-dashoffset="${c * (1 - v / 100)}" transform="rotate(-90 85 85)"/>
    <text x="85" y="90" text-anchor="middle" font-size="38">${value == null ? "–" : Math.round(v)}</text>
    <text class="ring-sub" x="85" y="114" text-anchor="middle">${esc(sub)}</text></svg>`;
}

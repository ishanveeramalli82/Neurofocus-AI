// Pop-out mini view: a small always-on-top window, like Spotify's mini
// player, that you can drag anywhere on screen while you work in other tabs
// or apps.
//
// Chrome and Edge (116+) support the Document Picture-in-Picture API, which
// gives a real mini window with live state, score, timer and Pause/End
// buttons. The camera preview moves into the mini window while it is open:
// a visible video keeps the camera delivering frames, so tracking continues
// at full speed while the main tab is in the background.
//
// Browsers without it but with video Picture-in-Picture (e.g. Safari) get a
// read-only floating card drawn on a canvas.

import { STATE_LABEL, fmtClock, fmtScore } from "./ui.js";

const STATE_COLOR = {
  FOCUSED: "#16a34a", LOOKING_AWAY: "#ea580c", LOOKING_DOWN: "#d97706",
  EYES_CLOSED: "#9333ea", ABSENT: "#64748b",
};

export function miniViewSupport() {
  if ("documentPictureInPicture" in window) return "document";
  if (document.pictureInPictureEnabled && HTMLCanvasElement.prototype.captureStream) return "video";
  return null;
}

export class MiniView {
  /** @param {{video: HTMLVideoElement, onPause: Function, onEnd: Function, onClose?: Function}} opts */
  constructor(opts) {
    this.opts = opts;
    this.win = null;
    this.mode = null;
    this.last = null;
  }

  get isOpen() { return !!this.win || (this.mode === "video" && document.pictureInPictureElement === this.pipVideo); }

  async open() {
    const support = miniViewSupport();
    if (!support) throw new Error("This browser cannot pop out a mini window. Use Chrome or Edge.");
    if (this.isOpen) return;
    this.mode = support;
    if (support === "document") await this._openDocument();
    else await this._openVideo();
    if (this.last) this.update(this.last);
  }

  async _openDocument() {
    const win = await window.documentPictureInPicture.requestWindow({ width: 320, height: 300 });
    this.win = win;
    const doc = win.document;
    doc.title = "NeuroFocus";
    const link = doc.createElement("link");
    link.rel = "stylesheet";
    link.href = new URL("/static/css/app.css", location.href).href;
    doc.head.append(link);
    if (document.documentElement.dataset.theme) doc.documentElement.dataset.theme = document.documentElement.dataset.theme;
    doc.body.className = "mini-body";
    doc.body.innerHTML = `
      <div class="mini">
        <div class="mini-video" id="miniVideo"></div>
        <div class="mini-row">
          <span class="mini-state" id="miniState"><span class="dot"></span><span>Waiting…</span></span>
          <span class="mini-time" id="miniTime">0:00</span>
        </div>
        <div class="mini-scores">
          <div><div class="mini-big" id="miniLive">–</div><div class="tiny">last 60 s</div></div>
          <div><div class="mini-big" id="miniSession">–</div><div class="tiny">session</div></div>
          <div><div class="mini-big" id="miniDist">0</div><div class="tiny">distractions</div></div>
        </div>
        <div class="meter"><div id="miniBar"></div></div>
        <div class="mini-alert hidden" id="miniAlert"></div>
        <div class="mini-actions">
          <button class="btn small" id="miniPause">Pause</button>
          <button class="btn small" id="miniBack">Open tab</button>
          <button class="btn small danger" id="miniEnd">End</button>
        </div>
      </div>`;
    const $ = (id) => doc.getElementById(id);
    $("miniPause").addEventListener("click", () => this.opts.onPause());
    $("miniEnd").addEventListener("click", () => this.opts.onEnd());
    $("miniBack").addEventListener("click", () => { window.focus(); });
    // Move the camera preview into the mini window (keeps frames flowing).
    const video = this.opts.video;
    this.videoHome = { parent: video.parentElement, next: video.nextSibling };
    $("miniVideo").append(video);
    video.play().catch(() => {});
    win.addEventListener("pagehide", () => {
      const { parent, next } = this.videoHome;
      parent.insertBefore(video, next);
      video.play().catch(() => {});
      this.win = null;
      this.opts.onClose?.();
    });
  }

  async _openVideo() {
    this.canvas = document.createElement("canvas");
    this.canvas.width = 480;
    this.canvas.height = 270;
    this.pipVideo = document.createElement("video");
    this.pipVideo.muted = true;
    this.pipVideo.srcObject = this.canvas.captureStream(4);
    this._draw(this.last || {});
    await this.pipVideo.play();
    await this.pipVideo.requestPictureInPicture();
    this.pipVideo.addEventListener("leavepictureinpicture", () => this.opts.onClose?.(), { once: true });
  }

  /** s: {state, live, session, elapsed, planned, distractions, paused, alert} */
  update(s) {
    this.last = s;
    if (this.mode === "document" && this.win) {
      const $ = (id) => this.win.document.getElementById(id);
      $("miniState").innerHTML = `<span class="dot s-${s.state}"></span><span class="s-${s.state}">${s.paused ? "Paused" : STATE_LABEL[s.state] || "Waiting…"}</span>`;
      $("miniTime").textContent = fmtClock(s.elapsed || 0);
      $("miniLive").textContent = fmtScore(s.live);
      $("miniSession").textContent = fmtScore(s.session);
      $("miniDist").textContent = s.distractions ?? 0;
      $("miniBar").style.width = `${s.planned ? Math.min(100, (100 * (s.elapsed || 0)) / s.planned) : 0}%`;
      $("miniPause").textContent = s.paused ? "Resume" : "Pause";
      $("miniAlert").textContent = s.alert || "";
      $("miniAlert").classList.toggle("hidden", !s.alert);
    } else if (this.mode === "video" && this.canvas) {
      this._draw(s);
    }
  }

  _draw(s) {
    const c = this.canvas.getContext("2d");
    const W = this.canvas.width, H = this.canvas.height;
    c.fillStyle = "#151b29";
    c.fillRect(0, 0, W, H);
    c.fillStyle = STATE_COLOR[s.state] || "#64748b";
    c.fillRect(0, 0, 12, H);
    c.fillStyle = "#e8ecf5";
    c.font = "bold 34px system-ui, sans-serif";
    c.fillText(s.paused ? "Paused" : STATE_LABEL[s.state] || "Waiting…", 36, 62);
    c.font = "bold 72px system-ui, sans-serif";
    c.fillText(fmtScore(s.live), 36, 160);
    c.font = "20px system-ui, sans-serif";
    c.fillStyle = "#aab3c7";
    c.fillText("score, last 60 s", 36, 190);
    c.fillText(`Session ${fmtScore(s.session)} · ${s.distractions ?? 0} distractions · ${fmtClock(s.elapsed || 0)}`, 36, 240);
  }

  close() {
    if (this.win) this.win.close();
    if (this.mode === "video" && document.pictureInPictureElement) document.exitPictureInPicture().catch(() => {});
    this.win = null;
  }
}

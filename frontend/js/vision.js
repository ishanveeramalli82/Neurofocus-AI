// Computer-vision front end. Runs entirely in the browser:
//   webcam frame -> MediaPipe Face Landmarker (478 landmarks + head transform)
//   -> 6 numeric features (face_present, yaw, pitch, ear, gaze_h, gaze_v)
// Only those numbers are sent to the server. Video never leaves the device.
// Feature definitions are documented in research/docs/03_algorithm.md.

// MediaPipe Tasks Vision 0.10.14 and the Face Landmarker model are bundled in
// frontend/vendor (see vendor/README.md), so no third-party server is contacted.
const MP_BASE = "/static/vendor/mediapipe";
const MODEL_URL = "/static/vendor/models/face_landmarker.task";
export const FRAME_HZ = 10;

// Landmark indices in the MediaPipe 478-point face mesh.
const EYE_R = { left: 33, right: 133, top: [160, 158], bottom: [144, 153], lid: [159, 145], iris: 468 };
const EYE_L = { left: 362, right: 263, top: [385, 387], bottom: [380, 373], lid: [386, 374], iris: 473 };
// EAR pairs follow Soukupová & Čech (2016): p2-p6 and p3-p5 over p1-p4.

function dist(a, b, W, H) { return Math.hypot((a.x - b.x) * W, (a.y - b.y) * H); }

function eyeFeatures(lm, e, W, H) {
  const p1 = lm[e.left], p4 = lm[e.right];
  const width = dist(p1, p4, W, H);
  const ear = (dist(lm[e.top[0]], lm[e.bottom[0]], W, H) + dist(lm[e.top[1]], lm[e.bottom[1]], W, H)) / (2 * width);
  const iris = lm[e.iris];
  // position of the iris along the corner-to-corner axis, 0 (image-left) .. 1 (image-right)
  const ax = (p4.x - p1.x) * W, ay = (p4.y - p1.y) * H;
  const u = (((iris.x - p1.x) * W) * ax + ((iris.y - p1.y) * H) * ay) / (ax * ax + ay * ay);
  const lidMidY = (lm[e.lid[0]].y + lm[e.lid[1]].y) / 2;
  const v = ((iris.y - lidMidY) * H) / width;
  return { ear, u, v };
}

const clamp = (x, lo, hi) => Math.max(lo, Math.min(hi, x));

/** Rotation -> yaw/pitch of the face's forward axis, in degrees.
 * MediaPipe returns a 4x4 matrix; its storage order is detected from where the
 * translation (face ~30-80 cm in front of camera) sits. */
function headPose(m) {
  const colMajor = Math.abs(m[14]) >= Math.abs(m[11]);
  const R = (r, c) => (colMajor ? m[c * 4 + r] : m[r * 4 + c]);
  const fx = R(0, 2), fy = R(1, 2), fz = R(2, 2); // forward axis = third column
  const yaw = (Math.atan2(fx, fz) * 180) / Math.PI;
  const pitch = (Math.atan2(fy, Math.hypot(fx, fz)) * 180) / Math.PI; // +up (verified in calibration)
  return { yaw, pitch };
}

export function computeFeatures(result, t, W, H) {
  const lm = result?.faceLandmarks?.[0];
  const mat = result?.facialTransformationMatrixes?.[0]?.data;
  if (!lm || lm.length < 478 || !mat) return { t, face_present: false };
  const { yaw, pitch } = headPose(mat);
  const r = eyeFeatures(lm, EYE_R, W, H), l = eyeFeatures(lm, EYE_L, W, H);
  const round = (x, n = 3) => Math.round(x * 10 ** n) / 10 ** n;
  return {
    t: round(t, 3),
    face_present: true,
    yaw: round(yaw, 2),
    pitch: round(pitch, 2),
    ear: round((r.ear + l.ear) / 2, 4),
    // centred iris offset scaled so +-1 is roughly the comfortable limit of eye rotation
    gaze_h: round(clamp(((r.u + l.u) / 2 - 0.5) * 4, -1, 1), 4),
    gaze_v: round(clamp(((r.v + l.v) / 2) * 4, -1, 1), 4),
    // Mouth aspect ratio (inner-lip gap / mouth width), used only for the
    // "signs of tiredness" yawn check. The attention engine ignores it.
    mar: round(dist(lm[13], lm[14], W, H) / dist(lm[61], lm[291], W, H), 4),
  };
}

// A worker-based ticker keeps sampling at ~10 Hz even when this tab is in the
// background (plain timers get throttled to 1 Hz or less there).
function makeTicker(hz, fn) {
  const src = `let id=setInterval(()=>postMessage(0),${Math.round(1000 / hz)});onmessage=()=>clearInterval(id);`;
  try {
    const url = URL.createObjectURL(new Blob([src], { type: "text/javascript" }));
    const w = new Worker(url);
    w.onmessage = fn;
    return () => { w.postMessage(0); w.terminate(); URL.revokeObjectURL(url); };
  } catch {
    const id = setInterval(fn, 1000 / hz);
    return () => clearInterval(id);
  }
}

export class VisionTracker {
  constructor(video, canvas) {
    this.video = video;
    this.canvas = canvas;
    this.landmarker = null;
    this.stream = null;
    this.stopTick = null;
    this.t0 = null;
    this.drawOverlay = true;
    this.fps = 0;
  }

  async init(onStatus = () => {}) {
    if (!navigator.mediaDevices?.getUserMedia) throw new Error("This browser cannot access a camera.");
    onStatus("Requesting camera permission…");
    this.stream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" }, audio: false,
    });
    this.video.srcObject = this.stream;
    this.video.muted = true;
    this.video.playsInline = true;
    await this.video.play();
    onStatus("Loading face-landmark model (first time can take a few seconds)…");
    const vision = await import(`${MP_BASE}/vision_bundle.mjs`);
    const files = await vision.FilesetResolver.forVisionTasks(`${MP_BASE}/wasm`);
    const opts = (delegate) => ({
      baseOptions: { modelAssetPath: MODEL_URL, delegate },
      runningMode: "VIDEO",
      numFaces: 1,
      outputFacialTransformationMatrixes: true,
      outputFaceBlendshapes: false,
    });
    try {
      this.landmarker = await vision.FaceLandmarker.createFromOptions(files, opts("GPU"));
    } catch {
      this.landmarker = await vision.FaceLandmarker.createFromOptions(files, opts("CPU"));
    }
    onStatus("");
  }

  /** Start sampling. onFrame(features) is called ~10 times per second. */
  start(onFrame, t0 = performance.now()) {
    this.t0 = t0;
    let last = -1, count = 0, fpsT = performance.now();
    this.stopTick = makeTicker(FRAME_HZ, () => {
      if (!this.landmarker || this.video.readyState < 2) return;
      const now = performance.now();
      if (now <= last) return;
      last = now;
      let result;
      try { result = this.landmarker.detectForVideo(this.video, now); } catch { return; }
      const W = this.video.videoWidth, H = this.video.videoHeight;
      const f = computeFeatures(result, (now - this.t0) / 1000, W, H);
      if (this.drawOverlay) this.draw(result, W, H);
      count++;
      if (now - fpsT > 2000) { this.fps = (count * 1000) / (now - fpsT); count = 0; fpsT = now; }
      onFrame(f);
    });
  }

  pause() { if (this.stopTick) { this.stopTick(); this.stopTick = null; } }

  draw(result, W, H) {
    const c = this.canvas;
    if (!c) return;
    if (c.width !== W) { c.width = W; c.height = H; }
    const ctx = c.getContext("2d");
    ctx.clearRect(0, 0, W, H);
    const lm = result?.faceLandmarks?.[0];
    if (!lm) return;
    ctx.fillStyle = "rgba(129,140,248,.85)";
    for (const i of [33, 160, 158, 133, 153, 144, 362, 385, 387, 263, 373, 380, 1, 152, 10, 234, 454]) {
      ctx.beginPath(); ctx.arc(lm[i].x * W, lm[i].y * H, 2.2, 0, 2 * Math.PI); ctx.fill();
    }
    ctx.fillStyle = "rgba(74,222,128,.95)";
    for (const i of [468, 473]) {
      ctx.beginPath(); ctx.arc(lm[i].x * W, lm[i].y * H, 3.5, 0, 2 * Math.PI); ctx.fill();
    }
  }

  stop() {
    this.pause();
    this.stream?.getTracks().forEach((t) => t.stop());
    this.stream = null;
    this.landmarker?.close?.();
    this.landmarker = null;
    if (this.canvas) this.canvas.getContext("2d").clearRect(0, 0, this.canvas.width, this.canvas.height);
  }
}

# Vendored third-party files

Bundled locally so the app works offline (e.g. at a science fair with no Wi-Fi)
and so the Content-Security-Policy can forbid all third-party scripts.

| Path | Source | Version | License |
|---|---|---|---|
| `mediapipe/vision_bundle.mjs`, `mediapipe/wasm/*` | npm package `@mediapipe/tasks-vision` | 0.10.14 | Apache-2.0 |
| `models/face_landmarker.task` | https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task | float16 v1 | Apache-2.0 (see the MediaPipe Face Landmarker model card) |

SHA-256 at the time of vendoring:

```
64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff  models/face_landmarker.task
e77f281f9619150d937023c355bae170e9120e3b9e43f1e23a2a7bee07197669  mediapipe/vision_bundle.mjs
```

Record these in your research paper's Materials section: the face-landmark
model is a fixed, versioned component of the system under test.

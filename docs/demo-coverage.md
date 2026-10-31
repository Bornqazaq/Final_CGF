# Real-time demo and coverage

File: `deliverables/video/Laser_Vault_Heist_Demo.mp4`, 1920x1080, 30 fps, 210 seconds.
Matching English captions are burned into the real application overlay and provided as SRT.
No music or narration; captions satisfy the brief. FPS remains visible throughout.
The deterministic controller issues normal input to the same Game logic as manual play.
The encoder samples the actual OpenGL backbuffer in wall-clock time, without time scaling.

| Time | Feature and evidence |
|---|---|
| 00:00-00:16 | Original room, 5+ distinct object types, textures, lighting (R2, R4, R5) |
| 00:16-00:29 | First-person movement, lamp off/on (R6, interaction 1) |
| 00:29-00:49 | Crouch, full animated thief in live CCTV, second view (R6, stretch CCTV, interaction 2) |
| 00:49-01:02 | Rotating fixtures and following spotlights (R3, R4, stretch spotlights) |
| 01:02-01:24 | Real contact, all-red alarm and real retry reset |
| 01:24-01:39 | Actual source snippets and driver/core-profile diagnostics (R1) |
| 01:39-03:12 | Continuous final route through moving/rotating laser boxes |
| 03:12-03:15 | Required crouch under the final beam, no cut |
| 03:15-03:19 | Wheel, bolts and hinged safe opening (R3, interaction 3) |
| 03:19-03:30 | Victory while the opened safe remains visible (stretch victory) |
| Entire video | Genuine live FPS counter (R7, local hardware only) |

Exact game-state transition times are recorded in `evidence/demo-gameplay-trace.csv`.
The MP4 frame ledger records elapsed wall time and whether a missed sampling slot duplicated
a previous image. This is capture scheduling, not game-time acceleration. The first
0.5-second FPS warm-up precedes capture. The final pass after retry contains no cuts.

To present: explain the problem and pipeline first using the 10-slide deck; play this
video next; then answer questions using the live game and `docs/defense-guide.md`.

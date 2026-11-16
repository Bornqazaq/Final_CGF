# Runtime demonstration

The built-in `--demo` mode supplies ordinary movement and interaction inputs to
the same gameplay logic as manual play. It captures a sequence covering the room,
lamp, live CCTV, rotating lights, alarm/retry, diagnostics, traversal and finale.
The complete sequence lasts approximately 3 minutes 45 seconds.

| Segment | Feature |
|---|---|
| Interior | Distinct scene objects, materials, UV textures and lighting |
| Lamp and CCTV | Interactive lighting and a real second-camera framebuffer |
| Moving equipment | Parent-child transforms and rotating spotlight directions |
| Failure | Laser contact, red alarm and retry |
| Diagnostics | OpenGL context and rendering information |
| Traversal | Continuous movement through the six hazards and final crouch |
| Finale | Wheel/bolt/door animation, full dance and Victory |

Recording reads the actual OpenGL backbuffer. The on-screen FPS counter and
feature captions identify the displayed systems. The report uses runtime captures
in `evidence/screenshots/report-current/`. Existing video ledgers and subtitle files
belong to their recorded release snapshot.

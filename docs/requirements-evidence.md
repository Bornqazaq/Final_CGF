# Requirements and evidence

Statuses describe implementation evidence, not awarded points. **Local** means implemented and checked here; **External** means a TA/human condition remains. Visual quality is review-based, not a universal artifact-free guarantee. Paths are relative to the repository. Video timings refer to the final 3:30 demo. Detailed capture mapping is in [demo-coverage.md](demo-coverage.md).

## Mandatory requirements

| ID | Requirement | Status | Code / evidence / check |
|---|---|---|---|
| R1 | C++17, OpenGL 3.3 core, own GLSL and VAO/VBO/EBO | Local | src/main.cpp, src/graphics.cpp, shaders; evidence/runtime-info.txt; demo 01:24–01:39 shows actual runtime/source diagnostics |
| R2 | At least five distinct 3D objects | Local | art/blender/vault.blend; assets/vault.scene; room, safe, desk, chair, lamp, monitor, plants, drawers; demo 00:00–00:16 |
| R3 | MVP and parent–child hierarchy | Local | src/scene.cpp, src/world.cpp, shaders/surface.vert; spots 00:49–01:02; safe wheel/bolts/hinge 03:15–03:19 |
| R4 | Per-fragment Blinn-Phong, multiple/dynamic lights | Local | shaders/surface.frag; six point lights, two rotating spots and moon; lamp 00:16–00:29; all-red alarm 01:03–01:24 |
| R5 | UV textures and mipmaps | Local | tools/blender/export_scene.py; src/graphics.cpp; assets/textures; report pp.15–17; runtime visual review |
| R6 | Mouse/keyboard, at least two interactions | Local input paths; manual usability external | src/main.cpp, src/game.cpp; three interactions exercised by tests and demo; native human-input testing is not claimed |
| R7 | 30+ FPS on TA at 1280×720, visible counter | Local measurements; TA external | evidence/benchmarks/summary.json, raw CSV; whole-video live counter; TA hardware unknown |
| R8 | Course build and accurate README | Local clean build; exact course starter external | CMakeLists.txt, tools/build/build.ps1, README; evidence/ctest-clean.txt; course starter not supplied |

## All 33 rubric items

| ID | Points | Status | Actual evidence and scope |
|---|---:|---|---|
| A1 | 4 | Local | R1; own indexed core pipeline; source overlay 01:24–01:39 |
| A2 | 5 | Local | R2/R3; original scene, safe and fixture hierarchy; report pp.11–16 |
| A3 | 6 | Local | R4; inverse-transpose normals, attenuation, soft spot cones; report p.15 |
| A4 | 5 | Local | UV exports, seeded original textures, trilinear mipmaps; report p.17; room/character screenshots |
| A5 | 8 | Local | All three stretch goals: rotating spots 00:49–01:02, live CCTV 00:29–00:49, safe-opening victory 03:15–03:30 |
| A6 | 2 | Prepared; understanding external | docs/defense-guide.md; slides 3–7; actual oral explanation not simulated |
| B1 | 5 | Local visual review | art/blender; original warm wood/plaster/brass vault and brown-clothed thief; evidence/screenshots/room-world-final.png, character-face-final.png |
| B2 | 4 | Local visual review with stated limits | Final room, face, rest/crouch poses and all demo milestones inspected; pose bounds and zero GL errors; small-shadow aliasing/LBS approximation remain documented |
| B3 | 4 | Local; TA external | Three real runs: 1281.7, 1183.8, 1215.8 average FPS; evidence/benchmarks; no unknown-hardware guarantee |
| B4 | 2 | Local | src/scene.cpp and graphics.cpp: static mesh/material instancing, one-time geometry/texture upload; report p.14 |
| C1 | 4 | Local logic/render checks; manual usability external | src/game.cpp fixed 1/240 s update, normalized movement, crouch clearance; tests/director_tests.cpp slow-frame comparison |
| C2 | 4 | Local | Lamp toggle, CCTV camera switch, safe opening; complete_gameplay_route and demo_and_slow_frames; 00:16, 00:29, 03:15 |
| C3 | 2 | Local | src/ui.cpp; start menu, F1 help, pause/alarm/victory controls; screenshots/start-menu.png |
| D1 | 3 | Local clean build; course environment external | Vendored dependencies, clean LLVM-MinGW Release build, all three CTest suites; portable extraction check in evidence/package-validation.json |
| D2 | 3 | Local | Separated graphics, game, world, animation, UI, input/director, capture and telemetry; own C++ modules below 500 lines; docs/architecture.md |
| D3 | 2 | Local | README.md, CREDITS.md, LICENSES, docs/dependency-lock.json; tested commands and platform limits stated |
| D4 | 2 | Actual Git history | Real core, asset, refinement and delivery commits. No backdated classroom milestones or fictional participants |
| E1 | 2 | Local | 26-page PDF follows supplied template sections; all pages visually inspected; figures 1–10; evidence/report-structure.json |
| E2 | 2 | Local | Report pp.3,9: objective, concrete problems and single-room scope |
| E3 | 3 | Local bibliographic audit | 18 verified journal articles, 16 excluding the two CACM entries; comparative review pp.4–8, DOI references pp.22–25; docs/references-verified.json, evidence/source-audit.json; ranking-source access limits disclosed |
| E4 | 3 | Local | Report pp.10–13: tools, actual process, architecture, inverse-transform collision, skinning and coordinate conversion |
| E5 | 2 | Local | Report pp.14–20: all feature screenshots, test suites, raw-frame-time methodology, hardware and performance chart/table |
| E6 | 1 | Local | Report pp.20–21: actual fixes, limitations and future work |
| E7 | 2 | Local | Numbered IEEE-style references, author/DOI/venue data and technical credits; CREDITS and full third-party notices |
| F1 | 3 | Materials ready; delivery external | Ten-slide PPTX/PDF explains problem, implementation and results; no live performance claimed |
| F2 | 2 | Materials ready; understanding external | Editable architecture and collision diagrams; skinning/lighting equations; slides 3–7 and defense guide |
| F3 | 2 | Materials ready; rehearsal external | Speaker notes target 520 seconds (8:40); 10 slides; user must rehearse actual spoken delivery |
| F4 | 3 | Materials ready; answers external | Defense questions and write-on-request tasks linked to real functions; no fabricated Q&A performance |
| G1 | 1 | Local | MP4 duration 210.07 s, within 3–6 minutes; evidence/video-validation.json |
| G2 | 3 | Local feature coverage; R7 TA qualifier external | docs/demo-coverage.md maps R1–R7 and all three stretch goals to actual visible events |
| G3 | 2 | Local | Real wall-clock OpenGL backbuffer capture; FPS continuously visible; frame ledger and gameplay trace; deterministic ordinary inputs, no teleports/invulnerability/time scaling |
| G4 | 2 | Local | 1920×1080, 30 fps, readable burned-in captions plus SRT; entire video decodes without errors; no music/narration needed |
| G5 | 2 | Local | Named feature captions; room → interactions → spots → failure/reset → source → continuous route → safe/victory |

## External assessment and delivery actions

The TA computer, exact course starter, native human keyboard/mouse usability, actual rehearsal, oral understanding and live defense remain unverified. The original course's classroom checkpoints, deadline, Moodle upload and TA invitation are human/organizational actions; no completion or grade is invented. The public repository and release are delivery artifacts, not proof of those conditions.

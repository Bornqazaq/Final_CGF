# Technical requirement coverage

| ID | Implementation | Source and evidence |
|---|---|---|
| R1 | OpenGL 3.3 Core, VAO/VBO/EBO, separate vertex and fragment shaders | `src/graphics.cpp`, `src/renderer.cpp`, `shaders/` |
| R2 | Vault, corridor, safe, furnishings, security fixtures and animated character | `assets/`, report interior screenshots |
| R3 | Model/view/projection matrices, inverse-transpose normals and parent-child transforms | `src/scene.cpp`, `src/world.cpp`, `shaders/surface.vert` |
| R4 | Per-fragment Blinn-Phong, eight point lights, two rotating spotlights and a toggleable lamp | `shaders/surface.frag`, report lighting and lamp figures |
| R5 | UV-mapped textures, generated mipmaps and trilinear filtering | `src/graphics.cpp`, `assets/textures/` |
| R6 | Keyboard/mouse controls, two camera modes and lamp/CCTV/safe interactions | `src/game.cpp`, `src/main.cpp`, `tests/camera_tests.cpp` |
| R7 | On-screen FPS counter and three measured 1280 × 720 runs | `src/ui.cpp`, `evidence/benchmarks-current/` |
| R8 | CMake build with included runtime libraries | `CMakeLists.txt`, `README.md` |

## Topic extensions

| Feature | Implementation |
|---|---|
| Rotating spotlights | Fixture hierarchy and light directions share world transforms |
| Live CCTV | A second-camera framebuffer supplies the physical monitor and enlarged view |
| Safe-opening victory | Wheel, bolt and door animation followed by a complete one-shot dance |

## Regression coverage

The seven CTest suites exercise gameplay mathematics, complete routes, slow-frame
behavior, animation data, the finale, camera/input/settings and GPU laser occlusion.
`evidence/ctest-current.txt` contains the latest test result. Report figures are
captured from the application in `evidence/screenshots/report-current/`.

## Measurement scope

Performance figures describe Windows x64 on the hardware listed in the README.
Other computers and operating systems require their own build and runtime checks.
Collision uses finite body samples at 240 Hz; spotlight cones are a visual effect,
and the current shadow map belongs to the directional light. These are the
implementation boundaries used in the report's evaluation.

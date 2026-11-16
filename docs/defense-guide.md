# Technical discussion guide

Students: Nurbek Yerbulekov, Makhmet Demesh, Nurassyl Nygmet<br>
Group: SE-2428

## Main concepts

The application combines indexed geometry, MVP transforms, parent-child animation,
per-fragment lighting, UV textures, skeletal deformation and framebuffer rendering.
The following source references connect those concepts to their implementation.

| Question | Answer and source |
|---|---|
| What do VAO/VBO/EBO store? | Mesh::Mesh in src/graphics.cpp creates vertex/index buffers; VAO remembers attributes and element binding; Mesh::draw uses glDrawElements. A VAO does not duplicate vertex data. |
| What does the vertex shader do? | shaders/surface.vert applies skin/instance/model transforms and MVP, passes world position/normal/UV. The fragment shader evaluates lighting for each covered fragment. Shader::Shader checks compile/link errors. |
| Why an inverse-transpose normal matrix? | A normal must remain perpendicular after a non-uniform scale. Multiplying by the position matrix breaks that constraint; transpose(inverse(mat3(M))) restores it, then normalize. |
| What is a UV/mipmap? | UV assigns 2D image coordinates to mesh corners. loadTexture in src/graphics.cpp uploads sRGB, calls glGenerateMipmap and GL_LINEAR_MIPMAP_LINEAR; prefiltered levels reduce distant aliasing. Repeating UVs intentionally tile floor/wall materials. |
| What creates the safe hierarchy? | Scene::updateWorld multiplies parent world by local. updateWorld in src/world.cpp changes safe hinge/wheel/bolt locals, then the hierarchy propagates them. |
| What exactly detects a laser? | pointInBox and sampledBodyHits in src/game.cpp use inverse beam transform and half extents; Game::playerHit tests upright body samples. The final crouch has sufficient clearance; this is sampled collision, not a capsule triangle solver. |
| How does animation reach the GPU? | Animator::load reads LVHA, Animator::update interpolates local TRS and computes globalBone*inverseBind. surface.vert blends weighted matrices. The full character appears in Renderer::frame's CCTV pass. |
| Why two CCTV color paths? | Renderer::frame renders linear scene color for the physical screen; a display-converted target feeds the enlarged ImGui view. The monitor never samples itself during its own pass. |
| How is FPS measured? | Frame wall time includes update, submission, UI, logging and present. Average FPS=1000/mean(ms); 1% low=1000/mean(slowest 1%). CPU timing cannot claim isolated GPU cost. |
| What work do libraries perform? | GLFW owns window/input/context; GLAD loads pointers; GLM supplies math; stb decodes images; ImGui draws UI. Game rules, scene/skin evaluation and graphics passes are project C++/GLSL. |

## Team topics

- Nurbek Yerbulekov: design, environment and character assets, animation integration,
  visual composition and clearance around the safe.
- Makhmet Demesh: oriented laser contact, state transitions and rendering passes.
- Nurassyl Nygmet: camera/input behavior, interactions, regression tests and measurements.

## Gameplay demonstration

Start the game, switch cameras, toggle the lamp and change the live CCTV view.
Show laser contact and retry, then cross the six-beam route and open the safe.
The wheel/bolt/door sequence is followed by the complete one-shot dance and Victory.
The runtime FPS counter and menu settings remain available during normal play.

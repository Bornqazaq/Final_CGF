# Presentation notes

## 1. Laser Vault Heist

Target: 35 seconds.

Introduce Laser Vault Heist as topic 12, a single-room first-person game for Computer Graphics Fundamentals. The goal is a complete, inspectable implementation using C++17 and OpenGL 3.3 core. The room and thief were made in Blender, including UVs, rig and actions. State the single author and group. This is the brief's teaching example, so there are no invented team members. Explain that the presentation will connect the visible game to its collision, shading and render pipeline, then show a real-time demo. Source: project README and the supplied topic brief.

## 2. The heist and its constraints

Target: 45 seconds.

Describe the playable loop: observe six moving or rotating lasers, walk through the vault, crouch under the final low beam and interact with the safe. A real contact triggers red illumination and ends the attempt; retry resets position, phases and the mechanism. There are three useful interactions: lamp, CCTV and safe. Scope is deliberately one room with no guard NPC, combat or multiplayer. The controller, collision body and rendered thief must agree about crouching. The final demo uses the same Game rules through deterministic input, so it is repeatable automated evidence rather than a claimed human playtest. Sources: game.cpp, director.cpp, README.

## 3. Architecture and frame pipeline

Target: 65 seconds.

Trace input from GLFW into the fixed-step accumulator. Game updates at 240 Hz, retaining short interaction edges until a step consumes them. World applies game state to node transforms and animation. Assets enter through documented native formats exported from Blender, then Scene builds its parent-first hierarchy and static batches. Rendering uses a moon depth pass, a separate CCTV framebuffer, the main HDR target, post-processing and UI. Explain that static matrices and meshes upload once; only dynamic values and bone palettes change each frame. All GL objects are destroyed before the context. The separation makes rule tests independent of the GPU. Sources: main.cpp, fixed_step.hpp, scene.cpp, renderer.cpp, graphics.cpp.

## 4. Collision in the laser’s local space

Target: 75 seconds.

Explain the equation q=inverse(M)*p: moving a world-space player sample into beam-local coordinates makes the oriented-box test three scalar comparisons. The long thin rectangle and its dashed enclosing world box illustrate a false positive that a world AABB would create. Rendering and contact share M. The implementation samples the upright body every 0.08 metres with a conservative local margin, plus the exact head point. The final beam is at 1.42 metres; standing body height is 1.90 and crouching is 1.29. A 240 Hz step reduces ordinary tunneling, but is not exact continuous collision for arbitrary speed. Show the short code and explain every term. Scientific comparison: Klosowski et al., DOI 10.1109/2945.675649; Jimenez et al., DOI 10.1016/S0097-8493(00)00130-8. Implementation: game.cpp.

## 5. Per-fragment lighting

Target: 60 seconds.

Describe the Blinn-Phong fragment shader using the surface normal, light vector and half-vector. Diffuse is clamped N dot L; the specular lobe is a shininess power of N dot H. Local light power is attenuated by distance; spotlights use smooth cone edges. Their directions follow the same rotating mounts seen in the screenshot. Six local lights, two spots and a directional moon are recolored on alarm. Only the moon has a 2048-square PCF shadow map. Visible dust cones are additive meshes, not a claim of physical volumetric transport. Explain linear lighting followed by the credited filmic fit and gamma. Sources: surface.frag, post.frag; Phong DOI 10.1145/360825.360839; Cook-Torrance DOI 10.1145/357290.357293; Narkowicz, https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/ (CC0).

## 6. Original character and animation

Target: 55 seconds.

The thief is original Blender geometry rather than an imported animation package. Show the neutral face view and crouch pose, then state the measured 21,782 triangles and 20 bones. Five clips cover idle, walk, crouched idle, crouched walk and interaction. Local TRS interpolates with quaternion slerp for rotations; skinning blends global bone matrices times inverse binds. Clips are in-place and stride phase follows travelled distance. Pose checks verify normalized weights and a 1.2755 metre crouched mesh maximum against a 1.29 metre body. The corrected arm pose compensates for torso lean. Linear blend skinning remains a simple approximation; dual quaternions could better preserve joint volume. Source: character_rig.py, animation.cpp, surface.vert; Kavan et al., DOI 10.1145/1409625.1409627.

## 7. Live CCTV with render-to-texture

Target: 50 seconds.

Point out that the monitor contains a second live scene camera, not a recorded image. Its framebuffer has color and depth attachments and is checked for completeness. The full animated thief is included in that pass but hidden from the first-person camera to avoid clipping. The monitor screen is excluded from its own render, preventing undefined read/write feedback. E switches between two camera locations. The physical screen samples linear color inside the main pipeline. The enlarged presentation view uses a separately display-converted texture, because feeding linear color directly to ImGui made it dark during development. Sources: renderer.cpp, world.cpp, surface.frag, ui.cpp and the real screenshot at 00:37.

## 8. Measured local performance

Target: 55 seconds.

Read the chart as uncapped whole-frame performance, not monitor refresh rate or isolated GPU timing. Three visible 1280 by 720 runs lasted 65 seconds with the first five discarded. The route kept CCTV, lasers, spotlights and animation active, with capture disabled. Average FPS is reciprocal mean frame time. The 1% low is reciprocal mean of the slowest one percent; values are 753.0, 470.4 and 686.3. Hardware is i5-13400F, RTX 5060 and 32 GiB. Background desktop work was possible. These local results exceed 60 FPS but cannot certify the unknown TA machine. Mention that all three CTest suites and a clean build passed. Source: evidence/benchmarks/summary.json and run-1.csv through run-3.csv.

## 9. Failure, reset and safe-opening victory

Target: 40 seconds.

Use these actual captured frames to explain the state machine. A beam contact changes all scene illumination to red and offers retry. Retry reconstructs the initial state rather than only changing a menu label. In the successful final attempt, the player crosses the last beam while crouched, backs away using normal collision-tested movement and opens the safe within interaction range. The wheel turns, bolts retract and the door rotates around its hinge; victory follows the sequence. The demo shows this without a cut in the final attempt. These frames are evidence from the same application and rules. Sources: game.cpp, world.cpp, director.cpp, demo-gameplay-trace.csv.

## 10. Results, limits and next checks

Target: 40 seconds.

Conclude with concrete deliverables: the standalone game, editable Blender sources, five clips, custom shaders and runtime formats, tests, raw measurements, the report's eighteen verified references and the real-time demo. The engineering lesson is consistency between render transforms, collision, pose and color space. State limits without claiming a grade: sampled collision, LBS, one shadow map and Windows-only recording. Native human input testing, TA hardware, exact starter compatibility and oral understanding require external checks. Future technical work would be swept collision and stronger deformation if the scope expands. Next play the 3:30 captioned demo, then open the source for questions. Source: README, report and docs/defense-guide.md.
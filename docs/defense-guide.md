# Defense guide

Student: Nurbek Yerbulekov  
Group: SE-2428

This document prepares a live defense; it is not evidence that a defense occurred.
The brief specifies one author instead of the old PDF's 3-5 person team. Do not invent
colleagues or classroom progress checks. Present the deck in about 8.5 minutes, then the
3.5-minute demo, then 3-5 minutes of questions. Rehearse in your own words.

## Be able to explain and write

1. **MVP:** write `gl_Position=P*V*M*vec4(p,1)` and explain right-to-left application,
   world space versus view space, perspective divide, and why normals need inverse transpose.
2. **Hierarchy:** derive safe-door world = safeWorld * hingeTranslation * doorRotation *
   localMesh. Move the hinge and predict which wheel/bolt children follow it.
3. **Laser test:** write inverse(M)*point and three half-extent comparisons. Give a point
   inside a rotated world AABB but outside the oriented box. Show the regression test.
4. **Blinn-Phong:** derive diffuse max(N.L,0), half-vector H=normalize(L+V), shininess,
   attenuation and spotlight cutoff. Explain why this is empirical rather than metallic PBR.
5. **Skinning:** write sum(w*globalBone*inverseBind*p); explain weights, rest pose,
   local TRS interpolation, slerp and why animations are in-place.
6. **CCTV:** draw the color/depth FBO, second camera and monitor texture. Explain the
   self-screen exclusion and the difference between linear rendering and display encoding.
7. **Fixed update:** explain why 240 Hz substeps reduce tunneling, why short E/R edges must
   survive until the next substep, and why this is not general continuous collision detection.
8. **Resource lifetime:** locate destructors for shaders, meshes, targets and textures;
   explain why static instance buffers upload once and the GL context must outlive deletion.

## Practical rehearsal

- Start the packaged executable, use Begin, mouse look, WASD, both crouch bindings and Esc.
- Toggle the lamp, switch the monitor view, intentionally touch a beam, press R.
- Complete the six-beam route and open the safe. Stay crouched at the last beam.
- Open `game.cpp`, `surface.vert`, `surface.frag` and `renderer.cpp` when explaining evidence.
- Run all CTest checks. Change a beam angle in a private working copy and predict collision.
- Inspect thief.blend, the five action names, T-pose, knees and face; explain the native export.
- Discuss the 18 scientific papers by method and tradeoff, not just by title.

## Honest answers to likely questions

**Why no GLB runtime parser?** The brief explicitly permits a documented original exporter
to avoid an extra course dependency. Both native assets and verified exchange GLBs ship.
**Why 1000+ FPS?** This compact scene is uncapped on an RTX 5060. Reported samples measure
the whole frame loop, not display refresh or isolated GPU time. This says nothing certain
about an unknown TA machine; rerun at 1280x720 there.
**Are spotlights fully volumetric?** No. Surface spot lighting is real; additive cone meshes
visualize the beam. Only the moon casts a PCF shadow map.
**What still needs external verification?** Native manual input/usability, TA hardware,
exact starter compatibility, understanding and live delivery. No automated grade is claimed.
**Why no AI Use Note?** The supplied brief supersedes that legacy PDF requirement. Ordinary
source, paper and license attribution remains in CREDITS and the report.

## Submission preparation

Keep the public repository link and final v1.0 tag, PDF report, slides and captioned video
ready. The old PDF says submission is due three days before the final exam, but no exam
schedule was supplied. Do not invent a deadline, claim an upload or send Teams/Moodle
messages automatically. Access invitations and final submission remain human actions.

## Short answers tied to actual functions

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

## Write-on-request exercises and expected core

1. **Point versus AABB:** given local q and half extent h, return abs(q.x)<=h.x &&
   abs(q.y)<=h.y && abs(q.z)<=h.z. Include boundary points and an outside test.
2. **Oriented box:** first calculate q=vec3(inverse(M)*vec4(worldPoint,1)). Explain why
   the visible beam's M must also drive this query. Compare pointInBox's epsilon.
3. **Time-driven laser:** reproduce Game::updateLasers' first height,
   h=2.35+0.55*sin(0.65*t), then compose translate(pivot)*rotateZ(angle)*translate(halfLength).
   Predict the height at t=0 and why using frame count would make speed frame-dependent.
4. **Parent-child:** write worldChild=worldParent*T*R*S; put the safe door pivot at its
   hinge and attach wheel/bolts below it. Explain which transforms are local.
5. **Lighting fragment:** normalize N,L,V; H=normalize(L+V); diffuse=max(dot(N,L),0);
   specular=pow(max(dot(N,H),0),shininess) only on the lit side. Multiply by light color
   and 1/(1+0.20*d+0.095*d*d). Locate the matching implementation in surface.frag.
6. **Switching light:** reproduce Game::interact's lamp branch (lamp=!lamp), then explain
   how updateWorld maps the state to emitted radiance rather than only changing UI text.

These are rehearsal prompts and expected reasoning, not a record of a completed oral exam.

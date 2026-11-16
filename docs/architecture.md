# Architecture and mathematical choices

`main.cpp` owns GLFW, input collection and the frame loop. `Game` in game.cpp advances
rules at 240 Hz using FixedStep (fixed_step.hpp). `world.cpp` applies game values to scene
nodes and animation selection. `Scene` loads manifests, composes parent transforms and
builds static instance groups. `graphics.cpp` owns Shader/Mesh/Texture/FBO operations;
`renderer.cpp` schedules shadow, CCTV, main HDR and post passes. `Animator` interpolates
sampled bone TRS, blends clips and uploads a skin palette. `ui.cpp` owns ImGui views.
`Director` and `RouteFollower` are deterministic QA controllers; neither changes positions
by teleport nor disables Game collision. `Recorder` captures real rendered frames.

```
GLFW input -> retained input edges -> fixed 1/240 s Game updates -> world/Animator
                                      |                         |
                                      +---- UI state -----------+
Assets -> Scene hierarchy -> static instance batches + dynamic transforms
         -> moon depth pass -> CCTV color/depth -> main HDR -> tone/glow -> UI -> present
```

## Point versus rotating laser box

For beam model matrix M and body sample p, q=inverse(M)*vec4(p,1).
Contact iff abs(q.x)<=halfExtent.x+padding.x and likewise y,z. Beam models contain
translation/rotation, with size kept in half extents. Body samples span y=0.12 to
bodyHeight in 0.08 m intervals plus the exact top, padding=(0.16,0.055,0.16) m.
This is a conservative finite body approximation built from the required point/box test.
A rotated world AABB is not used. The rendering and collision model matrices are shared.
Substeps reduce tunneling; this is not a continuous collision solver for arbitrary speed.

## Transform and skinning equations

M_world = M_parent * T * R * S. p_clip = P * V * M_world * p.
N = transpose(inverse(mat3(M_world))); normalize(N*n) after transformation.
Skin vertex p' = sum_i w_i * G_i(t) * inverseBind_i * p, sum_i w_i=1.
Local translations/scales lerp; normalized quaternions slerp; parent transforms compose
in order. Character root/world motion belongs to the controller, not in-place clips.

## Lighting and framebuffer

L = k_a*C + sum_l attenuation_l * spotlight_l * visibility_l *
(k_d*C*max(dot(N,Ldir),0) + k_s*pow(max(dot(N,H),0),shininess)),
where H=normalize(Ldir+Vdir). Emission is added independently.
The moon has a 2048x2048 depth shadow map with 3x3 PCF and bias. Other lights are unshadowed.
Spotlight factors interpolate inner/outer cone cosines. Cone meshes are additive visible
approximations, not physically integrated volumetric scattering.

CCTV uses a 640x360 color/depth FBO and excludes its own screen to avoid read/write
feedback. Its scene camera differs from the first-person camera and includes the thief.
The physical monitor samples linear color before the main HDR post pass. The enlarged
demo monitor uses a separately tone-mapped display texture, avoiding a dark linear image
in ImGui. Surface textures decode from sRGB; lighting is linear, final gamma is explicit.
Static matrices and textures upload once; dynamic uniforms and skin palettes update per frame.

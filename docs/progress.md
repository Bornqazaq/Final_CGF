# Implementation history

## Graphics foundation

- C++17 / OpenGL 3.3 Core application with separate GLSL programs.
- Indexed geometry, scene hierarchy, UV textures and per-fragment lighting.
- Live CCTV framebuffer, directional shadows and HDR display conversion.

## Gameplay and character

- Six animated laser barriers, sampled oriented contact and alarm/retry states.
- Imported character with twelve runtime clips and distance-driven skinning.
- First- and third-person cameras with obstacle-aware positioning.
- Hierarchical safe opening and a complete one-shot dance finale.

## Visual and input corrections

- Native Windows mouse events consumed once per frame.
- Depth-aware laser glow and separated inner-door bolt surfaces.
- Extended safe approach and relocated decorations.
- Enclosed entrance corridor with a visible locked gate and matching collision.
- Monitor-aware frame pacing, custom FPS limits and persistent settings.

The current implementation is described in README.md and the project report.

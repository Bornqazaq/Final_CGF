# Assets and coordinate conventions

The application reads prepared mesh, scene and animation files. Blender is used
for editing models and animation; the executable creates its own GPU buffers and
evaluates cameras, transforms, lights, skinning and draw passes in C++ and GLSL.

## Source assets

- `art/blender/vault.blend`: environment geometry and articulated safe.
- `art/blender/animated_thief.blend`: current character, rig and animation actions.
- `art/source/animated_thief/`: original FBX and texture package.
- `assets/exchange/`: GLB exchange copies.

## Runtime assets

- `assets/vault.scene`: environment materials, indexed meshes and node hierarchy.
- `assets/thief.scene`: character mesh and material declarations.
- `assets/thief.lvanim`: skeleton, inverse binds and twelve sampled animation clips.
- `assets/meshes/`: native LVHM indexed geometry.
- `assets/textures/`: environment maps and the character base-color map.

One unit is one metre. Blender coordinates `(x, y, z)` become `(x, z, -y)` in the
right-handed Y-up runtime. Vertices are converted once; local transforms and
inverse binds use the same basis change. The character faces +Z in bind pose.
Scene transforms compose as `world = parentWorld * local`.

Each character vertex retains at most four normalized joint influences. Unweighted
terminal markers are omitted from the runtime palette. The source rig has 66
bones, with 52 weighted bones in the exported character. Animation is stored as
local translation, quaternion and scale samples; locomotion displacement belongs
to the game controller.

The material shader uses base color and Blinn-Phong parameters. Source normal,
metallic and roughness maps remain in the editable asset package; they are not
sampled by the current surface shader. Native file layouts are specified in
[runtime-formats.md](runtime-formats.md). Character clip derivation is described
in [animated-thief-integration.md](animated-thief-integration.md).

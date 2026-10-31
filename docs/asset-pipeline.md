# Asset pipeline

The saved Blender scripts are executed in Blender. Runtime remains C++/OpenGL
and has no dependency on Blender, Meshy, Mixamo or a network connection.

Current editable sources: art/blender/vault.blend and animated_thief.blend. The earlier
procedural thief.blend and build_thief.py remain as historical source assets.

1. Preserve the supplied FBX and textures in art/source/animated_thief.
2. In Blender execute tools/blender/import_animated_thief.py with its real __file__ path.
   It uses the native wm.fbx_import operator, fixes source texture paths, retains seven
   supplied actions, bakes eight derived/adjusted actions and exports the 52-bone weighted subset.
3. Execute build_room.py for the 15 m room. It calls export_scene.py for vault.scene.
4. Execute export_exchange.py while both current scenes are loaded. It exports the
   vault GLB and delegates the character to export_animated_exchange.py, which retains
   exactly twelve named animation clips and compacts their referenced buffers.
5. Build and run CTest. The game loads thief.scene/thief.lvanim and vault.scene.

Meshes use LVHM, sampled local TRS clips use LVHA. The character front is +Z, up is Y,
units are metres. Four influences per vertex are normalized after reduction. Bone
matrices include the imported FBX bind transforms; the importer strips unweighted
terminal markers from the runtime palette. Source rigs retain all 66 bones.

The baked base-color texture and runtime Blinn-Phong shader preserve the supplied
appearance. The original roughness, metallic and normal maps remain packed in the
Blender source; the OpenGL material uses the existing engine's supported parameters.

Forward crouching samples the backward source cycle in reverse. Directional selection
uses actual displacement relative to the camera, and gait phase follows distance.
The non-looping dance clamps to its last frame. See animated-thief-integration.md,
evidence/animated-thief-import.json and evidence/safe-door-clearance.json.

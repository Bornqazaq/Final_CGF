# Implementation progress

## Plan

1. Read source requirements, inspect Blender, prepare the C++17 toolchain, record evidence matrix.
2. Build and run the OpenGL core application, camera, laser collision, alarm and retry.
3. Create the reference-based room in Blender, export and compare its appearance in the game.
4. Complete safe hierarchy, rotating spotlights, lighting, CCTV and three interactions.
5. Create and rig the thief, author five animation clips and implement GPU skinning.
6. Validate gameplay, clean builds, visual quality and measured performance.
7. Produce the report, slides, defense guide, 1080p gameplay video and delivery archive.
8. Publish the authorized public repository; tag v1.0 only after required local work is complete.

## Verified environment

Windows x64; Intel Core i5-13400F; NVIDIA GeForce RTX 5060; approximately 32 GiB RAM.
Blender 5.2.3 LTS is used for asset import, editing and export.

## External facts still unavailable

Course starter/build setup; TA hardware and OS; defense date and TA repository account. These are not grounds to invent results or block independent development.


## Completed implementation checkpoints

1. Working OpenGL greybox and collision/state tests, recorded in the first real Git commit.
2. Original Blender vault, humanoid rig and asset exports, recorded in the next real commit.
3. Final skinning/pose fixes, input-edge handling, CCTV color conversion, legal demo route,
   safe sequence, UI and real-time capture. Clean Release build and three suites pass.
4. Three uncapped local benchmark runs, real 1080p demo, 18-source research audit,
   26-page report and 10-slide editable presentation with 8:40 notes.
5. Portable release and full source/deliverable package, followed by final v1.0 publication.

These are actual development stages, not fabricated week-7/8/9 course attendance.
The requirement matrix preserves all remaining human and TA checks explicitly.

## Fresh-clone and portable checks

The runtime was also rebuilt from a fresh local clone of the committed implementation,
then all three suites passed again. The portable archive was extracted into a Unicode
path and run from Downloads without --root: start-menu rendering and a 40-second legal
route loop completed without GL errors. Two safe-opening cycles were observed. The
benchmark loop resets on the next simulation step, so its coarse trace need not retain
a Victory row; the separate final demo does retain the Victory state.

## Current character and finale integration

- Received the user's AnimatedThief FBX and textures from tmp/AnimatedThief. The input
  is preserved under art/source/animated_thief. The Meshy-exported file supplies the
  model, Mixamo-named skeleton and seven motions; service authorship of individual
  motions is not inferred solely from bone names.
- Imported through the native Blender FBX operator using Python. Current model: 30,725
  triangles, 52 weighted bones plus ancestors, twelve runtime clips. Derived forward
  crouching reverses the supplied backward cycle. Editable derived actions are saved.
- Walk, backward walk, four crouch directions, crouch/standing idle, reach and both
  dances are exported. FunnyDancing_02 is used in the finale at its full 7.5 s duration.
- Room extended from 12 to 15 m at the safe end. Full door sweep sampled at 51 angles:
  minimum gap to the last laser is 1.700 m. Collision bounds, safe target and route match.
- Safe opening runs 3.4 s; performer then appears and dances once for 7.5 s. Victory
  appears after the final frame. Movement locks; pause and retry work.
- Retargeted crouch lowers the pelvis 0.14 m with two-bone leg IK. All-frame runtime skinning bounds: hood <=1.287 m, sole >=0.001 m; see evidence/animation-validation.log.
- All six CTest suites pass. Character and full finale rendered in OpenGL without GL
  errors; trace confirms victory at safe_time 10.9 s and a held final frame.
- See docs/animated-thief-integration.md and evidence/animated-thief-import.json.
- Broader location art remains deferred. Report/PDF, slides and old recorded demo
  still describe the previous release; refresh them after the user's location work,
  accurately crediting the user-supplied model/animations and these derived clips.

## First/third-person cameras

- V switches once per press during gameplay. First person is the initial view. Third person shows the full character, follows crouching and uses a shoulder boom.
- The boom contracts before walls, ceiling beams, doorway frames, timber posts and furniture; the model hides if a contracted boom approaches the head. Camera choice persists through retry.
- Interactions and route aiming use the player eye position, so camera distance does not change reach or movement. The safe/dance cinematic retains its authored camera.
- All six CTest suites pass, including obstruction cases and a complete third-person route. Both views rendered in OpenGL without GL errors; control hints and README include V.

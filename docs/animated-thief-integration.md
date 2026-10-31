# Animated thief integration

The user supplied the Meshy character and merged animation FBX in tmp/AnimatedThief.
The preserved input is art/source/animated_thief; its source textures and FBX are unchanged.
The file contains a Mixamo-named skeleton and seven supplied animation actions. The bone names alone do
not establish which service originally authored every motion. The seven supplied
motions are preserved separately from the derived runtime clips.

## Runtime character

- 30,725 triangles, 52 weighted bones plus ancestors, at most four normalized influences.
- One baked base-color texture in assets/textures/thief_meshy_basecolor.png.
- Native mesh/animation export: assets/thief.scene, assets/meshes/thief_meshy.lvhm,
  assets/thief.lvanim. Y up, metres, front +Z. Original stature is retained.
- Editable Blender source: art/blender/animated_thief.blend.
- Rebuild in Blender with tools/blender/import_animated_thief.py.
- Source clips are retained. Walking/Running feed Walk/Run. The three supplied crouch
  directions feed CrouchBackward, CrouchLeft and CrouchRight.
- CrouchWalk (forward) samples the backward cycle in reverse. WalkBackward similarly
  reverses Walking. Root travel is removed while natural cyclic sway is retained.
- Idle and CrouchIdle average opposite gait phases and add subtle breathing. Interact
  adds a short right-arm reach. Derived actions are baked in Blender for editing. Crouch pelvis motion is lowered by 0.14 m; two-bone leg IK preserves limb lengths and sole contact. The source actions remain unchanged.
- Normal walking uses Walking. Crouching selects forward/back/left/right from actual
  movement relative to the camera. Locomotion phase follows distance travelled.
- All twelve clips and exact source durations are listed in evidence/animated-thief-import.json.

## Vault clearance and finale

Room length increased from 12 to 15 metres by extending the safe end. The six lasers,
desk and hazard route retain their positions. The safe, back wall, rear lights and
rear plants move back 3 metres; floor, walls, beams and collider bounds match.
The door's full 0вЂ“100 degree sweep has a measured minimum 1.700 m clearance from
the last laser (51 sampled angles, conservative transformed mesh bounds).
See evidence/safe-door-clearance.json. Safe interaction and the automated route move too.

Opening the safe starts State::Finale and locks movement/interactions. The wheel,
bolts and door complete their 3.4-second opening. The performer appears after the
door clears the stage. FunnyDancing_02 (runtime Dance) then plays exactly once
for its supplied 7.5 seconds against the open safe. The victory screen appears
after the final dance frame and the pose holds. Pause freezes the sequence;
retry resets it while preserving the duration read from the actual animation file.
Cherish_Pop_Dance is also retained as DanceLong for preview.

The camera uses a staged view inside the cleared zone. The performer stays outside
the open door. --finale-preview starts this same sequence for visual review;
--character-preview --clip CrouchWalk reviews any named clip.

## Verification and next work

CTest covers the legal route, alarm/retry, slow frames, moved safe, input lock,
pause, full dance timing, final-frame hold and imported animation integrity.
The actual OpenGL renderer was used for the character and finale screenshots. Runtime skinning checks all vertices in every crouch frame: maximum hood height 1.287 m, minimum sole height 0.001 m; see evidence/animation-validation.log.
Broader location art changes remain deferred until the user resumes that work.
Existing PDFs/slides/demo represent the earlier release and must be refreshed after
the remaining location work; they are not evidence for this new model or finale.

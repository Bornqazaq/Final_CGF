# Character and animation

The character has 30,725 triangles, 52 weighted bones and at most four normalized
influences per vertex. The source rig and seven imported motion actions are
preserved in `art/source/animated_thief/` and `art/blender/animated_thief.blend`.
Asset provenance is recorded in [CREDITS.md](../CREDITS.md).

## Clip mapping

| Runtime clip | Source or adjustment |
|---|---|
| Walk / Run | Walking / Running |
| WalkBackward | Walking sampled in reverse |
| CrouchBackward / CrouchLeft / CrouchRight | Corresponding directional crouch actions |
| CrouchWalk | Backward crouch cycle sampled in reverse |
| Idle / CrouchIdle | Opposing gait phases combined into a resting pose |
| Interact | Derived pose with an arm reach |
| Dance | FunnyDancing_02, 7.5 seconds, non-looping |
| DanceLong | Cherish_Pop_Dance, retained for preview |

Crouch poses lower the pelvis by 0.14 m; a two-bone leg adjustment preserves limb
lengths and foot contact. The maximum tested crouch height is approximately
1.287 m, below the 1.33 m collision proxy. The standing proxy is 1.78 m; eye heights
are 1.57 m standing and 1.22 m crouched. Locomotion phase follows travelled distance.
Exact clip durations are in `evidence/animated-thief-import.json`.

## Safe and finale

The 15 m room provides at least 1.70 m clearance between the door's full sweep and
the last beam. Opening the safe enters `State::Finale` and locks movement and
interactions. Wheel rotation, bolt retraction and door rotation take 3.4 seconds.
The character then plays the 7.5-second Dance clip once. Victory begins after the
entire 10.9-second sequence and the last pose holds. Pause freezes the sequence;
retry resets it.

`--character-preview --clip CrouchWalk` displays the character and selected clip.
`--finale-preview` starts the same finale used during normal play. Regression tests
check animation weights and bounds, complete duration, pause, input locking and
retry behavior.

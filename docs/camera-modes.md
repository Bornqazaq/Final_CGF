# Player camera modes

V toggles first/third person once per key press in Playing state. A new run defaults
to first person; retry preserves the chosen view. Menu, pause and cinematic states
do not toggle. --third-person starts that mode for visual verification.

The third-person camera sits 2.8 m behind the eye anchor with a 0.38 m shoulder
offset and 0.22 m elevation. It targets six metres ahead of the eye. Mouse pitch
is limited to +/-60 degrees in this mode. First-person pitch remains +/-85 degrees.
Crouching updates the shared eye anchor. WASD movement uses the horizontal camera
direction. In first person the character follows mouse yaw. In third person mouse
movement only orbits the camera; the body retains its heading at rest. Standing
movement turns the body toward actual displacement and plays Walk in every direction,
including A/D and S. Crouching retains body heading and selects the supplied forward,
backward or side cycle relative to that heading. Switching back to first person aligns
the body with the current view.

The camera sweeps the boom in <=0.025 m steps against 3D obstacle proxies padded
by 0.18 m. It covers room walls/ceiling, the open entrance frame, timber posts,
safe, cabinet, desk, chair, side table and plants. When boom length contracts below
0.65 m, the model is hidden in the main view to avoid seeing inside the hood.
CCTV and shadow rendering still use the character normally.

Interaction reach and bot look-at use eyePosition(), independent of camera().
The safe/dance sequence overrides both player camera modes, and V cannot interrupt
it. Existing pause, retry and the final one-shot dance remain intact.

tests/camera_tests.cpp checks both modes, wall/post/cabinet obstruction, passage
over the desk, interaction reach, pitch limits, view persistence, movement equality
and a complete third-person route through to victory. The two actual render
screenshots are evidence/screenshots/first-person.png and third-person.png.
Update these camera obstacle proxies together with gameplay collision when the
location layout is redesigned.

Windows mouse look consumes native WM_INPUT motion once per frame. Absolute-motion devices keep separate per-device baselines. Other platforms use GLFW raw motion where supported. Default sensitivity is 0.020 degrees per input unit; menu and pause provide a slider. Retry preserves the setting. Focus and capture changes reset pending motion. Input deltas and applied angles are recorded locally in evidence/mouse-input.csv. Obstacle avoidance changes camera distance without changing look direction.

Sensitivity is displayed as a multiplier from 0.10 to 10.00, using 0.022 degrees per count per unit (Source-style yaw/pitch scaling). The existing 0.020 degrees/count default remains unchanged and displays as 0.91. Reference: https://github.com/ValveSoftware/source-sdk-2013/blob/master/src/game/client/in_mouse.cpp

# Player camera modes

V toggles first/third person once per key press in Playing state. A new run defaults
to first person; retry preserves the chosen view. Menu, pause and cinematic states
do not toggle. --third-person starts that mode for visual verification.

The third-person camera sits 2.8 m behind the eye anchor with a 0.38 m shoulder
offset and 0.22 m elevation. It targets six metres ahead of the eye. Mouse pitch
is limited to +/-60 degrees in this mode. First-person pitch remains +/-85 degrees.
Crouching updates the shared eye anchor. Movement uses the horizontal player facing.

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

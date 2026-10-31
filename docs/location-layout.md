# Vault and entrance layout

The entrance now leads into an enclosed vestibule and an illuminated archive corridor.
A barred security gate at world Z = 2.65 m, with a visible padlock and lockdown sign,
closes the exit. Player centres stop at Z = 2.35 m and the camera at Z = 2.40 m,
allowing for body/camera clearance. The vestibule side walls constrain both views.

The two paintings occupy wall bays at room depths 1.65 m and 10.8 m. The deposit
cabinet is behind the final laser, centred at depth 11.5 m, with four columns of
drawers. The right forward sconce is at depth 3.6 m. These placements keep decorative
pieces clear of emitter rails and mounts. The central laser route is unchanged.

Teal lower wall panels, timber mouldings, brass trim, tiled corridor flooring, a
runner, paired wall lamps and the distant archive door complete the entrance view.
Corridor illumination is evaluated by the OpenGL surface shader using two additional
point lights; the shader supports up to twelve local lights.

Verification includes actual rendered entrance/room screenshots, evaluated Blender
bounds for decoration versus security hardware, both camera modes, physical gate
collision, the complete gameplay route, and the safe-opening/dance finale.
Use `--entrance-preview` for a repeatable entrance inspection.

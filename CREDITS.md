# Credits and licenses

Student: Nurbek Yerbulekov  
Group: SE-2428  
Course: Computer Graphics Fundamentals

This brief is a single-author teaching example. There are no invented collaborators.
The room, furniture and original procedural textures were created for this project
with the checked-in Blender/Python scripts. The current thief replaces the earlier
procedural character with the user's Meshy-exported model, textures, skeleton and
seven supplied motions (preserved in art/source/animated_thief). The input skeleton
uses Mixamo bone names; this alone does not establish where each motion was authored.
The integration scripts import these resources through Blender, derive the
missing forward crouch cycle, backward walk, idle poses and reach, and export twelve
runtime clips. The supplied model and motions retain their external provenance. No guard NPC or extracted game asset is used. Source provenance and
the exact derived motions are recorded in docs/animated-thief-integration.md.
The two user-supplied concept images guided the silhouette, palette and room composition;
they remain with the original local brief, and are not claimed as original project art
or redistributed in the public repository. Just Another Night Shift is a style reference,
not a source of meshes, maps, interface artwork or code.

| Component | Pinned source | Use | License |
|---|---|---|---|
| GLFW | 3.4, github.com/glfw/glfw | Window/context/input | zlib/libpng |
| GLM | 1.0.1, github.com/g-truc/glm | Vectors, matrices, quaternions | MIT, chosen from upstream options |
| Dear ImGui | 1.91.9b, github.com/ocornut/imgui | Menus, controls and FPS overlay | MIT |
| stb_image / stb_image_write | 003501f6d7a8668ce8b6d875e34dd97ad0d5d5b5, github.com/nothings/stb | PNG decode/capture | MIT, chosen from upstream options |
| GLAD | glad2 2.0.8, github.com/Dav1dde/glad | Generated OpenGL loading declarations | CC0 generated code; Apache-2.0 registry; MIT generator |
| Karla | Jonathan Pinhorn, Google Fonts ofl/karla | English UI font | SIL Open Font License 1.1 |
| Filmic fit | Krzysztof Narkowicz, 2016 | Five tone-mapping coefficients and rational expression | CC0 option offered by author |

License copies are in `LICENSES/`; upstream embedded notices remain in the vendor files.
The tone-mapping source is https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/ .
The surrounding shaders, glow pass and scene lighting are project code. No tutorial
renderer or LearnOpenGL source snippets are included. Scientific comparisons and their
DOIs are in `docs/references-verified.json` and the report; cited alternative algorithms
are not represented as implemented features.

Blender, CMake, Ninja, LLVM-MinGW, Python, LibreOffice and FFmpeg are development/document
or recording tools, not redistributed runtime dependencies. The demo has captions and no
music or third-party audio. Game sound is optional in the brief and is not implemented.

Original project source/art has no additional public license grant in this repository;
public visibility alone is not a license. The third-party licenses above govern their
respective components independently.

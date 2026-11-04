# Credits and licenses

Students: Nurbek Yerbulekov, Makhmet Demesh, Nurassyl Nygmet<br>
Group: SE-2428
Course: Computer Graphics Fundamentals

The room, corridor, furniture and environment textures were prepared for this
project in Blender. The current thief originates from a Meshy character package;
animation preparation used Mixamo. The original FBX, textures, skeleton and seven
motion actions are retained in `art/source/animated_thief/`. Runtime integration
includes forward crouch, backward walk, idle and reach derivations, producing twelve
clips; their mapping is described in `docs/animated-thief-integration.md`.

The character package was supplied by Nurbek Yerbulekov. Its service-specific usage
rights remain applicable; this repository does not add a separate redistribution
license to that package. Service information: https://www.meshy.ai/ and
https://www.mixamo.com/ .

Just Another Night Shift informed the visual style. No meshes, maps, interface
artwork or source code were extracted from that game. Reference images and course
documents are not redistributed in this repository.

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

Blender, CMake, Ninja, LLVM-MinGW and FFmpeg are authoring, build or recording
tools rather than runtime libraries. No music or third-party audio is included.

Original project source/art has no additional public license grant in this repository;
public visibility alone is not a license. The third-party licenses above govern their
respective components independently.

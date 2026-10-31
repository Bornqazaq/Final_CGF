# Native runtime formats

The brief permits an original exporter in place of a new GLB parser dependency.
GLB remains a verified exchange resource in `assets/exchange`; the game reads the following
uncompressed, documented formats directly and creates its own GPU buffers.
All binary integers/floats are little-endian, u32/i32 and IEEE-754 f32.

## LVHM version 1

Header: ASCII `LVHM`, u32 version=1, u32 vertexCount, u32 indexCount.
Then vertexCount records of 16 floats (64 bytes): position xyz, normal xyz, UV uv,
four normalized weights, four joint indices stored as floats. Then indexCount u32
indices. Static vertices have zero weights; the static shader path does not skin them.
The importer rejects bad headers, oversized counts, truncation and out-of-range indices.

## LVHA version 1

Header: ASCII `LVHA`, u32 version=1, u32 boneCount, u32 clipCount.
Each bone: u32 UTF-8 byte length + name bytes, i32 parent (-1 for root), 16 floats inverse
bind matrix in column-major order. Parents precede children. Each clip: length-prefixed
name, f32 durationSeconds, u32 frameCount, followed by frame-major then bone-major TRS
samples: translation xyz, quaternion xyzw, scale xyz (10 floats). Samples include both
loop endpoints. Playback maps time to neighboring samples; translation/scale use linear
interpolation and rotation uses quaternion slerp. Crossfades last 0.2 s.

## Text scene version 1

Quoted strings use JSON-compatible quotes without escaped path separators. Empty lines
and lines beginning # are comments. Records:

```
material "name" r g b specular shininess emission "texture-path-or--"
mesh "name" "mesh-path"
node "name" parent mesh material flags m00 m10 m20 m30 ... m33
```

Indices refer to earlier material/mesh declarations. Node matrices are column-major.
parent=-1 means a root; mesh=-1 means a transform-only node. Bit flags: 1 dynamic,
2 CCTV screen, 4 skinned character. Dynamic ancestry propagates to children at export;
those nodes are excluded from static instance batches. Manifest paths are relative to
`assets/`. Multiple manifests append with corrected indices.

## Coordinates and hierarchy

One unit is one metre. Blender (x,y,z) maps to runtime (x,z,-y), a right-handed Y-up
system. The conversion matrix C is applied once to vertices; transforms use C*M*C^-1.
Inverse binds use the same conjugation. Runtime world=parentWorld*local; clip=P*V*M*p.
The first-person camera faces -Z at yaw=-90 degrees. The character bind origin is on
the floor. Do not apply the coordinate conversion again when reading native assets.

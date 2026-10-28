# Sci-fi Supercomputer

Sci-fi Supercomputer — Jungle Jim (@jungle_jim), CC BY 4.0.
https://sketchfab.com/3d-models/sci-fi-supercomputer-9464e880c35e4fd29c0cdb6fefe5ebba
https://creativecommons.org/licenses/by/4.0/
Adapted for Kolonia: scaled, rear cabinet faces restored and mapped to metal backing, textures resized to 2K,
normal vectors renormalized, ARM maps packed, emission maps combined, and OBJ converted.
Original work is not endorsed by its creator.

`supercomputer.blend` is the converted editable source with packed 2K materials.
`computer-collision.json` stores the eight local convex collision pieces.
Model coordinates use Z up, with floor at local Z=-64; current map origins are Z=64.
The model is uniformly scaled to about 181 units wide, 48 deep and 89 high.
The OBJ export uses engine-axis conversion (X, Z, -Y), and standard authored OBJ UVs.
Materials retain the artist’s normal, roughness, metallic and emission detail.
No height maps or parallax/relief mapping are used.

Cleanup correction: the cabinet rear faces are retained. Their edges are shared
with the cabinet trim, which legitimately produces four edge-valence-three
seams when the imported object is welded. There are no open boundary edges.
Do not delete these visible panels on the basis of edge valence alone.
The rear UVs now use `jj_cabinet_back`: an opaque crop of the artist's casing
color/normal/physical maps. The unused black rear-atlas rectangle is not used.
The converted source has 542 triangles; model dimensions are unchanged.

The rear backing maps are 512 by 1024 crops of the original casing maps.
After moving computer instances, save the map and run from the package root:

    python3 tools/rebuild_supercomputer_collision.py

Then reload the map in NetRadiant. This replaces only generated computer
collision, using eight fitted common/fullclip pieces per instance. The cleanup
retains all four current placements and generates 32 hulls.

Material tuning (2026-10-27): the three computer materials use normal strength
0.35 and ORM roughness >= 115/255. This avoids the original mirror-zero-roughness
metal patches and reduces the exaggerated casing bumps. Base colors, metalness,
screens and emission are retained. The source Blender materials match.
See ../texture-audit/ for the audit and compiled-normal comparison.

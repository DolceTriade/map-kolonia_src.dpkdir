# Cave passage cleanup

Seven low-poly, closed rock linings replace the marked flat connecting passages.
The Impact Chamber–Alien Nursery route uses four tangent 160-unit-radius arcs,
with 256-unit floor clearance and 64-unit straight portal leads. Its middle
cross-section lies below y=-192, blocking every direct ray between the two
portals (both span y=-128..128). Room footprints and other routes are preserved.

`passages.blend` is the editable scene. Planar faces are retained as quads;
nonplanar curved faces remain triangulated. Hidden model backs use common/caulk.
The map uses common/fullclip for collision and local structural caulk enclosures.
Mounted fungal brackets emit area light from below the sloped overhangs.

Rebuild art and fitted collision data with Blender (no extra Python packages):

    blender --background --factory-startup --python tools/build_cave_passages.py

`passage-plan.json` records the portal geometry, origins and corridor footprints.
`room-footprints.json` and `floor-boundaries.json` preserve the surrounding room
and terrain references. Generated reports and collision planes go into ignored
`build/`. Rebuilding art does not automatically replace the corresponding map
brushes; update the passage_collision group when changing the shape.

Visible brush floors/ceilings use coherent world projections at a 0.5 reference
scale for the 2K materials. Passage wall UVs follow continuous perimeter length.
Only truly coplanar floor triangles were combined into quads. Rebuild lighting
and navigation after changing the map's geometry.

The floor skin sits 0.25 units above structural backing. Exported V is negated
to compensate for Pico and keep floor UVs aligned across brushes and models.
Collar UVs are fitted locally; Solidify rims are mapped with nonzero UV area.
Only distorted nonplanar quads are triangulated for local UV repair; truly
planar quads remain quads. Zero-area tessellation triangles are not exported.

Eight axial common/hint partitions, with common/hintskip on remaining faces,
keep valid visibility clusters throughout the caulk-lined S passage. They are
invisible and nonsolid in game. Preserve these when moving the passage.
Exposed portal header faces use rock; hidden/external faces remain caulk.

Validation: verbose BSP build with no leaks or degenerate T-junction edges;
coherent floor UV phase; valid interior clusters throughout seven passages;
and connected human-sized and large-alien-sized clearance tests. A direct
lighting test confirmed illumination below the new overhangs. Diagnostic
bakes remain outside the source package. Rebuild lighting and navigation for
in-game review after geometry changes.

The retained narrow wet_moss bands in four organic room linings are also
world-projected at the 0.5 reference scale. The cave geometry builder applies
the same correction on regeneration, instead of restoring fitted strip UVs.

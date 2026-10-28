# Cave geometry renewal

Nine cave/exterior lining meshes are reshaped from the original, closed assets.
The original models are retained as authoring inputs. Room openings remain fixed;
walls bow inward between openings and vaults sag into broad, uneven arches.
The rock skins are decimated to 48% of their former triangles. Soft details remain.

Regenerate models and fitted collision support planes with Blender:

    blender --background --factory-startup --python tools/build_cave_geometry.py

Generated models end in `_organic.obj`. The editable scene is `caves.blend`.
Intermediate reports go into ignored `devassets/cave-renewal/build/`.
`rooms.json` records the original model placements. `old-clips.json` records the
identified original lining collision cells. Collision retains their support
plane directions, transformed by an exact local affine approximation, with a one-unit allowance on each world axis. This preserves the original hull topology.
It does not use the dense bevel hulls from the reverted nursery experiment.

The map separately contains low, solid, sloping terrain wedges and shallow rock
folds in uncovered cave corridors. Existing structural brushes continue to seal
all areas. Those terrain wedges use caulk on hidden faces and the visible faces
use a texture scale of 0.5. The cave_terrain group is generated from the union of
original floor areas to avoid duplicate skins where structural brushes overlap.

Current Coast Sand Rocks 02 remains the main surface. Rock Wall 10 supplies
selected tilted fracture bands, and Aerial Rocks 01 adds ground/moss variation.
The CC0 maps are retained at 2K. The cave_ground material uses the original cavern floor from before the Coast Sand Rocks replacement: wet_rock_d, strata_n and wet_rock_p. The original maps are 2K, retaining the existing 0.5 reference scale. The former Aerial Rocks ground derivative remains as unused authoring data. The aerial wall albedo is darkened to match the cave palette. names ending `_n` are OpenGL normals
and `_p` holds AO, roughness and metallic in RGB. The package script uses DXN
for normal maps. New model shaders preserve authored normals without compiler
nonplanar smoothing. Rebuild BSP/visibility/lighting after geometry changes.

Sparse remaining skin edges are backed by simple five-plane fullclip prisms in the `cave_collision_edges` group. Source aerial diffuse is stored under `source-textures/` so the unused original is excluded from releases.

The cave floor uses `wet_rock_floor_matte_p.png`, derived from the original
`wet_rock_p.png`: its green roughness channel is `128 + 0.5 * original`
(clamped to 255). Red occlusion and blue metalness are preserved. This affects
only the `cave_ground` material and keeps the original albedo and normal map.

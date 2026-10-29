# Cave cleanup sources

The nine organic room shells keep their original vertex positions, normals and
triangle topology. Rock UVs are unwrapped into coherent islands in Blender, with
physical area normalized to the 0.5 reference density of the 2K materials.
Materials follow the original wall, vault and moss components rather than
per-face color noise. Floors and passage routes have not moved.

`rock-uv.blend` contains the mapped rock skins at their map positions, with PBR
preview materials. Complete base room authoring remains in
`../cave-renewal/caves.blend`. After regenerating base rooms, run:

    blender --background --factory-startup --python tools/unwrap_cave_rock.py

The UV script updates rock-skin UVs in the organic OBJ files without changing
positions, normals, faces or vegetation. Generated reports go into ignored
`build/`. `model-origins.json` positions the authoring objects in the map.

`northern-vault.blend` replaces fourteen intersecting ceiling fragments with a
closed, 46-triangle faceted ceiling across the full northern junction. Its
structural sealing roof remains in the map. The separate common/fullclip hulls
follow the underside; no height/displacement/parallax mapping is used.

Four obsolete high ceiling bevel strips were shortened to sit behind modeled
room walls. Visible caulk at doorway and terrain rims was textured; external
and concealed backing faces retain caulk. Two coplanar northern floor triangles
were combined into one quad without changing the occupied volume.

Computer repair sources are in `../supercomputer/`: the authored cabinet rear
panels are restored, and their unused black atlas region is replaced with an
opaque metal backing cropped from the original casing PBR maps. Other controls,
screens and all four current placements are retained. Stale collision at the old
positions was replaced with 32 fitted common/fullclip hulls.

Diagnostic geometry and lighting builds remain outside the source package.
Rebuild release lighting and navigation before reviewing in game.

Wall normal strength is 1.15 in the cave rock shaders, slightly stronger than
the default. The cave_base, cave_aerial and cave_fracture preview materials in
rock-uv.blend use the same strength. The original images and compiled lighting
remain unchanged. Texture/UV transitions remain a separate issue; see
../texture-audit/README.md.

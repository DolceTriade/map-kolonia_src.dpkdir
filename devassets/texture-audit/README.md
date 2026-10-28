# Texture continuity audit — 2026-10-27

Audited all **33 rendered materials** in the current compiled map: **65 distinct
referenced images**, no missing image references. `material-inventory.json`
records diffuse, normal, physical/specular, glow and editor images, dimensions,
normal conventions and diagnostic image-edge statistics. Source-only and unused
textures are outside the rendered-map audit. Sky cubemap joins are not evaluated
by the shared-triangle-edge test.

## Confirmed continuity problems

1. The nine organic cave meshes have independent UV islands. Each chart was
   rescaled separately in the previous cleanup, so adjacent charts can have
   different phase and orientation even with the same rock image. Removing
   stretch did not make these joins seamless.
2. Moss pockets, wall rock and vault rock use distinct scans with hard material
   boundaries. Matching UV numbers does not make different scans continuous.
3. Brush-to-model openings use separate mappings. Explicit examples include
   the ivory/ivory_planar join at (-896, -672), the east cave wall at
   (2848, -1472) and (2848, -1088), and ground joins near (724, -361) and
   (821, 860). See the 3D edge coordinates in `seam-audit.json`.

The scan found 33,935 same-image candidate UV discontinuities and 7,233
same/similar-plane different-image joins. These are **candidates, not a count of
visible errors**: many occur on mushrooms, signs, controls, props, trim, hard
corners, or concealed geometry. The repeatable tool examines exactly shared BSP
edges; intersecting surfaces and T-junction-only joins need separate inspection.

## Repair approach and remaining work

The global seam correction is **not applied**. The audit identifies real joins;
it does not certify the map as seamless.

* Use the brush thresholds as UV anchors and unwrap each connected rock surface
  together with its doorway/ceiling/floor joins. Share coordinates across actual
  smooth joins; put unavoidable UV cuts on concealed backs or strong creases.
* Blend the three existing rock scans and moss across a transition zone in the
  authoring material. Bake matching color, tangent normal and roughness maps;
  fading color alone leaves a normal/specular seam. Check the atlas resolution
  and package-size cost before producing room atlases.
* Keep deliberate manufactured panel joints, trim and screen atlases separate.
* Verify in neutral directional light, then in the cave's actual colored light.
  Avoid changing geometry or collision while repairing texture coordinates.

This requires coordinated authoring of connected surfaces. Independently
re-projecting each face or re-scaling charts repeats the existing problem.

Repeat the compiled audit from the source package root:

    python3 tools/audit_texture_seams.py --bsp maps/kolonia.bsp --output /tmp/kolonia-texture-audit

The script requires NumPy and changes no source files.

## Computer material correction

The authored OBJ normals match the imported asset at all 1,626 compared corners.
All 2,770 matched compiled vertices also retain those normals. ORM channel
packing is correct: green roughness, blue metalness, linear data. OpenGL normal
format is explicitly declared. There is no evidence of a mesh-normal export
error or swapped ORM channels.

However, large original metal panels have roughness zero and metalness one.
In Daemon's direct-light BRDF, zero roughness removes the broad highlight while
full metalness removes the diffuse contribution; these panels become black
away from a perfect specular direction. The casing normals also produce strong
slopes across otherwise flat panels.

Applied a material tuning: normalScale 0.35 0.35 1 for the three computer shaders,
and a roughness floor of 115/255 (~0.45). Occlusion and metalness channels, base
colors, normal images, controls, glow, geometry, placement and collision are
unchanged. Blender preview materials are synchronized. This is an appearance
adjustment, not a claim that every dark texel in the source art is an error.

The packaging script now uses linear mip filtering for explicitly referenced
physicalMap images. Normal maps retain DXN, gamma 1.0 and vector renormalization.
Color images retain color-gamma filtering. Repackage to update distributed maps.
Material-only changes can be reviewed by reloading the local map; no geometry
or lighting bake was changed by this audit.

Before/after captures use the user's actual engine build with gamma 2 and global
normal scale 0.55, at the same view and with the same baked map. See
[before](computer-before.jpg) and [after](computer-after.jpg). The revised casing
has less exaggerated relief; some dark authored art and unlit sides remain.
This is not a promise that all black shading has been eliminated.

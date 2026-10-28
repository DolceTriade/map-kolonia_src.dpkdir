textures/kolonia/ivory
{
 qer_editorImage textures/kolonia/ship_panel_d
 q3map_nonplanar
 q3map_shadeAngle 1 // Keep flat panels hard; preserve authored model normals.
 {
 diffuseMap textures/kolonia/ship_panel_d
 normalMap textures/kolonia/ship_panel_n
 normalFormat X Y Z
 physicalMap textures/kolonia/ship_panel_p
 }
}

textures/kolonia/metal
{
 qer_editorImage textures/kolonia/alloy_d
 q3map_nonplanar
 q3map_shadeAngle 55
 {
  diffuseMap textures/kolonia/alloy_d
  normalMap textures/kolonia/salvage_n
  normalFormat X Y Z
  physicalMap textures/kolonia/alloy_p
 }
}

textures/kolonia/deck
{
 qer_editorImage textures/kolonia/alloy_d
 q3map_nonplanar
 q3map_shadeAngle 55
 {
  diffuseMap textures/kolonia/alloy_d
  normalMap textures/kolonia/salvage_n
  normalFormat X Y Z
  physicalMap textures/kolonia/alloy_p
 }
}

textures/kolonia/rock
{
 qer_editorImage textures/kolonia/strata_d
 q3map_nonplanar
 q3map_shadeAngle 55
 {
  diffuseMap textures/kolonia/strata_d
  normalMap textures/kolonia/strata_n
  normalFormat X Y Z
  physicalMap textures/kolonia/strata_p


 }
}

textures/kolonia/moss
{
	q3map_nonplanar
 q3map_shadeAngle 60
 qer_editorImage textures/kolonia/moss_d
	{
		diffuseMap textures/kolonia/moss_d
		normalMap textures/kolonia/moss_n
 normalFormat X Y Z
		specularMap textures/kolonia/moss_s
	}
}

textures/kolonia/bio
{
	q3map_nonplanar
 q3map_shadeAngle 60
 qer_editorImage textures/kolonia/bio_d
	q3map_surfaceLight 850
 q3map_lightRGB 0.22 0.65 0.50
	q3map_lightImage textures/kolonia/bio_d
	{
		diffuseMap textures/kolonia/bio_d
		normalMap textures/kolonia/bio_n
 normalFormat X Y Z
		specularMap textures/kolonia/bio_s
		glowMap textures/kolonia/bio_d
	}
}

textures/kolonia/amber
{
 qer_editorImage textures/kolonia/amber_d
 q3map_nonplanar
 q3map_shadeAngle 60
 q3map_surfaceLight 650
 q3map_lightImage textures/kolonia/amber_light
 {
  diffuseMap textures/kolonia/amber_d
  normalMap textures/kolonia/amber_n
  normalFormat X Y Z
  physicalMap textures/kolonia/amber_p
  glowMap textures/kolonia/amber_g
 }
}

textures/kolonia/night
{
	q3map_nonplanar
 q3map_shadeAngle 60
 qer_editorImage textures/kolonia/rock_d
	surfaceparm sky
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_skyLight 30 3
	q3map_lightRGB 0.25 0.35 0.55
	skyparms textures/kolonia/night 512 -
}

textures/kolonia/window
{
 q3map_nonplanar
 q3map_shadeAngle 60
 qer_editorImage textures/kolonia/night_ft
 {
 diffuseMap textures/kolonia/night_ft
 normalMap textures/kolonia/metal_n
 normalFormat X Y Z
 specularMap textures/kolonia/metal_s
 glowMap textures/kolonia/night_ft
 }
}

textures/kolonia/amber_norad
{
 qer_editorImage textures/kolonia/amber_d
 q3map_nonplanar
 q3map_shadeAngle 60
 {
  diffuseMap textures/kolonia/amber_d
  normalMap textures/kolonia/amber_n
  normalFormat X Y Z
  physicalMap textures/kolonia/amber_p
  glowMap textures/kolonia/amber_g
 }
}

textures/kolonia/bio_norad
{
	q3map_nonplanar
 q3map_shadeAngle 60
 qer_editorImage textures/kolonia/bio_d
	{
		diffuseMap textures/kolonia/bio_d
		normalMap textures/kolonia/bio_n
 normalFormat X Y Z
		specularMap textures/kolonia/bio_s
		glowMap textures/kolonia/bio_d
	}
}

textures/kolonia/strata
{
 qer_editorImage textures/kolonia/strata_d
 q3map_nonplanar
 q3map_shadeAngle 55
 {
  diffuseMap textures/kolonia/strata_d
  normalMap textures/kolonia/strata_n
  normalFormat X Y Z
  physicalMap textures/kolonia/strata_p


 }
}

textures/kolonia/salvage
{
 qer_editorImage textures/kolonia/alloy_d
 q3map_nonplanar
 q3map_shadeAngle 55
 {
  diffuseMap textures/kolonia/alloy_d
  normalMap textures/kolonia/salvage_n
  normalFormat X Y Z
  physicalMap textures/kolonia/alloy_p
 }
}

textures/kolonia/cool_light
{
 qer_editorImage textures/kolonia/diffuser_d
 q3map_nonplanar
 q3map_surfaceLight 1050
 q3map_lightSubdivide 32 // Distribute shadow samples along the light strip.
 q3map_lightRGB 0.65 0.82 1
 q3map_lightImage textures/kolonia/diffuser_d
 {
 diffuseMap textures/kolonia/diffuser_d
 normalMap textures/kolonia/diffuser_n
 normalFormat X Y Z
 physicalMap textures/kolonia/diffuser_p
 glowMap textures/kolonia/diffuser_d
 }
}

textures/kolonia/cool_norad
{
 qer_editorImage textures/kolonia/diffuser_d
 q3map_nonplanar
 {
 diffuseMap textures/kolonia/diffuser_d
 normalMap textures/kolonia/diffuser_n
 normalFormat X Y Z
 physicalMap textures/kolonia/diffuser_p
 glowMap textures/kolonia/diffuser_d
 }
}

textures/kolonia/wet_rock
{
 qer_editorImage textures/kolonia/coast_sand_rocks_02_d
 q3map_shadeAngle 1 // Preserve model normals; keep lightmap projection planar.
 {
 diffuseMap textures/kolonia/coast_sand_rocks_02_d
 normalMap textures/kolonia/coast_sand_rocks_02_n
 normalFormat X Y Z
 physicalMap textures/kolonia/coast_sand_rocks_02_p


 }
}

textures/kolonia/wet_moss
{
 qer_editorImage textures/kolonia/coast_sand_rocks_02_d
 q3map_nonplanar
 q3map_shadeAngle 60
 {
 diffuseMap textures/kolonia/coast_sand_rocks_02_d
 normalMap textures/kolonia/coast_sand_rocks_02_n
 normalFormat X Y Z
 physicalMap textures/kolonia/coast_sand_rocks_02_p


 }
}

textures/kolonia/bridge_display
{
 qer_editorImage textures/kolonia/bridge_display_d
 q3map_nonplanar
 q3map_shadeAngle 60
 {
 diffuseMap textures/kolonia/bridge_display_d
 normalMap textures/kolonia/flat_n
 normalFormat X Y Z
 physicalMap textures/kolonia/display_p
 glowMap textures/kolonia/bridge_display_d
 }
}

textures/kolonia/medical_display
{
 qer_editorImage textures/kolonia/medical_display_d
 q3map_nonplanar
 q3map_shadeAngle 60
 {
 diffuseMap textures/kolonia/medical_display_d
 normalMap textures/kolonia/flat_n
 normalFormat X Y Z
 physicalMap textures/kolonia/display_p
 glowMap textures/kolonia/medical_display_d
 }
}

textures/kolonia/status_pulse
{
 qer_editorImage textures/kolonia/status_d
 q3map_nonplanar
 {
 map textures/kolonia/status_d
 blendFunc add
 rgbGen wave sin 0.65 0.35 0 0.6
 }
}

textures/kolonia/sign_amber
{
 qer_editorImage textures/kolonia/amber_light
 {
  diffuseMap textures/kolonia/amber_light
  glowMap textures/kolonia/amber_light
 }
}

textures/kolonia/foliage
{
 qer_editorImage textures/kolonia/foliage_d
 q3map_nonplanar
 q3map_shadeAngle 60
 {
  diffuseMap textures/kolonia/foliage_d
  normalMap textures/kolonia/foliage_n
  normalFormat X Y Z
  physicalMap textures/kolonia/foliage_p
 }
}

textures/kolonia/bark
{
 qer_editorImage textures/kolonia/bark_d
 q3map_nonplanar
 q3map_shadeAngle 60
 {
  diffuseMap textures/kolonia/bark_d
  normalMap textures/kolonia/bark_n
  normalFormat X Y Z
  physicalMap textures/kolonia/bark_p
 }
}

textures/kolonia/ship_light
{
 qer_editorImage textures/kolonia/ship_light_d
 q3map_nonplanar
 q3map_shadeAngle 1
 q3map_surfaceLight 650
 q3map_lightSubdivide 32 // Distribute shadow samples along the light strip.
 q3map_lightImage textures/kolonia/ship_light_g
 {
  diffuseMap textures/kolonia/ship_light_d
  normalMap textures/kolonia/ship_light_n
  normalFormat X Y Z
  physicalMap textures/kolonia/ship_light_p
  glowMap textures/kolonia/ship_light_g
 }
}

textures/kolonia/ship_light_norad
{
 qer_editorImage textures/kolonia/ship_light_d
 q3map_nonplanar
 q3map_shadeAngle 60
 {
  diffuseMap textures/kolonia/ship_light_d
  normalMap textures/kolonia/ship_light_n
  normalFormat X Y Z
  physicalMap textures/kolonia/ship_light_p
  glowMap textures/kolonia/ship_light_g
 }
}


// Structural joins retain the same PBR maps without cross-plane lightmap merging.
textures/kolonia/ivory_planar
{
 qer_editorImage textures/kolonia/ship_panel_d

 q3map_shadeAngle 1 // Keep flat panels hard; preserve authored model normals.
 {
 diffuseMap textures/kolonia/ship_panel_d
 normalMap textures/kolonia/ship_panel_n
 normalFormat X Y Z
 physicalMap textures/kolonia/ship_panel_p
 }
}


// Structural joins retain the same PBR maps without cross-plane lightmap merging.
textures/kolonia/wet_rock_planar
{
 qer_editorImage textures/kolonia/coast_sand_rocks_02_d

 q3map_shadeAngle 60
 {
 diffuseMap textures/kolonia/coast_sand_rocks_02_d
 normalMap textures/kolonia/coast_sand_rocks_02_n
 normalFormat X Y Z
 physicalMap textures/kolonia/coast_sand_rocks_02_p


 }
}

// Cave renewal: CC0 Poly Haven scans, OpenGL tangent normals and ARM data.
textures/kolonia/cave_fracture
{
 qer_editorImage textures/kolonia/rock_wall_10_d
 q3map_shadeAngle 1
 {
 diffuseMap textures/kolonia/rock_wall_10_d
 normalMap textures/kolonia/rock_wall_10_n
 normalFormat X Y Z
 physicalMap textures/kolonia/rock_wall_10_p
 }
}

// Cave renewal: CC0 Poly Haven scans, OpenGL tangent normals and ARM data.
textures/kolonia/cave_aerial
{
 qer_editorImage textures/kolonia/cave_aerial_d
 q3map_shadeAngle 1
 {
 diffuseMap textures/kolonia/cave_aerial_d
 normalMap textures/kolonia/aerial_rocks_01_n
 normalFormat X Y Z
 physicalMap textures/kolonia/aerial_rocks_01_p
 }
}

// Cave renewal: CC0 Poly Haven scans, OpenGL tangent normals and ARM data.
textures/kolonia/cave_ground
{
 qer_editorImage textures/kolonia/wet_rock_d
 q3map_shadeAngle 1
 {
 diffuseMap textures/kolonia/wet_rock_d
 normalMap textures/kolonia/strata_n
 normalFormat X Y Z
 physicalMap textures/kolonia/wet_rock_p
 }
}

textures/kolonia/cave_base
{
 qer_editorImage textures/kolonia/coast_sand_rocks_02_d
 q3map_shadeAngle 1
 {
 diffuseMap textures/kolonia/coast_sand_rocks_02_d
 normalMap textures/kolonia/coast_sand_rocks_02_n
 normalFormat X Y Z
 physicalMap textures/kolonia/coast_sand_rocks_02_p


 }
}

// Mounted fungal brackets emit area light below the cave overhangs.
textures/kolonia/cave_fungus_light
{
 qer_editorImage textures/kolonia/bio_d
 q3map_shadeAngle 1
 q3map_surfaceLight 1500
 q3map_lightRGB 0.22 0.65 0.50
 q3map_lightImage textures/kolonia/bio_d
 q3map_lightSubdivide 32
 q3map_backSplash 0 0
 {
 diffuseMap textures/kolonia/bio_d
 normalMap textures/kolonia/bio_n
 normalFormat X Y Z
 specularMap textures/kolonia/bio_s
 glowMap textures/kolonia/bio_d
 }
}

// Sci-fi Supercomputer by Jungle Jim, CC BY 4.0; adapted for Kolonia.
textures/kolonia/jj_computers
{
 qer_editorImage textures/kolonia/jj_computers_d
 q3map_shadeAngle 1
 {
 diffuseMap textures/kolonia/jj_computers_d
 normalMap textures/kolonia/jj_computers_n
 normalFormat X Y Z
 normalScale 0.35 0.35 1
 physicalMap textures/kolonia/jj_computers_p
 glowMap textures/kolonia/jj_computers_g
 }
}

// Sci-fi Supercomputer by Jungle Jim, CC BY 4.0; adapted for Kolonia.
textures/kolonia/jj_supercomputer
{
 qer_editorImage textures/kolonia/jj_supercomputer_d
 q3map_shadeAngle 1
 {
 diffuseMap textures/kolonia/jj_supercomputer_d
 normalMap textures/kolonia/jj_supercomputer_n
 normalFormat X Y Z
 normalScale 0.35 0.35 1
 physicalMap textures/kolonia/jj_supercomputer_p
 glowMap textures/kolonia/jj_supercomputer_g
 }
}

// Opaque cabinet rear, cropped from Jungle Jim's authored metal casing maps.
textures/kolonia/jj_cabinet_back
{
 qer_editorImage textures/kolonia/jj_cabinet_back_d
 q3map_shadeAngle 1
 {
 diffuseMap textures/kolonia/jj_cabinet_back_d
 normalMap textures/kolonia/jj_cabinet_back_n
 normalFormat X Y Z
 normalScale 0.35 0.35 1
 physicalMap textures/kolonia/jj_cabinet_back_p
 }
}

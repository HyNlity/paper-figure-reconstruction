# Figure specification v1

All paths resolve relative to the spec. `canvas` uses integer pixels. 2D positions and sizes use normalized fractions of the full canvas, x right, y down; widths of strokes and font sizes are pixels. `parent` identifies another group; children retain canvas coordinates (no implicit parent transform). Array order is paint order; objects beneath others appear first. `panels` and `protected_regions` use normalized `[x,y,w,h]` boxes.

Minimal runnable example:
```json
{
 "version": 1,
 "source": {"path":"reference.png", "figure":"original example", "rights":"author-created"},
 "canvas": {"width":800,"height":500,"background":"#ffffff"},
 "panels": [{"id":"a","bbox":[0,0,1,1]}],
 "components": [
  {"id":"annotations","type":"group"},
  {"id":"label","parent":"annotations","type":"text","x":0.1,"y":0.1,"text":"Pump","font_family":"Arial","font_size":22,"fill":"#222222"},
  {"id":"arrow","type":"line","x1":0.1,"y1":0.5,"x2":0.8,"y2":0.5,"stroke":"#663399","stroke_width":3,"arrow":true}
 ],
 "assumptions": []
}
```

Supported 2D types: group, text (baseline y; native `tspan` array optional), rect, ellipse, line, path (normalized SVG path coordinates), image. Rect/image use x,y,w,h; ellipse cx,cy,rx,ry. Images require `path`, `provenance: own_blender_render` and `source_blend`. Text spans use text and optional `baseline_shift` (`sub`/`super`), font_size. Colors are CSS sRGB. No reference rasters embedded as reconstructed assets.

Optional `scene`: `units`, `basis`, `camera` (location,target,type,ortho_scale), `lights` (location,energy,size), `samples`, `transparent`, `objects`. Object fields: id,type (cube/sphere/cylinder/cone), location, rotation_degrees, scale, color (RGB 0..1), roughness. `parent` is optional; local transforms are relative to that object. Custom builders may extend `scene` with scientifically meaningful parameters and must document their interpretation. Store procedural seeds, renderer/color management, material alpha and geometry controls explicitly when used. The primitive backend uses Blender default world units, Z up, camera -Z with Y up, Standard color management and radians only internally.

Optional `scene.base_blend` loads an existing file; optional `scene.scene_name` selects the scene. The primitive backend adds named objects and rejects collisions; use a custom builder for controlled updates. Preserve the original file by saving to a distinct output path. A custom script must accept `--spec PATH --out DIRECTORY` after Blender's `--`.

Record `source.sha256`, PDF page/crop, URL/DOI when available, plus asset provenance and confidence/assumptions for inferred geometry. Never represent a schematic atom array as a verified CIF model.

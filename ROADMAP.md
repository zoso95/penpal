# penpal Roadmap

Mapping every technique from the old libraries (gpyplotter, plottermagic, plottersvg, axifun notebooks) to planned penpal modules.

## Source Locations

**Old library code:** `/Users/gnb/dev/plotter-backups/drive-download-20260218T174932Z-1-001/`
See `OLD_CODE_CATALOG.md` for file-by-file index.

**plotter_exps archive:** `/Users/gnb/dev/plotter-backups/plotter_exps/`
SVG-only output archive (~170+ printed SVGs, project experiments). No source code — visual reference for techniques and production pieces. Key directories:
- `printed/` — production SVGs covering: cloth simulation, metaballs, lavalamp, glass overlay, moire, oil slick, bubbles, orbits, death series, grass, litho, ghost effects, grid progressions, diamonds, deco patterns, swirls, pencil effects, rainbow paper cutouts, splines, texture experiments
- `printed/oil_slick_box/` — oil slick moire SVGs (blue + purple layers)
- `printed/metaballs/` — metaball SVGs (multi-color thick/thin line variants)
- `printed/texture_lib/` — op-art triangle patterns ("shattered triangle", trippy op-art)
- `projects/moire/` — moire experiments: texture_lib (op-art triangles), shape_ring (concentric circles), splines, texture, shade_design, hexagon
- `projects/wallpapers/` — wallpaper group experiments (mono, duo, multicolor, normed)
- `projects/portraits/` — portrait technique experiments
- `projects/polygons/` — polygon tessellation experiments

**plotterart GitHub repo:** `https://github.com/zoso95/plotterart`
(To be cloned to `/Users/gnb/dev/plotterart`.) Contains `pieces/` directory with source notebooks for anaglyph, polygon tessellation, and other art pieces. Not yet indexed — will update catalog separately.

---

## Status Legend

- [x] Implemented in penpal (code exists and works)
- [~] Partially implemented (some functions exist, others missing)
- [ ] Not yet ported

---

## Phase 1: Core (DONE)

| penpal module | Status | Source | Key functions |
|---|---|---|---|
| `core/types.py` | [x] | — | Polyline, Lines, validate, from_segments |
| `core/paths.py` | [x] | — | Paths class: transform, clip, optimize, filter, combine |
| `core/transforms.py` | [x] | `gpyplotter/geometry.py`, `plottermagic/geom3d.py` | rotate, reflect, translate, scale (2D+3D), apply() |
| `core/units.py` | [x] | `plottersvg/utils/units.py` | in/mm/cm/pt/px conversion |
| `core/line_ops.py` | [x] | `gpyplotter/line_processing.py` | optimize (NN), filter_short, collapse, subsample, resample |
| `core/geo.py` | [x] | — | clip, clip_rect, clip_away, intersect, contains_points (Shapely backend) |
| `core/layer.py` | [x] | — | Layer = name + style + Paths |
| `core/drawing.py` | [x] | — | Drawing with layer management, show/save, _repr_svg_. **TODO:** `pen_width_mm()` unit-aware helper (currently `pen_width()` only returns inches) |
| `core/mesh.py` | [x] | — | Mesh class: rect/polar grids, warp, triangulate, to_paths |
| `core/noise.py` | [x] | — | simplex, fractal, ridged, curl, sine, domain_warp, compose (warp funcs for Mesh) |
| `backends/matplotlib.py` | [x] | `gpyplotter/plotting.py` | render() with grid lines |
| `io/svg_write.py` | [x] | `gpyplotter/inkscape.py` | Inkscape layer SVG, multi-layer save |
| `io/provenance.py` | [x] | `gpyplotter/saver.py` | Script capture, params JSON, git hash |

---

## Phase 2: Generators

| penpal module | Status | Source | Key functions/techniques |
|---|---|---|---|
| `gen/curves.py` | [x] | `axifun/spirals.ipynb`, `roses.ipynb` | circle, spiral, polygon_regular, rose, lissajous, hilbert, concentric_circles |
| `gen/grids.py` | [x] | `axifun/distortion grids.ipynb` | grid, distorted_grid, barrel_distortion, noise_grid, polar_noise_grid |
| `gen/fields.py` | [x] | `axifun/perlin noise.ipynb`, `random walk.ipynb` | flow_field, noise_walk |
| `gen/flow.py` | [x] | `axifun/flow field*.ipynb` | trace, trace_bidirectional, simplex/fractal/curl/radial/spiral/constant/domain_warp fields, seed generators (line/grid/circle/ring/random/poisson), show_field |
| `gen/attractors.py` | [x] | `axifun/dynamic system.ipynb` | random_attractor, lorenz, rossler, clifford, de_jong, bedhead |
| `gen/moire.py` | [x] | `axifun/` (6 moire experiments), `plotter_exps/projects/moire/` | oil_slick, metallic_grid, rotated_grids, concentric_circles, concentric_shapes, surface_contour_moire |
| `gen/contours.py` | [x] | `axifun/textures.ipynb` | contour_lines, contour_filled, gaussian_bumps, math_contours |
| `gen/spline_waves.py` | [x] | `axifun/spline waves.ipynb`, `plotter_exps/printed/splines/` | spline_waves, random_walk_waves, evolving_waves |
| `gen/polar.py` | [x] | `axifun/ribbons.ipynb` | ribbon, ribbon_pair, concentric_ribbons, polar_function, polar_grid |
| `gen/cloth.py` | [x] | `plotterart/pieces/cloth/` (moire, rainbow_road, line_driven_cloth) | drape, drape_linear, braid, perspective_drape, cloth_fill — boundary curve interpolation with radial noise, cardinal spline smoothing, 3D perspective projection |
| `gen/ifs.py` | [x] | `axifun/eric_s thing.ipynb` | flame (11 variation functions), barnsley_fern, sierpinski, dragon_curve |
| `gen/envelopes.py` | [x] | `axifun/1 over x grids.ipynb`, `axifun/front face logo.ipynb` | hyperbolic, diamond, string_art, parabolic_envelope, cardioid_envelope |

---

## Phase 3: Shading + Sampling

| penpal module | Status | Source | Key functions |
|---|---|---|---|
| `shading/hatch.py` | [x] | `gpyplotter/shading.py`, `plottermagic/shading/simple_shapes.py` | hatch_polygon, shade_polygon, shade_triangle, shade_quadrilateral, parallel_lines |
| `shading/polygon.py` | [ ] | `gpyplotter/polyshader.py` | PolygonShader base class, step_through_poly, step_and_shade_poly |
| `shading/arc.py` | [ ] | `plottermagic/shading/simple_shapes.py` | grid_arc_shading — diagonal strut fills |
| `shading/stipple.py` | [x] | — | stipple_polygon, stipple_rect, dots_at (poisson/grid/jittered/random) |
| `shading/dilation.py` | [x] | `axifun/dilated polygons` notebooks | dilate_polygon, dilate_rect, dilate_circle, multi_dilate |
| `sampling/poisson.py` | [x] | `gpyplotter/sampling.py` (consolidated from 3 sources) | poisson_disk, poisson_disk_n |
| `sampling/tessellation.py` | [x] | `gpyplotter/tiling.py` | voronoi, delaunay, voronoi_edges |
| `sampling/noise.py` | [x] | — | (see core/noise.py — OpenSimplex warp funcs) |

---

## Phase 4: Symmetry

| penpal module | Status | Source | Key functions |
|---|---|---|---|
| `symmetry/wallpaper.py` | [x] | `gpyplotter/tiling.py` | WallpaperGroup class — all 17 wallpaper groups |
| `symmetry/mandala.py` | [x] | — | cyclic, dihedral, radial_repeat |
| `symmetry/mirror_slice.py` | [x] | — | mirror_slice, mirror_slice_rect — Droste / recursive zoom effects |
| `symmetry/lattice.py` | [ ] | `gpyplotter/tiling.py` | Lattice types, fundamental domains |

---

## Phase 5: CV / Halftone (photo -> plotter lines)

**Partially implemented.** `penpal/cv/` exists with `image.py` and `halftone.py`.

### Implemented

| penpal module | Status | Source | Technique |
|---|---|---|---|
| `cv/image.py` — load | [x] | `gpyplotter/image_lib.py` | load, gamma_correct, inv_gamma_correct, smooth (gamma-aware blur), resize, map_to_drawing |
| `cv/halftone.py` — crosshatch | [x] | `axifun/cross hatching*.ipynb` | Multi-angle hatching per tone band, density from brightness |
| `cv/halftone.py` — line_scan | [x] | `axifun/line by line scan*.ipynb` | Threshold -> parallel horizontal lines -> emit visible segments |
| `cv/halftone.py` — edges | [x] | `axifun/edge detection.ipynb` | Sobel gradient magnitude -> contour extraction |
| `cv/halftone.py` — morphological_halftone | [x] | `axifun/dilation*.ipynb` | binary_erosion iterations -> concentric contour rings |

### Not Yet Implemented

#### Line Scan Family
| penpal module | Status | Source | Technique |
|---|---|---|---|
| `cv/halftone.py` — crosshatch_cmyk | [ ] | `axifun/cross hatching cmyk*.ipynb` | CMYK channel separation + per-channel hatching |
| `cv/halftone.py` — line_scan_wiggle | [ ] | `axifun/line by line scan-wiggle.ipynb`, `suiqggly line by line.ipynb` | Wiggle/squiggly line-by-line scanning |
| `cv/halftone.py` — line_scan_rotated | [ ] | `axifun/line by line scan-rotated.ipynb` | Line-by-line scanning at arbitrary angles |
| `cv/halftone.py` — directional_masks | [ ] | `axifun/random directional masks.ipynb` | Rotated hatching per brightness band with different angles per region |

#### Morphological / Contour
| penpal module | Status | Source | Technique |
|---|---|---|---|
| `cv/halftone.py` — contour | [ ] | `axifun/countours.ipynb`, `spline contours.ipynb` | Smooth image -> contour polylines, B-spline smoothing |
| `cv/halftone.py` — edge_tone | [ ] | `axifun/edge + tone.ipynb` | Edge detection + tone layers combined |
| `cv/halftone.py` — dilation_additive | [ ] | `axifun/dilation additive.ipynb` | Multiple brightness thresholds, erodes each separately, sums contour maps |

#### Stippling / Dot
| penpal module | Status | Source | Technique |
|---|---|---|---|
| `cv/halftone.py` — mezzotint | [x] | `axifun/mezzotint*.ipynb` | multinomial dot placement proportional to darkness |
| `cv/halftone.py` — dot_grid | [x] | `axifun/dot grid*.ipynb` | Regular grid dots + dot_grid_cmyk for CMYK variant |
| `cv/halftone.py` — voronoi_stipple | [x] | `axifun/vonroni*.ipynb` | Rejection sampling -> Voronoi -> ridge edges, density-weighted |
| `cv/halftone.py` — delaunay_shade | [ ] | `axifun/triangulation*.ipynb` | Poisson -> Delaunay -> per-triangle shading by brightness |
| `cv/halftone.py` — sphere_halftone | [ ] | `axifun/Sphere effect.ipynb` | Concentric circle halftone at grid positions (sphere-like 3D appearance) |

#### Dithering
| penpal module | Status | Source | Technique |
|---|---|---|---|
| `cv/dither.py` — floyd_steinberg | [x] | `axifun/dither demo.ipynb` | Classic Floyd-Steinberg error diffusion |
| `cv/dither.py` — stucki | [x] | `axifun/dither demo.ipynb` | Stucki kernel (wider diffusion) |
| `cv/dither.py` — jarvis_judice_ninke | [x] | — | JJN 12-neighbor kernel |
| `cv/dither.py` — atkinson | [x] | — | Atkinson dithering (classic Mac, 3/4 error diffusion) |
| `cv/dither.py` — dither_to_lines | [x] | — | Dither + render as horizontal line segments |
| `cv/halftone.py` — hilbert | [ ] | `axifun/hilbert curves.ipynb` | Brightness -> Hilbert curve order per cell |

#### Spiral Portrait
| penpal module | Status | Source | Technique |
|---|---|---|---|
| `cv/halftone.py` — spiral_portrait | [x] | `axifun/spirals.ipynb` | Archimedean spiral with sine-wave amplitude modulated by pixel brightness |

#### Texture / Multi-Scale Decomposition
| penpal module | Status | Source | Technique |
|---|---|---|---|
| `cv/texture.py` — gradient_warp | [x] | `sourcery/image_magic.py` | FFT-gradient displaced pixel grids ("death textures"). Density param for line count control. |
| `cv/texture.py` — portrait_warp | [x] | `sourcery/image_magic.py` | Two-pass gradient mesh warp + fraction-based tonal masking ("Bradway technique"). |
| `cv/texture.py` — integral_warp | [x] | `sourcery/image_magic.py` | 1D marginal CDF line redistribution — denser lines in darker regions. |
| `cv/texture.py` — laplacian_pyramid | [x] | `axifun/laplace pyramid.ipynb` | Decompose image into frequency bands via pyrDown/pyrUp. Each band rendered separately with different line techniques. |
| `cv/texture.py` — laplacian_blend | [x] | `sandbox/pyramid_blending.ipynb` | Seamless Laplacian pyramid blending of two images with mask. |
| `cv/texture.py` — repeat_blur_bands | [x] | `axifun/repeat blurs.ipynb` | Progressive maximum_filter at increasing sizes. Difference between scales reveals organic "snake skin" cell patterns. |
| `cv/datasets.py` | [x] | — | Auto-downloading image dataset library (DTD). Caches to `~/.penpal/datasets/`. |
| `cv/texture.py` — voronoi_laplacian | [ ] | `axifun/paul replica - vonroni-less dense laplacian good.ipynb` | Poisson disk -> Voronoi regions -> flood-fill color assignment -> per-region shading density from Laplacian band. The "snake skin painting" technique — organic cell-like fills driven by image frequency content. |

#### Image Utilities (remaining)
| penpal module | Status | Source | Key functions |
|---|---|---|---|
| `cv/edges.py` | [ ] | `axifun/edge detection.ipynb`, `skimage.ipynb` | Canny, CLAHE, binary_dilation, Roberts/Sobel/Scharr/Prewitt edge detectors |
| `cv/segmentation.py` | [ ] | `axifun/kmean tones.ipynb`, `sun.ipynb`, `c-c-c-clustering.ipynb` | KMeans tone separation for multi-pen, cluster-mask spline waves |
| `cv/duotone.py` | [ ] | `axifun/duotones.ipynb`, `axifun/grid random colors.ipynb` | Two-color line-by-line scanning, multi-color grid assignment |

---

## Phase 6: Warp / Distortion (image-driven geometry)

| penpal module | Status | Source | Technique |
|---|---|---|---|
| `cv/warp.py` — force_directed_grid | [ ] | `axifun/grid warp 5 - force directed.ipynb` | networkx graph, spring/repulsion constants from image brightness, iterative relaxation |
| `cv/warp.py` — grid_shift | [ ] | `axifun/grid shifting*.ipynb`, `radial grid shifting*.ipynb` | Row/column offsets from noise or radial functions |
| `cv/warp.py` — fluid_warp | [ ] | `axifun/fluid warping.ipynb` | Iterated domain warping: `g(x + g(x + g(x)))` |
| `cv/warp.py` — schism_grid | [ ] | `axifun/schism grid shift.ipynb` | Grid shifting with intentional discontinuities/schisms creating split patterns |
| `cv/warp.py` — refraction | [ ] | `axifun/refraction.ipynb`, `refraction continious.ipynb`, `plotter_exps/printed/glass_overlay.svg` | Parallel lines change angle at brightness boundaries, simulating light refraction |

---

## Phase 7: 3D Engine

### Phase 7a: Core Pipeline (DONE)

| penpal module | Status | Source | Key classes/functions |
|---|---|---|---|
| `render3d/project.py` | [x] | `plottermagic/line_render/camera.py` | look_at, perspective, project_points, project_lines, viewport_map |
| `render3d/camera.py` | [x] | `plottermagic/line_render/camera.py` | Camera class with orbit() classmethod |
| `render3d/shapes.py` | [x] | `plottermagic/line_render/polygon.py`, `polyhedron.py` | Face3D (with texture hatching), Mesh3D (box, plane factories), Wireframe, TextureSpec |
| `render3d/scene.py` | [x] | `plottermagic/line_render/render.py` | Scene class: backface cull -> project -> sort -> hidden line removal via Shapely difference -> Drawing |

### Phase 7b: NPR Sketch Rendering (DONE)

| penpal module | Status | Source | Key classes/functions |
|---|---|---|---|
| `render3d/lighting.py` | [x] | — | DirectionalLight, PointLight, compute_face_intensities (Lambert diffuse model) |
| `render3d/loader.py` | [x] | — | load_stl: binary + ASCII STL parser -> Mesh3D, with decimation support |
| `render3d/mesh_ops.py` | [x] | — | triangulate_mesh, weld_vertices, compute_face_normals, compute_vertex_normals, compute_curvature_directions (dihedral angle estimation), extract_silhouette_edges |
| `render3d/sketch.py` | [x] | Hertzmann & Zorin, Winkenbach & Salesin | sketch_render: curvature-driven hatching, lighting-based density, silhouette edges, auto-scaled spacing |

**Done:** Full NPR sketch pipeline — load STL -> triangulate -> weld vertices -> compute curvature -> lighting -> curvature-following hatching (dense in shadow, sparse in highlights) -> silhouette extraction -> hidden line removal -> Drawing.

### Phase 7c: Remaining 3D Features

| penpal module | Status | Source | Technique |
|---|---|---|---|
| `render3d/sphere.py` | [ ] | `axifun/spheres*.ipynb` | Analytical sphere: lat/lon grid, hidden-line by normal dot product |
| `render3d/anaglyph.py` | [ ] | `plotterart/pieces/anaglyph/` (9 stereoscopic notebooks) | Stereo pair rendering (red/cyan offset cameras). Left/right eye images with horizontal parallax displacement. |
| `render3d/contours.py` | [ ] | — | Suggestive contours (curvature zero-crossings) — silhouette extraction is done in mesh_ops.py, but suggestive contours remain |
| `render3d/surface.py` | [ ] | `axifun/distortion grids*.ipynb`, `radial grid shifting*.ipynb` | Deformable mesh surface for moire: Mesh + Z displacement by noise + camera projection -> interference patterns |

### Phase 7d: Moire / 3D Surface Projection

The "oil slick" effect: project regular patterns (grids, concentric circles) onto bumpy 3D surfaces. The moire interference emerges naturally from perspective compression of the pattern over the surface deformation. See `plotter_exps/printed/oil_slick_box/` (blue + purple layers) and `plotter_exps/printed/comissioned_moire.svg`.

| penpal module | Status | Source | Technique |
|---|---|---|---|
| `gen/moire.py` — overlapping_patterns | [ ] | `axifun/` (6 moire experiments), `plotter_exps/projects/moire/` | Overlapping rotated concentric circles, grids, line sets with slight angle/offset differences. Reference: `projects/moire/shape_ring/` (concentric circles), `projects/moire/splines/`, `projects/moire/hexagon/` |
| `gen/moire.py` — surface_project | [ ] | `axifun/distortion grids*.ipynb` | Project regular pattern onto noise-deformed 3D mesh surface via camera -> interference patterns |
| `gen/moire.py` — oil_slick | [ ] | `plotter_exps/printed/oil_slick_box/`, `plotter_exps/printed/perlin_metalic.svg` | Perlin noise moire: multi-layer patterns on noise-displaced surfaces, producing oil-slick iridescence effect |
| `render3d/surface.py` | [ ] | `axifun/distortion grids*.ipynb` | Deformable mesh surface: take core/Mesh, displace Z by noise/function, render as Face3D grid with pattern |

**Algorithm:** Define a regular grid in 3D. Displace Z-coordinates with noise (simplex, radial distortion, etc). The grid lines on the bumpy surface project to 2D through the camera, and the uneven compression creates moire interference. Can use existing `core/mesh.py` warping + `render3d/scene.py` projection.

---

## Phase 8: I/O

| penpal module | Status | Source | Key functions |
|---|---|---|---|
| `io/svg_write.py` | [x] | `gpyplotter/inkscape.py` | Multi-layer Inkscape SVG writer |
| `io/provenance.py` | [x] | `gpyplotter/saver.py` | capture_provenance, save_provenance, capture_source, git hash |
| `io/svg_read.py` | [ ] | `plottersvg/plottersvg/io/read.py` | Full SVG parser (polyline, polygon, line, rect, path, circle, ellipse) |
| `io/svg_pathutils.py` | [ ] | `plottersvg/plottersvg/elements/pathutils.py` | SVG path `d` attribute parser (M/L/H/V/Z/C/S/Q/T — no arcs) |
| `io/svg_stitch.py` | [ ] | `axifun/stich together SVGs*.ipynb` | Merge SVG files into multi-layer document |
| `io/gcode.py` | [ ] | — | GCode export for Bantam / AxiDraw |
| `io/axidraw.py` | [ ] | `gpyplottermod/draw svgs/` notebooks | pyaxidraw driver interface |

---

## Phase 9: Tiling / Partitioning

| penpal module | Status | Source | Technique |
|---|---|---|---|
| `sampling/partition.py` | [ ] | `plotterart/pieces/polygon_tess/network.py` | networkx-based polygon adjacency graph, BFS/DFS/random expansion partitioning |

---

## Phase 10: RL Environment

**Not yet started.** No `penpal/rl/` directory exists.

| penpal module | Status | Source | Description |
|---|---|---|---|
| `rl/env.py` | [ ] | — | Gymnasium env: target image -> stroke actions |
| `rl/rasterizer.py` | [ ] | — | Cairo-based fast line rasterizer |
| `rl/reward.py` | [ ] | — | L2 pixel, SSIM, VGG perceptual loss |
| `rl/stroke.py` | [ ] | — | Action space: line, bezier, arc strokes |
| `backends/cairo.py` | [ ] | — | Drawing.rasterize() backend |

---

## Phase 11: Effects & Simulation

New modules — not ported from old code, built fresh. Some have output references in `plotter_exps/printed/`.

| penpal module | Status | Source / Reference | Technique |
|---|---|---|---|
| `gen/cloth.py` | [x] | `plotterart/pieces/cloth/`, `plotter_exps/printed/cloth_*.svg` | Cloth drape/braid — boundary curve interpolation with radial noise, cardinal spline smoothing, 3D perspective projection, multi-strand braiding. See also `effects/cloth.py` for future spring/mass physics. |
| `effects/metaballs.py` | [x] | `plotter_exps/printed/metaballs/` | metaballs, metaball_field, animated_metaballs — sum of 1/r^2 fields, iso-contour extraction |
| `effects/lavalamp.py` | [ ] | `plotter_exps/printed/lavalamp.svg` | Lava lamp effect — animated metaballs with gravity and buoyancy, possibly frame-captured as static composition. |
| `effects/glass.py` | [ ] | `plotter_exps/printed/glass_overlay.svg`, `axifun/refraction*.ipynb` | Glass distortion — refracts/displaces lines behind a glass region (lens, pane, sphere). Snell's law or simplified radial distortion of line segments passing through the glass shape. |
| `effects/bubbles.py` | [ ] | `plotter_exps/printed/bubbles_etch.svg`, `bubbles_grid_etch.svg` | Bubble patterns — circular distortion fields with refraction-like displacement and highlight arcs. |
| `effects/easing.py` | [x] | — | 20+ easing functions: linear, ease_in/out (quad/cubic/quart/expo/circ), elastic, bounce, smoothstep, smootherstep, pulse, sawtooth, triangle_wave, remap |
| `effects/ghost.py` | [ ] | `plotter_exps/printed/ghosts.svg` | Ghost/echo effects — offset/faded duplicates of geometry with progressive distortion or transparency simulation via line density. |
| `effects/smoke.py` | [ ] | `plotter_exps/printed/smoke_strands.svg` | Smoke/strand simulation — turbulent noise-driven strand paths, possibly particle-based. |
| `effects/orbits.py` | [ ] | `plotter_exps/printed/orbits.svg` | Orbital mechanics — elliptical paths with gravitational interaction, possibly n-body or simple Kepler orbits. |

---

## Phase 12: Neural Network / Optimization Approaches

Experimental techniques using ML for line placement.

| penpal module | Status | Source | Technique |
|---|---|---|---|
| `nn/perceptual_lines.py` | [ ] | `axifun/photo realism nn.ipynb`, `axifun/vgg/` | VGG19 perceptual loss — iteratively place random lines that minimize perceptual distance to target image. TensorFlow VGG16/19 implementations in `axifun/vgg/`. |
| `nn/quadtree_graph.py` | [ ] | `axifun/photo realism qt graph.ipynb`, `qt graph stuff.ipynb` | Quadtree graph-based image partitioning for adaptive line placement. |
| `nn/photo_realism.py` | [ ] | `axifun/photo realism no NN.ipynb`, `photo realism (fast I think).ipynb` | Non-neural photo realism approaches (fast variants). |

---

## Phase 13: Evolutionary / Genetic Tuning

| penpal module | Status | Source | Technique |
|---|---|---|---|
| `evolve/genetic.py` | [ ] | — | Genetic algorithm for parameter tuning. Define a param search space, render a population grid, select favorites (human-in-the-loop) or use fitness metrics, breed + mutate → next generation. |
| `evolve/grid_search.py` | [ ] | — | Exhaustive / random grid search over param spaces with thumbnail rendering. |
| `evolve/fitness.py` | [ ] | — | Automated fitness functions: line density, coverage uniformity, complexity metrics, symmetry score, etc. For fully automated exploration or pre-filtering before human selection. |

---

## Phase 14: External Tool Integration

| penpal module | Status | Source | Technique |
|---|---|---|---|
| `integrations/blender.py` | [ ] | `axifun/blender/`, `axifun/blender/keepers/` | Blender 3D model -> SVG wireframe export pipeline. ~20 Blender wireframe SVGs in archive. |
| `integrations/mcp.py` | [ ] | — | MCP (Model Context Protocol) server exposing penpal as tools for Claude/LLMs. See design notes below. |

### MCP Server Design Notes

Expose penpal as an MCP tool server so Claude (or any MCP-compatible LLM) can generate plotter art conversationally. Key design questions:

**What to expose:**
- **High-level generators** as tools: `gradient_warp`, `portrait_warp`, `crosshatch`, `flow_field`, `moire`, etc. Each tool takes params and returns an SVG or image preview.
- **Drawing management**: create drawing, add layers, save SVG, show preview.
- **Image loading**: load from path, load from DTD dataset, resize.
- **Parameter exploration**: render a grid of parameter variations for visual comparison.

**Architecture options:**
1. **Thin wrapper** — Each penpal function becomes an MCP tool. Claude gets raw control but needs to know the API. Simple to implement.
2. **Sketch-to-art pipeline** — Higher-level tools like "render this photo as plotter art" that chain multiple steps internally. Easier for Claude to use.
3. **Hybrid** — High-level convenience tools + low-level building blocks for fine control.

**Preview/feedback loop:**
- Tools should return SVG or PNG previews so Claude can see what it generated and iterate.
- Could use `Drawing._repr_svg_()` for inline SVG or render to PNG via matplotlib.
- Parameter suggestions: tools could return "try adjusting X for more/less Y" hints.

**Session state:**
- MCP tools are stateless by default. Options:
  - Return serialized Drawing objects that can be passed back as input.
  - Server-side session with drawing state (more complex but better UX).
  - File-based: save to temp directory, return paths.

**Implementation:**
- Use `mcp` Python SDK (`pip install mcp`).
- One `penpal-mcp` server entry point.
- Could ship as `penpal[mcp]` optional dependency.

---

## Production Technique Reference (plotter_exps archive)

Techniques observed in `plotter_exps/printed/` that have production-quality outputs. These serve as visual targets for implementation. Grouped by category:

### Grid / Geometric Patterns
- `grid_progression.svg`, `grid_trippy*.svg`, `subtle_grid.svg` — grid-based pattern progressions
- `block_grad_grid/`, `blue_block_grid.svg` — block gradient grids
- `box_shading.svg`, `boxes_etch.svg`, `litho_boxes.svg` — box-based shading
- `deco_diamonds.svg`, `diamonds.svg` — art deco diamond patterns
- `circle_connected*.svg`, `circle_cutout.svg`, `circle_strip.svg` — circle compositions
- `illuminati.svg` — geometric eye/pyramid design
- `web.svg` — web-like radial pattern
- `cos_hourglass.svg` — cosine-based hourglass shape
- `curvilinear.svg` — curvilinear grid patterns

### Swirl / Spiral / Flow
- `swirl.svg`, `bw_swirl*.svg`, `trippy_swirl.svg` — swirl patterns
- `rainbow_spiral_trippy*.svg` — rainbow spiral with psychedelic effect
- `storm.svg`, `storm2.svg` — storm/vortex patterns
- `riptide_811.svg` — riptide flow pattern

### Color / Rainbow / Multi-Layer
- `rainbow_flower*.svg`, `rainbow_paper_cutout*.svg`, `rainbow_rect*.svg` — rainbow multi-pen layered pieces
- `rainbow_road/`, `rainbow_road_2/` — rainbow gradient road patterns
- `rainbow_stainglass/`, `rainbow_voroni/` — rainbow stained glass / Voronoi
- `perlin_rainbow*.svg` — Perlin noise with rainbow color mapping

### Pencil / Mixed Media
- `pencil_gradient.svg`, `pencil_circle_shaded.svg`, `pencil_square_shaded.svg` — pencil-drawn shading effects
- `pencil_lewitt.svg` — Sol LeWitt-inspired pencil patterns
- `pencil_stripes.svg`, `pencil_vertical.svg` — pencil stripe patterns
- `pencil_watercolor_test*.svg` (5 variants) — pencil + watercolor mixed media experiments

### Portrait / Figurative
- `agnes_litho.svg`, `agnes_strips_c*.svg`, `agnes_tones_c*.svg` — Agnes portrait variants
- `the_eyes.svg` — eye-focused portrait
- `projects/portraits/` — portrait experiment directory

### Lithography / Stained Glass / Decorative
- `litho_stainglass_1.svg`, `sainglass_4.svg`, `stainglass_8_10.svg` — stained glass patterns
- `stainglass_laser_print/` — laser-printed stained glass
- `las_meninans_geo_abstract.svg`, `nighthawks_geo_abstract.svg`, `school_athens_geo_abstract.svg` — geometric abstractions of famous paintings

### Death Series
- `death_bumps.svg`, `death_fuzzy.svg`, `death_guts*.svg` — "death" themed series with organic distortion

### Misc Production
- `dot_square.svg`, `dots_the_style.svg` — dot-based patterns
- `grass/` (3 SVGs) — grass/nature patterns
- `sunset/` — sunset gradient patterns
- `patchwork/` — patchwork quilt patterns
- `lewitt_challenge_pieces/` — Sol LeWitt wall drawing challenge
- `sky_grid.svg`, `sky_try/` — sky-themed grids
- `ocean_grid.svg` — ocean-themed grid
- `collectors_november.svg`, `welcome_november.svg` — seasonal collector pieces
- `exp_strip.svg`, `sun_strip.svg`, `circle_strip.svg` — strip-based compositions

---

## Utility Modules (port as needed)

| penpal module | Source | What |
|---|---|---|
| `utils/random_params.py` | `gpyplotter/random_parameters.py` | RandomParameters class for reproducible generative art |
| `utils/svg_utils.py` | `gpyplotter/svg_util.py` | SVG attribute parsing, CSS color resolution |

---

## Duplicated Code (consolidation guide)

These exist in multiple places in the old code. Consolidate to one canonical location:

| Technique | Locations | Canonical penpal module |
|---|---|---|
| Poisson disk sampling | `gpyplotter/sampling.py`, `plottermagic/random/possion_disk_sampling.py`, axifun inline | `sampling/poisson.py` (done) |
| NN pen optimization | `gpyplotter/line_processing.py`, `plottermagic/svg_processing/optimization.py` | `core/line_ops.py` (done) |
| shade_triangle/quad | `gpyplotter/shading.py`, `plottermagic/shading/simple_shapes.py` | `shading/hatch.py` (done) |
| 2D transforms | `gpyplotter/geometry.py`, `plottersvg/utils/geometry.py` | `core/transforms.py` (done) |
| matplotlib display | `gpyplotter/plotting.py`, `plottermagic/graphing/plot.py` | `backends/matplotlib.py` (done) |

---

## What's Done vs What's Missing

### Done (usable today)
- **Core** — Drawing, Paths, Layers, transforms, line ops, geo clipping, mesh, noise
- **Generators** — curves, grids, fields, flow tracing, attractors (Lorenz/Rossler/Clifford/de Jong/Bedhead/random), IFS/flame fractals (11 variations + Barnsley/Sierpinski/dragon), contour extraction (math/gaussian/scalar fields), line envelopes (hyperbolic/diamond/string art/parabolic/cardioid), spline waves (physics/random walk/evolving), polar/ribbons (ribbon fills, concentric ribbons, polar grid), moire (oil slick/metallic/rotated/concentric/surface contour), cloth/drape/braid (boundary curve interpolation with radial noise, perspective projection, multi-strand weave)
- **Shading** — polygon hatching (hatch, crosshatch, shade_triangle/quad), stipple fills (poisson/grid/jittered/random), dilation fills (concentric inset polygons via Shapely buffer)
- **Sampling** — Poisson disk, Voronoi/Delaunay tessellation
- **Symmetry** — wallpaper groups, mandala (cyclic/dihedral), Droste/mirror_slice
- **3D** — full render pipeline: camera, projection, shapes with textures, hidden line removal, NPR sketch rendering (lighting, curvature-driven hatching, silhouette extraction, STL loader)
- **CV/Halftone** — crosshatch, line scan, edge detection, morphological halftone, dot grid (BW + CMYK), mezzotint (importance-sampled stippling), voronoi stipple, spiral portrait, image loading/preprocessing
- **CV/Texture** — gradient warp (death textures with density control), portrait warp (Bradway technique), integral warp (1D marginal CDF redistribution), Laplacian pyramid decomposition, Laplacian pyramid blending, repeat blur bands
- **CV/Datasets** — auto-downloading image datasets (DTD — 47 categories, 5640 textures)
- **CV/Dithering** — Floyd-Steinberg, Stucki, Jarvis-Judice-Ninke, Atkinson, dither-to-lines
- **Effects** — easing library (20+ functions), metaballs (single/field/animated)
- **I/O** — SVG write (Inkscape layers), provenance tracking

### Missing (by priority)
1. **CV/Halftone (remaining)** — CMYK crosshatch, wiggle/rotated line scan, delaunay shade, sphere halftone, Hilbert curve halftone, directional masks
2. **CV/Texture (remaining)** — Voronoi-Laplacian "snake skin" rendering
3. **Moire / 3D surface projection** — project patterns onto bumpy surfaces for interference effects
4. **Warp** — force-directed grid, fluid warping, grid shifting, schism grid, refraction
5. **Effects / Simulation** — lavalamp, glass distortion, bubbles, ghost, smoke, orbits (cloth drape/braid done in gen/cloth.py — spring/mass physics cloth remains)
6. **3D extras** — sphere primitive, anaglyph stereo, suggestive contours, deformable surface
7. **SVG reader** — can write SVGs but can't read them back
8. **CV utilities** — edges (Canny/CLAHE), segmentation (KMeans), duotone
9. **Shading** — PolygonShader, arc shading
10. **I/O** — GCode export, SVG path parser, SVG stitching, AxiDraw driver
11. **Neural/optimization** — VGG perceptual line placement, quadtree graph, photo realism
12. **External integration** — Blender SVG export pipeline
13. **RL environment** — gymnasium env, cairo rasterizer, reward functions


# penpal Roadmap

Mapping every technique from the old libraries (gpyplotter, plottermagic, plottersvg, axifun notebooks) to planned penpal modules.

**Old code location:** `/Users/gnb/dev/plotter-backups/drive-download-20260218T174932Z-1-001/`

---

## Status Legend

- [x] Implemented in penpal
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
| `core/geo.py` | [x] | — | clip, clip_rect, intersect, contains_points (Shapely backend) |
| `core/layer.py` | [x] | — | Layer = name + style + Paths |
| `core/drawing.py` | [x] | — | Drawing with layer management, show/save, _repr_svg_ |
| `backends/matplotlib.py` | [x] | `gpyplotter/plotting.py` | render() with grid lines |
| `io/svg_write.py` | [x] | `gpyplotter/inkscape.py` | Inkscape layer SVG, multi-layer save |

---

## Phase 2: Generators

| penpal module | Status | Source | Key functions/techniques |
|---|---|---|---|
| `gen/curves.py` | [x] | `axifun/spirals.ipynb`, `roses.ipynb` | circle, spiral, polygon_regular, rose, lissajous, hilbert, concentric_circles |
| `gen/grids.py` | [x] | `axifun/distortion grids.ipynb` | grid, distorted_grid, barrel_distortion |
| `gen/fields.py` | [x] | `axifun/perlin noise.ipynb`, `random walk.ipynb` | flow_field, noise_walk |
| `gen/attractors.py` | [ ] | `axifun/dynamic system.ipynb` | Random matrix strange attractors: `x += M * sin(F1*x)^P + sin(F2*x)^P` |
| `gen/moire.py` | [ ] | `axifun/` (6 moire experiments) | Overlapping rotated concentric shapes (circles, polygons, splines) |
| `gen/contours.py` | [ ] | `axifun/textures.ipynb` | contour_lines, contour_grid — math function → iso-contours |
| `gen/spline_waves.py` | [ ] | `axifun/spline waves.ipynb` | Animated spline control points with velocity/acceleration |
| `gen/polar.py` | [ ] | `axifun/ribbons.ipynb` | Ribbon curves (offset pairs), polar grids |

---

## Phase 3: Shading + Sampling

| penpal module | Status | Source | Key functions |
|---|---|---|---|
| `shading/hatch.py` | [ ] | `gpyplotter/shading.py` | shade_triangle, shade_quadrilateral, parallel_lines, cross_hatch |
| `shading/polygon.py` | [ ] | `gpyplotter/polyshader.py` | PolygonShader base class, step_through_poly, step_and_shade_poly |
| `shading/arc.py` | [ ] | `plottermagic/shading/simple_shapes.py` | grid_arc_shading — diagonal strut fills |
| `shading/stipple.py` | [ ] | — | Dot/point-based fills |
| `shading/dilation.py` | [ ] | `axifun/dilated polygons` notebooks | Concentric inset polygons via Shapely buffer |
| `sampling/poisson.py` | [ ] | `gpyplotter/sampling.py` | Bridson Poisson disk sampling (3 duplicate implementations to consolidate) |
| `sampling/tessellation.py` | [ ] | `gpyplotter/tiling.py` | Voronoi, Delaunay, shard_and_connect |
| `sampling/noise.py` | [ ] | — | OpenSimplex wrapper, noise field utilities |

**Source note:** Poisson disk is duplicated in `gpyplotter/sampling.py`, `plottermagic/random/possion_disk_sampling.py`, and inline in axifun notebooks. Consolidate to one.

**Source note:** `shade_quadrilateral` / `shade_triangle` duplicated in `gpyplotter/shading.py` and `plottermagic/shading/simple_shapes.py`. Merge; plottermagic adds `grid_arc_shading` and `step_and_shade_poly`.

---

## Phase 4: Symmetry

| penpal module | Status | Source | Key functions |
|---|---|---|---|
| `symmetry/wallpaper.py` | [ ] | `gpyplotter/tiling.py` | WallpaperGroup class — all 17 wallpaper groups |
| `symmetry/mandala.py` | [ ] | — | Cyclic + dihedral radial symmetry |
| `symmetry/lattice.py` | [ ] | `gpyplotter/tiling.py` | Lattice types, fundamental domains |

---

## Phase 5: CV / Halftone (photo → plotter lines)

### Line Scan Family
| penpal module | Status | Source | Technique |
|---|---|---|---|
| `cv/halftone.py` — line_scan | [ ] | `axifun/line by line scan*.ipynb` | Threshold → parallel lines → mask → emit visible segments |
| `cv/halftone.py` — crosshatch | [ ] | `axifun/cross hatching*.ipynb` | Multi-angle hatching per tone band, continuous density variant |
| `cv/halftone.py` — crosshatch_cmyk | [ ] | `axifun/cross hatching cmyk*.ipynb` | CMYK channel separation + per-channel hatching |

### Morphological / Contour
| penpal module | Status | Source | Technique |
|---|---|---|---|
| `cv/halftone.py` — dilation_contours | [ ] | `axifun/dilation*.ipynb` | binary_erosion iterations → contour extraction |
| `cv/halftone.py` — contour | [ ] | `axifun/countours.ipynb`, `spline contours.ipynb` | Smooth image → Canny → contour polylines, B-spline smoothing |
| `cv/halftone.py` — edge_tone | [ ] | `axifun/edge + tone.ipynb` | Edge detection + tone layers combined |

### Stippling / Dot
| penpal module | Status | Source | Technique |
|---|---|---|---|
| `cv/halftone.py` — mezzotint | [ ] | `axifun/mezzotint*.ipynb` | multinomial dot placement proportional to darkness |
| `cv/halftone.py` — dot_grid | [ ] | `axifun/dot grid*.ipynb` | Regular grid dots, CMYK variant |
| `cv/halftone.py` — voronoi_stipple | [ ] | `axifun/vonroni*.ipynb` | Poisson sample → Voronoi → ridge edges, density-weighted |
| `cv/halftone.py` — delaunay_shade | [ ] | `axifun/triangulation*.ipynb` | Poisson → Delaunay → per-triangle shading by brightness |

### Dithering
| penpal module | Status | Source | Technique |
|---|---|---|---|
| `cv/halftone.py` — floyd_steinberg | [ ] | `axifun/dither demo.ipynb` | Classic Floyd-Steinberg error diffusion |
| `cv/halftone.py` — stucki | [ ] | `axifun/dither demo.ipynb` | Stucki kernel (wider diffusion) |
| `cv/halftone.py` — hilbert | [ ] | `axifun/hilbert curves.ipynb` | Brightness → Hilbert curve order per cell |

### Image Utilities
| penpal module | Status | Source | Key functions |
|---|---|---|---|
| `cv/image.py` | [ ] | `gpyplotter/image_lib.py` | load, gamma_correct, blur, sample, resize |
| `cv/edges.py` | [ ] | `axifun/edge detection.ipynb` | Canny, CLAHE, binary_dilation |
| `cv/segmentation.py` | [ ] | `axifun/kmean tones.ipynb` | KMeans tone separation for multi-pen |
| `cv/frequency.py` | [ ] | `axifun/laplace pyramid.ipynb` | Laplace pyramid decomposition for frequency-band rendering |

---

## Phase 6: Warp / Distortion (image-driven geometry)

| penpal module | Status | Source | Technique |
|---|---|---|---|
| `cv/warp.py` — force_directed_grid | [ ] | `axifun/grid warp 5 - force directed.ipynb` | networkx graph, spring/repulsion constants from image brightness, iterative relaxation |
| `cv/warp.py` — grid_shift | [ ] | `axifun/grid shifting*.ipynb`, `radial grid shifting*.ipynb` | Row/column offsets from noise or radial functions |
| `cv/warp.py` — fluid_warp | [ ] | `axifun/fluid warping.ipynb` | Iterated domain warping: `g(x + g(x + g(x)))` |

---

## Phase 7: 3D Engine

| penpal module | Status | Source | Key classes/functions |
|---|---|---|---|
| `render3d/camera.py` | [ ] | `plottermagic/line_render/camera.py` | Camera class: pos, look_at, fov, projection pipeline |
| `render3d/scene.py` | [ ] | `plottermagic/line_render/renderable.py`, `render.py` | Scene3D, RenderableCollection, render pipeline |
| `render3d/shapes.py` | [ ] | `plottermagic/line_render/line.py`, `polygon.py`, `polyhedron.py`, `point.py` | Line3D, Polygon3D, Polyhedron, Points3D |
| `render3d/shading3d.py` | [ ] | `plottermagic/shading/simple_shapes.py` | 3D polygon fill (hatch in 3D, project to 2D) |
| `render3d/clip.py` | [ ] | `plottermagic/line_render/render.py` (stub) | Frustum clipping — **missing in old code, needs implementation** |
| `render3d/sphere.py` | [ ] | `axifun/spheres*.ipynb` | Analytical sphere: lat/lon grid, hidden-line by normal dot product |
| `render3d/anaglyph.py` | [ ] | `plotterart/pieces/anaglyph/` | Stereo pair rendering (red/cyan offset cameras) |

**Gap:** `unit_cube_clipping` is stubbed in plottermagic's `render.py` — needs proper implementation.

**Gap:** Sphere uniform sampling (`plottermagic/random/sphere_sampling.py`) has URLs but no code.

---

## Phase 8: I/O

| penpal module | Status | Source | Key functions |
|---|---|---|---|
| `io/svg_write.py` | [x] | `gpyplotter/inkscape.py` | Multi-layer Inkscape SVG writer |
| `io/svg_read.py` | [ ] | `plottersvg/plottersvg/io/read.py` | Full SVG parser (polyline, polygon, line, rect, path, circle, ellipse) |
| `io/svg_pathutils.py` | [ ] | `plottersvg/plottersvg/elements/pathutils.py` | SVG path `d` attribute parser (M/L/H/V/Z/C/S/Q/T — no arcs) |
| `io/svg_stitch.py` | [ ] | `axifun/stich together SVGs*.ipynb` | Merge SVG files into multi-layer document |
| `io/gcode.py` | [ ] | — | GCode export for Bantam / AxiDraw |
| `io/provenance.py` | [ ] | `gpyplotter/saver.py` | Script capture, params JSON, git hash |
| `io/axidraw.py` | [ ] | `gpyplottermod/draw svgs/` notebooks | pyaxidraw driver interface |

---

## Phase 9: Tiling / Partitioning

| penpal module | Status | Source | Technique |
|---|---|---|---|
| `sampling/partition.py` | [ ] | `plotterart/pieces/polygon_tess/network.py` | networkx-based polygon adjacency graph, BFS/DFS/random expansion partitioning |

---

## Phase 10: RL Environment

| penpal module | Status | Source | Description |
|---|---|---|---|
| `rl/env.py` | [ ] | — | Gymnasium env: target image → stroke actions |
| `rl/rasterizer.py` | [ ] | — | Cairo-based fast line rasterizer |
| `rl/reward.py` | [ ] | — | L2 pixel, SSIM, VGG perceptual loss |
| `rl/stroke.py` | [ ] | — | Action space: line, bezier, arc strokes |
| `backends/cairo.py` | [ ] | — | Drawing.rasterize() backend |

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
| Poisson disk sampling | `gpyplotter/sampling.py`, `plottermagic/random/possion_disk_sampling.py`, axifun inline | `sampling/poisson.py` |
| NN pen optimization | `gpyplotter/line_processing.py`, `plottermagic/svg_processing/optimization.py` | `core/line_ops.py` (done) |
| shade_triangle/quad | `gpyplotter/shading.py`, `plottermagic/shading/simple_shapes.py` | `shading/hatch.py` |
| 2D transforms | `gpyplotter/geometry.py`, `plottersvg/utils/geometry.py` | `core/transforms.py` (done) |
| matplotlib display | `gpyplotter/plotting.py`, `plottermagic/graphing/plot.py` | `backends/matplotlib.py` (done) |

---

## Highest-Value Unported Techniques

These only exist in notebooks (no library code) and represent unique capabilities:

1. **Force-directed grid warping** — `axifun/grid warp 5 - force directed graphs.ipynb`
2. **Floyd-Steinberg / Stucki dithering** — `axifun/dither demo.ipynb`
3. **Hilbert curve halftoning** — `axifun/hilbert curves.ipynb`
4. **Fluid domain warping** — `axifun/fluid warping.ipynb`
5. **Strange attractors** — `axifun/dynamic system.ipynb`
6. **Morphological dilation contours** — `axifun/dilation.ipynb`
7. **Spline waves** — `axifun/spline waves.ipynb`
8. **SVG stitching** — `axifun/stich together SVGs*.ipynb`
9. **Continuous cross-hatching** (interpolated density) — `axifun/cross hatching bw contininous.ipynb`
10. **Ray tracer** (for depth/normal maps) — `axifun/ray tracer.ipynb`

---

## Suggested Build Priority

1. **Shading + Sampling** — these unlock the halftone pipeline
2. **CV/Halftone: crosshatch + line_scan** — the bread-and-butter photo-to-plotter technique
3. **SVG reader** — round-trip I/O
4. **Wallpaper groups** — unique artistic capability
5. **3D camera + scene** — enables perspective rendering
6. **Warp techniques** — force-directed grid, fluid warp
7. **Dithering** — Floyd-Steinberg, Stucki
8. **RL environment** — separate effort, depends on cairo backend

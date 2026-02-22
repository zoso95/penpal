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
| `core/geo.py` | [x] | — | clip, clip_rect, clip_away, intersect, contains_points (Shapely backend) |
| `core/layer.py` | [x] | — | Layer = name + style + Paths |
| `core/drawing.py` | [x] | — | Drawing with layer management, show/save, _repr_svg_ |
| `core/mesh.py` | [x] | — | Mesh class: rect/polar grids, warp, triangulate, to_paths |
| `core/noise.py` | [x] | — | simplex, fractal, ridged, curl, sine, domain_warp, compose (warp funcs for Mesh) |
| `backends/matplotlib.py` | [x] | `gpyplotter/plotting.py` | render() with grid lines |
| `io/svg_write.py` | [x] | `gpyplotter/inkscape.py` | Inkscape layer SVG, multi-layer save |
| `io/provenance.py` | [x] | `gpyplotter/saver.py` | Script capture, params JSON, git hash |

---

## Phase 2: Generators (DONE)

| penpal module | Status | Source | Key functions/techniques |
|---|---|---|---|
| `gen/curves.py` | [x] | `axifun/spirals.ipynb`, `roses.ipynb` | circle, spiral, polygon_regular, rose, lissajous, hilbert, concentric_circles |
| `gen/grids.py` | [x] | `axifun/distortion grids.ipynb` | grid, distorted_grid, barrel_distortion, noise_grid, polar_noise_grid |
| `gen/fields.py` | [x] | `axifun/perlin noise.ipynb`, `random walk.ipynb` | flow_field, noise_walk |
| `gen/flow.py` | [x] | `axifun/flow field*.ipynb` | trace, trace_bidirectional, simplex/fractal/curl/radial/spiral/constant/domain_warp fields, seed generators (line/grid/circle/ring/random/poisson), show_field |
| `gen/attractors.py` | [ ] | `axifun/dynamic system.ipynb` | Random matrix strange attractors: `x += M * sin(F1*x)^P + sin(F2*x)^P` |
| `gen/moire.py` | [ ] | `axifun/` (6 moire experiments) | Overlapping rotated concentric shapes (circles, polygons, splines) |
| `gen/contours.py` | [ ] | `axifun/textures.ipynb` | contour_lines, contour_grid — math function → iso-contours |
| `gen/spline_waves.py` | [ ] | `axifun/spline waves.ipynb` | Animated spline control points with velocity/acceleration |
| `gen/polar.py` | [ ] | `axifun/ribbons.ipynb` | Ribbon curves (offset pairs), polar grids |

---

## Phase 3: Shading + Sampling (DONE)

| penpal module | Status | Source | Key functions |
|---|---|---|---|
| `shading/hatch.py` | [x] | `gpyplotter/shading.py`, `plottermagic/shading/simple_shapes.py` | hatch_polygon, shade_polygon, shade_triangle, shade_quadrilateral, parallel_lines |
| `shading/polygon.py` | [ ] | `gpyplotter/polyshader.py` | PolygonShader base class, step_through_poly, step_and_shade_poly |
| `shading/arc.py` | [ ] | `plottermagic/shading/simple_shapes.py` | grid_arc_shading — diagonal strut fills |
| `shading/stipple.py` | [ ] | — | Dot/point-based fills |
| `shading/dilation.py` | [ ] | `axifun/dilated polygons` notebooks | Concentric inset polygons via Shapely buffer |
| `sampling/poisson.py` | [x] | `gpyplotter/sampling.py` (consolidated from 3 sources) | poisson_disk, poisson_disk_n |
| `sampling/tessellation.py` | [x] | `gpyplotter/tiling.py` | voronoi, delaunay, voronoi_edges |
| `sampling/noise.py` | [x] | — | (see core/noise.py — OpenSimplex warp funcs) |

---

## Phase 4: Symmetry (DONE)

| penpal module | Status | Source | Key functions |
|---|---|---|---|
| `symmetry/wallpaper.py` | [x] | `gpyplotter/tiling.py` | WallpaperGroup class — all 17 wallpaper groups |
| `symmetry/mandala.py` | [x] | — | cyclic, dihedral, radial_repeat |
| `symmetry/mirror_slice.py` | [x] | — | mirror_slice, mirror_slice_rect — Droste / recursive zoom effects |
| `symmetry/lattice.py` | [ ] | `gpyplotter/tiling.py` | Lattice types, fundamental domains |

---

## Phase 5: CV / Halftone (photo → plotter lines)

**Not yet started.** No `penpal/cv/` directory exists.

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

### Texture / Multi-Scale Decomposition
| penpal module | Status | Source | Technique |
|---|---|---|---|
| `cv/texture.py` — laplacian_pyramid | [ ] | `axifun/laplace pyramid.ipynb` | Decompose image into frequency bands via pyrDown/pyrUp. Each band rendered separately with different line techniques. Recombine for multi-scale detail. |
| `cv/texture.py` — repeat_blurs | [ ] | `axifun/repeat blurs.ipynb` | Progressive maximum_filter at increasing sizes [5,10,15,20,30,50,100]. Difference between scales reveals patterns at each frequency. Creates organic "snake skin" cell patterns. |
| `cv/texture.py` — voronoi_laplacian | [ ] | `axifun/paul replica - vonroni-less dense laplacian good.ipynb` | Poisson disk → Voronoi regions → flood-fill color assignment → per-region shading density from Laplacian band. The "snake skin painting" technique — organic cell-like fills driven by image frequency content. |

### Image Utilities
| penpal module | Status | Source | Key functions |
|---|---|---|---|
| `cv/image.py` | [ ] | `gpyplotter/image_lib.py` | load, gamma_correct, blur, sample, resize |
| `cv/edges.py` | [ ] | `axifun/edge detection.ipynb` | Canny, CLAHE, binary_dilation |
| `cv/segmentation.py` | [ ] | `axifun/kmean tones.ipynb` | KMeans tone separation for multi-pen |

---

## Phase 6: Warp / Distortion (image-driven geometry)

| penpal module | Status | Source | Technique |
|---|---|---|---|
| `cv/warp.py` — force_directed_grid | [ ] | `axifun/grid warp 5 - force directed.ipynb` | networkx graph, spring/repulsion constants from image brightness, iterative relaxation |
| `cv/warp.py` — grid_shift | [ ] | `axifun/grid shifting*.ipynb`, `radial grid shifting*.ipynb` | Row/column offsets from noise or radial functions |
| `cv/warp.py` — fluid_warp | [ ] | `axifun/fluid warping.ipynb` | Iterated domain warping: `g(x + g(x + g(x)))` |

---

## Phase 7: 3D Engine (DONE — basic pipeline)

| penpal module | Status | Source | Key classes/functions |
|---|---|---|---|
| `render3d/project.py` | [x] | `plottermagic/line_render/camera.py` | look_at, perspective, project_points, project_lines, viewport_map |
| `render3d/camera.py` | [x] | `plottermagic/line_render/camera.py` | Camera class with orbit() classmethod |
| `render3d/shapes.py` | [x] | `plottermagic/line_render/polygon.py`, `polyhedron.py` | Face3D (with texture hatching), Mesh3D (box, plane factories), Wireframe, TextureSpec |
| `render3d/scene.py` | [x] | `plottermagic/line_render/render.py` | Scene class: backface cull → project → sort → hidden line removal via Shapely difference → Drawing |
| `render3d/shading3d.py` | [x] | `plottermagic/shading/simple_shapes.py` | Integrated into Face3D.generate_texture_lines() — hatch in face-local 2D, map back to 3D |
| `render3d/sphere.py` | [ ] | `axifun/spheres*.ipynb` | Analytical sphere: lat/lon grid, hidden-line by normal dot product |
| `render3d/anaglyph.py` | [ ] | `plotterart/pieces/anaglyph/` | Stereo pair rendering (red/cyan offset cameras) |

**Done:** Camera, projection, shapes (Face3D/Mesh3D/Wireframe with textures), scene render pipeline with proper hidden line removal (front-to-back occlusion clipping via Shapely). Frustum clipping not needed — viewport_map handles the mapping.

**Not done:** Sphere primitive, anaglyph stereo rendering, NPR sketch rendering, moire surfaces.

### Phase 7b: Moire / 3D Surface Projection

The "oil slick" effect: project regular patterns (grids, concentric circles) onto bumpy 3D surfaces. The moire interference emerges naturally from perspective compression of the pattern over the surface deformation.

| penpal module | Status | Source | Technique |
|---|---|---|---|
| `gen/moire.py` — overlapping_patterns | [ ] | `axifun/` (6 moire experiments) | Overlapping rotated concentric circles, grids, line sets with slight angle/offset differences |
| `gen/moire.py` — surface_project | [ ] | `axifun/distortion grids*.ipynb` | Project regular pattern onto noise-deformed 3D mesh surface via camera → interference patterns |
| `render3d/surface.py` | [ ] | `axifun/distortion grids*.ipynb`, `radial grid shifting*.ipynb` | Deformable mesh surface: take core/Mesh, displace Z by noise/function, render as Face3D grid with pattern |

**Algorithm:** Define a regular grid in 3D. Displace Z-coordinates with noise (simplex, radial distortion, etc). The grid lines on the bumpy surface project to 2D through the camera, and the uneven compression creates moire interference. Can use existing `core/mesh.py` warping + `render3d/scene.py` projection.

### Phase 7c: NPR Sketch Rendering (3D model → realistic sketch)

Use 3D model geometry (normals, curvature) + lighting to generate hatching that looks like a hand-drawn sketch. Hatching follows principal curvature directions, density driven by lighting.

| penpal module | Status | Source | Technique |
|---|---|---|---|
| `render3d/lighting.py` | [ ] | — | Light class (point/directional), per-face diffuse+specular shading → intensity value |
| `render3d/npr.py` | [ ] | Hertzmann & Zorin, Winkenbach & Salesin | Curvature-driven hatching: estimate principal curvature directions, hatch along them, density from lighting |
| `render3d/contours.py` | [ ] | — | Silhouette extraction (normal ⊥ view), suggestive contours (curvature zero-crossings) |
| `render3d/loader.py` | [ ] | — | OBJ/STL mesh loader → Face3D/Mesh3D |

**Vision:** Load a 3D model → compute lighting → extract silhouettes + suggestive contours → fill lit surfaces with curvature-following hatching (sparse in highlights, dense in shadow) → plotter-ready sketch that looks hand-drawn.

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
| `rl/env.py` | [ ] | — | Gymnasium env: target image → stroke actions |
| `rl/rasterizer.py` | [ ] | — | Cairo-based fast line rasterizer |
| `rl/reward.py` | [ ] | — | L2 pixel, SSIM, VGG perceptual loss |
| `rl/stroke.py` | [ ] | — | Action space: line, bezier, arc strokes |
| `backends/cairo.py` | [ ] | — | Drawing.rasterize() backend |

---

## Phase 11: Effects & Simulation

New modules — not ported from old code, built fresh.

| penpal module | Status | Technique |
|---|---|---|
| `effects/cloth.py` | [ ] | Cloth simulation — spring/mass mesh that drapes, wrinkles, folds. Output as displaced line grids or draped patterns. |
| `effects/glass.py` | [ ] | Glass distortion — refracts/displaces lines behind a glass region (lens, pane, sphere). Snell's law or simplified radial distortion of line segments passing through the glass shape. |
| `effects/easing.py` | [ ] | Interpolation / easing library — envelope functions (ease-in, ease-out, bounce, elastic, overshoot, step, cubic, etc.) for animating parameters, modulating density, or shaping warp fields. |

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
- **Generators** — curves, grids, fields, flow tracing (comprehensive)
- **Shading** — polygon hatching (hatch, crosshatch, shade_triangle/quad)
- **Sampling** — Poisson disk, Voronoi/Delaunay tessellation
- **Symmetry** — wallpaper groups, mandala (cyclic/dihedral), Droste/mirror_slice
- **3D** — full render pipeline: camera, projection, shapes with textures, hidden line removal
- **I/O** — SVG write (Inkscape layers), provenance tracking

### Missing (by priority)
1. **CV/Halftone** — the entire photo-to-plotter pipeline (crosshatch, line scan, dithering, stippling) — this is the biggest gap
2. **CV/Texture** — Laplacian pyramid decomposition, repeat-blur frequency bands, Voronoi-Laplacian "snake skin" rendering
3. **Moire / 3D surface projection** — project patterns onto bumpy surfaces for interference effects ("oil slick")
4. **NPR sketch rendering** — lighting, curvature-driven hatching, silhouette/contour extraction from 3D models
5. **SVG reader** — can write SVGs but can't read them back
6. **Generators** — attractors, moire overlaps, contours, spline waves, polar/ribbons
7. **Warp** — force-directed grid, fluid warping, grid shifting
8. **Shading** — PolygonShader, arc shading, stipple, dilation fills
9. **3D extras** — sphere primitive, anaglyph stereo
10. **I/O** — GCode export, SVG path parser, SVG stitching, AxiDraw driver
11. **RL environment** — gymnasium env, cairo rasterizer, reward functions
12. **Effects** — cloth simulation, glass distortion, easing/interpolation envelopes

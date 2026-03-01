# penpal

A unified Python library for generative plotter art. Consolidates years of plotter experiments into one coherent toolkit — from 2D pattern generators to 3D NPR rendering to photo-to-line-art computer vision pipelines.

Everything converges on the same output: a `Drawing` with named layers, ready to export as multi-pen SVG for AxiDraw or any pen plotter.

```
Generators -> Paths -> Layer -> Drawing -> SVG / matplotlib
```

## Gallery

<p align="center">
<img src="gallery/03_flow_fields.png" width="30%" />
<img src="gallery/11_moire.png" width="30%" />
<img src="gallery/24_portrait_warp.png" width="30%" />
</p>
<p align="center">
<img src="gallery/25_death_textures.png" width="30%" />
<img src="gallery/02_attractors.png" width="30%" />
<img src="gallery/23_halftone.png" width="30%" />
</p>
<p align="center">
<img src="gallery/12_cloth_drape.png" width="30%" />
<img src="gallery/21_braid.png" width="30%" />
<img src="gallery/22_perspective_drape.png" width="30%" />
</p>
<p align="center">
<img src="gallery/27_stl_sketch.png" width="30%" />
<img src="gallery/07_envelopes.png" width="30%" />
<img src="gallery/06_fractals.png" width="30%" />
</p>
<p align="center">
<img src="gallery/15_wallpaper.png" width="30%" />
<img src="gallery/10_mandala.png" width="30%" />
<img src="gallery/16_droste.png" width="30%" />
</p>
<p align="center">
<img src="gallery/17_voronoi_hatched.png" width="30%" />
<img src="gallery/08_contours.png" width="30%" />
<img src="gallery/09_spline_waves.png" width="30%" />
</p>
<p align="center">
<img src="gallery/14_metaballs.png" width="30%" />
<img src="gallery/26_dithering.png" width="30%" />
<img src="gallery/13_polar_ribbons.png" width="30%" />
</p>
<p align="center">
<img src="gallery/20_lissajous.png" width="30%" />
<img src="gallery/04_noise_grid.png" width="30%" />
<img src="gallery/05_polar_noise_grid.png" width="30%" />
</p>
<p align="center">
<img src="gallery/19_barrel_distortion.png" width="30%" />
<img src="gallery/18_shading_fills.png" width="30%" />
<img src="gallery/01_basics.png" width="30%" />
</p>

## Quick Start

```bash
pip install -e .
# or with CV extras for photo-to-lines
pip install -e ".[cv]"
```

```python
import penpal
from penpal.gen import flow

d = penpal.Drawing(10, 8)  # 10x8 inches

# Trace a flow field
paths = flow.trace(flow.curl_field(), flow.seed_poisson(n=500))
d.layer('flow', color='#264653', linewidth=penpal.pen_width(0.2)).add(paths)

# Save multi-layer SVG (Inkscape layers for multi-pen plotting)
d.save('my_piece.svg')
d  # inline SVG preview in Jupyter
```

## What's In The Box

### Generators (`penpal.gen`)

| Module | What it does |
|--------|-------------|
| `curves` | Circle, spiral, polygon, rose, lissajous, hilbert, concentric circles |
| `grids` | Regular, distorted, barrel, noise, polar noise grids |
| `fields` | Flow field generation, noise walks |
| `flow` | Flow field tracing with 8 field types + 6 seed generators |
| `attractors` | Lorenz, Rossler, Clifford, de Jong, Bedhead, random attractors |
| `contours` | Contour line extraction from scalar fields, math functions, gaussian bumps |
| `envelopes` | Hyperbolic, diamond, string art, parabolic, cardioid envelopes |
| `spline_waves` | Physics-driven spline wave evolution |
| `polar` | Ribbon fills, concentric ribbons, polar functions/grids |
| `moire` | Oil slick, metallic grid, rotated grids, concentric moire, surface contour moire |
| `ifs` | Flame fractals (11 variations), Barnsley fern, Sierpinski, dragon curve |
| `cloth` | Cloth drape, braid, perspective drape (rainbow road), cloth fill |

### Computer Vision (`penpal.cv`)

Photo-to-plotter-lines pipeline:

| Module | What it does |
|--------|-------------|
| `halftone` | Crosshatch, line scan, edge detection, morphological halftone, dot grid, CMYK dot grid, mezzotint, voronoi stipple, spiral portrait |
| `texture` | Gradient warp ("death textures"), portrait warp (Bradway technique), integral warp, Laplacian pyramid decomposition/blending, repeat blur bands |
| `dither` | Floyd-Steinberg, Stucki, Jarvis-Judice-Ninke, Atkinson + dither-to-lines |
| `datasets` | Auto-downloading texture datasets (DTD: 47 categories, 5640 images) |

### 3D Rendering (`penpal.render3d`)

Full NPR (non-photorealistic rendering) pipeline:

- **STL loading** with decimation
- **Camera** with orbit positioning, perspective projection
- **Scene** with backface culling, depth sorting, hidden line removal (Shapely)
- **NPR sketch** rendering: curvature-driven hatching, lighting-based density, silhouette edges

### Shading & Sampling

| Module | What it does |
|--------|-------------|
| `shading/hatch` | Polygon hatching, crosshatch, shade triangle/quad |
| `shading/stipple` | Stipple fills (poisson, grid, jittered, random) |
| `shading/dilation` | Concentric inset polygon fills |
| `sampling/poisson` | Poisson disk sampling |
| `sampling/tessellation` | Voronoi, Delaunay tessellation |

### Symmetry

| Module | What it does |
|--------|-------------|
| `symmetry/wallpaper` | All 17 wallpaper groups |
| `symmetry/mandala` | Cyclic, dihedral, radial repeat |
| `symmetry/mirror_slice` | Droste / recursive zoom effects |

### Effects

| Module | What it does |
|--------|-------------|
| `effects/easing` | 20+ easing functions |
| `effects/metaballs` | Metaball fields, animated metaballs |

## Core Concepts

**Paths** is the workhorse type — an immutable collection of polylines (`List[np.ndarray]`). All generators return Paths. Transform, clip, filter, combine, then add to a layer.

```python
from penpal.gen.curves import spiral
from penpal.core.geo import clip_rect

p = spiral(outer_r=5, turns=8)
p = p.rotate(45).scale(1.5).translate(5, 4)
p = p.clip_rect(0, 0, 10, 8)  # clip to paper bounds
```

**Drawing** manages named layers with independent styles. Each layer maps to a pen on the plotter.

```python
d = penpal.Drawing(10, 8)
d.layer('outline', color='black', linewidth=penpal.pen_width(0.3)).add(outline_paths)
d.layer('fill', color='#e63946', linewidth=penpal.pen_width(0.2)).add(fill_paths)
d.save('piece.svg')  # Inkscape layers for multi-pen workflow
```

## Examples

30 Jupyter notebooks in `examples/` covering every module:

| Notebook | Technique |
|----------|-----------|
| `00_basics` | Drawing, layers, transforms, SVG export |
| `flow_fields` | Flow field tracing with curl, spiral, radial fields |
| `attractors` | Strange attractor systems |
| `fractals` | IFS flame fractals, Barnsley fern |
| `cloth_drapes` | Cloth drape, braid, perspective drape |
| `moire_patterns` | Moire interference patterns |
| `halftone` / `halftone_gallery` | Photo halftoning techniques |
| `death_textures` | Gradient-warped texture fields |
| `portrait_warp` | Bradway portrait technique, Laplacian blending |
| `wallpaper_groups` | Wallpaper group symmetry |
| `mandalas` | Mandala and radial symmetry |
| `stl_sketch` | 3D STL model NPR rendering |
| `voronoi_depth` / `voronoi_hatched` | Voronoi-based shading |
| `envelopes` | Line envelope patterns |
| `contours` | Contour extraction from scalar fields |
| `spline_waves` | Physics-driven wave evolution |
| `dithering` | Error diffusion dithering |
| `polar_ribbons` | Ribbon and polar pattern fills |
| `shading_fills` | Polygon hatching and stippling |

## Development

```bash
# Install in dev mode
pip install -e ".[cv]"

# Run tests (248 tests)
python -m pytest tests/ -v

# Launch Jupyter
jupyter lab examples/
```

## Dependencies

**Core:** numpy, matplotlib, shapely, scipy, opensimplex

**CV extras** (`pip install -e ".[cv]"`): opencv-python, scikit-image

## License

MIT

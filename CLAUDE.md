# penpal — Unified Plotter Art Library

## Project Overview

penpal consolidates three old plotter art libraries (gpyplotter, plottermagic, plottersvg) into one library with a unified core. The critical design goal: **all workflows (2D, 3D, CV, RL) converge on the same output abstraction** — `Drawing`.

## Architecture

```
Generators → Paths → Layer → Drawing → SVG / matplotlib / cairo
```

- **Paths** is the workhorse type — a manipulable collection of polylines (List[np.ndarray])
- **Layer** = name + style + Paths
- **Drawing** = physical paper dimensions + ordered layers
- **All generators return Paths** (not raw arrays)

## Core Types

```python
Polyline = np.ndarray  # shape (N, D) where D=2 or D=3
Lines = List[np.ndarray]  # list of polylines
```

Convention: column vectors, `matrix @ points`. 2D = 3x3 homogeneous, 3D = 4x4 homogeneous.

## Module Structure

```
penpal/
├── core/           # types, paths, layer, drawing, transforms, units, line_ops, geo
├── backends/       # matplotlib (display), cairo (fast raster for RL)
├── io/             # svg_write, svg_read, gcode, provenance
├── gen/            # curves, grids, fields, attractors, moire, contours
├── shading/        # hatch, polygon shader, stipple
├── sampling/       # poisson disk, tessellation, noise
├── symmetry/       # wallpaper groups, mandala
├── cv/             # halftone, edges, warp, image utils
├── render3d/       # scene, camera, shapes, 3D shading, clipping
└── rl/             # gymnasium env, cairo rasterizer, reward, stroke
```

## Working With This Codebase

### Running Tests

```bash
cd /Users/gnb/dev/penpal
.venv/bin/python -m pytest tests/ -v
```

### Key Design Decisions

1. **Generators return Paths, not raw arrays** — avoids wrapping pain in notebooks
2. **Shapely is a hidden backend** — geo.py accepts/returns numpy, uses Shapely internally. Uses `shapely.contains_xy()` (not deprecated `shapely.vectorized.contains`)
3. **Grid lines are display-only** — shown in `_repr_svg_()` and `show()`, not burned into saved SVGs
4. **Immutable transform pattern** — Paths methods return new Paths, never mutate
5. **matplotlib for display, custom XML for SVG save** — SVG writer supports Inkscape layers (`<g inkscape:groupmode="layer">`) for multi-pen plotting

### Common Pitfalls

- `spiral()` parameter is `outer_r`, not `radius`
- `Paths.filter()` parameter is `min_length`, not `min_len`
- `hatch()` density param needs `int()` cast for np.linspace
- matplotlib 3.8+ removed `cs.collections` from QuadContourSet — use `cs.allsegs` with fallback
- When adding to notebooks, call generators directly — they return Paths now

### Old Code Reference

Source files to port from are at:
`/Users/gnb/dev/plotter-backups/drive-download-20260218T174932Z-1-001/`

See `ROADMAP.md` for the full mapping of old techniques → penpal modules.

### Virtual Environment

```bash
source .venv/bin/activate
# or use .venv/bin/python directly
```

### Dependencies

Core: numpy, matplotlib, shapely, scipy, opensimplex
Optional: opencv-python, scikit-image (cv), gymnasium, pycairo (rl)
Dev: pytest, pytest-cov, jupyterlab

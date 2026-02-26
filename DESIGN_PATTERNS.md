# Design Patterns — Brainstorm

Observations on recurring patterns across generators. Goal: eventually extract
composable primitives so new effects = snapping together existing pieces, not
reimplementing algorithms.

**Status: brainstorm.** Collecting patterns as we port techniques. Will refactor
once we have ~10-15 techniques and the right abstractions are obvious.

---

## Existing Good Patterns

### noise.py — WarpFunc pipeline

Each noise type returns a `WarpFunc = (x, y) -> (dx, dy)`. Combinators build
complex behavior from simple pieces:

```python
mesh.warp(noise.fractal(amplitude=0.3, octaves=4))
mesh.warp(noise.compose(noise.simplex(0.2), noise.sine(0.1, freq_x=3)))
mesh.warp(noise.domain_warp(noise.curl(0.5), warp_amplitude=1.0))
```

Why it works:
- Single clear interface (WarpFunc)
- Each function is one idea (simplex, ridged, curl, sine)
- `compose()` = sum displacements, `domain_warp()` = chain coordinates
- Plugs directly into Mesh.warp()

### flow.py — FieldFunc + seeds + trace

Separates the three concerns of flow field art:

```python
field = flow.simplex_field(frequency=0.8, seed=42)
seeds = flow.seeds_line(0, 5, 8, 5, n=80)
paths = flow.trace(field, seeds, steps=500, step_size=0.03)
```

Why it works:
- Field is just `(x, y) -> angle` — swap in any function
- Seed strategy is independent of field
- Tracing params (steps, step_size, momentum) are separate knobs
- Custom fields are trivial: `lambda x, y: x * 0.5 + y * 0.3`

---

## Moire Decomposition

The current moire generators are monolithic. Here's what they decompose into:

### oil_slick
```
concentric_rings(n=300, max_r=15)
  → noise_z_project(noise_fn, z_base=2.0)     # the "oil slick" step
  → clip_circle(r=4.5)
```

### metallic_grid
```
parallel_lines(n=180, extent=15, directions='both')
  → noise_z_project(noise_fn, z_base=2.0)     # same step as oil_slick!
```

### rotated_grids
```
parallel_lines(n=80, extent=6)
  → overlay(angles=[0, 3])                     # copies with rotation offsets
```

### concentric_circles
```
concentric_rings(n=80, max_r=5)
  → overlay(centers=[(-0.3, 0), (0.3, 0)])     # copies with position offsets
```

### concentric_shapes
```
shape_copies(shape, scales=linspace(0.01, 5, 100))
  → overlay(offsets=[(0, 0, 0), (0.1, 0.05, 4)])  # copies with translate+rotate
```

### surface_contour_moire
```
gaussian_surface(n_bumps=20)
  → contour_extract(n_levels=100)
  → overlay(perturbation=0.02)                 # nearly-identical copy
```

### Recurring primitives:
- **noise_z_project**: the perspective-through-noise trick (x/z, y/z where z=noise+base).
  Shows up in oil_slick AND metallic_grid. Input geometry doesn't matter.
- **overlay**: take one set of paths, make N copies with slight offsets (rotation,
  translation, different noise params). The core of what makes "moire" — interference
  between nearly-identical copies.
- **contour_extract**: scalar field → Paths. Shows up in surface_contour_moire,
  probably will show up in topographic effects, metaballs, reaction-diffusion.

---

## Hypothetical Primitives

### Geometry Sources (→ Paths)
- `concentric_rings(n, max_r, n_points)` — already in moire.py, could be in curves.py
- `parallel_lines(n, extent, direction)` — already in grids.py as grid()
- `shape_copies(shape, scales)` — concentric scaled copies of arbitrary curve

### Point-wise Effects (Paths → Paths)
- `noise_z_project(paths, noise_fn, z_base)` — perspective division through noise field
- `field_warp(paths, warp_fn)` — displace points by a WarpFunc (already: mesh.warp)
- `radial_warp(paths, r_func)` — warp radial distance from origin

### Scalar Fields (→ 2D array or eval function)
- Gaussian bump sum (surface_contour_moire uses this)
- Noise fields (simplex, perlin, fractal)
- Metaball implicit surfaces (future)
- Reaction-diffusion state (future)

### Field → Paths Converters
- `contour_extract(field, levels)` — marching squares / matplotlib contour
- `threshold_boundary(field, value)` — single isoline

### Combinators
- `overlay(paths, offsets)` — N copies with transform offsets
- `compose(effect1, effect2, ...)` — chain effects (already: noise.compose)
- `layer_map(func, paths_list)` — apply same effect to multiple layers

---

## Two API Layers: Batteries-Included + Composable

Keep the hardcoded one-liner generators (oil_slick, metallic_grid, etc.) — they're
great for just fucking around and getting cool output fast. But also expose the
underlying primitives so you can build your own.

```python
# Layer 1: Batteries included — instant gratification
layers = moire.oil_slick(n_rings=300, seed=42)

# Layer 2: Composable — go deeper, swap pieces
rings = geo.concentric_rings(300, max_r=15)
projected = effects.noise_z_project(rings, noise_fn, z_base=2.0)
clipped = projected.clip_circle(4.5)
```

Both levels are useful:
- **Hardcoded generators** = great for hyperparameter tuning. Short function,
  clear params, easy to sweep/grid-search. Pass to a genetic algo or just
  tweak interactively.
- **Composable primitives** = great for invention. Swap concentric_rings for
  a hexagonal grid, replace noise_z_project with a gravity warp, chain two
  effects that were never meant to go together.

### Hyperparameter Tuning Use Case

A short generator function with named params is the perfect target for automated
tuning. Imagine:

```python
# Define the search space
space = {
    'n_rings': (50, 500),
    'persistence': (0.05, 0.3),
    'z_base': (1.5, 4.0),
    'clip_radius': (3.0, 6.0),
}

# Genetic algo: render a grid, pick favorites, evolve
tuner = penpal.evolve(make_drawing, space, population=12)
tuner.show_generation()  # renders 12 variants in a grid
tuner.select([0, 3, 7])  # pick the ones you like
tuner.next_generation()   # breed + mutate
```

This is a natural fit for generative art where "good" is subjective — human-in-the-loop
evolution. Could also do fully automated fitness (line density, coverage uniformity,
complexity metrics) for batch exploration.

---

## Open Questions

- Should `noise_z_project` be a Paths method? (`paths.project_through_noise(...)`)
  Or a standalone function in an `effects` module?
- How does clipping fit in? Currently Paths has `.clip()`, but circle clipping is manual.
- The `overlay` concept is interesting — it's not just "copy and offset", it's
  "generate N variants with different parameters". For moire, the parameter that
  varies is the noise (oil slick) or the position (concentric circles) or the
  angle (rotated grids). Is there a clean abstraction for "same structure,
  varied parameter"?
- `pen_width_mm()` — need a unit-aware pen width helper. Currently `pen_width()`
  only returns inches. Should probably live on Drawing or be unit-system aware.

---

## Multiple Pipeline Paradigms

Not everything should be the same kind of pipeline. Different workflow families
have different natural composition patterns. They all converge at the end:
**everything produces Paths → Layer → Drawing**.

### Procedural / Functional (mesh, noise, moire, flow fields)
- Pure function composition: `mesh.warp(noise.curl(0.5))`
- Stateless, reproducible (seed-based)
- Lends itself to: WarpFunc, FieldFunc, compose(), pipe()

### Image-based (CV: halftone, edges, segmentation, warp)
- Starts from raster (numpy/opencv), processes through pixel-space
- Only becomes Paths at the very end (contour extraction, hatch fill, etc.)
- Lends itself to: opencv-style sequential transforms, threshold → vectorize
- Different input type (image) so different pipeline entry point

### Scene graph (3D rendering, camera, lighting)
- OOP: Scene has Camera, Meshes, Lights
- Render step projects 3D → 2D silhouettes/contours → Paths
- Lends itself to: builder pattern, render settings objects

### Simulation (cloth, physics, reaction-diffusion, metaballs)
- Stateful time-stepping: init state → step() N times → extract final state
- Paths come from state snapshot (contour of RD field, cloth mesh edges, etc.)
- Lends itself to: Simulator class with .step() and .to_paths()

### The convergence point
All of these are different ways to **generate Paths**. The Drawing/Layer/SVG
system doesn't care how the Paths were made. So the pipeline design should
respect each family's natural paradigm rather than forcing one pattern on
everything.

---

## What To Watch For (as we port more techniques)

- [ ] Does noise_z_project show up outside of moire? (e.g., 3D rendering effects?)
- [ ] Does contour_extract show up outside of moire? (metaballs, reaction-diffusion, topo maps)
- [ ] What other "point-wise effects" emerge? (cloth sim displacement? gravity warp?)
- [ ] Are there patterns in how layers/colors get assigned? (auto-color-cycling?)
- [ ] Does the overlay pattern generalize to non-moire effects?

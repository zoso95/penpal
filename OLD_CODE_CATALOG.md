# Old Plotter Art Code Catalog

Comprehensive index of all files in:
`/Users/gnb/dev/plotter-backups/drive-download-20260218T174932Z-1-001/`

Generated 2026-02-25.

---

## Directory Structure Overview

```
drive-download-20260218T174932Z-1-001/
├── axifun/                    # ~100+ experiment notebooks (the main lab)
│   ├── blender/               # Blender 3D model SVG exports
│   │   └── keepers/           # Curated Blender outputs
│   ├── grids/                 # SVG output: grid patterns
│   ├── more_triangles/        # SVG output: triangle patterns
│   ├── pink_wave/             # SVG output: wave patterns
│   ├── triangles/             # SVG output: triangle patterns
│   ├── vgg/                   # VGG neural network code (TensorFlow)
│   │   └── test_data/
│   ├── voroni/                # SVG output: Voronoi patterns
│   │   ├── dixie/
│   │   ├── two color/
│   │   ├── v1/
│   │   └── v2/
│   └── walks/                 # SVG output: random walk / flow field patterns
├── gpyplottermod/             # First plotter library (gpyplotter)
│   ├── draw svgs/             # AxiDraw control & SVG drawing notebooks
│   ├── gpyplotter/            # Library source code
│   ├── notebooks/             # Usage notebooks
│   │   ├── experimental notebooks/
│   │   ├── portraits/
│   │   ├── projective geometry experiments/
│   │   ├── shaded polygons/
│   │   └── tiling/
│   └── tests/
├── plottermagic/              # Second plotter library
│   └── plottermagic/
│       ├── geometry/          # 3D geometry transforms
│       ├── graphing/          # Matplotlib plotting helpers
│       ├── line_render/       # 3D line rendering pipeline
│       ├── random/            # Sampling (Poisson disk, sphere)
│       ├── shading/           # Triangle/quad shading
│       └── svg_processing/    # SVG path optimization
├── plotterart/                # Art piece experiments
│   └── pieces/
│       ├── anaglyph/          # Stereoscopic 3D experiments
│       │   └── experiments/
│       │       └── triangles/
│       └── polygon_tess/      # Polygon tessellation with graph partitioning
│           └── experiments/
├── plottersvg/                # SVG DOM library (newer)
│   ├── examples/
│   └── plottersvg/
│       ├── elements/          # SVG path/shape elements
│       ├── io/                # SVG file reader
│       ├── svg/               # SVG container/group/layer
│       └── utils/             # Parsing, geometry, display utilities
├── plottersvg_old/            # SVG DOM library (older version)
│   ├── examples/
│   ├── plottersvg/
│   └── svgelements/
└── svgs/                      # 513 SVG output files
    ├── notebooks/
    │   ├── crosshatching/
    │   ├── dots/
    │   ├── old results pre saving lib/
    │   ├── projections/
    │   ├── shaded_polygons/
    │   └── wallpaper/
    └── production/
        └── 2019/11_nov/white_hole/
```

---

## axifun/ -- Experiment Notebooks

The main experimentation directory with ~100+ Jupyter notebooks. Each notebook is a standalone experiment exploring a plotter art technique.

### Cross-Hatching (Image -> Parallel Lines)

| File | Summary |
|------|---------|
| `axifun/cross hatching bw contininous.ipynb` | BW cross-hatching: draws parallel lines at 45/-45 degree angles through tonal threshold bands of a grayscale image. Density varies by brightness level. |
| `axifun/cross hatching cmyk-continious.ipynb` | CMYK cross-hatching: separates image into C/M/Y/K channels, draws each with offset angles (60/-30, 45/-45, 30/-60, 15/-75), producing multi-pen color portraits. |
| `axifun/cross hatching cmyk.ipynb` | CMYK cross-hatching variant with discrete threshold bands instead of continuous tone. |
| `axifun/cross hatching dont fuck with this one.ipynb` | Production-quality BW cross-hatching. Appears to be the "golden" version. |
| `axifun/cross hatching dont fuck with this one-Copy1.ipynb` | Copy of the production cross-hatching notebook. |
| `axifun/cross hatching emma stone.ipynb` | Cross-hatching applied specifically to an Emma Stone portrait. |
| `axifun/cross hatching test-Copy1.ipynb` | Early cross-hatching test/prototype. |

### Line-by-Line Scanning (Image -> Horizontal Lines)

| File | Summary |
|------|---------|
| `axifun/line by line scan.ipynb` | Row-by-row raster scanning: thresholds image at multiple levels, draws horizontal line segments where pixels are dark. Produces tonal portraits from horizontal strokes. |
| `axifun/line by line scan-CMYK.ipynb` | CMYK variant of line-by-line scanning with separate color channels. |
| `axifun/line by line scan-CMYK-Copy1.ipynb` | Copy of CMYK line scan. |
| `axifun/line by line scan-Copy2.ipynb` | Copy of basic line scan. |
| `axifun/line by line scan-flowers.ipynb` | Line-by-line scanning applied to a flower image. |
| `axifun/line by line scan-GEOFF.ipynb` | Line-by-line scanning applied to a portrait of Geoff. |
| `axifun/line by line scan-rotated.ipynb` | Line-by-line scanning with lines drawn at an angle instead of horizontal. |
| `axifun/line by line scan-rotated-Copy2.ipynb` | Copy of rotated line scan. |
| `axifun/line by line scan-wiggle.ipynb` | Line-by-line scanning where lines wiggle/oscillate instead of being straight. |
| `axifun/suiqggly line by line.ipynb` | Squiggly variant of line-by-line scanning with wavy lines. |
| `axifun/line by line and outline.ipynb` | Combines line-by-line scanning with Canny edge detection outlines overlaid. |

### Dilation/Erosion Contours (Image -> Topographic Contours)

| File | Summary |
|------|---------|
| `axifun/dilation.ipynb` | Creates topographic-map contour portraits by repeated binary erosion of thresholded image masks. Each erosion level produces a concentric contour ring. Uses gamma-aware preprocessing. |
| `axifun/dilation additive.ipynb` | Additive variant: uses multiple brightness thresholds, erodes each separately, sums contour maps to create denser contours in darker regions. |
| `axifun/countours.ipynb` | Contour extraction from images using matplotlib's contourf/contour with multiple threshold levels. |

### Grid Warping & Distortion

| File | Summary |
|------|---------|
| `axifun/distortion grids - good.ipynb` | Warped grids: creates a regular grid, perturbs vertices with random noise, fills each cell with shaded parallel lines. The "good" production version. |
| `axifun/distortion grids.ipynb` | Basic grid distortion experiment with random vertex perturbation. |
| `axifun/distortion grids-multidimensional.ipynb` | Multi-dimensional grid distortion exploring higher-order perturbation. |
| `axifun/distortion grids-multidimensional-Copy1.ipynb` | Copy of multi-dimensional grid distortion. |
| `axifun/grid shifting.ipynb` | Grid shifting: creates warped grids with noise-perturbed vertices and shades cells with parallel lines, randomly assigning cells to color layers. |
| `axifun/grid warp 5 - force directed graphs.ipynb` | Force-directed graph relaxation: grid vertices are pushed/pulled based on image brightness to create organic warped grids. |
| `axifun/grid warp photo.ipynb` | Grid warping driven by photo brightness values to control vertex displacement. |
| `axifun/grid warp photo - bad sampling.ipynb` | Failed experiment: grid warp photo with poor sampling. |
| `axifun/grid warp photo - bad threshold grid.ipynb` | Failed experiment: grid warp photo with poor thresholding. |
| `axifun/grid warp try 4 - pushing and repelling lines.ipynb` | Grid warping where lines push and repel based on proximity. |
| `axifun/radial grid shifting.ipynb` | Polar coordinate grids with noise perturbation on radius and angle. |
| `axifun/radial grid shifting + distortion.ipynb` | Combines radial grid with barrel/pincushion lens distortion. |
| `axifun/radial grid shifting bands.ipynb` | Radial grid with banding effects. |
| `axifun/radial grid shifting- multilayer.ipynb` | Multi-layer/multi-color radial grid shifting. |
| `axifun/radial grid shifting-Copy1.ipynb` | Copy of radial grid shifting. |
| `axifun/schism grid shift.ipynb` | Grid shifting with intentional discontinuities/schisms creating split patterns. Noise-perturbed vertices with periodic offset jumps. |
| `axifun/mc grids.ipynb` | Monte Carlo grids: cartesian and polar grids with random perturbation functions. Explores both rectangular and radial grid warping. |

### Voronoi / Delaunay / Tessellation

| File | Summary |
|------|---------|
| `axifun/vonroni.ipynb` | Voronoi/Delaunay tessellation from Poisson disk samples weighted by image brightness. Denser points in darker areas, triangulated with Delaunay. |
| `axifun/vonroni-dna affect.ipynb` | Voronoi diagram with DNA-like connecting strand effects between regions. |
| `axifun/paul replica.ipynb` | Portrait reproduction using brightness-weighted sampling + Delaunay triangulation. |
| `axifun/paul replica - vonroni.ipynb` | Paul portrait with Voronoi tessellation overlay. |
| `axifun/paul replica - vonroni-less dense laplacian good.ipynb` | Less dense Voronoi portrait with Laplacian pyramid preprocessing. Marked as "good". |
| `axifun/paul replica - vonroni-less dense- two color.ipynb` | Two-color Voronoi portrait with separate layers for light and dark. |
| `axifun/paul replica- triangles laplace.ipynb` | Portrait with Delaunay triangulation and Laplacian pyramid preprocessing. |
| `axifun/paul work.ipynb` | Work-in-progress portrait experiments. |
| `axifun/delany triangle grid warp.ipynb` | Delaunay triangulation of brightness-weighted multinomial samples, creating triangle meshes that are denser in darker image regions. |
| `axifun/triangulation.ipynb` | Basic Delaunay triangulation of random points. Simple test notebook. |
| `axifun/triangle grid.ipynb` | Delaunay triangulation of Gaussian-distributed points, with each triangle shaded by parallel lines. Supports skip patterns for visual interest. |

### Halftone / Dot Grid

| File | Summary |
|------|---------|
| `axifun/dot grid.ipynb` | BW halftone dots: divides image into grid cells, draws circles sized by local mean brightness. Produces classic halftone effect. |
| `axifun/dot grid cymk.ipynb` | CMYK halftone dots: separate dot grids for each color channel with angle offsets. |
| `axifun/Sphere effect.ipynb` | Concentric circle halftone: draws nested circles at grid positions with radius proportional to local image brightness. Produces a sphere-like 3D appearance. |

### Stipple / Mezzotint / Random Sampling

| File | Summary |
|------|---------|
| `axifun/mezzotint.ipynb` | Mezzotint/stipple: uses multinomial sampling weighted by pixel brightness to scatter dots/marks. Denser stippling in darker areas. |
| `axifun/mezzotint-CMYK.ipynb` | CMYK mezzotint with separate stipple layers per color channel. |
| `axifun/disk sampling - basic.ipynb` | Poisson disk sampling with minimum distance modulated by image brightness. Produces even point distributions. |
| `axifun/disk sampling + triangulation.ipynb` | Poisson disk sampling followed by Delaunay triangulation to create mesh portraits. |

### Spiral / Parametric Curves

| File | Summary |
|------|---------|
| `axifun/spirals.ipynb` | Archimedean spiral portrait: traces a spiral from center outward with sine-wave amplitude modulated by pixel brightness along the path. |
| `axifun/roses.ipynb` | Rose curves (rhodonea): generates r=cos(k*theta) parametric curves with various n/d ratios. |
| `axifun/front face rose.ipynb` | Rose curve composition: inner rose curve with outer petal ring, filtered by distance. Creates logo-like radial designs. |
| `axifun/front face logo.ipynb` | Line envelope logo: draws 1/x hyperbolic line envelopes in four quadrants to create a diamond/star pattern. Same as `1 over x grids.ipynb` but with line-by-line scanning combined. |

### Space-Filling Curves

| File | Summary |
|------|---------|
| `axifun/hilbert curves.ipynb` | Hilbert space-filling curves: divides image into grid cells, draws variable-order Hilbert curves per cell based on local brightness. Denser curves in darker regions. |

### Flow Fields / Random Walks / Noise

| File | Summary |
|------|---------|
| `axifun/random walk - perlin noise.ipynb` | Flow fields: particles follow simplex/Perlin noise velocity fields across the canvas. Traces are collected as polylines. |
| `axifun/perlin noise.ipynb` | Perlin noise visualization and exploration. |
| `axifun/fluid warping.ipynb` | Fluid-dynamics-inspired warping of image content using noise-based displacement fields. |
| `axifun/sun random walk.ipynb` | K-means color clustering of a sun image, then random walkers constrained within each cluster's connected components. Walkers produce organic line textures within color regions. |

### Edge Detection

| File | Summary |
|------|---------|
| `axifun/edge detection.ipynb` | Canny edge detection applied to images, extracting contour lines for plotter output. |
| `axifun/edge + tone.ipynb` | Combines Canny edge detection with tonal cross-hatching. Overlays edge outlines on hatched tonal regions. |
| `axifun/skimage.ipynb` | Scikit-image edge detection exploration: tries Roberts, Sobel, Scharr, Prewitt edge detectors and various threshold methods on images. |

### Clustering / Segmentation

| File | Summary |
|------|---------|
| `axifun/c-c-c-clustering.ipynb` | K-means color clustering experiments on images. |
| `axifun/clustering and triangulation.ipynb` | K-means clustering combined with Delaunay triangulation for segmented mesh generation. |
| `axifun/kmean tones.ipynb` | K-means tonal separation: clusters image into tone bands, creates erosion contours per cluster, outputs separate SVG layers per color/tone. |
| `axifun/kmean tones-Copy1.ipynb` | Copy of K-means tones. |
| `axifun/kmeans and contours.ipynb` | K-means clustering followed by contour extraction per cluster. |
| `axifun/sun.ipynb` | K-means color segmentation of a sun photograph into 6 clusters, then erosion-contour rendering per cluster. Each cluster becomes a separate SVG layer for multi-pen plotting. |
| `axifun/sun mask.ipynb` | K-means segmentation of sun image, then spline-wave curves masked to each cluster's connected components. Combines random walk curves with cluster masks. |

### Directional Masking / Refraction

| File | Summary |
|------|---------|
| `axifun/random directional masks.ipynb` | Rotated hatching per brightness band: for each tonal threshold, draws parallel lines at a different angle, masked to the threshold region. Creates directional texture variation. |
| `axifun/refraction.ipynb` | Refraction simulation: parallel lines change angle when crossing brightness boundaries in an image, simulating light refraction through a lens. |
| `axifun/refraction continious.ipynb` | Continuous refraction variant with smoother angle transitions. |

### Dynamic Systems / Chaos / Attractors

| File | Summary |
|------|---------|
| `axifun/dynamic system.ipynb` | Strange attractor generation: iterates random matrix transformations to produce chaotic trajectories. Traces form attractor-like patterns. |
| `axifun/dynamic system-Copy1.ipynb` | Copy of dynamic system notebook. |
| `axifun/eric_s thing.ipynb` | Flame fractal / chaos game: implements IFS (iterated function system) with 11 variations (linear, sinusoidal, spherical, swirl, horseshoe, polar, handkerchief, heart, disc, spiral, hyperbolic). Renders via chaos game algorithm with postprocessing (gamma, KDE, Gaussian blur). |
| `axifun/eric_s thing plotter.ipynb` | Plotter-adapted version of flame fractal chaos game. |

### Spline / Wave / Ribbon Patterns

| File | Summary |
|------|---------|
| `axifun/spline waves.ipynb` | Random-walk control points with cubic spline interpolation. Produces flowing wave-like parallel curves. |
| `axifun/spline contours.ipynb` | Contour extraction from images using `skimage.measure.find_contours`, then interpolating between contour halves to create filled shading regions. |
| `axifun/ribbons.ipynb` | Ribbon patterns: sinusoidal boundary curves interpolated with cosine easing to create flowing ribbon-like forms between parallel curves. |

### Geometric Patterns

| File | Summary |
|------|---------|
| `axifun/1 over x grids.ipynb` | Line envelope patterns: draws lines between interpolated points on two axes, creating hyperbolic envelope curves forming a diamond/star shape. |
| `axifun/diamond.ipynb` | Diamond pattern: random line segments along diamond edges with random spatial offsets, creating scattered diamond-shaped line textures. |
| `axifun/slanted lines.ipynb` | Random slanted line segments along one edge of a diamond with large random offsets, creating scattered directional line textures. |
| `axifun/textures.ipynb` | Texture experiments and explorations. |
| `axifun/grid random colors.ipynb` | Warped grid with cells randomly assigned to 4 color layers for multi-pen plotting. |

### Spheres / 3D Effects

| File | Summary |
|------|---------|
| `axifun/spheres.ipynb` | Random circles with Zipf-distributed radii. Simple scatter of unfilled circles. |
| `axifun/spheres4dayz.ipynb` | Sphere compositions: generates points inside unit spheres, K-means clusters them, draws convex hulls and Delaunay triangulations per cluster. Creates organic sphere-packing patterns. |

### Image Processing / Preprocessing

| File | Summary |
|------|---------|
| `axifun/laplace pyramid.ipynb` | Laplacian pyramid image decomposition: builds Gaussian/Laplacian pyramids using pyrDown/pyrUp, explores frequency-band separation for per-band line rendering. |
| `axifun/repeat blurs.ipynb` | Iterative maximum filter blur exploration: applies progressively larger max filters to an image and computes differences between blur levels. |
| `axifun/dither demo.ipynb` | Dithering algorithm demonstration. |
| `axifun/dither test.ipynb` | Dithering test/exploration. |

### Photo Realism / Neural Network Approaches

| File | Summary |
|------|---------|
| `axifun/photo realism nn.ipynb` | Neural network-guided line placement: uses VGG19 feature matching to iteratively add random lines that minimize perceptual distance to a target image. (Experimental, incomplete.) |
| `axifun/photo realism no NN.ipynb` | Photo realism without neural networks. |
| `axifun/photo realism (fast I think).ipynb` | Fast photo realism variant. |
| `axifun/photo realism qt graph.ipynb` | Photo realism using quadtree graph structures. |
| `axifun/qt graph stuff.ipynb` | Quadtree graph exploration for image partitioning. |

### Data Visualization

| File | Summary |
|------|---------|
| `axifun/stars.ipynb` | Star catalog data visualization: reads astronomical star data and plots star positions/magnitudes for plotter output. |
| `axifun/ig data parser and analysis.ipynb` | Instagram data parsing and analysis. |
| `axifun/ig scraper.ipynb` | Instagram scraping tool. |
| `axifun/instagram keywords.ipynb` | Instagram keyword analysis. |

### SVG Stitching / Utilities

| File | Summary |
|------|---------|
| `axifun/stich together SVGs (from lineset).ipynb` | SVG stitcher: combines multiple SVG files into one multi-layer Inkscape SVG using BeautifulSoup. Reads paths from separate files, wraps each in an Inkscape layer group. |
| `axifun/stich together SVGs (from paths).ipynb` | SVG stitcher variant for path-based SVGs. |
| `axifun/stich together SVGs (from polylines).ipynb` | SVG stitcher variant for polyline-based SVGs. |
| `axifun/personal library test.ipynb` | Tests importing the gpyplotter library. |

### Miscellaneous / Untitled

| File | Summary |
|------|---------|
| `axifun/diagonal lines in matrix test.ipynb` | Test: extracting values along diagonal lines in a matrix using scipy.ndimage.map_coordinates. Scratch pad for line-sampling technique. |
| `axifun/hmm weird test thing.ipynb` | Mostly empty test notebook with matplotlib/image imports. |
| `axifun/Untitled.ipynb` | Untitled notebook (likely scratch). |
| `axifun/Untitled1.ipynb` | Untitled notebook. |
| `axifun/Untitled2.ipynb` | Untitled notebook. |
| `axifun/Untitled3.ipynb` | Untitled notebook. |

### axifun/vgg/ -- VGG Neural Network Code

| File | Summary |
|------|---------|
| `axifun/vgg/vgg16.py` | VGG16 TensorFlow implementation for feature extraction. |
| `axifun/vgg/vgg19.py` | VGG19 TensorFlow implementation for perceptual loss in line placement. |
| `axifun/vgg/vgg19_trainable.py` | Trainable VGG19 variant. |
| `axifun/vgg/test_vgg16.py` | VGG16 test script. |
| `axifun/vgg/test_vgg19.py` | VGG19 test script. |
| `axifun/vgg/test_vgg19_trainable.py` | Trainable VGG19 test script. |
| `axifun/vgg/utils.py` | VGG utility functions. |
| `axifun/clean_up_notbook.py` | Notebook cleanup utility script. |

### axifun/ SVG Output Subdirectories

| Directory | Contents |
|-----------|----------|
| `axifun/blender/` | ~20 Blender 3D model wireframe SVG exports |
| `axifun/blender/keepers/` | Curated subset of Blender SVGs |
| `axifun/grids/` | SVG outputs from grid distortion experiments |
| `axifun/more_triangles/` | SVG outputs from triangle shading experiments |
| `axifun/pink_wave/` | SVG outputs with wave/ribbon patterns |
| `axifun/triangles/` | SVG outputs from triangle grid experiments |
| `axifun/voroni/` | SVG outputs from Voronoi experiments (~30 files across v1/, v2/, dixie/, two color/) |
| `axifun/walks/` | SVG outputs from random walk / flow field experiments |

---

## gpyplottermod/ -- First Library (gpyplotter)

### Library Source: gpyplottermod/gpyplotter/

| File | Summary |
|------|---------|
| `gpyplotter/geometry.py` | 2D transform functions using 3x3 homogeneous matrices: `rot2d()`, `ref2d()`, `translate2d()`, `rot2d_about_pt()`, `ref2d_about_point()`, `create_pinhole_camera()`. |
| `gpyplotter/shading.py` | Shading functions: `shade_triangle()`, `shade_quadrilateral()` (parallel fill lines), `parrallel_line_shading()`, `lines_in_polygon()` (Shapely clipping), `lines_in_mask()`. |
| `gpyplotter/tiling.py` | `shard_and_connect()`: BFS/DFS graph partitioning of polygon tessellations across N color groups. Implements 6 wallpaper group symmetry patterns via rotation/reflection compositions. |
| `gpyplotter/sampling.py` | Poisson disk sampling (Bridson's algorithm) with cell grid acceleration. Returns evenly-spaced random point distributions. |
| `gpyplotter/line_processing.py` | Line utilities: `random_sample()`, `optimize_lines_nearest_neighbor()` (KDTree TSP heuristic for pen travel minimization), `lines_to_matrix()`/`matrix_to_lines()` conversion. |
| `gpyplotter/image_lib.py` | Image utilities: `load_image()`, `smooth_like_a_pro()` (gamma-aware blur: linearize -> blur -> re-gamma), `edge_detection()` (Canny wrapper). |
| `gpyplotter/plotting.py` | Matplotlib plotting helper: `make_configured_plot()` with axis/grid/limits config dict. |
| `gpyplotter/polyshader.py` | Postprocessing pipeline framework: chains probabilistic functions (random sampling, transformations) over line collections. |
| `gpyplotter/inkscape.py` | Inkscape SVG layer template generation for multi-pen output. |
| `gpyplotter/saver.py` | SVG saving utilities. |
| `gpyplotter/svg_util.py` | SVG manipulation utilities. |
| `gpyplotter/random_parameters.py` | Random parameter generation for art experiments. |

### Notebooks: gpyplottermod/notebooks/

| File | Summary |
|------|---------|
| `notebooks/portraits/cross hatching.ipynb` | Production cross-hatching using gpyplotter library functions. Cleaner implementation than axifun versions. |
| `notebooks/portraits/continuous tone dots.ipynb` | Continuous tone dot grid portrait using library halftone functions. |
| `notebooks/tiling/wallpaper generator.ipynb` | Wallpaper group pattern generator: creates seed shapes, applies crystallographic symmetry operations (rotation, reflection, glide), expands via BFS to fill canvas. |
| `notebooks/experimental notebooks/cross hatching boundary experiment.ipynb` | Experiments with boundary handling in cross-hatching (Shapely polygon clipping). |
| `notebooks/experimental notebooks/two layer foreground and background experiment shapely.ipynb` | Two-layer composition: foreground/background separation using Shapely polygon operations. |
| `notebooks/projective geometry experiments/projective geometry.ipynb` | Projective geometry transformations applied to polygon tessellations. |
| `notebooks/projective geometry experiments/projective geometry - test.ipynb` | Projective geometry test notebook. |
| `notebooks/projective geometry experiments/projective geometry- triangles.ipynb` | Projective geometry applied to triangle meshes. |
| `notebooks/projective geometry experiments/projective geo - pertrude out.ipynb` | Projective extrusion/protrusion of polygon shapes. |
| `notebooks/projective geometry experiments/dilated polygons.ipynb` | Polygon dilation/erosion experiments. |
| `notebooks/shaded polygons/polygons.ipynb` | Basic shaded polygon generation with quad fill. |
| `notebooks/shaded polygons/shaded triangles - original.ipynb` | Original shaded triangle mesh generation. |
| `notebooks/shaded polygons/shaded triangles tiled.ipynb` | Tiled shaded triangle patterns. |
| `notebooks/shaded polygons/mechanical madness.ipynb` | "Mechanical madness": dense overlapping shaded polygons with aggressive shading. |
| `notebooks/shaded polygons/production - mech mad.ipynb` | Production version of mechanical madness. |
| `notebooks/shaded polygons/distance polygons.ipynb` | Distance-based polygon shading experiments. |
| `notebooks/shaded polygons/dilated polygons-Copy1.ipynb` | Dilated polygon experiment copy. |
| `notebooks/shaded polygons/triangle_voroni_experiment.ipynb` | Triangle + Voronoi combined shading experiment. |
| `notebooks/shaded polygons/experiment.py` | Python script for polygon shading experiments. |

### AxiDraw Control: gpyplottermod/draw svgs/

| File | Summary |
|------|---------|
| `draw svgs/axidraw_draw_svg.ipynb` | AxiDraw plotter SVG drawing control notebook. |
| `draw svgs/axidraw_calibration.ipynb` | AxiDraw plotter calibration notebook. |
| `draw svgs/axidraw_config.py` | AxiDraw configuration settings. |
| `draw svgs/janky layers by color.ipynb` | Splits multi-color SVGs into separate layers by stroke color. |
| `draw svgs/fucking inkscape.ipynb` | Inkscape SVG format debugging. |

---

## plottermagic/ -- Second Library

### Library Source: plottermagic/plottermagic/

#### 3D Line Rendering Pipeline

| File | Summary |
|------|---------|
| `line_render/camera.py` | 3D camera system: `Camera` class with view matrix (look-at), perspective projection (FOV via `cotdg`), `make_viewport_matrix()`. `DefaultCamera` with sensible defaults. |
| `line_render/render.py` | Render pipeline: `map_to_cam_space()` -> `map_to_proj_space()` -> `map_to_viewport()` -> `get_2d()`. Composes camera/projection/viewport transforms. |
| `line_render/point.py` | `Points` class: wraps 3D/4D homogeneous point arrays. Supports `transform()` with optional renormalization and `to_2d()` projection. |
| `line_render/line.py` | 3D line segment renderable. |
| `line_render/polygon.py` | 3D polygon renderable. |
| `line_render/polyhedron.py` | 3D polyhedron renderable. |
| `line_render/renderable.py` | Base `Renderable` class and `TaggedRenderObject` for color-tagged 2D output. |

#### Geometry

| File | Summary |
|------|---------|
| `geometry/geom3d.py` | 3D geometry: 4x4 homogeneous matrix helpers (`pt()`, `hpt()`, `translate()`, `diag_scale()`, `reflect_axis()`). |

#### Shading

| File | Summary |
|------|---------|
| `shading/simple_shapes.py` | `shade_triangle()`, `shade_quadrilateral()` (interpolated parallel fill lines with alternating direction optimization), `grid_arc_shading()` (arc-based triangle fill). `step_and_shade_poly()` for arbitrary polygon shading by decomposition into quads. |

#### Sampling

| File | Summary |
|------|---------|
| `random/possion_disk_sampling.py` | Poisson disk sampling (Bridson's algorithm). Duplicate of gpyplotter's implementation. |
| `random/sphere_sampling.py` | Uniform sphere surface sampling. |

#### SVG Processing

| File | Summary |
|------|---------|
| `svg_processing/optimization.py` | SVG path optimization: `optimize_lines_nearest_neighbor()` uses KDTree to find nearest unvisited line endpoints (TSP greedy heuristic). Considers line direction reversal. `collapse_lines()` merges nearby endpoints. |

#### Graphing

| File | Summary |
|------|---------|
| `graphing/plot.py` | Matplotlib plot configuration helper. |

---

## plotterart/ -- Art Piece Experiments

### Anaglyph 3D: plotterart/pieces/anaglyph/experiments/

| File | Summary |
|------|---------|
| `experiments/simple spheres.ipynb` | Stereoscopic anaglyph: renders point clouds (spheres) through left/right cameras with slight horizontal offset, plots left in red and right in cyan for 3D glasses viewing. Point size scaled by depth. |
| `experiments/concentric circles.ipynb` | Anaglyph concentric circle patterns for stereoscopic depth. |
| `experiments/triangles/triangles.ipynb` | Anaglyph 3D triangulated surfaces. |
| `experiments/triangles/3d grid.ipynb` | Anaglyph 3D grid patterns. |
| `experiments/triangles/chaotic.ipynb` | Anaglyph chaotic triangle arrangements. |
| `experiments/triangles/layers.ipynb` | Anaglyph multi-layer triangle compositions. |
| `experiments/triangles/med dense.ipynb` | Medium density anaglyph triangle mesh. |
| `experiments/triangles/sphere.ipynb` | Anaglyph sphere rendered with triangulation. |
| `experiments/triangles/super dense.ipynb` | Very dense anaglyph triangle mesh. |

### Polygon Tessellation: plotterart/pieces/polygon_tess/

| File | Summary |
|------|---------|
| `polygon_tess/network.py` | Graph-based polygon partition: builds NetworkX adjacency graph from Voronoi regions (shared vertices = edge), then BFS/DFS/random partitions into N color groups. Supports sequential, random, and shuffle partition strategies. |
| `polygon_tess/experiments/prod.ipynb` | Production polygon tessellation with graph-partitioned shading. |
| `polygon_tess/experiments/dialtion.ipynb` | Polygon dilation experiments. |
| `polygon_tess/experiments/funk test.ipynb` | "Funky" shading test on tessellated polygons. |

---

## plottersvg/ -- SVG DOM Library (Newer Version)

| File | Summary |
|------|---------|
| `plottersvg/elements/core.py` | Core SVG element base classes. |
| `plottersvg/elements/paths.py` | SVG path element (d attribute parsing). |
| `plottersvg/elements/conic.py` | SVG conic section elements (circle, ellipse). |
| `plottersvg/elements/ordered.py` | Ordered element collections. |
| `plottersvg/elements/pathutils.py` | Path manipulation utilities. |
| `plottersvg/svg/svg.py` | SVG document root element. |
| `plottersvg/svg/container.py` | SVG container elements. |
| `plottersvg/svg/group.py` | SVG `<g>` group element. |
| `plottersvg/svg/layer.py` | Inkscape layer support (`<g inkscape:groupmode="layer">`). |
| `plottersvg/svg/attributes.py` | SVG attribute handling. |
| `plottersvg/io/read.py` | SVG file reader/parser. |
| `plottersvg/utils/geometry.py` | SVG geometry utilities. |
| `plottersvg/utils/parsing.py` | SVG string parsing utilities. |
| `plottersvg/utils/display.py` | SVG display/rendering utilities. |
| `plottersvg/utils/units.py` | SVG unit conversion. |
| `plottersvg/utils/dictionary.py` | Dictionary utilities. |

### plottersvg/ Example Notebooks

| File | Summary |
|------|---------|
| `plottersvg/examples/gentle intro.ipynb` | Introduction to the plottersvg API. |
| `plottersvg/examples/group elements.ipynb` | Working with SVG groups and layers. |
| `plottersvg/examples/read file.ipynb` | Reading/parsing existing SVG files. |
| `plottersvg/examples/run old.ipynb` | Running old code with the new library. |

---

## plottersvg_old/ -- SVG DOM Library (Older Version)

| File | Summary |
|------|---------|
| `plottersvg_old/plottersvg/svg.py` | SVG document handling (older API). |
| `plottersvg_old/plottersvg/container.py` | SVG containers. |
| `plottersvg_old/plottersvg/geometry.py` | SVG geometry. |
| `plottersvg_old/plottersvg/parse.py` | SVG parser. |
| `plottersvg_old/plottersvg/utils.py` | Utilities. |
| `plottersvg_old/svgelements/` | SVG element definitions (core, elements, paths, pathutils, conic, ordered). |

### plottersvg_old/ Example Notebooks

| File | Summary |
|------|---------|
| `plottersvg_old/development.ipynb` | Library development notebook. |
| `plottersvg_old/examples/gentle intro.ipynb` | API introduction. |
| `plottersvg_old/examples/fileio.ipynb` | File I/O examples. |
| `plottersvg_old/examples/fileio check.ipynb` | File I/O verification. |
| `plottersvg_old/examples/group elements.ipynb` | Group element examples. |
| `plottersvg_old/examples/plot file.ipynb` | Plotting from SVG files. |

---

## svgs/ -- SVG Output Archive (513 files)

| Directory | Count | Contents |
|-----------|-------|----------|
| `svgs/notebooks/crosshatching/` | ~20 | Cross-hatching portrait SVGs (BW and CMYK) |
| `svgs/notebooks/dots/` | ~10 | Halftone dot grid SVGs |
| `svgs/notebooks/wallpaper/` | ~50 | Wallpaper group pattern SVGs |
| `svgs/notebooks/wallpaper/long/` | ~10 | Long-format wallpaper SVGs |
| `svgs/notebooks/wallpaper/printed stuff/` | ~5 | Printed/production wallpaper SVGs |
| `svgs/notebooks/wallpaper/royalty plot/` | ~5 | Royalty-themed wallpaper SVGs |
| `svgs/notebooks/shaded_polygons/` | ~80 | Shaded polygon tessellation SVGs |
| `svgs/notebooks/shaded_polygons/carole/` | ~10 | Carole-themed shaded polygons |
| `svgs/notebooks/shaded_polygons/exp1 - good/` | ~20 | Best polygon experiments |
| `svgs/notebooks/shaded_polygons/random_exp/` | ~30 | Random polygon experiments |
| `svgs/notebooks/shaded_polygons/random_exp/mech_madness/` | ~15 | Mechanical madness polygon SVGs |
| `svgs/notebooks/projections/` | ~10 | Projective geometry SVGs |
| `svgs/notebooks/old results pre saving lib/` | ~100+ | Pre-library SVGs (wallpapers, projective geo) |
| `svgs/production/2019/11_nov/white_hole/` | ~10 | Production piece: white hole design |

### svgs/notebooks/old results pre saving lib/ Notebooks

| File | Summary |
|------|---------|
| `wallpapers scripts/wallpaper group dev.ipynb` | Wallpaper group symmetry development notebook. |
| `wallpapers scripts/wallpaper test.ipynb` | Wallpaper group testing notebook. |

---

## Technique Cross-Reference Index

### Cross-Hatching / Parallel Line Fills
- `axifun/cross hatching *.ipynb` (7 notebooks)
- `axifun/line by line scan*.ipynb` (9 notebooks)
- `axifun/random directional masks.ipynb`
- `axifun/suiqggly line by line.ipynb`
- `axifun/line by line and outline.ipynb`
- `gpyplottermod/gpyplotter/shading.py` -- `shade_quadrilateral()`, `parrallel_line_shading()`
- `gpyplottermod/notebooks/portraits/cross hatching.ipynb`
- `plottermagic/plottermagic/shading/simple_shapes.py` -- `shade_quadrilateral()`

### Halftone / Dot Grid
- `axifun/dot grid.ipynb`
- `axifun/dot grid cymk.ipynb`
- `axifun/Sphere effect.ipynb`
- `gpyplottermod/notebooks/portraits/continuous tone dots.ipynb`

### Stipple / Mezzotint
- `axifun/mezzotint.ipynb`
- `axifun/mezzotint-CMYK.ipynb`

### Contour / Dilation-Erosion
- `axifun/dilation.ipynb`
- `axifun/dilation additive.ipynb`
- `axifun/countours.ipynb`
- `axifun/kmean tones.ipynb`
- `axifun/sun.ipynb`
- `axifun/spline contours.ipynb`

### Grid Warping / Distortion
- `axifun/distortion grids*.ipynb` (4 notebooks)
- `axifun/grid shifting.ipynb`
- `axifun/grid warp*.ipynb` (4 notebooks)
- `axifun/radial grid shifting*.ipynb` (5 notebooks)
- `axifun/schism grid shift.ipynb`
- `axifun/mc grids.ipynb`

### Voronoi / Delaunay / Tessellation
- `axifun/vonroni*.ipynb` (2 notebooks)
- `axifun/paul replica*.ipynb` (5 notebooks)
- `axifun/delany triangle grid warp.ipynb`
- `axifun/triangulation.ipynb`
- `axifun/triangle grid.ipynb`
- `axifun/disk sampling + triangulation.ipynb`
- `plotterart/pieces/polygon_tess/network.py` -- graph partitioning

### Spiral / Parametric Curves
- `axifun/spirals.ipynb`
- `axifun/roses.ipynb`
- `axifun/front face rose.ipynb`
- `axifun/hilbert curves.ipynb`

### Flow Fields / Noise / Random Walks
- `axifun/random walk - perlin noise.ipynb`
- `axifun/perlin noise.ipynb`
- `axifun/fluid warping.ipynb`
- `axifun/sun random walk.ipynb`

### Edge Detection
- `axifun/edge detection.ipynb`
- `axifun/edge + tone.ipynb`
- `axifun/skimage.ipynb`
- `axifun/line by line and outline.ipynb`
- `gpyplottermod/gpyplotter/image_lib.py` -- `edge_detection()`

### Clustering / Segmentation
- `axifun/c-c-c-clustering.ipynb`
- `axifun/clustering and triangulation.ipynb`
- `axifun/kmean tones*.ipynb`
- `axifun/kmeans and contours.ipynb`
- `axifun/sun.ipynb`
- `axifun/sun mask.ipynb`

### 3D Rendering / Anaglyph
- `plottermagic/plottermagic/line_render/` -- full 3D pipeline (camera, projection, viewport)
- `plotterart/pieces/anaglyph/experiments/` -- 9 stereoscopic notebooks
- `axifun/blender/` -- Blender SVG exports

### Wallpaper Groups / Symmetry
- `gpyplottermod/gpyplotter/tiling.py` -- `shard_and_connect()`, symmetry operations
- `gpyplottermod/notebooks/tiling/wallpaper generator.ipynb`
- `svgs/notebooks/wallpaper/` -- ~50 wallpaper SVGs

### Shaded Polygons
- `gpyplottermod/notebooks/shaded polygons/` -- 8 notebooks
- `plotterart/pieces/polygon_tess/` -- graph-partitioned polygon shading
- `svgs/notebooks/shaded_polygons/` -- ~80 SVGs

### SVG Processing / Optimization
- `plottermagic/plottermagic/svg_processing/optimization.py` -- KDTree nearest-neighbor path optimization
- `gpyplottermod/gpyplotter/line_processing.py` -- `optimize_lines_nearest_neighbor()`
- `axifun/stich together SVGs*.ipynb` -- SVG file stitching

### Poisson Disk Sampling
- `gpyplottermod/gpyplotter/sampling.py`
- `plottermagic/plottermagic/random/possion_disk_sampling.py`
- `axifun/disk sampling - basic.ipynb`
- `axifun/disk sampling + triangulation.ipynb`

### Image Preprocessing
- `gpyplottermod/gpyplotter/image_lib.py` -- gamma-aware blur (`smooth_like_a_pro`)
- `axifun/laplace pyramid.ipynb` -- Laplacian pyramid
- `axifun/repeat blurs.ipynb` -- iterative max filter
- `axifun/dither demo.ipynb`, `axifun/dither test.ipynb`

### Refraction / Light Simulation
- `axifun/refraction.ipynb`
- `axifun/refraction continious.ipynb`

### Chaos / Fractal / IFS
- `axifun/eric_s thing.ipynb` -- flame fractals with 11 IFS variations
- `axifun/dynamic system.ipynb` -- strange attractors

### Neural Network Approaches
- `axifun/photo realism nn.ipynb` -- VGG19 perceptual loss
- `axifun/vgg/` -- VGG16/19 TensorFlow implementations

### Duotone / Multi-Layer Color
- `axifun/duotones.ipynb` -- two-color line-by-line scanning
- `axifun/grid random colors.ipynb` -- multi-color grid assignment

---

## Key Algorithms Worth Porting to penpal

1. **Cross-hatching** (axifun notebooks + gpyplotter/shading.py) -- parallel line fills at angles, masked to brightness bands
2. **Poisson disk sampling** (gpyplotter/sampling.py) -- brightness-modulated minimum distance
3. **Wallpaper group tiling** (gpyplotter/tiling.py) -- BFS graph partitioning + symmetry ops
4. **SVG path optimization** (plottermagic/svg_processing/optimization.py) -- KDTree nearest-neighbor TSP
5. **3D line rendering** (plottermagic/line_render/) -- camera, projection, viewport pipeline
6. **Polygon shading** (plottermagic/shading/simple_shapes.py) -- quad/triangle fill with alternating direction
7. **Graph-based tessellation partitioning** (plotterart/polygon_tess/network.py) -- NetworkX adjacency, BFS/DFS/random
8. **Gamma-aware image preprocessing** (gpyplotter/image_lib.py) -- linearize -> blur -> re-gamma
9. **Dilation/erosion contours** (axifun/dilation.ipynb) -- topographic contour maps from binary erosion
10. **Flame fractals / IFS** (axifun/eric_s thing.ipynb) -- chaos game with variation functions


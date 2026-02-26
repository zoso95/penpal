# plotterart Repository Catalog

Comprehensive catalog of `/Users/gnb/dev/plotterart/` -- 730 .py and .ipynb files across the `pieces/`, `image_pieces/`, and `bin/` directories.

## Repository Overview

**Author:** Geoffrey Bradway (geoff.bradway@gmail.com)
**URL:** https://www.normedvector.space
**Dependencies:** jupyterlab, scipy, numpy, matplotlib, networkx, sklearn, shapely, ipywidgets, svgwrite, plotly, noise, svgpathtools, svglib, tqdm, solidpython, viewscad, numpy-stl, pygalmesh
**Linked libraries:** plottermagic (3D rendering, line rendering, geometry, shading), pdesign/parametric-design (canvas, shapes, lines, transforms, smoothing), exp_management (experiment tracking)

---

## Top-Level Files

### setup.py
Standard setuptools package configuration. Installs `plotterart` as an editable package, reads dependencies from `requirements.txt`.

### bin/activate_this.py
Virtual environment activation helper script.

---

## image_pieces/ (2 files)

- **grace furby.ipynb** -- Image-based plotter piece, likely portrait processing.
- **sky.ipynb** -- Image-based plotter piece with sky imagery.

---

## pieces/ Directory (705 files)

### pieces/"shaders"/ (2 files)
GPU-style shader techniques reimplemented in numpy for plotter output.

- **basic.ipynb** -- Implements GLSL-style fragment shader logic in numpy, computing per-pixel color via UV coordinates on a meshgrid. Proof of concept for translating GPU shaders to plotter-friendly representations.
- **fbm.ipynb** -- Fractional Brownian Motion shader implementation, likely generating noise textures using FBM octave summation.

### pieces/2d_moires/ (59 files)
The largest and most developed technique family -- 2D moire pattern generation through overlapping line fields and noise-driven distortion.

#### 2d_moires/ (top level)
- **brainstorming.ipynb** -- Exploratory notebook generating moire-like patterns by interpolating between randomly perturbed closed curves using complex-number polar coordinates, with convolution smoothing to control curve roughness.
- **implied_shape.ipynb** -- Moire patterns that imply 3D shapes through line interference.
- **marbles.ipynb** -- Marble-like moire textures.
- **meshgrid_test.ipynb / meshgrid_test2.ipynb** -- Testing meshgrid approaches for moire generation.
- **perlin_sun.ipynb** -- Perlin noise-driven radial moire patterns with sun-like composition.
- **scratch.ipynb / test_run.ipynb** -- Quick experiments.

#### 2d_moires/custom noise/ (10 files)
- **laplace_moire.ipynb / laplace_moire-smoothed.ipynb** -- Moire patterns using Laplacian noise fields, with smoothed variants for cleaner interference.
- **laplace_noise_metallic.ipynb** -- Metallic-looking textures from Laplacian noise applied to moire grids.
- **four_squares-flow.ipynb / four_squares-metalic.ipynb** -- Four-panel compositions using flow-field and metallic noise moires.
- **all together now.ipynb** -- Combined moire technique using multiple noise types.
- **square grid.ipynb** -- Square grid base for moire interference.

#### 2d_moires/glass/ (3 files)
- **glass - try 1/2/3.ipynb** -- Iterative attempts at simulating glass-like refraction moire effects by distorting overlapping line grids.

#### 2d_moires/infer/ (1 file)
- **Untitled.ipynb** -- Experimental moire inference work.

#### 2d_moires/metalic_perlin/ (6 files)
- **metalic_perlin.ipynb** -- Core technique: Perlin noise creates height-field distortions on grid lines, producing metallic/brushed-metal moire textures.
- **perlin_grid.ipynb** -- Grid-based Perlin noise moire.
- **bumpy.ipynb** -- Bumpy metallic surface moire effects.
- **tri_color.ipynb** -- Three-color metallic moire composition.
- **print.ipynb / print-Copy1.ipynb** -- Print-ready versions.

#### 2d_moires/moire/ (10 files, including collab/ and texture work/)
- **moire.ipynb** -- Core 2D moire technique: concentric circles/spirals projected through Perlin noise height fields using perspective division (x/z, y/z), creating iridescent surface textures from overlapping layers with different noise parameters.
- **grid.ipynb** -- Grid-based moire patterns.
- **hexagons.ipynb** -- Hexagonal moire grids.
- **splines.ipynb** -- Spline-based moire curves.
- **arangements.ipynb** -- Compositional arrangements of moire elements.
- **multicolor shape ring.ipynb / multicolor shape background.ipynb** -- Multi-pen moire compositions.
- **cool texture.ipynb** -- Textural moire effects.
- **collab/collab1.ipynb** -- Collaborative moire piece.
- **texture work/blue steel.ipynb** -- Blue-steel metallic moire texture.
- **texture work/op triangle.ipynb** -- Op-art triangular moire.

#### 2d_moires/oil_slick/ (14 files)
- **oil_slick.ipynb** -- Core oil slick technique: multiple Perlin noise layers with varying persistence/lacunarity parameters create overlapping interference patterns that resemble oil-on-water iridescence. Lines are projected through noise height fields.
- **lavalamp.ipynb / lavalamp2.ipynb** -- Lava lamp-style flowing moire compositions.
- **production.ipynb / simplified.ipynb / simplify2.ipynb** -- Production-ready and simplified versions.
- **onblackpaper.ipynb** -- Inverted for dark paper printing.
- **print.ipynb / try1.ipynb** -- Print-ready and experimental versions.
- **oil slick weird shape.ipynb** -- Non-rectangular oil slick compositions.

#### 2d_moires/spheres/ (1 file)
- **spherers.ipynb** -- Spherical moire patterns using radial projection.

#### 2d_moires/surface_moires/ (4 files)
- **surface_contours.ipynb** -- Surface contour-based moire interference.
- **trial_by_fire.ipynb** -- Experimental surface moire approach.
- **Untitled.ipynb / Untitled1.ipynb** -- Additional experiments.

### pieces/acrylic/ (3 files)
Designs for acrylic painting with plotter.

- **hellow world stripes.ipynb** -- Simple stripe patterns for acrylic painting tests.
- **rect_in_rect.ipynb** -- Nested rectangles for acrylic.
- **white_stripes.ipynb** -- White stripe compositions.

### pieces/agnes/ (8 files)
Agnes Martin-inspired minimalist grid and stripe compositions.

- **strips.ipynb** -- Core Agnes Martin technique: minimal grid compositions with precise line placement, creating subdivided rectangular panels within a border using calculated spacing ratios.
- **3 color grad.ipynb** -- Three-color gradient in Agnes Martin style.
- **color mix.ipynb / color pencil grad.ipynb / color pencil strips.ipynb** -- Color pencil gradient and strip explorations.
- **grace.ipynb** -- Named piece in Agnes Martin style.
- **triad.ipynb** -- Three-section grid composition.
- **Untitled.ipynb** -- Additional experiments.

### pieces/anaglyph/ (8 files)
Stereoscopic 3D anaglyph (red/cyan) compositions using dual-camera projection.

- **experiments/simple spheres.ipynb** -- Renders point clouds on spheres from two camera positions (left/right eye offset), plotting left in cyan and right in red to create stereoscopic depth. Point size scales with depth.
- **experiments/concentric circles.ipynb** -- Concentric circle anaglyphs.
- **experiments/triangles/ (7 files)** -- Various triangle-based anaglyph experiments: dense grids, chaotic arrangements, layered compositions, sphere projections.

### pieces/black_etching/ (8 files)
Dense line patterns designed for metallic/black pen on white paper, mimicking etching techniques.

- **bubbles.ipynb** -- Random concentric circle clusters (bubbles) drawn as scaled circle exteriors at random positions, creating a bubbly etching texture.
- **bubble_grid.ipynb** -- Grid-arranged bubble patterns.
- **fun_geometry.ipynb** -- Geometric etching compositions.
- **hlines.ipynb** -- Horizontal line etching patterns.
- **small-box.ipynb** -- Small box etching compositions.
- **squares.ipynb** -- Square-based etching patterns.

### pieces/block grids/ (10+ files)
Grid-based compositions using blocks and tetris-like arrangements.

- **black tetris.ipynb / blue tetris.ipynb** -- Tetris-inspired block grid compositions.
- **copper grid.ipynb** -- Copper-colored grid patterns.
- **corner gradient.ipynb** -- Gradient effects from corner positions.
- **grass.ipynb** -- Grass-textured block grids.
- **litho.ipynb** -- Lithography-style block grids.
- **mono block grid.ipynb** -- Monochrome block grid composition.

### pieces/circle_grids/ (7 files)
Circle-based grid compositions with lattice arrangements.

- **circle_grid.ipynb** -- Base circle grid composition.
- **circle_grid-lattice.ipynb / circle_grid-lattice-black.ipynb** -- Circle grids on lattice structures with black pen variants.
- **circle_grid-lattice-black-dense.ipynb** -- Dense lattice circle compositions.

### pieces/cloth/ (14 files)
Simulated cloth/drape effects using line interpolation and perspective projection.

- **moire.ipynb** -- Core cloth technique: generates cloth-like drapes and columns by interpolating curves between two reference lines. Radius and angle are perturbed with noise, then curves are spline-interpolated. Creates draped fabric with column effects, composited using Shapely boolean operations for occlusion.
- **3d.ipynb** -- 3D cloth simulation using perspective projection (x/z, y/z division) of curves with random z-depth variation, interpolating between top and bottom curves to create perspective cloth strips.
- **line driven cloth.ipynb** -- Cloth generated from pairs of driving lines with noisy radius/angle perturbation along control points, creating fabric-like wave patterns.
- **metal_mesh/cool_mesh_grif.ipynb / curviture stuff.ipynb / mesh_print.ipynb** -- Metal mesh textures using curvature-driven grid distortion.
- **corona.ipynb** -- Corona-like cloth radiation pattern.
- **fourier.ipynb** -- Fourier-based cloth simulation.
- **rainbow_road.ipynb** -- Rainbow-colored cloth strip.
- **surface_test.ipynb / black_etching.ipynb** -- Surface cloth tests and etching-style cloth.

### pieces/concept/ (2 files)
Conceptual/minimal pieces.

- **lines.ipynb** -- Minimalist line compositions.
- **suqare_grid.ipynb** -- Square grid concepts.

### pieces/death_textures/ (31 files)
Complex texture generation through image gradient warping and multi-layer blending -- a core technique for photorealistic plotter art.

- **germ.ipynb** -- Generates dense organic textures using FFT-smoothed image gradients to warp regular grids, creating germ/cell-like patterns.
- **bumps.ipynb** -- Bump-textured surface effects.
- **cool diagonals.ipynb** -- Diagonal texture patterns.
- **fuzzy.ipynb** -- Fuzzy/soft texture generation.
- **shiny.ipynb** -- Shiny metallic texture effects.
- **worms.ipynb** -- Worm-like organic texture patterns.
- **two_layer.ipynb** -- Two-layer texture compositing.
- **blending/ (17 files)** -- Texture blending experiments using Laplacian pyramid blending, two-step integration, and multi-scale gradient composition. Includes production prints combining paint textures with organic patterns.
- **prints/ (4 files)** -- Print-ready texture pieces.

### pieces/design_lib_brainstorm/ (2 .py files)
Early library design exploration.

- **transforms.py** -- Prototype transform functions (contract, translate, rotate, mirror) using Shapely affinity operations. This was an early version of what became pdesign.transforms.
- **__init__.py** -- Package init.

### pieces/fft/ (14 files)
FFT (Fast Fourier Transform) based surface and texture generation.

- **fft_smoothing.ipynb** -- Core FFT technique: constructs frequency-domain patterns by placing random values on polygon perimeters in FFT space, then applies inverse FFT with varying Gaussian smoothing to create surfaces. These surfaces are rendered as perspective-projected grid meshlines (x/z, y/z), creating metallic/crystalline wireframe textures.
- **metal.ipynb** -- Metallic surface textures via FFT.
- **combine_image_textures.ipynb** -- Combining multiple FFT-generated textures.
- **draw_on_image.ipynb** -- Drawing on images using FFT-derived line fields.
- **inital try with shapes.ipynb** -- Shape-based FFT frequency domain experiments.
- **interp.ipynb** -- Interpolation between FFT surfaces.
- **line detection.ipynb** -- Line detection in FFT domain.
- **two diff surfaces.ipynb** -- Differencing two FFT surfaces.
- **moon/ (3 files)** -- Moon-themed FFT surface pieces with gradient shading.

### pieces/gifs/ (1 file)
- **planets.ipynb** -- Animated GIF generation of planetary orbits using 3D rendering.

### pieces/impasto/ (13 files)
Thick-paint (impasto) inspired pieces using heavy line work and bold compositions.

- **flow.ipynb** -- Cardinal spline interpolation between pairs of noisy diagonal lines, creating thick flowing brush-stroke effects with variable line width.
- **dots.ipynb** -- Poisson disk sampled dot patterns sorted by grid cells for optimal plotting order, creating stipple-like impasto dot fields.
- **planets.ipynb** -- Solar system / orbital ring compositions using concentric circles and vertical lines through center points.
- **astroturf.ipynb** -- Astroturf-like dense texture.
- **big piece.ipynb / sun compostion.ipynb / sun strip.ipynb** -- Large-format impasto compositions with sun themes.
- **circe strip.ipynb / circle in square.ipynb / diamond strip.ipynb** -- Geometric impasto strip compositions.
- **illuminati.ipynb** -- Triangle/eye-themed impasto.
- **dots and sphere.ipynb** -- Combined dot and sphere impasto.

### pieces/junk/ (2 subdirs)
Experimental/abandoned work.

- **leap/** -- Leap motion controller experiments.
- **ostromoukhov/** -- Ostromoukhov stippling algorithm experiments.

### pieces/laplace noise/ (1 file)
- **Untitled.ipynb** -- Laplacian noise field experiments.

### pieces/laser cutter/ (32 files)
Designs for laser cutting rather than pen plotting, using SVG output for cut paths.

- **first_piece_exploratory.ipynb** -- Initial laser cutter explorations.
- **circle_grid.ipynb / hexagons.ipynb / squares.ipynb** -- Geometric grid patterns for laser cutting.
- **four layer grid.ipynb / five layer phantasm.ipynb** -- Multi-layer laser cut pieces.
- **double_moire_grid.ipynb** -- Moire grids designed for physical layer overlay.
- **rainbow_voroni.ipynb / white voronoi.ipynb** -- Voronoi-based laser cut designs.
- **perlin squares.ipynb** -- Perlin noise modulated square grids.
- **whirlpool.ipynb** -- Whirlpool pattern laser cuts.
- **black rainbows/ (3 files)** -- Canyon, metaball, and brainstorm pieces for black paper with rainbow underlays.
- **clouds/ (1 file)** -- Cloud-shaped laser cut pieces.
- **notan/ (1 file)** -- Notan (light/dark balance) inspired cuts.
- **prints/ (3 files)** -- Production-ready laser cut files.

### pieces/lewitt/ and pieces/lewitt challenge/ (31+31 = 62 files)
Sol LeWitt-inspired daily drawing challenge -- 30 days of algorithmic wall drawing interpretations.

- **day - 1.ipynb through day - 30.ipynb** -- Each implements a different Sol LeWitt wall drawing instruction algorithmically. Techniques span line density, geometric partitioning, color theory, and systematic variation. Duplicated across two directory locations.

### pieces/litho/ (19 files)
Lithography-style prints combining moire, geometric, and minimalist approaches.

- **litho moire.ipynb** -- Creates moire interference by overlaying perlin-noise-warped grids and concentric circles with slight offsets, applying polar coordinate rotation transforms.
- **frank stella.ipynb** -- Frank Stella-inspired geometric compositions.
- **newman boxes.ipynb** -- Barnett Newman-inspired color field boxes.
- **geometric shades.ipynb** -- Geometric shading patterns.
- **litho spiral.ipynb** -- Spiral-based lithography composition.
- **minimalist_edges.ipynb** -- Minimalist edge-based compositions.
- **wiggly squares.ipynb** -- Wavy/wiggly square grids.
- **grid warped.ipynb** -- Warped grid lithography.
- **agnes type stuff.ipynb** -- Agnes Martin-influenced litho.
- **four_squares-flow.ipynb** -- Four-panel flow field litho.

### pieces/moire/ (same as 2d_moires/moire/)
Appears to be a duplicate/symlink of `2d_moires/moire/`.

### pieces/new_wallpaper_groups/ (3 .py files)
Improved wallpaper group symmetry implementation.

- **groups.py** -- Implements the 17 wallpaper group symmetry operations (reflection, glide reflection, rotation) using Shapely affinity transforms. Operations include `ref_vertical`, `ref_horizontal`, `glide_horizontal`, `glide_vertical`, `rotate_180`.
- **groupings.py** -- Higher-level grouping/tiling logic.
- **slicing.py** -- Slicing operations for wallpaper pattern generation.

### pieces/old bad/ (1 file)
- **wave_column/Untitled.ipynb** -- Abandoned wave column experiment.

### pieces/openscad/ (7 files)
3D printable designs using OpenSCAD via SolidPython.

- **my_piece.ipynb / rot_piece.ipynb** -- 3D printed art pieces.
- **square_interleave.ipynb** -- Interleaved square 3D designs.
- **jpg.ipynb / png_tet.ipynb** -- Image-to-3D conversion experiments.
- **test.ipynb** -- OpenSCAD testing.

### pieces/painting/ (31 files)
Acrylic/watercolor painting compositions driven by algorithmic line generation.

- **brownian motion.ipynb / brownian motion-wokring.ipynb** -- Brownian motion random walk paintings.
- **spiral.ipynb / spirals.ipynb** -- Spiral-based painting compositions.
- **swirl.ipynb** -- Swirling paint compositions.
- **squiggles.ipynb** -- Squiggle-based painting patterns.
- **sine_wave.ipynb** -- Sine wave paintings.
- **circles.ipynb** -- Circle-based paintings.
- **random walk.ipynb** -- Random walk painting paths.
- **fun_geometric.ipynb** -- Fun geometric painting compositions.
- **litho painting.ipynb** -- Lithography-style painting.
- **pieter_parsing.ipynb / piter.ipynb** -- Parsing/interpreting Pieter Bruegel paintings.
- **line drawings/ (5 files)** -- Portrait line drawings of "Marie" using realism techniques with different shading approaches.

### pieces/paper/ and pieces/paper_cutouts/ (5 files)
Paper cutting and layered paper designs.

- **cutouts.ipynb / cutouts-production.ipynb** -- Paper cutout designs.
- **cutout anaglyph.ipynb** -- 3D anaglyph paper cutouts.
- **rainbow cutting.ipynb / rainbow squares.ipynb** -- Rainbow-colored paper cut designs.

### pieces/patreon/ (11 files)
Pieces designed for Patreon supporter rewards.

- **circle_card.ipynb** -- Circular card design.
- **collectors - 1 - rect half.ipynb** -- Collector edition rectangular design.
- **color_pencil_grad.ipynb** -- Color pencil gradient card.
- **rainbow road.ipynb** -- Rainbow road card.
- **shaded.ipynb** -- Shaded card design.
- **brainstorming/square_cross.ipynb** -- Square cross brainstorm.
- **meh/ (3 files)** -- Welcome card designs (not great).

### pieces/pencil/ (20 files)
Colored pencil and graphite pencil-specific plotter designs, optimized for pencil media.

- **gradient.ipynb** -- Creates density gradients using vertical lines with non-linear spacing (sqrt progression), producing left-to-right tonal gradients purely through line density.
- **center_gradient.ipynb** -- Center-radiating gradient.
- **shaded circle.ipynb / shaded_box.ipynb** -- Pencil-shaded geometric shapes.
- **stripes.ipynb / variable stripes.ipynb / long stripe.ipynb** -- Stripe patterns with variable density.
- **grid_progression.ipynb** -- Progressive grid density.
- **calibration.ipynb** -- Pencil calibration test patterns.
- **5x7 watercolor test (5 variants)** -- Watercolor pencil test pieces at 5x7 size.
- **addition table.ipynb** -- Additive color mixing table.
- **lewitt add boxes.ipynb** -- LeWitt-inspired additive box compositions.
- **rect in rect.ipynb / reflexted square.ipynb / square_cross.ipynb / big box.ipynb** -- Geometric pencil compositions.

### pieces/perlin/ (2 files)
Pure Perlin noise explorations.

- **experiment.ipynb** -- Perlin noise field experiments.
- **interactive.ipynb** -- Interactive Perlin noise parameter exploration with widgets.

### pieces/poetry/ (2 files)
Text/poetry-based plotter output.

- **ee_1.ipynb** -- E.E. Cummings-inspired text layout piece.
- **Untitled.ipynb** -- Poetry experiment.

### pieces/polygon_tess/ (4 files, 2 .py)
Polygon tessellation using Voronoi diagrams and graph partitioning.

- **network.py** -- Graph-based region partitioning: builds adjacency graphs from Voronoi regions, then partitions using BFS/DFS/random traversal with sequential/random/shuffle partition assignment. Used for tessellation coloring.
- **__init__.py** -- Package init.
- **experiments/ and good/** -- Experimental and successful tessellation results.

### pieces/portraits/ (54 files)
Portrait rendering techniques -- crosshatching, stippling, edge detection, halftoning.

- **crosshatching.ipynb** -- Core crosshatch portrait technique: loads grayscale image, thresholds into tonal bands, overlays rotated parallel line grids (at 45/-45 degrees) with density proportional to darkness, clips to tonal masks, adds Canny edge contour overlay. Uses plottermagic grid/masking/image_processing modules.
- **stippling/ (18 files)** -- Extensive stippling work:
  - **bridsons/ (6 files)** -- Bridson's Poisson disk sampling for image-weighted stippling with diffusion, pairwise adjustment, rescaling, and large grid variants.
  - **llyods.ipynb / lloyds_chunked.ipynb** -- Lloyd's relaxation weighted stippling.
  - **CAH stipple.ipynb** -- Correlated area halftoning stipple.
  - **dithering-CAH.ipynb** -- Dithering-based halftone stippling.
- **trippy outlines/ (11 files)** -- Morphological edge contours with repeated offset/erosion creating psychedelic outline effects. Includes cubist variations, direction flipping, smooth toning, and hatching fills.
- **stochasic_halftones.ipynb** -- Stochastic halftone dot patterns.
- **error drawing.ipynb** -- Error-diffusion based drawing.
- **RAG.ipynb / grad+rag.ipynb** -- Region Adjacency Graph based portrait segmentation.
- **nine-greyscale.ipynb** -- Nine-level greyscale portrait.
- **random lines.ipynb / trippy lines.ipynb** -- Random and psychedelic line portrait styles.

### pieces/rainbow/ (21 files)
Multi-color/rainbow pen compositions.

- **rainbow_road.ipynb** -- Rainbow gradient road/stripe compositions.
- **frank stella.ipynb** -- Frank Stella-inspired rainbow concentric shapes.
- **circle_square.ipynb** -- Circle-in-square rainbow compositions.
- **diagonal.ipynb / cross.ipynb** -- Diagonal and cross rainbow patterns.
- **flowers.ipynb** -- Rainbow flower compositions.
- **perlin.ipynb** -- Perlin noise rainbow fields.
- **trippy grid.ipynb** -- Psychedelic rainbow grid.
- **triangles.ipynb / square triangle.ipynb** -- Geometric rainbow shapes.
- **cheap sphere.ipynb** -- Simple rainbow sphere.
- **from image ref.ipynb** -- Rainbow from image reference.
- **litho.ipynb** -- Rainbow lithography.

### pieces/reaction_diff/ (2 files)
Gray-Scott reaction-diffusion simulation for organic pattern generation.

- **basics.ipynb** -- Implements Gray-Scott reaction-diffusion model: two chemicals A and B with diffusion (Laplacian), feed/kill rates, simulated over 20,000 timesteps on a 200x200 grid. The resulting concentration field is sampled along concentric circles and used to modulate radius, creating organic pattern visualizations where reaction-diffusion textures warp circular line drawings.
- **Untitled.ipynb** -- Additional reaction-diffusion experiments.

### pieces/realism/ (52 files)
The most technically ambitious directory -- photorealistic line rendering of images.

- **dynamic_systems.ipynb** -- Core "dynamic systems" approach: loads texture images, computes multi-scale FFT-smoothed gradients (Sobel derivatives at multiple blur levels), displaces a regular pixel grid along negative gradient directions, producing cloth-like warped grid renderings that reproduce image tonality. Extensively parameterized with gamma correction, gradient smoothing, and multi-level weighting.
- **grid_warping/ (7 files)** -- Grid warping for image reproduction using integral images and gradient-based displacement. Key technique: compute cumulative integral image, use it to non-uniformly redistribute grid lines, warping denser lines into darker regions.
  - **using image integrals/ (5 files)** -- Image integral table approach for grid warping with fixed contours.
  - **two_step_warping with resampling.ipynb** -- Two-step warping with mesh resampling.
- **mcmc/ (4 files)** -- Markov Chain Monte Carlo sampling for image reproduction:
  - **stippling.ipynb** -- MCMC stippling: samples point positions proportional to image darkness using Metropolis-Hastings random walks with acceptance probability based on pixel intensity ratios.
  - **multiscale.ipynb** -- Multi-scale MCMC approaches.
  - **everything is sane in this one.ipynb** -- Validated MCMC implementation.
- **neural networks/ (4 files)** -- Neural network approaches for line art:
  - **line rasterization - try 1.ipynb / batch.ipynb** -- Training neural networks (PyTorch) to learn line rasterization from coordinate inputs, attempting to learn a differentiable line renderer.
  - **pytorch check.ipynb** -- PyTorch setup verification.
- **portraits/ (9 files)** -- Portrait-specific realism:
  - **napolean/ (7 files)** -- Napoleon portrait rendered via contour shading, sharpening, and multi-technique approaches.
  - **geoff_japan.ipynb / marie.ipynb** -- Personal portrait pieces.
  - **tonal_pyramid.ipynb** -- Tonal pyramid-based shading.
  - **dithering attempt.ipynb** -- Dithering for portraits.
  - **new library!!.ipynb** -- Testing new plottermagic library features.
- **smooth wrinkels/ (4 files)** -- Cloth/wrinkle texture rendering using derivative-based grid warping.
- **bilateral.ipynb** -- Bilateral filter-based image processing for line art.
- **hough-lines.ipynb** -- Hough line transform for image abstraction.
- **sampling.ipynb** -- Importance sampling for image-weighted line placement.
- **semi_working (4 variants)** -- Iterative development of working realism techniques.
- **prints/ (5 files)** -- Print-ready realism pieces.

### pieces/rendering/ (6 files)
3D wireframe rendering using the plottermagic 3D engine.

- **TESTS.ipynb** -- Interactive 3D rendering test suite using plottermagic's camera, render, and occlusion modules. Tests unit cubes, face rendering, multi-object scenes, and textured shapes with interactive widget controls for camera position. Implements both non-occluded and occluded rendering passes.
- **buggy city.ipynb** -- Procedural city skyline: generates random-sized unit cubes (buildings) arranged along two axes with varying width/height, rendered from configurable camera angles with interactive sliders for distance, angle, and elevation.
- **mostly debugging/ (3 files)** -- Step-by-step rendering debugging, simple render tests, and unit cube verification.

### pieces/sandbox/ (67 files)
Experimental sandbox for testing new ideas and techniques.

- **2d fft.ipynb** -- 2D FFT experiments.
- **analytic gradient methods.ipynb** -- Analytical gradient computation for line art.
- **ast.ipynb / ast_test.py** -- Python AST manipulation for generative code (shapely geometry operations driven by AST).
- **copper lines.ipynb** -- Copper pen line experiments.
- **diamond grid.ipynb** -- Diamond-shaped grid patterns.
- **dictionary.ipynb** -- Dictionary-based generative experiments.
- **free form displacement.ipynb** -- Freeform mesh displacement.
- **gabor.ipynb** -- Gabor filter-based texture generation.
- **grid_warping!!!.ipynb** -- Grid warping breakthrough experiments.
- **laplace noise.ipynb** -- Laplacian noise fields.
- **mobius.ipynb** -- Mobius strip rendering.
- **moire fft.ipynb / moire_warped.ipynb** -- FFT and warped moire experiments.
- **pyramid_blending.ipynb** -- Laplacian pyramid image blending.
- **radially_wraped_grid.ipynb** -- Radially warped grid patterns.
- **skeletons.ipynb** -- Morphological skeleton extraction for line art.
- **smoke.ipynb** -- Smoke simulation experiments.
- **triangle_comp.ipynb** -- Triangle-based compositions.
- **unit_square.ipynb** -- Unit square transform experiments.
- **bman/ (4 files)** -- Burning Man themed pieces: man structure rendering with rotation, ash-themed compositions.
- **color theory/ (3 files)** -- Color theory explorations including transparency and portrait coloring.
- **draw via grad/ (7 files)** -- Drawing by following image gradients -- a precursor to the realism/dynamic_systems approach. "Kinda actually works" subfolder contains the breakthrough versions using 2x line density and gradient clipping.
- **geometric reduction/ (6 files)** -- Reduces famous paintings (Nighthawks, Las Meninas, Caravaggio) to geometric line abstractions using edge detection, Hough line transforms, and probabilistic line fitting.
- **intrinsic_images/ (2 files)** -- Intrinsic image decomposition experiments.
- **line_param/ (1 file)** -- Line parameterization experiments.
- **raytracing/ (13 files)** -- Numpy-based ray tracing:
  - **fast rt/ (10 files)** -- Vectorized numpy ray tracer with sphere intersection, Lambert+Blinn-Phong+reflection shading, shadows, and plane rendering. Includes layer decomposition for multi-pen plotting.
  - **weekend/ (2 files)** -- "Ray Tracing in One Weekend" implementation in numpy with vec3 class, recursive reflection, and checkered ground planes.
  - **intro code.ipynb / opt try 1/2.ipynb** -- Initial ray tracer and optimization attempts.
- **surfaces/ (6 files)** -- 3D surface visualization: antelope canyon textures, bilateral surface filtering, pyramid blending, surface simulation, wrapping paper patterns.
- **will.ipynb / will collab painting.ipynb** -- Collaborative painting pieces.

### pieces/smoke/ (7 files)
Smoke strand and wisp generation using radial coordinate perturbation.

- **smoke strands.ipynb** -- Core smoke technique: generates strands by iteratively perturbing lines in radial coordinates -- adds cumulative FFT-smoothed noise to radius and random walk noise to angle, then converts back to Cartesian. Multiple starting lines create bundled smoke wisps that diverge organically. Includes velocity-based random walk layer.
- **exploratory.ipynb** -- Initial smoke effect exploration.
- **simplex.ipynb** -- Simplex noise-driven smoke.
- **grad perlin.ipynb** -- Gradient Perlin noise smoke.
- **Line CAH - first pass.ipynb** -- Correlated area halftoning smoke.
- **cloth-print.ipynb** -- Cloth-textured smoke print.

### pieces/sourcery/ (2 .py files)
Image processing utility library used across multiple piece directories.

- **image_magic.py** -- Key utility module providing:
  - `get_fft_smoothed()` -- FFT-based Gaussian smoothing of images.
  - `est_smooth_grad()` -- Multi-scale gradient estimation using weighted Sobel derivatives at multiple FFT smoothing levels, with optional postprocessing (clip/norm/scale).
  - `mask_lines()` -- Clips line arrays to boolean masks by detecting mask transitions and extracting visible segments.
  - `make_int_mesh()` / `make_lin_mesh()` -- Creates integer/linear coordinate meshes.
  - `resample_2d_mesh()` -- Resamples meshes to different resolutions.
  - `eval2d_on_mesh()` -- Evaluates 2D vector fields on mesh coordinates using `ndimage.map_coordinates`.
- **__init__.py** -- Empty package init.

### pieces/spirals/ (10 files)
Spiral-based compositions with multi-level and rainbow variants.

- **spirals.ipynb** -- Base spiral generation.
- **multilevel spiral.ipynb** -- Multi-level/nested spiral compositions.
- **circliural multilevel.ipynb** -- Circular multilevel spirals.
- **riptide.ipynb** -- Riptide/vortex spiral piece.
- **print-spirals.ipynb / print - bw spiral.ipynb / print full swirl.ipynb / print- bw cutout.ipynb** -- Print-ready spiral pieces.
- **rainbow circliural multilevel.ipynb** -- Rainbow colored multilevel spiral.

### pieces/tutorial_mods/ (3 files)
Modified tutorial examples.

- **depth line interactive.ipynb** -- Interactive depth line visualization.
- **with lines.ipynb** -- Tutorial modification with line additions.

### pieces/wallpaper_groups/ (2 .py files)
Mathematical wallpaper group symmetry implementations.

- **wallpaper.py** -- `WallpaperGroup` class implementing the 17 plane symmetry groups. Takes origin and two basis vectors, determines lattice shape (square/rectangle/rhombus/hexagonal), computes corners/centers/midpoints, and lists valid symmetry patterns (e.g., "o", "2222", "*2222", "442" for square lattice). Uses plottermagic's geom2d for transformations.
- **__init__.py** -- Package init.

### pieces/wave_column/ (1 file)
- **Untitled.ipynb** -- Wave column experiment.

### pieces/waves/ (14 files, 2 .py)
Wave and curve generation with physics-inspired dynamics.

- **util.py** -- Wave generation utility: `make_wave()` creates initial curves from triangular noise, `make_noisy_curves()` iteratively applies noise-driven acceleration/velocity to evolve curves over time with cardinal spline smoothing, producing organic wave progressions. Supports closed curves and alternating draw direction.
- **__init__.py** -- Package init.
- **turtletoy/ (6 files)** -- Turtle graphics-style wave implementations including calligraphy, interactive wave, and signature generators.
- **given_curves/ (3 files)** -- Parabola-based wave compositions with reflections.
- **rainbows/ (4 files)** -- Rainbow-colored wave compositions.
- **experiments/ (1 file)** -- Line grid wave experiments.

### pieces/weed/ (7 files)
Cannabis-themed commissioned/commercial pieces.

- **production.ipynb** -- Production-ready cannabis piece.
- **circle reference.ipynb / oil slick reference.ipynb / sunset reference.ipynb** -- Reference-based compositions.
- **demo-gradient.ipynb** -- Gradient demo piece.
- **mockup.ipynb** -- Design mockup.

---

## Technique Cross-Reference Index

### By Technique Category

#### Noise & Fields
| Technique | Primary Location | Also Used In |
|-----------|-----------------|--------------|
| Perlin noise fields | `perlin/`, `2d_moires/oil_slick/` | `litho/`, `rainbow/`, `laser cutter/`, `smoke/` |
| Laplacian noise | `laplace noise/`, `2d_moires/custom noise/` | `sandbox/` |
| Simplex noise | `smoke/simplex.ipynb` | -- |
| FFT-based surface generation | `fft/` | `sourcery/image_magic.py`, `realism/`, `death_textures/` |
| Reaction-diffusion (Gray-Scott) | `reaction_diff/` | -- |
| Flow fields | `2d_moires/custom noise/four_squares-flow.ipynb` | `impasto/flow.ipynb` |

#### Image Processing & Realism
| Technique | Primary Location | Also Used In |
|-----------|-----------------|--------------|
| Gradient-based grid warping | `realism/dynamic_systems.ipynb` | `death_textures/`, `sourcery/image_magic.py` |
| Image integral warping | `realism/grid_warping/` | -- |
| Crosshatching portraits | `portraits/crosshatching.ipynb` | -- |
| Stippling (Bridson/Lloyd/MCMC) | `portraits/stippling/`, `realism/mcmc/` | -- |
| Halftoning | `portraits/stochasic_halftones.ipynb` | -- |
| Edge detection / Hough lines | `realism/hough-lines.ipynb` | `sandbox/geometric reduction/` |
| Bilateral filtering | `realism/bilateral.ipynb` | `sandbox/surfaces/` |
| Pyramid blending | `death_textures/blending/` | `sandbox/pyramid_blending.ipynb` |
| Neural line rasterization | `realism/neural networks/` | -- |
| Geometric reduction (paintings) | `sandbox/geometric reduction/` | -- |

#### Moire & Interference
| Technique | Primary Location | Also Used In |
|-----------|-----------------|--------------|
| Overlapping line grids | `2d_moires/moire/` | `litho/litho moire.ipynb` |
| Perlin-projected moire | `2d_moires/oil_slick/` | `2d_moires/moire/` |
| Metallic Perlin moire | `2d_moires/metalic_perlin/` | -- |
| Surface contour moire | `2d_moires/surface_moires/` | -- |
| Glass refraction moire | `2d_moires/glass/` | -- |
| Cloth moire | `cloth/moire.ipynb` | -- |

#### 3D Rendering
| Technique | Primary Location | Also Used In |
|-----------|-----------------|--------------|
| Perspective projection (plottermagic) | `rendering/` | `cloth/3d.ipynb`, `gifs/` |
| Wireframe city generation | `rendering/buggy city.ipynb` | -- |
| Occlusion culling | `rendering/TESTS.ipynb` | -- |
| Ray tracing (numpy vectorized) | `sandbox/raytracing/` | -- |
| Anaglyph stereoscopy | `anaglyph/` | `paper/cutout anaglyph.ipynb` |
| Polygon shading/textures | `rendering/` (via plottermagic) | -- |

#### Simulation & Physics
| Technique | Primary Location | Also Used In |
|-----------|-----------------|--------------|
| Cloth simulation | `cloth/` | `realism/smooth wrinkels/` |
| Smoke strands | `smoke/` | `sandbox/smoke.ipynb` |
| Brownian motion | `painting/brownian motion.ipynb` | -- |
| Wave dynamics | `waves/` | -- |
| Reaction-diffusion | `reaction_diff/` | -- |

#### Symmetry & Tiling
| Technique | Primary Location | Also Used In |
|-----------|-----------------|--------------|
| Wallpaper groups (17 types) | `wallpaper_groups/`, `new_wallpaper_groups/` | -- |
| Voronoi tessellation | `polygon_tess/` | `laser cutter/` |
| Graph-based partitioning | `polygon_tess/network.py` | -- |

#### Composition & Style
| Technique | Primary Location | Also Used In |
|-----------|-----------------|--------------|
| Agnes Martin minimalism | `agnes/` | `litho/agnes type stuff.ipynb` |
| Sol LeWitt wall drawings | `lewitt/`, `lewitt challenge/` | `pencil/lewitt add boxes.ipynb` |
| Frank Stella concentric shapes | `litho/frank stella.ipynb` | `rainbow/frank stella.ipynb` |
| Black etching | `black_etching/` | `cloth/black_etching.ipynb` |
| Rainbow multi-pen | `rainbow/` | `spirals/`, `paper_cutouts/`, `patreon/` |
| Impasto thick lines | `impasto/` | -- |
| Pencil-optimized | `pencil/` | -- |

#### Output & Tooling
| Technique | Primary Location | Also Used In |
|-----------|-----------------|--------------|
| SVG output for plotter | all pieces via `canvas.fig.savefig()` | -- |
| OpenSCAD / 3D printing | `openscad/` | -- |
| Laser cutter SVG | `laser cutter/` | -- |
| GIF animation | `gifs/` | `sandbox/geometric reduction/*-video.ipynb` |
| GLSL shader port | `"shaders"/` | -- |

### By Library Module Used

| Module | Pieces Using It |
|--------|----------------|
| `pdesign` (canvas, shapes, lines, transforms, smooth) | ~60% of all pieces |
| `plottermagic.line_render` (camera, render, occlusion) | `rendering/`, `anaglyph/`, `gifs/` |
| `plottermagic.shading` (grid, masking, simple_shapes) | `portraits/crosshatching`, `rendering/` |
| `plottermagic.images` (image_processing) | `portraits/`, `realism/` |
| `plottermagic.io` (io, location) | `realism/`, `death_textures/`, `portraits/` |
| `plottermagic.geometry` (geom2d, geom3d, splines) | `wallpaper_groups/`, `rendering/`, `waves/` |
| `plottermagic.random` (possion_disk_sampling) | `impasto/dots.ipynb`, `portraits/stippling/` |
| `sourcery.image_magic` | `realism/`, `death_textures/` |
| `polygon_tess.network` | `polygon_tess/` |
| `scipy.ndimage` (fourier_gaussian, sobel, map_coordinates) | `realism/`, `fft/`, `death_textures/`, `smoke/` |
| `noise` (pnoise2) | `2d_moires/`, `litho/`, `perlin/`, `fft/` |
| `torch` (PyTorch) | `realism/neural networks/` |
| `shapely` | nearly all pieces |

### File Count by Directory

| Directory | .ipynb | .py | Total |
|-----------|--------|-----|-------|
| 2d_moires | 59 | 0 | 59 |
| sandbox | 67 | 1 | 68 |
| portraits | 54 | 0 | 54 |
| realism | 52 | 0 | 52 |
| lewitt + lewitt challenge | 62 | 0 | 62 |
| death_textures | 31 | 0 | 31 |
| laser cutter | 32 | 0 | 32 |
| painting | 31 | 0 | 31 |
| rainbow | 21 | 0 | 21 |
| pencil | 20 | 0 | 20 |
| litho | 19 | 0 | 19 |
| cloth | 14 | 0 | 14 |
| fft | 14 | 0 | 14 |
| waves | 14 | 2 | 16 |
| impasto | 13 | 0 | 13 |
| block grids | 10+ | 0 | 10+ |
| patreon | 11 | 0 | 11 |
| spirals | 10 | 0 | 10 |
| agnes | 8 | 0 | 8 |
| anaglyph | 8 | 0 | 8 |
| black_etching | 8 | 0 | 8 |
| smoke | 7 | 0 | 7 |
| weed | 7 | 0 | 7 |
| circle_grids | 7 | 0 | 7 |
| openscad | 7 | 0 | 7 |
| rendering | 6 | 0 | 6 |
| paper + paper_cutouts | 5 | 0 | 5 |
| new_wallpaper_groups | 0 | 3 | 3 |
| acrylic | 3 | 0 | 3 |
| tutorial_mods | 3 | 0 | 3 |
| wallpaper_groups | 0 | 2 | 2 |
| sourcery | 0 | 2 | 2 |
| design_lib_brainstorm | 0 | 2 | 2 |
| polygon_tess | 0 | 2 | 2 |
| reaction_diff | 2 | 0 | 2 |
| perlin | 2 | 0 | 2 |
| poetry | 2 | 0 | 2 |
| concept | 2 | 0 | 2 |
| "shaders" | 2 | 0 | 2 |
| image_pieces | 2 | 0 | 2 |
| gifs | 1 | 0 | 1 |
| wave_column | 1 | 0 | 1 |
| old bad | 1 | 0 | 1 |
| laplace noise | 1 | 0 | 1 |
| Other (bin, top-level) | 0 | 2 | 2 |

#!/usr/bin/env python3
"""Render gallery images for penpal example techniques.

Generates one PNG per technique using matplotlib's savefig.
Each function creates a Drawing, renders it via the matplotlib backend,
and saves as PNG.

Usage:
    .venv/bin/python gallery/render_gallery.py
"""

import os
import sys

# Ensure penpal is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from penpal.core.drawing import Drawing
from penpal.core.paths import Paths

GALLERY_DIR = os.path.dirname(os.path.abspath(__file__))
DPI = 200
BG_COLOR = "white"


def save_drawing_png(drawing, name, dpi=DPI):
    """Render a Drawing to PNG via matplotlib."""
    fig, ax = drawing.show(grid=False)
    ax.set_axis_off()
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    fig.tight_layout(pad=0.3)
    path = os.path.join(GALLERY_DIR, f"{name}.png")
    fig.savefig(path, dpi=dpi, facecolor=BG_COLOR, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {path}")


# ---------------------------------------------------------------------------
# 1. Basics — Hilbert curve + circles
# ---------------------------------------------------------------------------
def render_basics():
    from penpal.gen.curves import hilbert, circle, spiral

    d = Drawing(8, 8, center=True, show_grid=False)
    h = hilbert(order=5, size=6, origin=(-3, -3))
    d.layer("hilbert", color="#2563EB", linewidth=0.008).add(h)

    for r in [1.0, 2.0, 3.0]:
        c = circle(center=(0, 0), radius=r)
        d.layer("circles", color="#DC2626", linewidth=0.01).add(c)

    s = spiral(center=(0, 0), outer_r=3.5, turns=8, num_points=1000)
    d.layer("spiral", color="#059669", linewidth=0.008).add(s)
    save_drawing_png(d, "01_basics")


# ---------------------------------------------------------------------------
# 2. Strange Attractors
# ---------------------------------------------------------------------------
def render_attractors():
    from penpal.gen.attractors import lorenz

    d = Drawing(10, 8, center=True, show_grid=False)

    # Lorenz attractor - classic butterfly shape
    att = lorenz(n_steps=30000, dt=0.005, projection="xz")
    # Split into segments for matplotlib
    all_pts = att.lines[0]
    seg_len = 500
    segs = [all_pts[i:i + seg_len] for i in range(0, len(all_pts), seg_len)
            if len(all_pts[i:i + seg_len]) >= 2]
    att = Paths(segs)

    # Normalize to drawing bounds
    xmin = min(s[:, 0].min() for s in segs)
    xmax = max(s[:, 0].max() for s in segs)
    ymin = min(s[:, 1].min() for s in segs)
    ymax = max(s[:, 1].max() for s in segs)
    scale = min(8 / (xmax - xmin + 1e-10), 6 / (ymax - ymin + 1e-10)) * 0.9
    cx = (xmin + xmax) / 2
    cy = (ymin + ymax) / 2
    att = att.translate(-cx, -cy).scale(scale)
    d.layer("attractor", color="#1E293B", linewidth=0.006).add(att)
    save_drawing_png(d, "02_attractors")


# ---------------------------------------------------------------------------
# 3. Flow Fields
# ---------------------------------------------------------------------------
def render_flow_fields():
    from penpal.gen import flow

    d = Drawing(8, 10, show_grid=False)
    field = flow.curl_field(frequency=0.6, seed=42)
    seeds = flow.seeds_grid(0.2, 0.2, 7.8, 9.8, nx=30, ny=40)
    paths = flow.trace(field, seeds, steps=300, step_size=0.03,
                       momentum=0.9, bounds=(0, 0, 8, 10))
    d.layer("flow", color="#1E293B", linewidth=0.008).add(paths)
    save_drawing_png(d, "03_flow_fields")


# ---------------------------------------------------------------------------
# 4. Noise Grid
# ---------------------------------------------------------------------------
def render_noise_grid():
    from penpal.gen.grids import noise_grid

    d = Drawing(8, 10, show_grid=False)
    g = noise_grid(x0=0.2, y0=0.2, x1=7.8, y1=9.8,
                   rows=40, cols=32, amplitude=0.2, frequency=0.7,
                   smooth=True, seed=77)
    d.layer("grid", color="#1E293B", linewidth=0.008).add(g)
    save_drawing_png(d, "04_noise_grid")


# ---------------------------------------------------------------------------
# 5. Polar Noise Grid
# ---------------------------------------------------------------------------
def render_polar_noise_grid():
    from penpal.gen.grids import polar_noise_grid

    d = Drawing(10, 10, center=True, show_grid=False)
    g = polar_noise_grid(center=(0, 0), inner_r=0.3, outer_r=4.5,
                         n_rings=30, n_spokes=48,
                         amplitude=0.15, frequency=0.8, twist=1.5,
                         smooth=True, seed=42)
    d.layer("polar", color="#1E293B", linewidth=0.008).add(g)
    save_drawing_png(d, "05_polar_noise_grid")


# ---------------------------------------------------------------------------
# 6. Fractals — Dragon Curve
# ---------------------------------------------------------------------------
def render_fractals():
    from penpal.gen.ifs import barnsley_fern, dragon_curve

    d = Drawing(10, 10, center=True, show_grid=False)
    f = barnsley_fern(n_points=80000)
    f = f.scale(0.8)
    d.layer("fern", color="#059669", linewidth=0.003).add(f)

    dc = dragon_curve(order=12)
    pts = dc.lines[0]
    xr = pts[:, 0].max() - pts[:, 0].min()
    yr = pts[:, 1].max() - pts[:, 1].min()
    sc = min(4 / max(xr, 1), 4 / max(yr, 1))
    dc = dc.translate(-pts[:, 0].mean(), -pts[:, 1].mean()).scale(sc)
    d.layer("dragon", color="#7C3AED", linewidth=0.005).add(dc)
    save_drawing_png(d, "06_fractals")


# ---------------------------------------------------------------------------
# 7. Envelopes — Cardioid + Diamond
# ---------------------------------------------------------------------------
def render_envelopes():
    from penpal.gen.envelopes import cardioid_envelope, diamond

    d = Drawing(10, 10, center=True, show_grid=False)

    # Cardioid envelope
    card = cardioid_envelope(n_lines=120, radius=4.0, multiplier=2.0)
    d.layer("cardioid", color="#DC2626", linewidth=0.008).add(card)

    # Inner diamond
    dia = diamond(n_lines=30, size=2.0)
    d.layer("diamond", color="#2563EB", linewidth=0.008).add(dia)
    save_drawing_png(d, "07_envelopes")


# ---------------------------------------------------------------------------
# 8. Contours — Gaussian Bumps
# ---------------------------------------------------------------------------
def render_contours():
    from penpal.gen.contours import gaussian_bumps

    d = Drawing(10, 8, center=True, show_grid=False)
    bumps = gaussian_bumps(n_bumps=8, x_range=(-4.5, 4.5), y_range=(-3.5, 3.5),
                           n_levels=35, seed=42, resolution=300)
    d.layer("contours", color="#1E293B", linewidth=0.008).add(bumps)
    save_drawing_png(d, "08_contours")


# ---------------------------------------------------------------------------
# 9. Spline Waves
# ---------------------------------------------------------------------------
def render_spline_waves():
    from penpal.gen.spline_waves import spline_waves

    d = Drawing(10, 8, show_grid=False)
    waves = spline_waves(n_points=12, n_frames=80,
                         x_range=(0.5, 9.5), y_range=(1, 7),
                         force_scale=0.04, damping=0.96, seed=42)
    d.layer("waves", color="#1E293B", linewidth=0.008).add(waves)
    save_drawing_png(d, "09_spline_waves")


# ---------------------------------------------------------------------------
# 10. Mandala (Dihedral Symmetry)
# ---------------------------------------------------------------------------
def render_mandala():
    from penpal.symmetry import dihedral
    from penpal.gen.curves import rose, spiral, circle

    d = Drawing(10, 10, center=True, show_grid=False)

    # Create a wedge with some interesting art
    wedge = Paths()
    # Rose curve
    r = rose(center=(0, 0), radius=3.5, k=7, num_points=800)
    wedge = wedge + r
    # Some circles
    for rad in [1.0, 2.0, 3.0, 4.0]:
        wedge = wedge + circle(center=(0, 0), radius=rad, num_points=200)

    # Spiral element
    s = spiral(center=(1.5, 0), outer_r=0.8, turns=4, num_points=200)
    mandala = dihedral(s, n=8, center=(0, 0))

    d.layer("rose", color="#7C3AED", linewidth=0.008).add(wedge)
    d.layer("spirals", color="#DC2626", linewidth=0.006).add(mandala)
    save_drawing_png(d, "10_mandala")


# ---------------------------------------------------------------------------
# 11. Moire — Concentric Circles
# ---------------------------------------------------------------------------
def render_moire():
    from penpal.gen.moire import concentric_circles, combine_layers

    d = Drawing(10, 10, center=True, show_grid=False)
    layers = concentric_circles(n_rings=80, max_radius=6.0,
                                 centers=[(0, 0), (1.5, 0.5)],
                                 n_points=300)
    colors = ["#1E293B", "#DC2626"]
    for i, (paths, color) in enumerate(zip(layers, colors)):
        d.layer(f"moire_{i}", color=color, linewidth=0.01, alpha=0.8).add(paths)
    save_drawing_png(d, "11_moire")


# ---------------------------------------------------------------------------
# 12. Cloth Drape
# ---------------------------------------------------------------------------
def render_cloth():
    from penpal.gen.cloth import cloth_fill

    d = Drawing(10, 8, show_grid=False)

    # Two sinusoidal boundary curves
    n = 200
    x = np.linspace(0.5, 9.5, n)
    y_a = 1.0 + 0.5 * np.sin(x * 1.2)
    y_b = 7.0 + 0.3 * np.sin(x * 0.8 + 1.0)
    curve_a = np.column_stack([x, y_a])
    curve_b = np.column_stack([x, y_b])

    cloth = cloth_fill(curve_a, curve_b, n_curves=80,
                       noise_amp=0.08, spline=True, easing="cosine",
                       seed=42)
    d.layer("cloth", color="#1E293B", linewidth=0.006).add(cloth)
    save_drawing_png(d, "12_cloth_drape")


# ---------------------------------------------------------------------------
# 13. Polar Ribbons
# ---------------------------------------------------------------------------
def render_polar_ribbons():
    from penpal.gen.polar import concentric_ribbons

    d = Drawing(10, 10, center=True, show_grid=False)
    ribbons = concentric_ribbons(n_ribbons=6, n_fills=12,
                                  inner_r=0.5, outer_r=4.5,
                                  noise_amplitude=0.1, seed=42)
    d.layer("ribbons", color="#1E293B", linewidth=0.006).add(ribbons)
    save_drawing_png(d, "13_polar_ribbons")


# ---------------------------------------------------------------------------
# 14. Metaballs
# ---------------------------------------------------------------------------
def render_metaballs():
    from penpal.effects.metaballs import metaballs

    d = Drawing(10, 10, center=True, show_grid=False)
    mb = metaballs(n_balls=7, threshold=1.0, n_contours=15,
                   x_range=(-4.5, 4.5), y_range=(-4.5, 4.5),
                   resolution=400, seed=42)
    d.layer("metaballs", color="#1E293B", linewidth=0.008).add(mb)
    save_drawing_png(d, "14_metaballs")


# ---------------------------------------------------------------------------
# 15. Wallpaper Groups
# ---------------------------------------------------------------------------
def render_wallpaper():
    from penpal.symmetry import WallpaperGroup
    from penpal.gen.curves import rose

    d = Drawing(10, 10, show_grid=False)

    wg = WallpaperGroup(origin=(0, 0), b1=(0, 2), b2=(2, 0))
    motif = rose(center=(1, 1), radius=0.8, k=3, num_points=200)
    tiled = wg.generate(motif, "*442", nx=5, ny=5)

    d.layer("wallpaper", color="#1E293B", linewidth=0.008).add(tiled)
    save_drawing_png(d, "15_wallpaper")


# ---------------------------------------------------------------------------
# 16. Droste Effect (Mirror Slice)
# ---------------------------------------------------------------------------
def render_droste():
    from penpal.symmetry import mirror_slice
    from penpal.gen.curves import rose, polygon_regular
    from penpal.gen.envelopes import cardioid_envelope

    d = Drawing(10, 10, center=True, show_grid=False)

    # Create base art
    base = Paths()
    base = base + rose(center=(0, 0), radius=4.0, k=5, num_points=500)
    base = base + cardioid_envelope(n_lines=60, radius=3.5, multiplier=3.0)
    for n in [3, 5, 7]:
        base = base + polygon_regular(center=(0, 0), radius=3.5, n_sides=n)

    droste = mirror_slice(base, center=(0, 0), n_levels=5,
                          outer_r=4.5, inner_r=0.3, zoom_factor=1.8)
    d.layer("droste", color="#1E293B", linewidth=0.006).add(droste)
    save_drawing_png(d, "16_droste")


# ---------------------------------------------------------------------------
# 17. Voronoi Hatched
# ---------------------------------------------------------------------------
def render_voronoi_hatched():
    from penpal.sampling import poisson_disk, voronoi
    from penpal.shading import hatch_polygon

    d = Drawing(8, 10, show_grid=False)

    pts = poisson_disk(8, 10, min_dist=0.8, seed=42)
    cells = voronoi(pts, bounds=(0, 0, 8, 10))

    rng = np.random.default_rng(42)
    for cell in cells:
        angle = rng.uniform(0, 180)
        spacing = rng.uniform(0.06, 0.2)
        hatched = hatch_polygon(cell, angle=angle, spacing=spacing)
        d.layer("hatches", color="#1E293B", linewidth=0.006).add(hatched)
        # Draw cell boundary
        d.layer("cells", color="#94A3B8", linewidth=0.01).add(Paths([cell]))

    save_drawing_png(d, "17_voronoi_hatched")


# ---------------------------------------------------------------------------
# 18. Shading Fills Demo
# ---------------------------------------------------------------------------
def render_shading():
    from penpal.shading import hatch_polygon, stipple_polygon

    d = Drawing(10, 8, show_grid=False)

    # Hexagon with cross-hatching
    hex_pts = np.column_stack([
        2.5 + 1.8 * np.cos(np.linspace(0, 2 * np.pi, 7)),
        4.0 + 1.8 * np.sin(np.linspace(0, 2 * np.pi, 7))
    ])
    h1 = hatch_polygon(hex_pts, angle=0, spacing=0.08)
    h2 = hatch_polygon(hex_pts, angle=60, spacing=0.08)
    h3 = hatch_polygon(hex_pts, angle=120, spacing=0.08)
    d.layer("hatch", color="#1E293B", linewidth=0.005).add(h1)
    d.layer("hatch").add(h2)
    d.layer("hatch").add(h3)
    d.layer("hex_outline", color="#DC2626", linewidth=0.015).add(Paths([hex_pts]))

    # Circle with hatching at 45 degrees
    t = np.linspace(0, 2 * np.pi, 101)
    circle_pts = np.column_stack([5.5 + 1.5 * np.cos(t), 4.0 + 1.5 * np.sin(t)])
    h4 = hatch_polygon(circle_pts, angle=45, spacing=0.06)
    d.layer("hatch2", color="#2563EB", linewidth=0.005).add(h4)
    d.layer("circle_outline", color="#2563EB", linewidth=0.015).add(Paths([circle_pts]))

    # Triangle with stippling
    tri = np.array([[8.0, 2.5], [9.5, 5.5], [8.0, 5.5], [8.0, 2.5]])
    stippled = stipple_polygon(tri, density=100, seed=42)
    d.layer("stipple", color="#059669", linewidth=0.005).add(stippled)
    d.layer("tri_outline", color="#059669", linewidth=0.015).add(Paths([tri]))

    save_drawing_png(d, "18_shading_fills")


# ---------------------------------------------------------------------------
# 19. Barrel Distortion Grid
# ---------------------------------------------------------------------------
def render_barrel():
    from penpal.gen.grids import barrel_distortion

    d = Drawing(8, 10, show_grid=False)
    g = barrel_distortion(x0=0.3, y0=0.3, x1=7.7, y1=9.7,
                          rows=25, cols=20, k=0.5,
                          points_per_line=80)
    d.layer("barrel", color="#1E293B", linewidth=0.008).add(g)
    save_drawing_png(d, "19_barrel_distortion")


# ---------------------------------------------------------------------------
# 20. Lissajous + Rose Curves
# ---------------------------------------------------------------------------
def render_curves():
    from penpal.gen.curves import lissajous, rose, spiral

    d = Drawing(10, 10, center=True, show_grid=False)

    colors = ["#DC2626", "#2563EB", "#059669", "#D97706", "#7C3AED"]
    for i, (fx, fy) in enumerate([(3, 2), (5, 4), (7, 6), (5, 3), (4, 3)]):
        l = lissajous(center=(0, 0), a=3.5, b=3.5,
                      freq_x=fx, freq_y=fy, phase=i * 0.3,
                      num_points=1000)
        d.layer(f"liss_{i}", color=colors[i], linewidth=0.008, alpha=0.6).add(l)

    save_drawing_png(d, "20_lissajous")


# ---------------------------------------------------------------------------
# 21. Braid
# ---------------------------------------------------------------------------
def render_braid():
    from penpal.gen.cloth import braid

    d = Drawing(12, 6, show_grid=False)
    x = np.linspace(0.5, 11.5, 150)
    curve_a = np.column_stack([x, 0.8 * np.sin(x * 0.7)])
    curve_b = np.column_stack([x, 0.8 * np.sin(x * 0.7) + 3.5])
    strands = braid(curve_a, curve_b, n_strands=4, n_curves_per_strand=30,
                    weave_freq=4.0, weave_amp=0.15, noise_amp=0.02, seed=42)
    colors = ["#264653", "#2a9d8f", "#e9c46a", "#e63946"]
    for i, (strand, color) in enumerate(zip(strands, colors)):
        strand = strand.translate(0, 1.25)
        d.layer(f"strand_{i}", color=color, linewidth=0.006).add(strand)
    save_drawing_png(d, "21_braid")


# ---------------------------------------------------------------------------
# 22. Perspective Drape (Rainbow Road)
# ---------------------------------------------------------------------------
def render_perspective():
    from penpal.gen.cloth import perspective_drape

    d = Drawing(12, 8, show_grid=False)
    x = np.linspace(-5, 15, 300)
    y = np.full_like(x, -3.0)
    base = np.column_stack([x, y])
    p = perspective_drape(base, dx=2.0, dy=8.0, z_range=(1.0, 2.5),
                          n_z_control=30, n_curves=60, focal_length=1.0,
                          z_smooth=5, x_noise=0.15, seed=42)
    p = p.translate(1, 0)
    d.layer("road", color="#1a1a2e", linewidth=0.01).add(p)
    save_drawing_png(d, "22_perspective_drape")


# ---------------------------------------------------------------------------
# 23. Halftone (requires CV extras)
# ---------------------------------------------------------------------------
def render_halftone():
    from penpal.cv import image, halftone

    img = image.load("examples/assets/the_eyes_of_tj_eckleburg.jpg")
    d = Drawing(10, 8, show_grid=False)
    p = halftone.crosshatch(img, angles=(0, 45, 90, 135), n_bands=8, max_density=800)
    p = image.map_to_drawing(p, img.shape, d)
    d.layer("xhatch", color="#1a1a2e", linewidth=0.004).add(p)
    save_drawing_png(d, "23_halftone")


# ---------------------------------------------------------------------------
# 24. Portrait Warp (Bradway technique)
# ---------------------------------------------------------------------------
def render_portrait():
    from penpal.cv import image, texture

    img = image.load("examples/assets/the_eyes_of_tj_eckleburg.jpg")
    d = Drawing(10, 8, show_grid=False)
    p = texture.portrait_warp(img, n_lines=250, grad_smooth=2.5,
                              warp_strength=-0.8, tonal_denom=4,
                              tonal_gamma=0.65, stride=1, morph_clean=3)
    p = image.map_to_drawing(p, img.shape, d)
    d.layer("portrait", color="#1a1a2e", linewidth=0.006).add(p)
    save_drawing_png(d, "24_portrait_warp")


# ---------------------------------------------------------------------------
# 25. Death Textures (requires DTD dataset)
# ---------------------------------------------------------------------------
def render_death_textures():
    from penpal.cv import image, texture, datasets

    img, _ = datasets.load_random("dtd", "cracked", seed=42)
    d = Drawing(10, 8, show_grid=False)
    p = texture.gradient_warp(img, alpha=-10, gamma=4.0, fft_sigma=3,
                              grad_smooth=0.5, h_stride=2, v_stride=2, density=2.0)
    p = image.map_to_drawing(p, img.shape, d)
    d.layer("death", color="#1a1a2e", linewidth=0.006).add(p)
    save_drawing_png(d, "25_death_textures")


# ---------------------------------------------------------------------------
# 26. Dithering
# ---------------------------------------------------------------------------
def render_dithering():
    from penpal.cv import image, dither

    img = image.load("examples/assets/the_eyes_of_tj_eckleburg.jpg")
    d = Drawing(10, 8, show_grid=False)
    p = dither.dither_to_lines(img, kernel="atkinson", row_skip=2)
    p = image.map_to_drawing(p, img.shape, d)
    d.layer("dither", color="#1a1a2e", linewidth=0.004).add(p)
    save_drawing_png(d, "26_dithering")


# ---------------------------------------------------------------------------
# 27. STL Sketch (NPR rendering)
# ---------------------------------------------------------------------------
def render_stl_sketch():
    from penpal.render3d.loader import load_stl
    from penpal.render3d.sketch import sketch_render
    from penpal.render3d.camera import Camera
    from penpal.render3d.lighting import DirectionalLight

    mesh = load_stl("examples/assets/perseus.stl", max_faces=3000)
    cam = Camera.orbit(distance=200, elevation=20, azimuth=45)
    light = DirectionalLight(direction=(1, 1, -1))
    d = sketch_render(mesh, cam, [light], width=10, height=8)
    save_drawing_png(d, "27_stl_sketch")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

RENDERS = [
    ("Basics", render_basics),
    ("Attractors", render_attractors),
    ("Flow Fields", render_flow_fields),
    ("Noise Grid", render_noise_grid),
    ("Polar Noise Grid", render_polar_noise_grid),
    ("Fractals", render_fractals),
    ("Envelopes", render_envelopes),
    ("Contours", render_contours),
    ("Spline Waves", render_spline_waves),
    ("Mandala", render_mandala),
    ("Moire", render_moire),
    ("Cloth Drape", render_cloth),
    ("Polar Ribbons", render_polar_ribbons),
    ("Metaballs", render_metaballs),
    ("Wallpaper", render_wallpaper),
    ("Droste", render_droste),
    ("Voronoi Hatched", render_voronoi_hatched),
    ("Shading Fills", render_shading),
    ("Barrel Distortion", render_barrel),
    ("Lissajous", render_curves),
    ("Braid", render_braid),
    ("Perspective Drape", render_perspective),
    ("Halftone", render_halftone),
    ("Portrait Warp", render_portrait),
    ("Death Textures", render_death_textures),
    ("Dithering", render_dithering),
    ("STL Sketch", render_stl_sketch),
]


def main():
    print(f"Rendering {len(RENDERS)} gallery images to {GALLERY_DIR}/\n")
    for name, func in RENDERS:
        print(f"[{name}]")
        try:
            func()
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
        print()
    print("Done!")


if __name__ == "__main__":
    main()

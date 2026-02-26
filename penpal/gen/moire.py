"""Moire pattern generators.

Techniques for creating visual interference patterns. All generators return Paths.

Three families of moire:
1. **Noise-projected** — regular patterns (grids, circles) displaced by noise and
   perspective-divided to create oil-slick / metallic interference effects.
2. **Overlapping** — classic 2D moire from superimposed rotated/offset patterns.
3. **Surface contour** — contour lines of nearly-identical surfaces that interfere.

Ported from plotterart/pieces/2d_moires/ and plotterart/pieces/moire/.
"""

from __future__ import annotations

from typing import List, Optional, Tuple, Union

import numpy as np

from penpal.core.paths import Paths


# ---------------------------------------------------------------------------
# Noise helpers (uses opensimplex, same as core/noise.py)
# ---------------------------------------------------------------------------

def _make_noise(seed: int = None):
    """Create an OpenSimplex instance."""
    from opensimplex import OpenSimplex
    rng = np.random.default_rng(seed)
    return OpenSimplex(seed=int(rng.integers(0, 2**31)))


def _eval_noise_1d(noise_fn, x: np.ndarray, y: np.ndarray,
                   scale: float, octaves: int, persistence: float,
                   lacunarity: float, offset: Tuple[float, float] = (0., 0.)):
    """Evaluate layered simplex noise along parallel arrays x, y.

    Returns 1D array of noise values normalized to ~[-1, 1] (same length as x).
    Normalization ensures output is independent of octave/persistence settings,
    matching the behavior of noise.pnoise2() from the original code.
    """
    out = np.zeros_like(x, dtype=float)
    amp = 1.0
    freq = 1.0
    max_amp = 0.0
    for _ in range(octaves):
        for i in range(len(x)):
            out[i] += amp * noise_fn.noise2(
                scale * freq * x[i] + offset[0],
                scale * freq * y[i] + offset[1],
            )
        max_amp += amp
        amp *= persistence
        freq *= lacunarity
    return out / max_amp


def _eval_noise_grid(noise_fn, xx: np.ndarray, yy: np.ndarray,
                     scale: float, octaves: int, persistence: float,
                     lacunarity: float, offset: Tuple[float, float] = (0., 0.)):
    """Evaluate layered simplex noise on a 2D meshgrid.

    Returns 2D array same shape as xx, normalized to ~[-1, 1].
    """
    out = np.zeros_like(xx, dtype=float)
    amp = 1.0
    freq = 1.0
    max_amp = 0.0
    for _ in range(octaves):
        for i in range(xx.shape[0]):
            for j in range(xx.shape[1]):
                out[i, j] += amp * noise_fn.noise2(
                    scale * freq * xx[i, j] + offset[0],
                    scale * freq * yy[i, j] + offset[1],
                )
        max_amp += amp
        amp *= persistence
        freq *= lacunarity
    return out / max_amp


# ---------------------------------------------------------------------------
# 1. Noise-projected moire (oil slick / metallic)
# ---------------------------------------------------------------------------

def oil_slick(
    n_rings: int = 300,
    n_points: int = 200,
    max_radius: float = 15.0,
    noise_layers: Optional[List[dict]] = None,
    scale: float = 0.25,
    noise_offset: Tuple[float, float] = (0., 0.),
    z_base: float = 2.0,
    clip_radius: Optional[float] = None,
    simplify_tolerance: float = 1e-3,
    seed: int = None,
) -> Union[Paths, List[Paths]]:
    """Generate oil-slick moire from concentric circles projected through noise.

    Creates concentric rings in polar coordinates, displaces each point's
    "depth" with Perlin noise, then perspective-divides (x/z, y/z) to create
    organic interference patterns.

    Parameters
    ----------
    n_rings : int
        Number of concentric circles per layer.
    n_points : int
        Points per circle (angular resolution).
    max_radius : float
        Outer radius of the ring set.
    noise_layers : list of dict, optional
        Each dict defines a noise layer with keys:
        - octaves (int, default 2)
        - persistence (float)
        - lacunarity (float)
        If None, uses two default layers that produce nice interference.
    scale : float
        Spatial scale for noise evaluation.
    noise_offset : tuple
        (x, y) offset into noise space.
    z_base : float
        Base z value added to noise (must be > max noise amplitude to avoid
        division by zero). Default 2.0.
    clip_radius : float, optional
        If set, clips output to a circle of this radius centered at origin.
    simplify_tolerance : float
        Polyline simplification tolerance (Shapely).
    seed : int, optional
        Random seed for noise.

    Returns
    -------
    List[Paths]
        One Paths per noise layer. When overlaid, the different noise
        parameters cause the rings to interfere, creating the oil-slick effect.
        Use different pen colors per layer for multi-color output.
    """
    if noise_layers is None:
        noise_layers = [
            {"octaves": 2, "persistence": 0.1, "lacunarity": 3},
            {"octaves": 2, "persistence": 0.14, "lacunarity": 4},
        ]

    noise_fn = _make_noise(seed)
    theta = np.linspace(0, 2 * np.pi, n_points, endpoint=False)
    radii = np.linspace(max_radius / n_rings, max_radius, n_rings)

    result_layers = []

    for lparams in noise_layers:
        oct_ = lparams.get("octaves", 2)
        pers_ = lparams.get("persistence", 0.1)
        lac_ = lparams.get("lacunarity", 3)

        all_lines = []
        for r in radii:
            x = r * np.cos(theta)
            y = r * np.sin(theta)

            z = _eval_noise_1d(noise_fn, x, y, scale, oct_, pers_, lac_,
                               offset=noise_offset) + z_base

            proj_x = x / z
            proj_y = y / z

            pts = np.column_stack([proj_x, proj_y])
            # Close the ring
            pts = np.vstack([pts, pts[0:1]])

            if clip_radius is not None:
                # Distance-based clipping: keep points within radius
                dist = np.hypot(pts[:, 0], pts[:, 1])
                if np.all(dist > clip_radius):
                    continue

            all_lines.append(pts)

        if clip_radius is not None:
            from penpal.core.geo import clip
            clip_circle_pts = _circle_polygon(clip_radius, 128)
            all_lines = clip(all_lines, clip_circle_pts)

        result_layers.append(Paths(all_lines))

    return result_layers


def metallic_grid(
    n_lines: int = 200,
    n_points: int = 400,
    extent: float = 15.0,
    noise_layers: Optional[List[dict]] = None,
    scale: float = 0.25,
    noise_offset: Tuple[float, float] = (0., 0.),
    z_base: float = 2.0,
    directions: str = "both",
    simplify_tolerance: float = 1e-4,
    seed: int = None,
) -> Union[Paths, List[Paths]]:
    """Generate metallic moire from straight grid lines projected through noise.

    Same perspective-division technique as oil_slick, but with horizontal and
    vertical grid lines instead of concentric circles.

    Parameters
    ----------
    n_lines : int
        Number of lines in each direction.
    n_points : int
        Points per line (spatial resolution along each line).
    extent : float
        Half-width of the grid (lines span -extent to +extent).
    noise_layers : list of dict, optional
        Noise parameters per layer (same format as oil_slick).
    scale : float
        Spatial scale for noise.
    noise_offset : tuple
        Offset into noise space.
    z_base : float
        Base z value.
    directions : str
        "both" for horizontal + vertical, "h" for horizontal only,
        "v" for vertical only.
    simplify_tolerance : float
        Polyline simplification tolerance.
    seed : int, optional
        Random seed.

    Returns
    -------
    List[Paths]
        One Paths per noise layer.
    """
    if noise_layers is None:
        noise_layers = [
            {"octaves": 2, "persistence": 2.2, "lacunarity": 0.35},
            {"octaves": 2, "persistence": 2.86, "lacunarity": 0.35},
            {"octaves": 2, "persistence": 3.86, "lacunarity": 0.35},
        ]

    noise_fn = _make_noise(seed)
    line_positions = np.linspace(-extent, extent, n_lines)
    t = np.linspace(-extent, extent, n_points)

    result_layers = []

    for lparams in noise_layers:
        oct_ = lparams.get("octaves", 2)
        pers_ = lparams.get("persistence", 2.0)
        lac_ = lparams.get("lacunarity", 0.35)

        all_lines = []

        if directions in ("both", "v"):
            for xo in line_positions:
                x = np.full_like(t, xo)
                y = t
                z = _eval_noise_1d(noise_fn, x, y, scale, oct_, pers_, lac_,
                                   offset=noise_offset) + z_base
                pts = np.column_stack([x / z, y / z])
                all_lines.append(pts)

        if directions in ("both", "h"):
            for yo in line_positions:
                x = t
                y = np.full_like(t, yo)
                z = _eval_noise_1d(noise_fn, x, y, scale, oct_, pers_, lac_,
                                   offset=noise_offset) + z_base
                pts = np.column_stack([x / z, y / z])
                all_lines.append(pts)

        result_layers.append(Paths(all_lines))

    return result_layers


# ---------------------------------------------------------------------------
# 2. Classic 2D overlapping moire
# ---------------------------------------------------------------------------

def rotated_grids(
    n_lines: int = 80,
    extent: float = 10.0,
    angles: Optional[List[float]] = None,
    spacing: Optional[float] = None,
) -> List[Paths]:
    """Generate overlapping rotated line grids (classic moire).

    Parameters
    ----------
    n_lines : int
        Number of parallel lines per grid.
    extent : float
        Half-width — lines span from -extent to +extent.
    angles : list of float, optional
        Rotation angles in degrees for each grid layer.
        Default: [0, 3] — a slight angle difference creates strong moire.
    spacing : float, optional
        If set, overrides n_lines to use this fixed line spacing.

    Returns
    -------
    List[Paths]
        One Paths per angle.
    """
    if angles is None:
        angles = [0, 3]

    if spacing is not None:
        n_lines = int(2 * extent / spacing)

    positions = np.linspace(-extent, extent, n_lines)
    layers = []

    for angle in angles:
        lines = []
        for pos in positions:
            pts = np.array([
                [pos, -extent],
                [pos, extent],
            ])
            lines.append(pts)
        p = Paths(lines)
        if angle != 0:
            p = p.rotate(angle)
        layers.append(p)

    return layers


def concentric_circles(
    n_rings: int = 60,
    max_radius: float = 10.0,
    centers: Optional[List[Tuple[float, float]]] = None,
    n_points: int = 200,
) -> List[Paths]:
    """Generate overlapping sets of concentric circles.

    Slight offset between centers creates classic circular moire.

    Parameters
    ----------
    n_rings : int
        Rings per set.
    max_radius : float
        Outer radius.
    centers : list of (x, y), optional
        Center for each set. Default: [(0, 0), (0.5, 0)] — slight offset.
    n_points : int
        Points per circle.

    Returns
    -------
    List[Paths]
        One Paths per center.
    """
    if centers is None:
        centers = [(0, 0), (0.5, 0)]

    theta = np.linspace(0, 2 * np.pi, n_points + 1)
    radii = np.linspace(max_radius / n_rings, max_radius, n_rings)
    layers = []

    for cx, cy in centers:
        lines = []
        for r in radii:
            pts = np.column_stack([cx + r * np.cos(theta), cy + r * np.sin(theta)])
            lines.append(pts)
        layers.append(Paths(lines))

    return layers


def concentric_shapes(
    shape: np.ndarray,
    n_copies: int = 100,
    max_scale: float = 3.0,
    min_scale: float = 0.01,
    offsets: Optional[List[Tuple[float, float, float]]] = None,
    n_layers: int = 2,
) -> List[Paths]:
    """Generate moire from concentric scaled copies of an arbitrary closed curve.

    This is the spline moire technique — take a shape (polygon, spline curve),
    create many scaled copies radiating outward, then overlay multiple sets with
    slight rotation/translation offsets.

    Parameters
    ----------
    shape : np.ndarray
        Base shape as (N, 2) array of points (should be closed or will be closed).
    n_copies : int
        Number of concentric copies per layer.
    max_scale : float
        Scale of outermost copy.
    min_scale : float
        Scale of innermost copy.
    offsets : list of (dx, dy, angle_deg), optional
        Translation and rotation offset per layer. Default generates random
        small offsets.
    n_layers : int
        Number of overlapping layers (ignored if offsets is provided).

    Returns
    -------
    List[Paths]
        One Paths per layer.
    """
    # Ensure closed
    if not np.allclose(shape[0], shape[-1]):
        shape = np.vstack([shape, shape[0:1]])

    # Center the shape
    centroid = shape[:-1].mean(axis=0)
    centered = shape - centroid

    scales = np.linspace(min_scale, max_scale, n_copies)

    if offsets is None:
        rng = np.random.default_rng()
        offsets = []
        for _ in range(n_layers):
            dx = rng.uniform(-0.5, 0.5)
            dy = rng.uniform(-0.5, 0.5)
            angle = rng.uniform(-15, 15)
            offsets.append((dx, dy, angle))

    layers = []
    for dx, dy, angle in offsets:
        lines = []
        angle_rad = np.radians(angle)
        cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)
        rot = np.array([[cos_a, -sin_a], [sin_a, cos_a]])

        for s in scales:
            pts = centered * s
            pts = pts @ rot.T
            pts = pts + np.array([dx, dy])
            lines.append(pts)

        layers.append(Paths(lines))

    return layers


# ---------------------------------------------------------------------------
# 3. Surface contour moire
# ---------------------------------------------------------------------------

def surface_contour_moire(
    width: float = 11.0,
    height: float = 14.0,
    n_bumps: int = 20,
    n_contours: int = 100,
    perturbation: float = 0.01,
    n_surfaces: int = 2,
    resolution: int = 300,
    levels_mode: str = "percentile",
    seed: int = None,
) -> List[Paths]:
    """Generate moire from contour lines of nearly-identical surfaces.

    Creates a bumpy surface (sum of Gaussians), then extracts contour lines.
    A second surface with slight noise perturbation produces contours that
    mostly overlap but diverge in places, creating moire interference.

    Parameters
    ----------
    width, height : float
        Dimensions of the surface.
    n_bumps : int
        Number of Gaussian bumps.
    n_contours : int
        Number of contour levels to extract.
    perturbation : float
        Scale of noise added to create the second surface. Small values
        (0.001-0.1) create tight moire; larger values create looser patterns.
    n_surfaces : int
        Number of surface variants (each gets a slight perturbation).
    resolution : int
        Grid resolution for surface evaluation.
    levels_mode : str
        "percentile" — levels at equal percentiles of the surface (uniform
        visual density). "linear" — evenly spaced in value (denser near bumps).
    seed : int, optional
        Random seed.

    Returns
    -------
    List[Paths]
        One Paths per surface variant.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    rng = np.random.default_rng(seed)

    x = np.linspace(0, width, resolution)
    y = np.linspace(0, height, resolution)
    xx, yy = np.meshgrid(x, y)

    # Build base surface from sum of Gaussians
    z_base = np.zeros_like(xx)
    for _ in range(n_bumps):
        mu_x = rng.uniform(0, width)
        mu_y = rng.uniform(0, height)
        sigma = rng.uniform(0.5, 2.0)
        amplitude = rng.uniform(1, 5)
        dist_sq = (xx - mu_x) ** 2 + (yy - mu_y) ** 2
        z_base += amplitude * np.exp(-0.5 * dist_sq / sigma ** 2)

    # Build perturbation surfaces
    noise_surfaces = []
    for _ in range(n_surfaces):
        z_noise = np.zeros_like(xx)
        for _ in range(n_bumps):
            mu_x = rng.uniform(0, width)
            mu_y = rng.uniform(0, height)
            sigma = rng.uniform(0.5, 2.0)
            dist_sq = (xx - mu_x) ** 2 + (yy - mu_y) ** 2
            z_noise += np.exp(-0.5 * dist_sq / sigma ** 2)
        noise_surfaces.append(z_noise)

    # Extract contours for each surface variant
    layers = []
    for i in range(n_surfaces):
        if i == 0:
            surface = z_base
        else:
            surface = z_base + perturbation * noise_surfaces[i]

        if levels_mode == "percentile":
            levels = np.percentile(surface, np.linspace(0, 100, n_contours))
            # Remove duplicates
            levels = np.unique(levels)
        else:
            levels = np.linspace(surface.min(), surface.max(), n_contours)

        # Use matplotlib contour extraction
        fig, ax = plt.subplots()
        cs = ax.contour(x, y, surface, levels=levels)

        all_lines = []
        for collection in cs.allsegs:
            for seg in collection:
                if len(seg) > 1:
                    all_lines.append(np.array(seg))

        plt.close(fig)
        layers.append(Paths(all_lines))

    return layers


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _circle_polygon(radius: float, n_points: int = 128) -> np.ndarray:
    """Create a circle as a polygon (N, 2) array for clipping."""
    theta = np.linspace(0, 2 * np.pi, n_points + 1)
    return np.column_stack([radius * np.cos(theta), radius * np.sin(theta)])


def combine_layers(layers: List[Paths]) -> Paths:
    """Combine multiple moire layers into a single Paths for preview."""
    all_lines = []
    for p in layers:
        all_lines.extend(p.lines)
    return Paths(all_lines)

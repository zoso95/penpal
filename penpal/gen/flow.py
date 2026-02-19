"""Flow fields — trace streamlines through vector fields.

Composable design: define a field, choose seed points, trace.

    from penpal.gen import flow

    field = flow.simplex_field(frequency=0.8, seed=42)
    seeds = flow.seeds_line(0, 5, 8, 5, n=80)
    paths = flow.trace(field, seeds, steps=500, step_size=0.03, momentum=0.95)

Custom fields are just functions (x, y) -> angle_in_radians:

    paths = flow.trace(lambda x, y: x * 0.5 + y * 0.3, seeds, steps=200)
"""

from __future__ import annotations

from typing import Callable, Tuple, Optional, Sequence

import numpy as np

from penpal.core.paths import Paths


# A field function maps (x, y) -> angle in radians
FieldFunc = Callable[[float, float], float]


# ---------------------------------------------------------------------------
# Field functions — each returns a FieldFunc
# ---------------------------------------------------------------------------

def simplex_field(frequency: float = 1.0, scale: float = 1.0,
                  seed: int = None) -> FieldFunc:
    """Simplex noise field.

    angle = noise(x * freq, y * freq) * scale * 2pi

    Parameters
    ----------
    frequency : float
        Spatial frequency — higher = field changes faster.
    scale : float
        Angular scale — 1.0 gives full 2pi range, 0.5 gives pi range.
    seed : int, optional
        For reproducibility.
    """
    from opensimplex import OpenSimplex
    rng = np.random.default_rng(seed)
    noise = OpenSimplex(seed=int(rng.integers(0, 2**31)))

    def _field(x, y):
        return noise.noise2(x * frequency, y * frequency) * scale * 2 * np.pi
    return _field


def fractal_field(frequency: float = 1.0, scale: float = 1.0,
                  octaves: int = 4, persistence: float = 0.5,
                  lacunarity: float = 2.0, seed: int = None) -> FieldFunc:
    """Fractal (fBm) noise field — multiple octaves for richer detail.

    Parameters
    ----------
    frequency : float
        Base frequency.
    scale : float
        Angular scale (1.0 = full 2pi range).
    octaves : int
        Number of noise layers.
    persistence : float
        Amplitude decay per octave (0-1).
    lacunarity : float
        Frequency multiplier per octave.
    seed : int, optional
        For reproducibility.
    """
    from opensimplex import OpenSimplex
    rng = np.random.default_rng(seed)
    noise = OpenSimplex(seed=int(rng.integers(0, 2**31)))

    def _field(x, y):
        total = 0.0
        amp = 1.0
        freq = frequency
        total_amp = 0.0
        for _ in range(octaves):
            total += noise.noise2(x * freq, y * freq) * amp
            total_amp += amp
            amp *= persistence
            freq *= lacunarity
        return (total / total_amp) * scale * 2 * np.pi
    return _field


def curl_field(frequency: float = 1.0, seed: int = None) -> FieldFunc:
    """Curl noise field — divergence-free, creates swirling flow patterns.

    Streamlines traced through a curl field never converge or diverge,
    creating smooth, non-crossing flows.
    """
    from opensimplex import OpenSimplex
    rng = np.random.default_rng(seed)
    noise = OpenSimplex(seed=int(rng.integers(0, 2**31)))

    eps = 1e-4

    def _field(x, y):
        # Curl of scalar potential: direction is perpendicular to gradient
        n_dx = noise.noise2((x + eps) * frequency, y * frequency)
        n_mx = noise.noise2((x - eps) * frequency, y * frequency)
        n_dy = noise.noise2(x * frequency, (y + eps) * frequency)
        n_my = noise.noise2(x * frequency, (y - eps) * frequency)
        dpsi_dx = (n_dx - n_mx) / (2 * eps)
        dpsi_dy = (n_dy - n_my) / (2 * eps)
        # Curl direction: (dpsi_dy, -dpsi_dx)
        return np.arctan2(-dpsi_dx, dpsi_dy)
    return _field


def radial_field(center: Tuple[float, float] = (0, 0),
                 outward: bool = True) -> FieldFunc:
    """Radial field — vectors point away from (or toward) center."""
    cx, cy = center

    def _field(x, y):
        angle = np.arctan2(y - cy, x - cx)
        return angle if outward else angle + np.pi
    return _field


def spiral_field(center: Tuple[float, float] = (0, 0),
                 tightness: float = 0.3) -> FieldFunc:
    """Spiral field — combination of tangential + radial.

    tightness controls how quickly the spiral expands (0 = pure circles,
    1 = 45 degree spiral).
    """
    cx, cy = center

    def _field(x, y):
        # Tangential angle (perpendicular to radial)
        angle = np.arctan2(y - cy, x - cx) + np.pi / 2
        # Add radial component
        return angle + np.arctan(tightness)
    return _field


def constant_field(angle: float = 0.0) -> FieldFunc:
    """Constant direction field (all streamlines go the same direction).

    angle in radians. 0 = right, pi/2 = up.
    """
    def _field(x, y):
        return angle
    return _field


def domain_warp_field(inner: FieldFunc, warp_amplitude: float = 1.0,
                      warp_frequency: float = 0.5,
                      seed: int = None) -> FieldFunc:
    """Domain-warped field — feed noise into coordinates of another field.

    Creates alien, turbulent-looking flow patterns.
    """
    from opensimplex import OpenSimplex
    rng = np.random.default_rng(seed)
    noise = OpenSimplex(seed=int(rng.integers(0, 2**31)))

    def _field(x, y):
        wx = noise.noise2(x * warp_frequency, y * warp_frequency) * warp_amplitude
        wy = noise.noise2(x * warp_frequency + 50, y * warp_frequency + 50) * warp_amplitude
        return inner(x + wx, y + wy)
    return _field


def compose_fields(*fields: FieldFunc,
                   weights: Sequence[float] = None) -> FieldFunc:
    """Blend multiple fields by weighted circular mean of angles."""
    if weights is None:
        weights = [1.0] * len(fields)
    total_w = sum(weights)

    def _field(x, y):
        # Circular mean: average the unit vectors, then get angle
        sx = sum(w * np.cos(f(x, y)) for f, w in zip(fields, weights))
        sy = sum(w * np.sin(f(x, y)) for f, w in zip(fields, weights))
        return np.arctan2(sy / total_w, sx / total_w)
    return _field


# ---------------------------------------------------------------------------
# Seed generators — each returns an (N, 2) numpy array
# ---------------------------------------------------------------------------

def seeds_line(x0: float, y0: float, x1: float, y1: float,
               n: int = 50) -> np.ndarray:
    """Evenly spaced points along a line segment."""
    return np.column_stack([
        np.linspace(x0, x1, n),
        np.linspace(y0, y1, n),
    ])


def seeds_grid(x0: float, y0: float, x1: float, y1: float,
               nx: int = 20, ny: int = 20) -> np.ndarray:
    """Regular grid of seed points."""
    xs = np.linspace(x0, x1, nx)
    ys = np.linspace(y0, y1, ny)
    xg, yg = np.meshgrid(xs, ys)
    return np.column_stack([xg.ravel(), yg.ravel()])


def seeds_circle(cx: float, cy: float, r: float,
                 n: int = 50) -> np.ndarray:
    """Points evenly spaced around a circle."""
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.column_stack([cx + r * np.cos(angles), cy + r * np.sin(angles)])


def seeds_ring(cx: float, cy: float, inner_r: float, outer_r: float,
               n_rings: int = 10, n_per_ring: int = 50) -> np.ndarray:
    """Concentric rings of seed points (good for radial flow fields)."""
    seeds = []
    for r in np.linspace(inner_r, outer_r, n_rings):
        if r == 0:
            seeds.append(np.array([[cx, cy]]))
        else:
            seeds.append(seeds_circle(cx, cy, r, n_per_ring))
    return np.vstack(seeds)


def seeds_random(x0: float, y0: float, x1: float, y1: float,
                 n: int = 200, seed: int = None) -> np.ndarray:
    """Uniformly random seed points."""
    rng = np.random.default_rng(seed)
    return np.column_stack([
        rng.uniform(x0, x1, n),
        rng.uniform(y0, y1, n),
    ])


def seeds_poisson(x0: float, y0: float, x1: float, y1: float,
                  min_dist: float = 0.5, seed: int = None) -> np.ndarray:
    """Poisson disk distributed seeds (even blue-noise spacing)."""
    from penpal.sampling.poisson import poisson_disk
    return poisson_disk(x1 - x0, y1 - y0, min_dist=min_dist,
                        x0=x0, y0=y0, seed=seed)


# ---------------------------------------------------------------------------
# Tracer — the core function
# ---------------------------------------------------------------------------

def trace(field: FieldFunc, seeds: np.ndarray,
          steps: int = 500, step_size: float = 0.05,
          momentum: float = 0.0,
          bounds: Tuple[float, float, float, float] = None,
          min_length: int = 2) -> Paths:
    """Trace streamlines through a field from seed points.

    Parameters
    ----------
    field : callable
        (x, y) -> angle in radians.
    seeds : ndarray (N, 2)
        Starting positions for streamlines.
    steps : int
        Maximum steps per streamline.
    step_size : float
        Distance per step (in drawing units).
    momentum : float (0 to <1)
        Velocity smoothing. 0 = pure Euler (responsive to local field),
        0.95 = high inertia (smooth sweeping curves, ribbon-like).
        This is the key parameter for beautiful flow field art.
    bounds : (x0, y0, x1, y1), optional
        Stop a streamline when it exits bounds.
    min_length : int
        Discard streamlines shorter than this many points.

    Returns
    -------
    Paths
    """
    seeds = np.asarray(seeds)
    if seeds.ndim == 1:
        seeds = seeds.reshape(1, 2)

    lines = []
    for i in range(len(seeds)):
        pts = np.zeros((steps, 2), dtype=np.float64)
        pts[0] = seeds[i]
        vx, vy = 0.0, 0.0

        n_pts = steps
        for j in range(1, steps):
            x, y = pts[j - 1]
            angle = field(x, y)

            # Target velocity from field
            tvx = np.cos(angle) * step_size
            tvy = np.sin(angle) * step_size

            # Apply momentum (exponential moving average on velocity)
            if momentum > 0 and j > 1:
                vx = momentum * vx + (1 - momentum) * tvx
                vy = momentum * vy + (1 - momentum) * tvy
            else:
                vx, vy = tvx, tvy

            pts[j] = [x + vx, y + vy]

            # Bounds check
            if bounds is not None:
                bx0, by0, bx1, by1 = bounds
                if pts[j, 0] < bx0 or pts[j, 0] > bx1 or pts[j, 1] < by0 or pts[j, 1] > by1:
                    n_pts = j + 1
                    break

        line = pts[:n_pts]
        if len(line) >= min_length:
            lines.append(line)

    return Paths(lines) if lines else Paths()


def trace_bidirectional(field: FieldFunc, seeds: np.ndarray,
                        steps: int = 500, step_size: float = 0.05,
                        momentum: float = 0.0,
                        bounds: Tuple[float, float, float, float] = None,
                        min_length: int = 2) -> Paths:
    """Trace streamlines in both directions from each seed point.

    Same as trace() but also traces backwards (reversed field direction),
    then joins the two halves. This produces longer, more natural-looking
    streamlines that pass through the seed rather than starting at it.
    """
    seeds = np.asarray(seeds)
    if seeds.ndim == 1:
        seeds = seeds.reshape(1, 2)

    # Reversed field
    def rev_field(x, y):
        return field(x, y) + np.pi

    fwd = trace(field, seeds, steps=steps, step_size=step_size,
                momentum=momentum, bounds=bounds, min_length=1)
    bwd = trace(rev_field, seeds, steps=steps, step_size=step_size,
                momentum=momentum, bounds=bounds, min_length=1)

    lines = []
    for i in range(len(seeds)):
        fwd_line = fwd.lines[i] if i < len(fwd.lines) else None
        bwd_line = bwd.lines[i] if i < len(bwd.lines) else None

        if fwd_line is not None and bwd_line is not None and len(bwd_line) > 1:
            # Reverse backward trace and prepend (skip duplicate seed point)
            combined = np.vstack([bwd_line[::-1][:-1], fwd_line])
            lines.append(combined)
        elif fwd_line is not None:
            lines.append(fwd_line)
        elif bwd_line is not None:
            lines.append(bwd_line[::-1])

    lines = [l for l in lines if len(l) >= min_length]
    return Paths(lines) if lines else Paths()


def show_field(field: FieldFunc, x0: float, y0: float, x1: float, y1: float,
               nx: int = 20, ny: int = 20,
               length: float = None) -> Paths:
    """Visualize a field as short direction indicators at grid points.

    Draws a small line segment at each grid point showing the field direction.
    Useful for understanding and debugging fields before tracing.

    Parameters
    ----------
    field : callable
        (x, y) -> angle in radians.
    x0, y0, x1, y1 : float
        Bounding box for the visualization grid.
    nx, ny : int
        Number of sample points along each axis.
    length : float, optional
        Length of each indicator line. Defaults to ~60% of grid spacing.

    Returns
    -------
    Paths
    """
    xs = np.linspace(x0, x1, nx)
    ys = np.linspace(y0, y1, ny)

    if length is None:
        dx = (x1 - x0) / max(nx - 1, 1)
        dy = (y1 - y0) / max(ny - 1, 1)
        length = min(dx, dy) * 0.6

    lines = []
    half = length / 2
    for x in xs:
        for y in ys:
            angle = field(x, y)
            cx_off = np.cos(angle) * half
            cy_off = np.sin(angle) * half
            lines.append(np.array([
                [x - cx_off, y - cy_off],
                [x + cx_off, y + cy_off],
            ]))
    return Paths(lines)

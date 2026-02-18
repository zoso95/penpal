"""Grid generators: regular grids, distorted grids, barrel distortion, noise warp.

All generators return Paths.
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline

from penpal.core.paths import Paths


def grid(
    x0: float = 0,
    y0: float = 0,
    x1: float = 8,
    y1: float = 10,
    spacing: float = 0.5,
) -> Paths:
    """Generate a regular rectangular grid of lines."""
    lines = []
    # Vertical lines
    for x in np.arange(x0, x1 + spacing * 0.01, spacing):
        lines.append(np.array([[x, y0], [x, y1]], dtype=np.float64))
    # Horizontal lines
    for y in np.arange(y0, y1 + spacing * 0.01, spacing):
        lines.append(np.array([[x0, y], [x1, y]], dtype=np.float64))
    return Paths(lines)


def distorted_grid(
    x0: float = 0,
    y0: float = 0,
    x1: float = 8,
    y1: float = 10,
    rows: int = 20,
    cols: int = 16,
    noise_scale: float = 0.1,
    seed: int = None,
) -> Paths:
    """Generate a grid with random vertex displacement."""
    rng = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, cols + 1)
    ys = np.linspace(y0, y1, rows + 1)
    xg, yg = np.meshgrid(xs, ys)

    # Add noise to interior points only
    noise_x = rng.normal(0, noise_scale, xg.shape)
    noise_y = rng.normal(0, noise_scale, yg.shape)
    noise_x[0, :] = noise_x[-1, :] = noise_x[:, 0] = noise_x[:, -1] = 0
    noise_y[0, :] = noise_y[-1, :] = noise_y[:, 0] = noise_y[:, -1] = 0
    xg += noise_x
    yg += noise_y

    lines = []
    # Horizontal lines
    for i in range(rows + 1):
        pts = np.column_stack([xg[i, :], yg[i, :]])
        lines.append(pts)
    # Vertical lines
    for j in range(cols + 1):
        pts = np.column_stack([xg[:, j], yg[:, j]])
        lines.append(pts)
    return Paths(lines)


def barrel_distortion(
    x0: float = 0,
    y0: float = 0,
    x1: float = 8,
    y1: float = 10,
    rows: int = 20,
    cols: int = 16,
    k: float = 0.3,
    points_per_line: int = 50,
) -> Paths:
    """Generate a grid with barrel/pincushion distortion.

    k > 0: barrel distortion
    k < 0: pincushion distortion
    """
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    max_r = np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2) / 2

    def distort(pts):
        dx = pts[:, 0] - cx
        dy = pts[:, 1] - cy
        r = np.sqrt(dx**2 + dy**2) / max_r
        scale = 1 + k * r**2
        return np.column_stack([cx + dx * scale, cy + dy * scale])

    lines = []
    xs = np.linspace(x0, x1, cols + 1)
    ys = np.linspace(y0, y1, rows + 1)

    # Horizontal lines (with intermediate points for curvature)
    for y in ys:
        x_pts = np.linspace(x0, x1, points_per_line)
        pts = np.column_stack([x_pts, np.full_like(x_pts, y)])
        lines.append(distort(pts))
    # Vertical lines
    for x in xs:
        y_pts = np.linspace(y0, y1, points_per_line)
        pts = np.column_stack([np.full_like(y_pts, x), y_pts])
        lines.append(distort(pts))
    return Paths(lines)


def noise_grid(
    x0: float = 0,
    y0: float = 0,
    x1: float = 8,
    y1: float = 10,
    rows: int = 60,
    cols: int = 48,
    amplitude: float = 0.3,
    frequency: float = 0.8,
    smooth: bool = True,
    points_per_line: int = 100,
    seed: int = None,
) -> Paths:
    """Generate a grid warped by simplex noise with optional spline smoothing.

    This produces the organic, cloth-like distortion effect.

    Parameters
    ----------
    amplitude : float
        Max displacement in drawing units.
    frequency : float
        Noise frequency (higher = more wrinkles).
    smooth : bool
        If True, fit cubic splines through displaced grid points
        for smooth curves (cloth-like). If False, straight segments.
    points_per_line : int
        Number of points per line when smooth=True.
    """
    from opensimplex import OpenSimplex

    rng = np.random.default_rng(seed)
    noise = OpenSimplex(seed=int(rng.integers(0, 2**31)))

    xs = np.linspace(x0, x1, cols + 1)
    ys = np.linspace(y0, y1, rows + 1)
    xg, yg = np.meshgrid(xs, ys)

    # Displace grid points with noise
    dx = np.zeros_like(xg)
    dy = np.zeros_like(yg)
    for i in range(xg.shape[0]):
        for j in range(xg.shape[1]):
            x, y = xg[i, j], yg[i, j]
            dx[i, j] = noise.noise2(x * frequency, y * frequency) * amplitude
            dy[i, j] = noise.noise2(x * frequency + 100, y * frequency + 100) * amplitude

    xg_d = xg + dx
    yg_d = yg + dy

    lines = []

    if smooth and cols >= 3:
        # Fit cubic splines through displaced grid points
        t_row = np.linspace(0, 1, cols + 1)
        t_fine = np.linspace(0, 1, points_per_line)
        t_col = np.linspace(0, 1, rows + 1)

        for i in range(rows + 1):
            cs_x = CubicSpline(t_row, xg_d[i, :])
            cs_y = CubicSpline(t_row, yg_d[i, :])
            pts = np.column_stack([cs_x(t_fine), cs_y(t_fine)])
            lines.append(pts)
        for j in range(cols + 1):
            cs_x = CubicSpline(t_col, xg_d[:, j])
            cs_y = CubicSpline(t_col, yg_d[:, j])
            pts = np.column_stack([cs_x(t_fine), cs_y(t_fine)])
            lines.append(pts)
    else:
        for i in range(rows + 1):
            pts = np.column_stack([xg_d[i, :], yg_d[i, :]])
            lines.append(pts)
        for j in range(cols + 1):
            pts = np.column_stack([xg_d[:, j], yg_d[:, j]])
            lines.append(pts)

    return Paths(lines)


def polar_noise_grid(
    center: tuple = (0, 0),
    inner_r: float = 0.5,
    outer_r: float = 4.0,
    n_rings: int = 40,
    n_spokes: int = 60,
    amplitude: float = 0.2,
    frequency: float = 1.0,
    twist: float = 0.0,
    smooth: bool = True,
    points_per_line: int = 100,
    seed: int = None,
) -> Paths:
    """Generate a polar grid warped by noise.

    Produces the turbine/radial distortion effect.

    Parameters
    ----------
    center : (x, y)
    inner_r, outer_r : float
        Radial extent.
    n_rings : int
        Number of concentric rings.
    n_spokes : int
        Number of radial spokes.
    amplitude : float
        Noise displacement amplitude.
    frequency : float
        Noise frequency.
    twist : float
        Additional angular twist proportional to radius (radians).
    """
    from opensimplex import OpenSimplex

    rng = np.random.default_rng(seed)
    noise = OpenSimplex(seed=int(rng.integers(0, 2**31)))
    cx, cy = center

    radii = np.linspace(inner_r, outer_r, n_rings + 1)
    angles = np.linspace(0, 2 * np.pi, n_spokes + 1)
    rg, ag = np.meshgrid(radii, angles)

    # Apply twist
    ag = ag + twist * (rg - inner_r) / (outer_r - inner_r)

    # Convert to cartesian and displace with noise
    xg = cx + rg * np.cos(ag)
    yg = cy + rg * np.sin(ag)

    dx = np.zeros_like(xg)
    dy = np.zeros_like(yg)
    for i in range(xg.shape[0]):
        for j in range(xg.shape[1]):
            x, y = xg[i, j], yg[i, j]
            dx[i, j] = noise.noise2(x * frequency, y * frequency) * amplitude
            dy[i, j] = noise.noise2(x * frequency + 100, y * frequency + 100) * amplitude

    xg_d = xg + dx
    yg_d = yg + dy

    lines = []

    if smooth:
        # Rings (closed curves) — wrap-around spline
        for j in range(n_rings + 1):
            ring_x = xg_d[:, j]
            ring_y = yg_d[:, j]
            # Close the ring by appending first points
            ring_x_c = np.concatenate([ring_x, ring_x[:1]])
            ring_y_c = np.concatenate([ring_y, ring_y[:1]])
            t = np.linspace(0, 1, len(ring_x_c))
            t_fine = np.linspace(0, 1, points_per_line + 1)
            try:
                cs_x = CubicSpline(t, ring_x_c, bc_type='periodic')
                cs_y = CubicSpline(t, ring_y_c, bc_type='periodic')
                pts = np.column_stack([cs_x(t_fine), cs_y(t_fine)])
                lines.append(pts)
            except Exception:
                pts = np.column_stack([ring_x_c, ring_y_c])
                lines.append(pts)

        # Spokes (radial lines)
        t_spoke = np.linspace(0, 1, n_rings + 1)
        t_fine = np.linspace(0, 1, points_per_line)
        for i in range(n_spokes):
            spoke_x = xg_d[i, :]
            spoke_y = yg_d[i, :]
            if len(spoke_x) >= 4:
                cs_x = CubicSpline(t_spoke, spoke_x)
                cs_y = CubicSpline(t_spoke, spoke_y)
                pts = np.column_stack([cs_x(t_fine), cs_y(t_fine)])
            else:
                pts = np.column_stack([spoke_x, spoke_y])
            lines.append(pts)
    else:
        # Rings
        for j in range(n_rings + 1):
            ring_x = np.concatenate([xg_d[:, j], xg_d[:1, j]])
            ring_y = np.concatenate([yg_d[:, j], yg_d[:1, j]])
            lines.append(np.column_stack([ring_x, ring_y]))
        # Spokes
        for i in range(n_spokes):
            lines.append(np.column_stack([xg_d[i, :], yg_d[i, :]]))

    return Paths(lines)

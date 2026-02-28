"""Dot/point-based polygon fills.

Creates small circle marks at sampled positions within polygons,
using various sampling strategies (regular grid, random, poisson disk).

All functions return Paths.
"""

from __future__ import annotations

import numpy as np
from shapely.geometry import Polygon as ShapelyPolygon, Point as ShapelyPoint

from penpal.core.paths import Paths


def stipple_polygon(
    polygon: np.ndarray,
    density: float = 5.0,
    dot_radius: float = 0.02,
    n_circle_points: int = 12,
    method: str = "poisson",
    seed: int | None = None,
) -> Paths:
    """Fill a polygon with stipple dots.

    Parameters
    ----------
    polygon : ndarray, shape (N, 2)
        Polygon vertices.
    density : float
        Approximate spacing between dots (lower = denser).
    dot_radius : float
        Radius of each dot circle.
    n_circle_points : int
        Number of points per dot circle.
    method : str
        Sampling method: 'poisson', 'random', 'grid', or 'jittered'.
    seed : int, optional
        Random seed.

    Returns
    -------
    Paths
        Small circles at sample positions.
    """
    rng = np.random.default_rng(seed)
    poly = ShapelyPolygon(polygon)
    minx, miny, maxx, maxy = poly.bounds

    if method == "grid":
        points = _sample_grid(minx, miny, maxx, maxy, density)
    elif method == "jittered":
        points = _sample_jittered(minx, miny, maxx, maxy, density, rng)
    elif method == "random":
        area = (maxx - minx) * (maxy - miny)
        n_pts = int(area / (density * density))
        points = np.column_stack([
            rng.uniform(minx, maxx, n_pts),
            rng.uniform(miny, maxy, n_pts),
        ])
    else:  # poisson
        points = _sample_poisson(minx, miny, maxx, maxy, density, rng)

    # Filter to polygon interior
    from shapely import contains_xy
    mask = contains_xy(poly, points[:, 0], points[:, 1])
    interior_pts = points[mask]

    # Generate dot circles
    return _dots_at_points(interior_pts, dot_radius, n_circle_points)


def stipple_rect(
    x0: float, y0: float, x1: float, y1: float,
    density: float = 5.0,
    dot_radius: float = 0.02,
    n_circle_points: int = 12,
    method: str = "poisson",
    seed: int | None = None,
) -> Paths:
    """Fill a rectangle with stipple dots.

    Parameters
    ----------
    x0, y0 : float
        Lower-left corner.
    x1, y1 : float
        Upper-right corner.
    density : float
        Spacing between dots.
    dot_radius : float
        Radius of each dot.
    n_circle_points : int
        Points per dot circle.
    method : str
        'poisson', 'random', 'grid', or 'jittered'.
    seed : int, optional
        Random seed.

    Returns
    -------
    Paths
        Small circles at sample positions.
    """
    polygon = np.array([
        [x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]
    ])
    return stipple_polygon(polygon, density, dot_radius, n_circle_points,
                           method, seed)


def dots_at(
    points: np.ndarray,
    radius: float = 0.02,
    n_points: int = 12,
) -> Paths:
    """Draw small circles at given points.

    Parameters
    ----------
    points : ndarray, shape (N, 2)
        Center positions.
    radius : float
        Circle radius.
    n_points : int
        Points per circle.

    Returns
    -------
    Paths
        Small circles.
    """
    return _dots_at_points(points, radius, n_points)


def _dots_at_points(centers, radius, n_points):
    """Generate small circles at center points."""
    theta = np.linspace(0, 2 * np.pi, n_points + 1)
    dx = radius * np.cos(theta)
    dy = radius * np.sin(theta)

    lines = []
    for cx, cy in centers:
        circle = np.column_stack([cx + dx, cy + dy])
        lines.append(circle)

    return Paths(lines)


def _sample_grid(minx, miny, maxx, maxy, spacing):
    """Regular grid sampling."""
    xs = np.arange(minx, maxx, spacing)
    ys = np.arange(miny, maxy, spacing)
    X, Y = np.meshgrid(xs, ys)
    return np.column_stack([X.ravel(), Y.ravel()])


def _sample_jittered(minx, miny, maxx, maxy, spacing, rng):
    """Jittered grid sampling."""
    pts = _sample_grid(minx, miny, maxx, maxy, spacing)
    jitter = rng.uniform(-spacing * 0.3, spacing * 0.3, pts.shape)
    return pts + jitter


def _sample_poisson(minx, miny, maxx, maxy, min_dist, rng, k=30):
    """Simple Poisson disk sampling via Bridson's algorithm."""
    cell_size = min_dist / np.sqrt(2)
    nx = int(np.ceil((maxx - minx) / cell_size))
    ny = int(np.ceil((maxy - miny) / cell_size))
    grid = -np.ones((nx, ny), dtype=int)

    samples = []

    # First point
    x0 = rng.uniform(minx, maxx)
    y0 = rng.uniform(miny, maxy)
    samples.append([x0, y0])
    gx = int((x0 - minx) / cell_size)
    gy = int((y0 - miny) / cell_size)
    grid[gx, gy] = 0
    active = [0]

    while active:
        idx = rng.integers(len(active))
        ref = samples[active[idx]]
        found = False

        for _ in range(k):
            angle = rng.uniform(0, 2 * np.pi)
            dist = rng.uniform(min_dist, 2 * min_dist)
            px = ref[0] + dist * np.cos(angle)
            py = ref[1] + dist * np.sin(angle)

            if px < minx or px >= maxx or py < miny or py >= maxy:
                continue

            gx = int((px - minx) / cell_size)
            gy = int((py - miny) / cell_size)

            if gx < 0 or gx >= nx or gy < 0 or gy >= ny:
                continue

            # Check neighbors
            ok = True
            for di in range(-2, 3):
                for dj in range(-2, 3):
                    ni, nj = gx + di, gy + dj
                    if 0 <= ni < nx and 0 <= nj < ny and grid[ni, nj] >= 0:
                        sx, sy = samples[grid[ni, nj]]
                        if (px - sx) ** 2 + (py - sy) ** 2 < min_dist ** 2:
                            ok = False
                            break
                    if not ok:
                        break

            if ok:
                samples.append([px, py])
                grid[gx, gy] = len(samples) - 1
                active.append(len(samples) - 1)
                found = True
                break

        if not found:
            active.pop(idx)

    return np.array(samples)

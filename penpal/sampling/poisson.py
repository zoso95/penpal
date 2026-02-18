"""Bridson's Poisson disk sampling — blue-noise point distribution.

Produces evenly-spaced random points with a minimum distance guarantee.
"""

from __future__ import annotations

import numpy as np


def poisson_disk(
    width: float,
    height: float,
    min_dist: float,
    k: int = 30,
    x0: float = 0,
    y0: float = 0,
    seed: int = None,
) -> np.ndarray:
    """Generate Poisson disk samples in a rectangle.

    Parameters
    ----------
    width, height : float
        Rectangle dimensions.
    min_dist : float
        Minimum distance between any two points.
    k : int
        Number of candidates per active point (higher = tighter packing).
    x0, y0 : float
        Origin offset of the rectangle.
    seed : int, optional
        Random seed.

    Returns
    -------
    np.ndarray, shape (N, 2)
        Point positions.
    """
    rng = np.random.default_rng(seed)

    # Cell grid for spatial lookup
    cell_size = min_dist / np.sqrt(2)
    cols = int(np.ceil(width / cell_size))
    rows = int(np.ceil(height / cell_size))
    grid = {}  # (col, row) -> point index

    points = []

    def _grid_coords(pt):
        return int((pt[0] - x0) / cell_size), int((pt[1] - y0) / cell_size)

    def _valid(pt):
        if pt[0] < x0 or pt[0] >= x0 + width or pt[1] < y0 or pt[1] >= y0 + height:
            return False
        gc, gr = _grid_coords(pt)
        # Check 5x5 neighborhood
        for dc in range(-2, 3):
            for dr in range(-2, 3):
                nc, nr = gc + dc, gr + dr
                if (nc, nr) in grid:
                    idx = grid[(nc, nr)]
                    dist = np.sqrt((pt[0] - points[idx][0]) ** 2 + (pt[1] - points[idx][1]) ** 2)
                    if dist < min_dist:
                        return False
        return True

    # Seed with first point
    first = np.array([x0 + rng.uniform(0, width), y0 + rng.uniform(0, height)])
    points.append(first)
    grid[_grid_coords(first)] = 0
    active = [0]

    while active:
        idx = rng.integers(0, len(active))
        ref = points[active[idx]]
        found = False
        for _ in range(k):
            angle = rng.uniform(0, 2 * np.pi)
            r = rng.uniform(min_dist, 2 * min_dist)
            candidate = ref + np.array([r * np.cos(angle), r * np.sin(angle)])
            if _valid(candidate):
                points.append(candidate)
                grid[_grid_coords(candidate)] = len(points) - 1
                active.append(len(points) - 1)
                found = True
                break
        if not found:
            active.pop(idx)

    return np.array(points, dtype=np.float64)


def poisson_disk_n(
    width: float,
    height: float,
    n: int,
    x0: float = 0,
    y0: float = 0,
    k: int = 30,
    seed: int = None,
) -> np.ndarray:
    """Generate approximately n Poisson disk samples by estimating min_dist.

    Parameters
    ----------
    n : int
        Target number of points.
    """
    area = width * height
    # Approximate: each point "owns" a circle of radius min_dist/2
    min_dist = np.sqrt(area / n) * 0.85
    return poisson_disk(width, height, min_dist, k=k, x0=x0, y0=y0, seed=seed)

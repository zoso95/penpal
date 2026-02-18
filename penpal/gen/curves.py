"""Curve generators: circle, spiral, polygon, rose, lissajous, hilbert.

All generators return Paths.
"""

from __future__ import annotations

import numpy as np

from penpal.core.paths import Paths


def circle(center=(0, 0), radius: float = 1.0, num_points: int = 100) -> Paths:
    """Generate a circle as a closed polyline."""
    cx, cy = center
    t = np.linspace(0, 2 * np.pi, num_points + 1)
    pts = np.column_stack([cx + radius * np.cos(t), cy + radius * np.sin(t)])
    return Paths([pts])


def polygon_regular(center=(0, 0), radius: float = 1.0, n_sides: int = 6) -> Paths:
    """Generate a regular polygon (closed)."""
    cx, cy = center
    angles = np.linspace(0, 2 * np.pi, n_sides + 1)
    pts = np.column_stack([cx + radius * np.cos(angles), cy + radius * np.sin(angles)])
    return Paths([pts])


def spiral(
    center=(0, 0),
    inner_r: float = 0.0,
    outer_r: float = 1.0,
    turns: float = 5,
    num_points: int = 500,
) -> Paths:
    """Generate an Archimedean spiral."""
    cx, cy = center
    t = np.linspace(0, turns * 2 * np.pi, num_points)
    r = np.linspace(inner_r, outer_r, num_points)
    pts = np.column_stack([cx + r * np.cos(t), cy + r * np.sin(t)])
    return Paths([pts])


def rose(
    center=(0, 0),
    radius: float = 1.0,
    k: float = 5,
    num_points: int = 500,
) -> Paths:
    """Generate a rose curve r = radius * cos(k * theta)."""
    cx, cy = center
    # For integer k: period is pi if k even, 2pi if k odd
    t = np.linspace(0, 2 * np.pi, num_points)
    r = radius * np.cos(k * t)
    pts = np.column_stack([cx + r * np.cos(t), cy + r * np.sin(t)])
    return Paths([pts])


def lissajous(
    center=(0, 0),
    a: float = 1.0,
    b: float = 1.0,
    freq_x: float = 3,
    freq_y: float = 2,
    phase: float = 0,
    num_points: int = 500,
) -> Paths:
    """Generate a Lissajous curve."""
    cx, cy = center
    t = np.linspace(0, 2 * np.pi, num_points)
    pts = np.column_stack([
        cx + a * np.sin(freq_x * t + phase),
        cy + b * np.sin(freq_y * t),
    ])
    return Paths([pts])


def hilbert(order: int = 4, size: float = 1.0, origin=(0, 0)) -> Paths:
    """Generate a Hilbert space-filling curve."""
    def _hilbert_d2xy(n, d):
        x = y = 0
        s = 1
        while s < n:
            rx = 1 if (d & 2) else 0
            ry = 1 if ((d & 1) ^ rx) else 0
            if ry == 0:
                if rx == 1:
                    x = s - 1 - x
                    y = s - 1 - y
                x, y = y, x
            x += s * rx
            y += s * ry
            d >>= 2
            s <<= 1
        return x, y

    n = 2**order
    total = n * n
    pts = np.zeros((total, 2), dtype=np.float64)
    for i in range(total):
        x, y = _hilbert_d2xy(n, i)
        pts[i] = [x, y]
    # Normalize to [0, size] and offset
    pts = pts / (n - 1) * size
    pts[:, 0] += origin[0]
    pts[:, 1] += origin[1]
    return Paths([pts])


def concentric_circles(
    center=(0, 0),
    n_rings: int = 10,
    max_r: float = 1.0,
    points_per_ring: int = 100,
) -> Paths:
    """Generate concentric circles."""
    lines = []
    for i in range(1, n_rings + 1):
        r = max_r * i / n_rings
        t = np.linspace(0, 2 * np.pi, points_per_ring + 1)
        cx, cy = center
        pts = np.column_stack([cx + r * np.cos(t), cy + r * np.sin(t)])
        lines.append(pts)
    return Paths(lines)

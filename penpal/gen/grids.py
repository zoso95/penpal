"""Grid generators: regular grids, distorted grids, barrel distortion.

All generators return Paths.
"""

from __future__ import annotations

import numpy as np

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

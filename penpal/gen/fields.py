"""Flow field and noise-based generators.

All generators return Paths.
"""

from __future__ import annotations

import numpy as np

from penpal.core.paths import Paths


def flow_field(
    width: float = 8,
    height: float = 10,
    num_lines: int = 200,
    steps: int = 50,
    step_size: float = 0.05,
    frequency: float = 1.0,
    seed: int = None,
) -> Paths:
    """Generate lines following a noise-based flow field."""
    from opensimplex import OpenSimplex

    rng = np.random.default_rng(seed)
    noise = OpenSimplex(seed=int(rng.integers(0, 2**31)))

    lines = []
    starts_x = rng.uniform(0, width, num_lines)
    starts_y = rng.uniform(0, height, num_lines)

    for i in range(num_lines):
        pts = np.zeros((steps, 2), dtype=np.float64)
        pts[0] = [starts_x[i], starts_y[i]]
        for j in range(1, steps):
            x, y = pts[j - 1]
            angle = noise.noise2(x * frequency, y * frequency) * 2 * np.pi
            pts[j] = [x + np.cos(angle) * step_size, y + np.sin(angle) * step_size]
            # Stop if out of bounds
            if pts[j, 0] < 0 or pts[j, 0] > width or pts[j, 1] < 0 or pts[j, 1] > height:
                pts = pts[: j + 1]
                break
        if len(pts) >= 2:
            lines.append(pts)
    return Paths(lines)


def noise_walk(
    start=(0, 0),
    steps: int = 500,
    step_size: float = 0.05,
    frequency: float = 1.0,
    seed: int = None,
) -> Paths:
    """Generate a single random walk guided by noise."""
    from opensimplex import OpenSimplex

    rng = np.random.default_rng(seed)
    noise = OpenSimplex(seed=int(rng.integers(0, 2**31)))

    pts = np.zeros((steps, 2), dtype=np.float64)
    pts[0] = start
    t_offset = rng.uniform(0, 1000)

    for i in range(1, steps):
        x, y = pts[i - 1]
        angle = noise.noise2(x * frequency + t_offset, y * frequency) * 2 * np.pi
        pts[i] = [x + np.cos(angle) * step_size, y + np.sin(angle) * step_size]
    return Paths([pts])

"""Iterated Function System (IFS) and flame fractal generators.

Port of axifun/eric_s thing.ipynb — chaos game with 11 variation functions,
plus classic IFS fractals (Barnsley fern, Sierpinski, etc).

All generators return Paths.
"""

from __future__ import annotations

import numpy as np

from penpal.core.paths import Paths


# ---------------------------------------------------------------------------
# Variation functions: (x, y) -> (x', y')
# From Scott Draves' flame algorithm
# ---------------------------------------------------------------------------

def _linear(x, y):
    return x, y


def _sinusoidal(x, y):
    return np.sin(x), np.sin(y)


def _spherical(x, y):
    r2 = x * x + y * y + 1e-10
    return x / r2, y / r2


def _swirl(x, y):
    r2 = x * x + y * y
    s, c = np.sin(r2), np.cos(r2)
    return x * s - y * c, x * c + y * s


def _horseshoe(x, y):
    r = np.sqrt(x * x + y * y) + 1e-10
    return (x - y) * (x + y) / r, 2 * x * y / r


def _polar(x, y):
    r = np.sqrt(x * x + y * y)
    theta = np.arctan2(y, x)
    return theta / np.pi, r - 1


def _handkerchief(x, y):
    r = np.sqrt(x * x + y * y)
    theta = np.arctan2(y, x)
    return r * np.sin(theta + r), r * np.cos(theta - r)


def _heart(x, y):
    r = np.sqrt(x * x + y * y)
    theta = np.arctan2(y, x)
    return r * np.sin(theta * r), -r * np.cos(theta * r)


def _disc(x, y):
    r = np.sqrt(x * x + y * y)
    theta = np.arctan2(y, x)
    return theta / np.pi * np.sin(np.pi * r), theta / np.pi * np.cos(np.pi * r)


def _spiral_var(x, y):
    r = np.sqrt(x * x + y * y) + 1e-10
    theta = np.arctan2(y, x)
    return (np.cos(theta) + np.sin(r)) / r, (np.sin(theta) - np.cos(r)) / r


def _hyperbolic(x, y):
    r = np.sqrt(x * x + y * y) + 1e-10
    theta = np.arctan2(y, x)
    return np.sin(theta) / r, r * np.cos(theta)


VARIATIONS = {
    "linear": _linear,
    "sinusoidal": _sinusoidal,
    "spherical": _spherical,
    "swirl": _swirl,
    "horseshoe": _horseshoe,
    "polar": _polar,
    "handkerchief": _handkerchief,
    "heart": _heart,
    "disc": _disc,
    "spiral": _spiral_var,
    "hyperbolic": _hyperbolic,
}


def flame(
    n_points: int = 50000,
    n_functions: int = 3,
    variations: list[str] | None = None,
    seed: int | None = None,
    skip: int = 20,
    bounds: float = 2.0,
) -> Paths:
    """Generate a flame fractal using the chaos game with variation functions.

    Creates random affine transforms combined with nonlinear variation
    functions and iterates the chaos game algorithm.

    Parameters
    ----------
    n_points : int
        Number of points to generate (after skipping warmup).
    n_functions : int
        Number of IFS functions to use.
    variations : list of str, optional
        Which variation functions to use. If None, picks randomly.
        Available: linear, sinusoidal, spherical, swirl, horseshoe,
        polar, handkerchief, heart, disc, spiral, hyperbolic.
    seed : int, optional
        Random seed for reproducibility.
    skip : int
        Warmup iterations to skip before recording points.
    bounds : float
        Points outside [-bounds, bounds] are discarded.

    Returns
    -------
    Paths
        Single polyline of the fractal trajectory.
    """
    rng = np.random.default_rng(seed)

    var_names = list(VARIATIONS.keys())
    if variations is None:
        variations = [rng.choice(var_names) for _ in range(n_functions)]

    # Generate random affine transforms: f(x,y) = (ax+by+c, dx+ey+f)
    affines = []
    for _ in range(n_functions):
        a, b, c = rng.uniform(-1, 1, 3)
        d, e, f = rng.uniform(-1, 1, 3)
        affines.append((a, b, c, d, e, f))

    var_funcs = [VARIATIONS[v] for v in variations]

    # Chaos game
    x, y = rng.uniform(-0.5, 0.5, 2)
    points = []
    total_iters = n_points + skip

    for i in range(total_iters):
        idx = rng.integers(n_functions)
        a, b, c, d, e, f = affines[idx]

        # Apply affine transform
        x_new = a * x + b * y + c
        y_new = d * x + e * y + f

        # Apply variation function
        x_new, y_new = var_funcs[idx](x_new, y_new)

        # Check bounds and NaN
        if np.isnan(x_new) or np.isnan(y_new):
            x, y = rng.uniform(-0.5, 0.5, 2)
            continue
        if abs(x_new) > bounds or abs(y_new) > bounds:
            x, y = x_new * 0.1, y_new * 0.1
            continue

        x, y = x_new, y_new

        if i >= skip:
            points.append([x, y])

    if len(points) < 2:
        return Paths()

    return Paths([np.array(points)])


def barnsley_fern(n_points: int = 50000, seed: int | None = None) -> Paths:
    """Generate Barnsley's fern fractal.

    Parameters
    ----------
    n_points : int
        Number of points to generate.
    seed : int, optional
        Random seed.

    Returns
    -------
    Paths
        Single polyline of the fern.
    """
    rng = np.random.default_rng(seed)

    # Barnsley fern IFS parameters
    # Each row: (a, b, c, d, e, f, probability)
    transforms = [
        (0.00, 0.00, 0.00, 0.00, 0.16, 0.00, 0.01),   # stem
        (0.85, 0.04, 0.00, -0.04, 0.85, 1.60, 0.85),   # main body
        (0.20, -0.26, 0.00, 0.23, 0.22, 1.60, 0.07),   # left leaf
        (-0.15, 0.28, 0.00, 0.26, 0.24, 0.44, 0.07),   # right leaf
    ]
    probs = np.array([t[6] for t in transforms])
    probs /= probs.sum()
    cum_probs = np.cumsum(probs)

    x, y = 0.0, 0.0
    points = np.empty((n_points, 2))

    for i in range(n_points):
        points[i] = [x, y]
        r = rng.random()
        idx = np.searchsorted(cum_probs, r)
        a, b, c, d, e, f, _ = transforms[idx]
        x_new = a * x + b * y + c
        y_new = d * x + e * y + f
        x, y = x_new, y_new

    return Paths([points])


def sierpinski(n_points: int = 50000, seed: int | None = None) -> Paths:
    """Generate Sierpinski triangle via chaos game.

    Parameters
    ----------
    n_points : int
        Number of points to generate.
    seed : int, optional
        Random seed.

    Returns
    -------
    Paths
        Single polyline of the triangle.
    """
    rng = np.random.default_rng(seed)

    # Triangle vertices
    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.5, np.sqrt(3) / 2],
    ])

    x, y = rng.uniform(0, 1, 2)
    points = np.empty((n_points, 2))

    for i in range(n_points):
        idx = rng.integers(3)
        x = (x + vertices[idx, 0]) / 2
        y = (y + vertices[idx, 1]) / 2
        points[i] = [x, y]

    return Paths([points])


def dragon_curve(order: int = 12) -> Paths:
    """Generate a dragon curve fractal via L-system unfolding.

    Parameters
    ----------
    order : int
        Number of recursive folds. Higher = more detail.

    Returns
    -------
    Paths
        Single polyline of the dragon curve.
    """
    # Build turn sequence: 1 = right, 0 = left
    turns = [1]
    for _ in range(order):
        turns = turns + [1] + [1 - t for t in reversed(turns)]

    # Walk the turns
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    direction = 0
    x, y = 0.0, 0.0
    points = [[x, y]]

    for turn in turns:
        if turn == 1:
            direction = (direction + 1) % 4
        else:
            direction = (direction - 1) % 4
        dx, dy = directions[direction]
        x += dx
        y += dy
        points.append([x, y])

    return Paths([np.array(points)])

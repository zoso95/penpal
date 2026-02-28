"""Scalar field contour extraction.

Extract iso-contour polylines from 2D scalar fields. Reusable primitive
for metaballs, reaction-diffusion, topographic maps, etc.

All generators return Paths.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import matplotlib.pyplot as plt

from penpal.core.paths import Paths


def contour_lines(
    field: np.ndarray | Callable,
    levels: int | list[float] = 20,
    x_range: tuple[float, float] = (-5, 5),
    y_range: tuple[float, float] = (-5, 5),
    resolution: int = 200,
    min_length: int = 5,
) -> Paths:
    """Extract iso-contour lines from a scalar field.

    Parameters
    ----------
    field : ndarray or callable
        Either a 2D array of values, or a function f(X, Y) -> Z
        where X, Y are meshgrid arrays.
    levels : int or list of float
        Number of contour levels, or explicit level values.
    x_range : tuple
        Horizontal extent (xmin, xmax). Used when field is callable.
    y_range : tuple
        Vertical extent (ymin, ymax). Used when field is callable.
    resolution : int
        Grid resolution when field is callable.
    min_length : int
        Minimum number of points for a contour to be kept.

    Returns
    -------
    Paths
        Contour polylines.
    """
    if callable(field):
        x = np.linspace(x_range[0], x_range[1], resolution)
        y = np.linspace(y_range[0], y_range[1], resolution)
        X, Y = np.meshgrid(x, y)
        Z = field(X, Y)
    else:
        Z = field
        h, w = Z.shape
        x = np.linspace(x_range[0], x_range[1], w)
        y = np.linspace(y_range[0], y_range[1], h)
        X, Y = np.meshgrid(x, y)

    lines = _extract_contours(X, Y, Z, levels, min_length)
    return Paths(lines)


def contour_filled(
    field: np.ndarray | Callable,
    levels: int | list[float] = 10,
    x_range: tuple[float, float] = (-5, 5),
    y_range: tuple[float, float] = (-5, 5),
    resolution: int = 200,
    min_length: int = 5,
) -> list[Paths]:
    """Extract filled contour bands as separate Paths per level.

    Returns a list of Paths, one per contour band, suitable for
    assigning to different layers/colors.

    Parameters
    ----------
    field : ndarray or callable
        Either a 2D array or f(X, Y) -> Z.
    levels : int or list of float
        Number of contour levels, or explicit level values.
    x_range, y_range : tuple
        Spatial extent.
    resolution : int
        Grid resolution when field is callable.
    min_length : int
        Minimum contour length.

    Returns
    -------
    list of Paths
        One Paths per contour band.
    """
    if callable(field):
        x = np.linspace(x_range[0], x_range[1], resolution)
        y = np.linspace(y_range[0], y_range[1], resolution)
        X, Y = np.meshgrid(x, y)
        Z = field(X, Y)
    else:
        Z = field
        h, w = Z.shape
        x = np.linspace(x_range[0], x_range[1], w)
        y = np.linspace(y_range[0], y_range[1], h)
        X, Y = np.meshgrid(x, y)

    if isinstance(levels, int):
        level_vals = np.linspace(np.nanmin(Z), np.nanmax(Z), levels + 2)[1:-1]
    else:
        level_vals = np.array(levels)

    result = []
    for lv in level_vals:
        level_lines = _extract_contours(X, Y, Z, [lv], min_length)
        result.append(Paths(level_lines))

    return result


def gaussian_bumps(
    n_bumps: int = 10,
    x_range: tuple[float, float] = (-5, 5),
    y_range: tuple[float, float] = (-5, 5),
    resolution: int = 200,
    n_levels: int = 30,
    amplitude_range: tuple[float, float] = (0.5, 2.0),
    sigma_range: tuple[float, float] = (0.5, 2.0),
    seed: int | None = None,
    min_length: int = 5,
) -> Paths:
    """Generate contours of a random Gaussian bump field.

    Places random Gaussian bumps and extracts iso-contours, producing
    topographic-map-like patterns.

    Parameters
    ----------
    n_bumps : int
        Number of Gaussian bumps to place.
    x_range, y_range : tuple
        Spatial extent.
    resolution : int
        Grid resolution.
    n_levels : int
        Number of contour levels to extract.
    amplitude_range : tuple
        Range of bump amplitudes (min, max).
    sigma_range : tuple
        Range of bump widths (min, max).
    seed : int, optional
        Random seed.
    min_length : int
        Minimum contour points.

    Returns
    -------
    Paths
        Contour polylines of the bump field.
    """
    rng = np.random.default_rng(seed)
    x = np.linspace(x_range[0], x_range[1], resolution)
    y = np.linspace(y_range[0], y_range[1], resolution)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)

    for _ in range(n_bumps):
        cx = rng.uniform(x_range[0], x_range[1])
        cy = rng.uniform(y_range[0], y_range[1])
        amp = rng.uniform(*amplitude_range)
        sig = rng.uniform(*sigma_range)
        sign = rng.choice([-1, 1])
        Z += sign * amp * np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / (2 * sig ** 2))

    return contour_lines(Z, levels=n_levels, x_range=x_range, y_range=y_range,
                         min_length=min_length)


def math_contours(
    func_str: str = "sin(X) * cos(Y)",
    x_range: tuple[float, float] = (-5, 5),
    y_range: tuple[float, float] = (-5, 5),
    resolution: int = 200,
    n_levels: int = 20,
    min_length: int = 5,
) -> Paths:
    """Generate contours from a math expression.

    Parameters
    ----------
    func_str : str
        Math expression using X, Y as variables. Uses numpy namespace.
        Examples: "sin(X) * cos(Y)", "X**2 + Y**2", "sin(X*Y)"
    x_range, y_range : tuple
        Spatial extent.
    resolution : int
        Grid resolution.
    n_levels : int
        Number of contour levels.
    min_length : int
        Minimum contour points.

    Returns
    -------
    Paths
        Contour polylines.
    """
    x = np.linspace(x_range[0], x_range[1], resolution)
    y = np.linspace(y_range[0], y_range[1], resolution)
    X, Y = np.meshgrid(x, y)

    # Safe evaluation with numpy functions
    namespace = {
        "X": X, "Y": Y, "np": np,
        "sin": np.sin, "cos": np.cos, "tan": np.tan,
        "sqrt": np.sqrt, "abs": np.abs, "exp": np.exp,
        "log": np.log, "pi": np.pi,
        "arctan2": np.arctan2, "hypot": np.hypot,
    }
    Z = eval(func_str, {"__builtins__": {}}, namespace)  # noqa: S307

    return contour_lines(Z, levels=n_levels, x_range=x_range, y_range=y_range,
                         min_length=min_length)


def _extract_contours(X, Y, Z, levels, min_length=5):
    """Extract contour lines using matplotlib's contour machinery.

    Returns list of numpy arrays (polylines).
    """
    fig, ax = plt.subplots(1, 1)
    try:
        cs = ax.contour(X, Y, Z, levels=levels)
        lines = []
        # matplotlib 3.8+ removed cs.collections, use cs.allsegs
        if hasattr(cs, "allsegs"):
            for level_segs in cs.allsegs:
                for seg in level_segs:
                    if len(seg) >= min_length:
                        lines.append(np.array(seg))
        else:
            for collection in cs.collections:
                for path in collection.get_paths():
                    verts = path.vertices
                    if len(verts) >= min_length:
                        lines.append(np.array(verts))
    finally:
        plt.close(fig)

    return lines

"""Polar and ribbon pattern generators.

Port of axifun/ribbons.ipynb — cosine-eased interpolation between boundary
curves, creating smooth ribbon fills and polar pattern effects.

All generators return Paths.
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline

from penpal.core.paths import Paths


def ribbon(
    curve_a: np.ndarray,
    curve_b: np.ndarray,
    n_fills: int = 20,
    easing: str = "cosine",
) -> Paths:
    """Fill the region between two curves with interpolated ribbons.

    Creates smooth ribbon fills by interpolating between two boundary curves
    with easing for organic appearance.

    Parameters
    ----------
    curve_a : ndarray, shape (N, 2)
        First boundary curve.
    curve_b : ndarray, shape (M, 2)
        Second boundary curve (resampled to match if different length).
    n_fills : int
        Number of intermediate curves to generate.
    easing : str
        Interpolation easing: 'linear', 'cosine', 'ease_in', 'ease_out'.

    Returns
    -------
    Paths
        Boundary curves plus n_fills intermediate curves.
    """
    # Resample curves to same length
    n = max(len(curve_a), len(curve_b))
    a = _resample_curve(curve_a, n)
    b = _resample_curve(curve_b, n)

    lines = [a.copy()]
    for i in range(1, n_fills + 1):
        t = i / (n_fills + 1)
        alpha = _ease(t, easing)
        interp = a + alpha * (b - a)
        lines.append(interp)
    lines.append(b.copy())

    return Paths(lines)


def ribbon_pair(
    n_points: int = 200,
    x_range: tuple[float, float] = (0, 10),
    width: float = 1.0,
    amplitude: float = 0.5,
    frequency: float = 2.0,
    n_fills: int = 15,
    seed: int | None = None,
) -> Paths:
    """Generate a ribbon from a pair of sinusoidal boundary curves.

    Parameters
    ----------
    n_points : int
        Points per boundary curve.
    x_range : tuple
        Horizontal extent.
    width : float
        Base distance between boundary curves.
    amplitude : float
        Sine wave amplitude for boundaries.
    frequency : float
        Sine wave frequency.
    n_fills : int
        Number of fill curves between boundaries.
    seed : int, optional
        Random seed.

    Returns
    -------
    Paths
        Ribbon fill curves.
    """
    rng = np.random.default_rng(seed)
    x = np.linspace(x_range[0], x_range[1], n_points)

    phase_a = rng.uniform(0, 2 * np.pi) if seed is not None else 0
    phase_b = phase_a + rng.uniform(0.5, 1.5) if seed is not None else np.pi / 3

    y_a = amplitude * np.sin(2 * np.pi * frequency * x / (x_range[1] - x_range[0]) + phase_a)
    y_b = y_a + width + amplitude * 0.3 * np.sin(
        2 * np.pi * frequency * 1.5 * x / (x_range[1] - x_range[0]) + phase_b
    )

    curve_a = np.column_stack([x, y_a])
    curve_b = np.column_stack([x, y_b])

    return ribbon(curve_a, curve_b, n_fills=n_fills)


def concentric_ribbons(
    n_ribbons: int = 5,
    n_fills: int = 10,
    inner_r: float = 1.0,
    outer_r: float = 5.0,
    n_points: int = 200,
    noise_amplitude: float = 0.0,
    seed: int | None = None,
) -> Paths:
    """Generate concentric circular ribbons with optional noise perturbation.

    Parameters
    ----------
    n_ribbons : int
        Number of ribbon bands.
    n_fills : int
        Fill curves per ribbon band.
    inner_r : float
        Inner radius.
    outer_r : float
        Outer radius.
    n_points : int
        Points per circle.
    noise_amplitude : float
        Random radial perturbation (0 = perfect circles).
    seed : int, optional
        Random seed.

    Returns
    -------
    Paths
        All ribbon fill curves.
    """
    rng = np.random.default_rng(seed)
    radii = np.linspace(inner_r, outer_r, n_ribbons + 1)
    theta = np.linspace(0, 2 * np.pi, n_points + 1)

    all_lines = []
    for i in range(n_ribbons):
        r_inner = radii[i]
        r_outer = radii[i + 1]

        noise_i = 0
        noise_o = 0
        if noise_amplitude > 0:
            noise_i = rng.normal(0, noise_amplitude, n_points + 1)
            noise_i[-1] = noise_i[0]  # close curve
            noise_o = rng.normal(0, noise_amplitude, n_points + 1)
            noise_o[-1] = noise_o[0]

        r_a = r_inner + noise_i
        r_b = r_outer + noise_o

        curve_a = np.column_stack([r_a * np.cos(theta), r_a * np.sin(theta)])
        curve_b = np.column_stack([r_b * np.cos(theta), r_b * np.sin(theta)])

        band = ribbon(curve_a, curve_b, n_fills=n_fills)
        all_lines.extend(band.lines)

    return Paths(all_lines)


def polar_function(
    func,
    theta_range: tuple[float, float] = (0, 2 * np.pi),
    n_points: int = 500,
    closed: bool = True,
) -> Paths:
    """Generate a curve from a polar function r = f(theta).

    Parameters
    ----------
    func : callable
        Function f(theta) -> r. Takes array, returns array.
    theta_range : tuple
        Angular range.
    n_points : int
        Number of sample points.
    closed : bool
        Whether to close the curve.

    Returns
    -------
    Paths
        Single polyline of the polar curve.
    """
    theta = np.linspace(theta_range[0], theta_range[1], n_points)
    r = func(theta)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    pts = np.column_stack([x, y])

    if closed:
        pts = np.vstack([pts, pts[0:1]])

    return Paths([pts])


def polar_grid(
    n_rings: int = 10,
    n_spokes: int = 12,
    inner_r: float = 0.5,
    outer_r: float = 5.0,
    n_points: int = 100,
) -> Paths:
    """Generate a polar coordinate grid (rings + radial spokes).

    Parameters
    ----------
    n_rings : int
        Number of concentric rings.
    n_spokes : int
        Number of radial lines.
    inner_r : float
        Innermost ring radius.
    outer_r : float
        Outermost ring radius.
    n_points : int
        Points per ring.

    Returns
    -------
    Paths
        Ring and spoke polylines.
    """
    lines = []
    theta = np.linspace(0, 2 * np.pi, n_points + 1)

    # Rings
    for r in np.linspace(inner_r, outer_r, n_rings):
        ring = np.column_stack([r * np.cos(theta), r * np.sin(theta)])
        lines.append(ring)

    # Spokes
    spoke_angles = np.linspace(0, 2 * np.pi, n_spokes, endpoint=False)
    for angle in spoke_angles:
        spoke = np.array([
            [inner_r * np.cos(angle), inner_r * np.sin(angle)],
            [outer_r * np.cos(angle), outer_r * np.sin(angle)],
        ])
        lines.append(spoke)

    return Paths(lines)


def _resample_curve(pts, n):
    """Resample a curve to n points via linear interpolation."""
    if len(pts) == n:
        return pts
    t_orig = np.linspace(0, 1, len(pts))
    t_new = np.linspace(0, 1, n)
    return np.column_stack([
        np.interp(t_new, t_orig, pts[:, 0]),
        np.interp(t_new, t_orig, pts[:, 1]),
    ])


def _ease(t, kind="cosine"):
    """Apply easing function to interpolation parameter t in [0, 1]."""
    if kind == "cosine":
        return 0.5 - np.cos(t * np.pi) / 2
    elif kind == "ease_in":
        return t * t
    elif kind == "ease_out":
        return 1 - (1 - t) ** 2
    else:  # linear
        return t

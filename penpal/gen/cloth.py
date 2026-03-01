"""Cloth, drape, and braid generators.

Port of old cloth simulation notebooks (moire.ipynb, line_driven_cloth.ipynb,
rainbow_road.ipynb). Generates organic ribbon/fabric shapes by interpolating
between boundary curves with radial noise perturbation and optional
3D perspective projection.

All generators return Paths.
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline

from penpal.core.paths import Paths
from penpal.core.line_ops import resample_polyline


def _cardinal_spline(
    points: np.ndarray,
    tension: float = 0.0,
    n_per_segment: int = 30,
) -> np.ndarray:
    """Catmull-Rom cardinal spline interpolation through control points.

    Parameters
    ----------
    points : ndarray, shape (N, D)
        Control points.
    tension : float
        Tension parameter (0 = Catmull-Rom, 1 = linear).
    n_per_segment : int
        Interpolated points per segment.

    Returns
    -------
    ndarray, shape (M, D)
        Smooth interpolated polyline.
    """
    if len(points) < 2:
        return points.copy()
    if len(points) == 2:
        t = np.linspace(0, 1, n_per_segment).reshape(-1, 1)
        return points[0] + t * (points[1] - points[0])

    # Pad endpoints for boundary tangent estimation
    pts = np.vstack([
        2 * points[0] - points[1],
        points,
        2 * points[-1] - points[-2],
    ])

    s = (1 - tension) / 2
    result = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for j in range(n_per_segment):
            t = j / n_per_segment
            t2 = t * t
            t3 = t2 * t
            h1 = 2 * t3 - 3 * t2 + 1
            h2 = t3 - 2 * t2 + t
            h3 = -2 * t3 + 3 * t2
            h4 = t3 - t2
            pt = h1 * p1 + h2 * s * (p2 - p0) + h3 * p2 + h4 * s * (p3 - p1)
            result.append(pt)

    result.append(pts[-2])
    return np.array(result)


def _smooth_1d(signal: np.ndarray, window: int) -> np.ndarray:
    """Moving average smoothing with wrapped padding."""
    if window < 2 or len(signal) < window:
        return signal.copy()
    flat = signal.ravel()
    padded = np.concatenate([flat[-window:], flat, flat[:window]])
    smoothed = np.convolve(padded, np.ones(window) / window, mode='same')
    return smoothed[window:-window].reshape(signal.shape)


def drape(
    curve_a: np.ndarray,
    curve_b: np.ndarray,
    n_curves: int = 100,
    r_start: float = 3.0,
    r_end: float = 0.5,
    noise_amp: float = 0.3,
    angle_drift: float = 0.015,
    smooth_window: int = 3,
    spline: bool = True,
    spline_tension: float = 0.0,
    seed: int | None = None,
) -> Paths:
    """Generate cloth-like drape curves between two boundary curves.

    Interpolates between two boundaries using radial distance and angle,
    with noise perturbation for organic fabric appearance.

    Parameters
    ----------
    curve_a : ndarray, shape (N, 2)
        First boundary curve (the "anchor" edge).
    curve_b : ndarray, shape (M, 2)
        Second boundary curve (the "drape" edge).
    n_curves : int
        Number of intermediate cloth lines.
    r_start : float
        Radial scale at first curve (larger = further from curve_b).
    r_end : float
        Radial scale at last curve.
    noise_amp : float
        Amplitude of random noise added to radial distance.
    angle_drift : float
        Per-step random walk magnitude on the angle (creates twist).
    smooth_window : int
        Moving average window for noise smoothing (1 = no smoothing).
    spline : bool
        Whether to smooth curves with cardinal spline interpolation.
    spline_tension : float
        Tension parameter for cardinal spline (0 = Catmull-Rom).
    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    Paths
        Collection of cloth drape curves.
    """
    rng = np.random.default_rng(seed)

    # Resample to same length (minimum 20 for smooth splines)
    n = max(len(curve_a), len(curve_b), 20)
    a = resample_polyline(curve_a, n)
    b = resample_polyline(curve_b, n)

    # Compute radial basis between curves
    diff = a - b
    r_base = np.linalg.norm(diff, axis=1).reshape(-1, 1)
    t_base = np.arctan2(diff[:, 0], diff[:, 1]).reshape(-1, 1)

    # Add noise to radial distance
    r_noise = r_base + rng.uniform(-noise_amp, noise_amp, size=r_base.shape)
    if smooth_window > 1:
        r_noise = _smooth_1d(r_noise, smooth_window)

    lines = []
    for frac in np.linspace(0, 1, n_curves):
        r = r_start * (1 - frac) + r_end * frac

        # Angle random walk
        t_base += angle_drift * rng.uniform(-1, 1, size=t_base.shape)

        # Construct curve in Cartesian
        direction = np.hstack([np.sin(t_base), np.cos(t_base)])
        curve = r * r_noise * direction + b

        if spline and len(curve) >= 3:
            curve = _cardinal_spline(curve, tension=spline_tension)

        lines.append(curve)

    return Paths(lines)


def drape_linear(
    p1: tuple[float, float],
    p2: tuple[float, float],
    offset: tuple[float, float] = (0, 1),
    n_sections: int = 25,
    n_curves: int = 150,
    r_start: float = 3.0,
    r_end: float = 0.5,
    shrinkage: float = 0.0,
    **kwargs,
) -> Paths:
    """Generate a drape between two parallel linear boundaries.

    Convenience wrapper around `drape()` — defines boundaries as straight
    lines between p1→p2 with a perpendicular offset.

    Parameters
    ----------
    p1 : tuple
        Start point of boundary line.
    p2 : tuple
        End point of boundary line.
    offset : tuple
        Perpendicular offset vector from curve_a to curve_b.
    n_sections : int
        Number of control points along each boundary.
    n_curves : int
        Number of intermediate cloth lines.
    r_start : float
        Radial scale at first curve.
    r_end : float
        Radial scale at last curve.
    shrinkage : float
        Fraction to shrink curve_b at boundaries (0-0.5).
    **kwargs
        Additional arguments passed to `drape()`.

    Returns
    -------
    Paths
        Collection of cloth drape curves.
    """
    p1 = np.asarray(p1, dtype=float)
    p2 = np.asarray(p2, dtype=float)
    w = np.asarray(offset, dtype=float)

    t = np.linspace(0, 1, n_sections)
    curve_a = np.array([(1 - s) * p1 + s * p2 for s in t])

    t2 = np.linspace(shrinkage, 1 - shrinkage, n_sections)
    curve_b = np.array([(1 - s) * p1 + s * p2 + w for s in t2])

    return drape(curve_a, curve_b, n_curves=n_curves,
                 r_start=r_start, r_end=r_end, **kwargs)


def braid(
    curve_a: np.ndarray,
    curve_b: np.ndarray,
    n_strands: int = 3,
    n_curves_per_strand: int = 30,
    weave_freq: float = 3.0,
    weave_amp: float = 0.3,
    noise_amp: float = 0.1,
    spline: bool = True,
    seed: int | None = None,
) -> list[Paths]:
    """Generate braided/woven strands between two boundary curves.

    Creates multiple interleaved cloth strips that alternate front/back,
    producing a woven or braided appearance. Returns one Paths per strand
    for multi-layer/multi-pen plotting.

    Parameters
    ----------
    curve_a : ndarray, shape (N, 2)
        First boundary curve.
    curve_b : ndarray, shape (M, 2)
        Second boundary curve.
    n_strands : int
        Number of woven strands.
    n_curves_per_strand : int
        Fill curves per strand.
    weave_freq : float
        Number of over/under cycles along the curve length.
    weave_amp : float
        Amplitude of the weave displacement (fraction of total width).
    noise_amp : float
        Random noise on fill curves.
    spline : bool
        Whether to apply cardinal spline smoothing.
    seed : int, optional
        Random seed.

    Returns
    -------
    list[Paths]
        One Paths per strand. Use separate layers for over/under effect.
    """
    rng = np.random.default_rng(seed)

    # Resample to same length
    n = max(len(curve_a), len(curve_b), 50)
    a = resample_polyline(curve_a, n)
    b = resample_polyline(curve_b, n)

    # Parameter along the curves
    t_param = np.linspace(0, 1, n)
    diff = b - a

    strands = []
    for s in range(n_strands):
        # Each strand occupies a band within the a-b space
        band_lo = s / n_strands
        band_hi = (s + 1) / n_strands

        # Phase offset for alternating over/under
        phase = 2 * np.pi * s / n_strands

        lines = []
        for i in range(n_curves_per_strand):
            # Position within band
            frac = band_lo + (band_hi - band_lo) * i / max(1, n_curves_per_strand - 1)

            # Weave sinusoid displaces the fill curve across bands
            weave = weave_amp * np.sin(2 * np.pi * weave_freq * t_param + phase)
            frac_displaced = np.clip(frac + weave, 0, 1)

            # Interpolate between boundaries
            curve = a + frac_displaced.reshape(-1, 1) * diff

            # Add noise
            if noise_amp > 0:
                curve += rng.normal(0, noise_amp, curve.shape)

            if spline and len(curve) >= 4:
                curve = _cardinal_spline(curve, n_per_segment=10)

            lines.append(curve)

        strands.append(Paths(lines))

    return strands


def perspective_drape(
    base_curve: np.ndarray,
    dx: float = 0.0,
    dy: float = 4.0,
    dz: float = 0.0,
    z_range: tuple[float, float] = (1.0, 2.0),
    n_z_control: int = 20,
    n_curves: int = 40,
    focal_length: float = 1.0,
    z_smooth: int = 3,
    x_noise: float = 0.0,
    seed: int | None = None,
) -> Paths:
    """Generate a 3D perspective cloth drape from a 2D base curve.

    Lifts a base curve into 3D by adding a random height profile,
    creates a translated top curve, projects both to 2D via perspective,
    then interpolates between them. Creates the "rainbow road" effect.

    Parameters
    ----------
    base_curve : ndarray, shape (N, 2)
        2D base curve (x, y coordinates).
    dx, dy, dz : float
        Translation offset from base to top curve in 3D space.
    z_range : tuple
        Min and max z-height for random height profile.
    n_z_control : int
        Number of random control points for z-height variation.
    n_curves : int
        Number of interpolated curves between base and top.
    focal_length : float
        Perspective focal length (larger = less perspective).
    z_smooth : int
        Smoothing window for z-height profile.
    x_noise : float
        Random perturbation to x-offset along curve (0 = uniform offset).
    seed : int, optional
        Random seed.

    Returns
    -------
    Paths
        Perspective-projected cloth curves.
    """
    rng = np.random.default_rng(seed)
    n = len(base_curve)

    # Generate z-height profile
    z_ctrl = rng.uniform(z_range[0], z_range[1], n_z_control)
    z_ctrl[0] = z_range[0]
    z_ctrl[-1] = z_range[0]

    # Smooth
    if z_smooth > 1:
        z_ctrl = _smooth_1d(z_ctrl.reshape(-1, 1), z_smooth).ravel()

    # Interpolate z to match base curve length
    z_ctrl_smooth = _cardinal_spline(z_ctrl.reshape(-1, 1), n_per_segment=max(2, n // n_z_control))
    z = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(z_ctrl_smooth)), z_ctrl_smooth.ravel())

    x = base_curve[:, 0]
    y = base_curve[:, 1]
    w = np.ones(n)

    # Build 4D homogeneous coords
    base_homo = np.vstack([x, y, z, w])  # (4, N)

    # Top curve: translate in 3D
    top_homo = base_homo.copy()
    top_homo[0, :] += dx
    top_homo[1, :] += dy
    top_homo[2, :] += dz

    # Optional x-noise for organic look
    if x_noise > 0:
        x_perturb = rng.uniform(1 - x_noise, 1 + x_noise, n)
        x_perturb = _smooth_1d(x_perturb.reshape(-1, 1), max(2, n // 10)).ravel()
        base_homo[0, :] *= x_perturb
        top_homo[0, :] *= x_perturb

    # Projection matrix (weak perspective)
    proj = np.array([
        [focal_length, 0, 0, 0],
        [0, focal_length, 0, 0],
        [0, 0, 1, 0],
    ])

    # Project to 2D
    base_2d = _project(proj, base_homo)
    top_2d = _project(proj, top_homo)

    # Interpolate between projected curves
    lines = []
    for frac in np.linspace(0, 1, n_curves):
        curve = base_2d * (1 - frac) + top_2d * frac
        lines.append(curve)

    return Paths(lines)


def _project(proj_matrix: np.ndarray, homo_coords: np.ndarray) -> np.ndarray:
    """Project 4D homogeneous coordinates to 2D.

    Parameters
    ----------
    proj_matrix : ndarray, shape (3, 4)
        Projection matrix.
    homo_coords : ndarray, shape (4, N)
        Homogeneous coordinates.

    Returns
    -------
    ndarray, shape (N, 2)
        Projected 2D points.
    """
    projected = proj_matrix @ homo_coords  # (3, N)
    # Perspective divide
    projected = projected / projected[2:3, :]
    return projected[:2, :].T  # (N, 2)


def cloth_fill(
    curve_a: np.ndarray,
    curve_b: np.ndarray,
    n_curves: int = 50,
    noise_amp: float = 0.0,
    spline: bool = True,
    spline_tension: float = 0.0,
    easing: str = "linear",
    seed: int | None = None,
) -> Paths:
    """Simple interpolated fill between two curves with optional noise.

    Like `polar.ribbon()` but with cardinal spline smoothing and noise
    perturbation for a more organic cloth-like appearance.

    Parameters
    ----------
    curve_a : ndarray, shape (N, 2)
        First boundary curve.
    curve_b : ndarray, shape (M, 2)
        Second boundary curve.
    n_curves : int
        Number of fill curves (excluding boundaries).
    noise_amp : float
        Amplitude of random perpendicular noise.
    spline : bool
        Whether to apply cardinal spline smoothing.
    spline_tension : float
        Tension for cardinal spline.
    easing : str
        Interpolation easing: 'linear', 'cosine', 'ease_in', 'ease_out'.
    seed : int, optional
        Random seed.

    Returns
    -------
    Paths
        Boundary curves plus interpolated fill curves.
    """
    rng = np.random.default_rng(seed)

    n = max(len(curve_a), len(curve_b), 20)
    a = resample_polyline(curve_a, n)
    b = resample_polyline(curve_b, n)

    diff = b - a
    # Perpendicular direction for noise
    norms = np.sqrt(np.sum(diff ** 2, axis=1, keepdims=True))
    norms = np.maximum(norms, 1e-10)
    perp = np.column_stack([-diff[:, 1], diff[:, 0]]) / norms

    lines = [a.copy()]
    for i in range(1, n_curves + 1):
        t = i / (n_curves + 1)
        alpha = _ease_value(t, easing)
        curve = a + alpha * diff

        if noise_amp > 0:
            noise = rng.normal(0, noise_amp, n).reshape(-1, 1) * perp
            curve = curve + noise

        if spline and len(curve) >= 4:
            curve = _cardinal_spline(curve, tension=spline_tension)

        lines.append(curve)
    lines.append(b.copy())

    return Paths(lines)


def _ease_value(t: float, kind: str = "linear") -> float:
    """Apply easing function to interpolation parameter."""
    if kind == "cosine":
        return 0.5 - np.cos(t * np.pi) / 2
    elif kind == "ease_in":
        return t * t
    elif kind == "ease_out":
        return 1 - (1 - t) ** 2
    else:
        return t

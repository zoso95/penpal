"""Physics-driven spline wave generators.

Port of axifun/spline waves.ipynb — control points with velocity and
acceleration evolve over time, cubic spline interpolation per frame.

All generators return Paths.
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline

from penpal.core.paths import Paths


def spline_waves(
    n_points: int = 10,
    n_frames: int = 100,
    x_range: tuple[float, float] = (0, 10),
    y_range: tuple[float, float] = (-3, 3),
    force_scale: float = 0.03,
    damping: float = 0.98,
    resolution: int = 200,
    seed: int | None = None,
) -> Paths:
    """Generate flowing wave curves via physics simulation of spline control points.

    Each control point has position, velocity, and acceleration. Random forces
    drive organic motion. Cubic spline interpolation produces smooth curves.

    Parameters
    ----------
    n_points : int
        Number of spline control points.
    n_frames : int
        Number of animation frames (one curve per frame).
    x_range : tuple
        Horizontal extent of the control points.
    y_range : tuple
        Vertical range for initial control point positions.
    force_scale : float
        Magnitude of random acceleration forces.
    damping : float
        Velocity damping factor (0-1). Lower = more friction.
    resolution : int
        Number of interpolated points per curve.
    seed : int, optional
        Random seed.

    Returns
    -------
    Paths
        One polyline per frame.
    """
    rng = np.random.default_rng(seed)
    x_ctrl = np.linspace(x_range[0], x_range[1], n_points)
    y_ctrl = rng.uniform(y_range[0], y_range[1], n_points)
    vy = np.zeros(n_points)

    x_fine = np.linspace(x_range[0], x_range[1], resolution)
    lines = []

    for _ in range(n_frames):
        # Physics step
        acc = rng.normal(0, force_scale, n_points)
        vy = vy * damping + acc
        y_ctrl = y_ctrl + vy

        # Spline interpolation
        cs = CubicSpline(x_ctrl, y_ctrl)
        y_fine = cs(x_fine)
        lines.append(np.column_stack([x_fine, y_fine]))

    return Paths(lines)


def random_walk_waves(
    n_points: int = 10,
    n_frames: int = 100,
    x_range: tuple[float, float] = (0, 10),
    step_size: float = 0.1,
    noise_scale: float = 0.05,
    resolution: int = 200,
    seed: int | None = None,
) -> Paths:
    """Generate wave curves via random walk of control points.

    Simpler than physics simulation — each point does an integer random
    walk with small Gaussian noise added.

    Parameters
    ----------
    n_points : int
        Number of spline control points.
    n_frames : int
        Number of curves to generate.
    x_range : tuple
        Horizontal extent.
    step_size : float
        Size of the random walk step.
    noise_scale : float
        Gaussian noise added per step.
    resolution : int
        Interpolation resolution.
    seed : int, optional
        Random seed.

    Returns
    -------
    Paths
        One polyline per frame.
    """
    rng = np.random.default_rng(seed)
    x_ctrl = np.linspace(x_range[0], x_range[1], n_points)
    y_ctrl = np.zeros(n_points)

    x_fine = np.linspace(x_range[0], x_range[1], resolution)
    lines = []

    for _ in range(n_frames):
        dy = rng.choice([-1, 0, 1], n_points) * step_size
        dy += rng.normal(0, noise_scale, n_points)
        y_ctrl = y_ctrl + dy

        cs = CubicSpline(x_ctrl, y_ctrl)
        y_fine = cs(x_fine)
        lines.append(np.column_stack([x_fine, y_fine]))

    return Paths(lines)


def evolving_waves(
    n_waves: int = 20,
    n_points: int = 200,
    x_range: tuple[float, float] = (0, 10),
    base_amplitude: float = 1.0,
    frequency_range: tuple[float, float] = (0.5, 3.0),
    phase_drift: float = 0.2,
    amplitude_drift: float = 0.1,
    seed: int | None = None,
) -> Paths:
    """Generate gradually evolving sinusoidal waves.

    Each successive wave has slightly drifted phase and amplitude,
    creating a smooth progression of related curves.

    Parameters
    ----------
    n_waves : int
        Number of wave curves to generate.
    n_points : int
        Points per curve.
    x_range : tuple
        Horizontal extent.
    base_amplitude : float
        Starting wave amplitude.
    frequency_range : tuple
        Range for random wave frequency.
    phase_drift : float
        Phase change per wave.
    amplitude_drift : float
        Amplitude change per wave.
    seed : int, optional
        Random seed.

    Returns
    -------
    Paths
        One polyline per wave.
    """
    rng = np.random.default_rng(seed)
    x = np.linspace(x_range[0], x_range[1], n_points)

    freq = rng.uniform(*frequency_range)
    phase = 0.0
    amp = base_amplitude

    lines = []
    for _ in range(n_waves):
        y = amp * np.sin(2 * np.pi * freq * x / (x_range[1] - x_range[0]) + phase)
        lines.append(np.column_stack([x, y]))

        phase += rng.normal(0, phase_drift)
        amp += rng.normal(0, amplitude_drift)

    return Paths(lines)

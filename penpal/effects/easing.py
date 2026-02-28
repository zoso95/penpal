"""Easing / interpolation functions.

All functions map t in [0, 1] -> output in [0, 1] (or slightly beyond for
elastic/bounce). Work with both scalar and numpy array inputs.

Useful for: modulating density, animating parameters, shaping warp fields,
controlling ribbon interpolation, and any smooth transitions.
"""

from __future__ import annotations

import numpy as np


def linear(t):
    """Linear interpolation (identity)."""
    return np.asarray(t, dtype=float)


def ease_in(t):
    """Quadratic ease-in (slow start)."""
    t = np.asarray(t, dtype=float)
    return t * t


def ease_out(t):
    """Quadratic ease-out (slow end)."""
    t = np.asarray(t, dtype=float)
    return 1 - (1 - t) ** 2


def ease_in_out(t):
    """Quadratic ease-in-out (slow start and end)."""
    t = np.asarray(t, dtype=float)
    return np.where(t < 0.5, 2 * t * t, 1 - (-2 * t + 2) ** 2 / 2)


def ease_in_cubic(t):
    """Cubic ease-in."""
    t = np.asarray(t, dtype=float)
    return t ** 3


def ease_out_cubic(t):
    """Cubic ease-out."""
    t = np.asarray(t, dtype=float)
    return 1 - (1 - t) ** 3


def ease_in_out_cubic(t):
    """Cubic ease-in-out."""
    t = np.asarray(t, dtype=float)
    return np.where(t < 0.5, 4 * t ** 3, 1 - (-2 * t + 2) ** 3 / 2)


def ease_in_quart(t):
    """Quartic ease-in."""
    t = np.asarray(t, dtype=float)
    return t ** 4


def ease_out_quart(t):
    """Quartic ease-out."""
    t = np.asarray(t, dtype=float)
    return 1 - (1 - t) ** 4


def ease_in_out_quart(t):
    """Quartic ease-in-out."""
    t = np.asarray(t, dtype=float)
    return np.where(t < 0.5, 8 * t ** 4, 1 - (-2 * t + 2) ** 4 / 2)


def ease_in_expo(t):
    """Exponential ease-in."""
    t = np.asarray(t, dtype=float)
    return np.where(t == 0, 0.0, 2.0 ** (10 * t - 10))


def ease_out_expo(t):
    """Exponential ease-out."""
    t = np.asarray(t, dtype=float)
    return np.where(t == 1, 1.0, 1 - 2.0 ** (-10 * t))


def ease_in_circ(t):
    """Circular ease-in."""
    t = np.asarray(t, dtype=float)
    return 1 - np.sqrt(1 - t ** 2)


def ease_out_circ(t):
    """Circular ease-out."""
    t = np.asarray(t, dtype=float)
    return np.sqrt(1 - (t - 1) ** 2)


def ease_in_elastic(t, amplitude: float = 1.0, period: float = 0.3):
    """Elastic ease-in (springy overshoot at start)."""
    t = np.asarray(t, dtype=float)
    if amplitude < 1:
        amplitude = 1
        s = period / 4
    else:
        s = period / (2 * np.pi) * np.arcsin(1 / amplitude)
    return np.where(
        (t == 0) | (t == 1),
        t,
        -(amplitude * 2.0 ** (10 * (t - 1)) * np.sin((t - 1 - s) * (2 * np.pi) / period))
    )


def ease_out_elastic(t, amplitude: float = 1.0, period: float = 0.3):
    """Elastic ease-out (springy overshoot at end)."""
    t = np.asarray(t, dtype=float)
    if amplitude < 1:
        amplitude = 1
        s = period / 4
    else:
        s = period / (2 * np.pi) * np.arcsin(1 / amplitude)
    return np.where(
        (t == 0) | (t == 1),
        t,
        amplitude * 2.0 ** (-10 * t) * np.sin((t - s) * (2 * np.pi) / period) + 1
    )


def ease_out_bounce(t):
    """Bounce ease-out (bouncing ball effect)."""
    t = np.asarray(t, dtype=float)
    n1 = 7.5625
    d1 = 2.75

    result = np.empty_like(t)
    mask1 = t < 1 / d1
    mask2 = (~mask1) & (t < 2 / d1)
    mask3 = (~mask1) & (~mask2) & (t < 2.5 / d1)
    mask4 = ~(mask1 | mask2 | mask3)

    result[mask1] = n1 * t[mask1] ** 2
    t2 = t[mask2] - 1.5 / d1
    result[mask2] = n1 * t2 * t2 + 0.75
    t3 = t[mask3] - 2.25 / d1
    result[mask3] = n1 * t3 * t3 + 0.9375
    t4 = t[mask4] - 2.625 / d1
    result[mask4] = n1 * t4 * t4 + 0.984375

    return result


def ease_in_bounce(t):
    """Bounce ease-in."""
    t = np.asarray(t, dtype=float)
    return 1 - ease_out_bounce(1 - t)


def smoothstep(t):
    """Hermite smoothstep (3t^2 - 2t^3)."""
    t = np.asarray(t, dtype=float)
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def smootherstep(t):
    """Ken Perlin's smootherstep (6t^5 - 15t^4 + 10t^3)."""
    t = np.asarray(t, dtype=float)
    t = np.clip(t, 0, 1)
    return t * t * t * (t * (t * 6 - 15) + 10)


def step(t, threshold: float = 0.5):
    """Hard step function."""
    t = np.asarray(t, dtype=float)
    return np.where(t < threshold, 0.0, 1.0)


def pulse(t, center: float = 0.5, width: float = 0.2):
    """Smooth pulse (Gaussian-like bump)."""
    t = np.asarray(t, dtype=float)
    return np.exp(-((t - center) ** 2) / (2 * (width / 2.355) ** 2))


def sawtooth(t, period: float = 1.0):
    """Sawtooth wave (repeating linear ramp)."""
    t = np.asarray(t, dtype=float)
    return (t / period) % 1.0


def triangle_wave(t, period: float = 1.0):
    """Triangle wave (repeating linear up-down)."""
    t = np.asarray(t, dtype=float)
    phase = (t / period) % 1.0
    return np.where(phase < 0.5, 2 * phase, 2 * (1 - phase))


def remap(t, in_min: float = 0, in_max: float = 1,
          out_min: float = 0, out_max: float = 1,
          easing=None):
    """Remap values from one range to another with optional easing.

    Parameters
    ----------
    t : array-like
        Input values.
    in_min, in_max : float
        Input range.
    out_min, out_max : float
        Output range.
    easing : callable, optional
        Easing function to apply to normalized [0,1] value.

    Returns
    -------
    ndarray
        Remapped values.
    """
    t = np.asarray(t, dtype=float)
    normalized = (t - in_min) / (in_max - in_min + 1e-10)
    normalized = np.clip(normalized, 0, 1)

    if easing is not None:
        normalized = easing(normalized)

    return out_min + normalized * (out_max - out_min)

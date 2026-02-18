"""Noise functions for mesh warping.

Each function returns a callable with signature (x, y) -> (dx, dy),
suitable for passing to Mesh.warp().

Usage:
    mesh.warp(noise.simplex(amplitude=0.3, frequency=1.0, seed=42))
    mesh.warp(noise.fractal(amplitude=0.3, octaves=4))
    mesh.warp(noise.curl(amplitude=0.5))
    mesh.warp(noise.ridged(amplitude=0.3, frequency=0.8))
    mesh.warp(noise.sine(amplitude=0.2, freq_x=3, freq_y=5))

Custom noise:
    mesh.warp(lambda x, y: (np.sin(x * 3) * 0.2, np.cos(y * 5) * 0.1))
"""

from __future__ import annotations

from typing import Callable, Tuple

import numpy as np


# Type alias: a warp function takes (x, y) arrays and returns (dx, dy) arrays
WarpFunc = Callable[[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]


def _make_simplex(seed: int = None):
    """Create an OpenSimplex noise instance with optional seed."""
    from opensimplex import OpenSimplex
    rng = np.random.default_rng(seed)
    return OpenSimplex(seed=int(rng.integers(0, 2**31)))


def _eval_simplex(noise, x: np.ndarray, y: np.ndarray,
                  frequency: float, offset: float = 0.0) -> np.ndarray:
    """Evaluate simplex noise over a grid. Returns array same shape as x."""
    out = np.zeros_like(x)
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            out[i, j] = noise.noise2(
                x[i, j] * frequency + offset,
                y[i, j] * frequency + offset,
            )
    return out


def simplex(amplitude: float = 0.3, frequency: float = 1.0,
            seed: int = None) -> WarpFunc:
    """Smooth simplex noise displacement.

    Each vertex is displaced by (dx, dy) sampled from 2D simplex noise.
    The x and y displacements use different noise slices (offset by 100)
    so they're independent.

    Parameters
    ----------
    amplitude : float
        Max displacement in drawing units.
    frequency : float
        Spatial frequency — higher = tighter variation.
    seed : int, optional
        For reproducibility.
    """
    def _warp(x, y):
        noise = _make_simplex(seed)
        dx = _eval_simplex(noise, x, y, frequency, offset=0.0) * amplitude
        dy = _eval_simplex(noise, x, y, frequency, offset=100.0) * amplitude
        return dx, dy
    return _warp


def fractal(amplitude: float = 0.3, frequency: float = 1.0,
            octaves: int = 4, persistence: float = 0.5,
            lacunarity: float = 2.0, seed: int = None) -> WarpFunc:
    """Fractal (fBm) noise — multiple octaves of simplex layered together.

    Produces more natural, detailed noise than single-octave simplex.
    Each octave adds finer detail at decreasing amplitude.

    Parameters
    ----------
    amplitude : float
        Max displacement of the combined noise.
    frequency : float
        Base frequency (lowest octave).
    octaves : int
        Number of noise layers. More octaves = more detail.
    persistence : float
        How much each octave's amplitude decreases (0-1).
        Lower = smoother, higher = more detail.
    lacunarity : float
        How much each octave's frequency increases.
        2.0 is standard (each octave is twice the frequency).
    seed : int, optional
        For reproducibility.
    """
    def _warp(x, y):
        noise = _make_simplex(seed)
        dx = np.zeros_like(x)
        dy = np.zeros_like(y)
        amp = 1.0
        freq = frequency
        total_amp = 0.0
        for _ in range(octaves):
            dx += _eval_simplex(noise, x, y, freq, offset=0.0) * amp
            dy += _eval_simplex(noise, x, y, freq, offset=100.0) * amp
            total_amp += amp
            amp *= persistence
            freq *= lacunarity
        # Normalize so total amplitude matches the requested amplitude
        dx *= amplitude / total_amp
        dy *= amplitude / total_amp
        return dx, dy
    return _warp


def ridged(amplitude: float = 0.3, frequency: float = 1.0,
           octaves: int = 4, persistence: float = 0.5,
           lacunarity: float = 2.0, seed: int = None) -> WarpFunc:
    """Ridged multifractal noise — sharp creases and ridges.

    Like fractal noise but with |noise| creating sharp edges where
    the noise crosses zero. Produces mountain-ridge-like patterns.

    Parameters
    ----------
    amplitude : float
        Max displacement.
    frequency : float
        Base frequency.
    octaves : int
        Number of layers.
    persistence : float
        Amplitude falloff per octave.
    lacunarity : float
        Frequency multiplier per octave.
    seed : int, optional
        For reproducibility.
    """
    def _warp(x, y):
        noise = _make_simplex(seed)
        dx = np.zeros_like(x)
        dy = np.zeros_like(y)
        amp = 1.0
        freq = frequency
        total_amp = 0.0
        for _ in range(octaves):
            # Ridged: 1 - |noise| creates sharp valleys at zero crossings
            raw_x = _eval_simplex(noise, x, y, freq, offset=0.0)
            raw_y = _eval_simplex(noise, x, y, freq, offset=100.0)
            dx += (1.0 - np.abs(raw_x)) * amp
            dy += (1.0 - np.abs(raw_y)) * amp
            total_amp += amp
            amp *= persistence
            freq *= lacunarity
        # Center around zero and scale
        dx = (dx / total_amp - 0.5) * 2 * amplitude
        dy = (dy / total_amp - 0.5) * 2 * amplitude
        return dx, dy
    return _warp


def curl(amplitude: float = 0.3, frequency: float = 1.0,
         seed: int = None) -> WarpFunc:
    """Curl noise — divergence-free, produces fluid-like swirling patterns.

    Computes the curl of a scalar noise field, so displacement vectors
    follow contour lines of the noise rather than crossing them. This
    produces beautiful swirling, flow-like distortion.

    Parameters
    ----------
    amplitude : float
        Max displacement.
    frequency : float
        Spatial frequency of the underlying noise field.
    seed : int, optional
        For reproducibility.
    """
    def _warp(x, y):
        noise = _make_simplex(seed)
        eps = 1e-4  # finite difference step
        # Compute partial derivatives of noise field via finite differences
        # curl of scalar field ψ: (∂ψ/∂y, -∂ψ/∂x)
        n_center = _eval_simplex(noise, x, y, frequency)
        n_dx = _eval_simplex(noise, x + eps, y, frequency)
        n_dy = _eval_simplex(noise, x, y + eps, frequency)
        dpsi_dx = (n_dx - n_center) / eps
        dpsi_dy = (n_dy - n_center) / eps
        # Curl: rotate gradient 90 degrees
        dx = dpsi_dy * amplitude
        dy = -dpsi_dx * amplitude
        return dx, dy
    return _warp


def sine(amplitude: float = 0.2, freq_x: float = 1.0, freq_y: float = 1.0,
         phase_x: float = 0.0, phase_y: float = 0.0,
         coupled: bool = False) -> WarpFunc:
    """Sinusoidal wave displacement.

    Produces regular, predictable wave patterns. When coupled=True,
    both axes influence both displacement components, creating more
    interesting interference patterns.

    Parameters
    ----------
    amplitude : float
        Max displacement.
    freq_x, freq_y : float
        Spatial frequency along each axis (in cycles per drawing unit).
    phase_x, phase_y : float
        Phase offset in radians.
    coupled : bool
        If True, displacement depends on both axes (creates interference).
        If False, x-displacement depends only on y, and vice versa.
    """
    def _warp(x, y):
        if coupled:
            dx = np.sin(x * freq_x * 2 * np.pi + y * freq_y * np.pi + phase_x) * amplitude
            dy = np.cos(y * freq_y * 2 * np.pi + x * freq_x * np.pi + phase_y) * amplitude
        else:
            dx = np.sin(y * freq_y * 2 * np.pi + phase_x) * amplitude
            dy = np.sin(x * freq_x * 2 * np.pi + phase_y) * amplitude
        return dx, dy
    return _warp


def domain_warp(inner: WarpFunc, warp_amplitude: float = 1.0,
                warp_frequency: float = 0.5, seed: int = None) -> WarpFunc:
    """Domain warping — feed noise into the coordinates of another noise.

    Produces alien, organic-looking distortion by warping the input
    coordinates of another noise function with a separate noise field.
    Popularized by Inigo Quilez.

    Parameters
    ----------
    inner : WarpFunc
        The inner noise function to apply after coordinate warping.
    warp_amplitude : float
        How much to displace coordinates before feeding to inner noise.
    warp_frequency : float
        Frequency of the coordinate-warping noise.
    seed : int, optional
        Seed for the coordinate-warping noise.
    """
    def _warp(x, y):
        # First pass: warp the coordinates
        noise = _make_simplex(seed)
        wx = _eval_simplex(noise, x, y, warp_frequency, offset=0.0) * warp_amplitude
        wy = _eval_simplex(noise, x, y, warp_frequency, offset=50.0) * warp_amplitude
        # Second pass: evaluate inner noise at warped coordinates
        return inner(x + wx, y + wy)
    return _warp


def compose(*funcs: WarpFunc) -> WarpFunc:
    """Compose multiple noise functions by summing their displacements.

    Usage:
        mesh.warp(noise.compose(
            noise.simplex(amplitude=0.2, frequency=0.5),
            noise.sine(amplitude=0.1, freq_x=3),
        ))
    """
    def _warp(x, y):
        dx_total = np.zeros_like(x)
        dy_total = np.zeros_like(y)
        for f in funcs:
            dx, dy = f(x, y)
            dx_total += dx
            dy_total += dy
        return dx_total, dy_total
    return _warp

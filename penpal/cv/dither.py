"""Error-diffusion dithering algorithms.

Convert grayscale images to dithered dot/line patterns suitable for
plotter output. Each algorithm quantizes pixels and diffuses the
quantization error to neighboring pixels.

All functions take (H, W) float64 [0, 255] images and return Paths
in pixel coordinates.
"""

from __future__ import annotations

import numpy as np

from penpal.core.paths import Paths
from penpal.cv.image import smooth


def floyd_steinberg(
    image: np.ndarray,
    n_levels: int = 2,
    sigma: float = 1.0,
    dot_radius: float = 0.8,
    n_circle_points: int = 8,
) -> Paths:
    """Floyd-Steinberg error diffusion dithering.

    Classic 4-neighbor error diffusion with weights [7, 3, 5, 1]/16.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    n_levels : int
        Number of quantization levels (2 = pure black/white).
    sigma : float
        Pre-smoothing.
    dot_radius : float
        Radius of dots for dark pixels.
    n_circle_points : int
        Points per dot circle.

    Returns
    -------
    Paths in pixel coordinates.
    """
    positions = [(0, 1), (1, -1), (1, 0), (1, 1)]
    weights = [7, 3, 5, 1]
    return _dither(image, n_levels, sigma, dot_radius, n_circle_points,
                   positions, weights)


def stucki(
    image: np.ndarray,
    n_levels: int = 2,
    sigma: float = 1.0,
    dot_radius: float = 0.8,
    n_circle_points: int = 8,
) -> Paths:
    """Stucki error diffusion dithering.

    Wider 12-neighbor diffusion kernel for smoother results.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    n_levels : int
        Quantization levels.
    sigma : float
        Pre-smoothing.
    dot_radius : float
        Dot radius.
    n_circle_points : int
        Points per circle.

    Returns
    -------
    Paths in pixel coordinates.
    """
    positions = [
        (0, 1), (0, 2),
        (1, -2), (1, -1), (1, 0), (1, 1), (1, 2),
        (2, -2), (2, -1), (2, 0), (2, 1), (2, 2),
    ]
    weights = [
        8, 4,
        2, 4, 8, 4, 2,
        1, 2, 4, 2, 1,
    ]
    return _dither(image, n_levels, sigma, dot_radius, n_circle_points,
                   positions, weights)


def jarvis_judice_ninke(
    image: np.ndarray,
    n_levels: int = 2,
    sigma: float = 1.0,
    dot_radius: float = 0.8,
    n_circle_points: int = 8,
) -> Paths:
    """Jarvis-Judice-Ninke error diffusion dithering.

    12-neighbor kernel, alternative to Stucki.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    n_levels : int
        Quantization levels.
    sigma : float
        Pre-smoothing.
    dot_radius : float
        Dot radius.
    n_circle_points : int
        Points per circle.

    Returns
    -------
    Paths in pixel coordinates.
    """
    positions = [
        (0, 1), (0, 2),
        (1, -2), (1, -1), (1, 0), (1, 1), (1, 2),
        (2, -2), (2, -1), (2, 0), (2, 1), (2, 2),
    ]
    weights = [
        7, 5,
        3, 5, 7, 5, 3,
        1, 3, 5, 3, 1,
    ]
    return _dither(image, n_levels, sigma, dot_radius, n_circle_points,
                   positions, weights)


def atkinson(
    image: np.ndarray,
    n_levels: int = 2,
    sigma: float = 1.0,
    dot_radius: float = 0.8,
    n_circle_points: int = 8,
) -> Paths:
    """Atkinson dithering (as used in classic Macintosh).

    Only diffuses 3/4 of the error, creating higher contrast results
    with more white space.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    n_levels : int
        Quantization levels.
    sigma : float
        Pre-smoothing.
    dot_radius : float
        Dot radius.
    n_circle_points : int
        Points per circle.

    Returns
    -------
    Paths in pixel coordinates.
    """
    positions = [
        (0, 1), (0, 2),
        (1, -1), (1, 0), (1, 1),
        (2, 0),
    ]
    # Atkinson only diffuses 6/8 = 3/4 of error
    weights = [1, 1, 1, 1, 1, 1]
    return _dither(image, n_levels, sigma, dot_radius, n_circle_points,
                   positions, weights, weight_sum_override=8)


def dither_to_lines(
    image: np.ndarray,
    n_levels: int = 2,
    sigma: float = 1.0,
    kernel: str = "floyd_steinberg",
    row_skip: int = 2,
) -> Paths:
    """Dither image and render as horizontal line segments.

    Instead of dots, draws horizontal lines through dark pixels,
    better suited for pen plotter output.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    n_levels : int
        Quantization levels.
    sigma : float
        Pre-smoothing.
    kernel : str
        Dithering kernel: 'floyd_steinberg', 'stucki', 'atkinson'.
    row_skip : int
        Draw every nth row (1 = every row).

    Returns
    -------
    Paths in pixel coordinates.
    """
    img = smooth(image, sigma).copy()
    h, w = img.shape

    # Run dithering to get quantized image
    thresholds = np.linspace(0, 255, n_levels)[1:]

    kernels = {
        "floyd_steinberg": (
            [(0, 1), (1, -1), (1, 0), (1, 1)],
            [7, 3, 5, 1], 16,
        ),
        "stucki": (
            [(0, 1), (0, 2), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2),
             (2, -2), (2, -1), (2, 0), (2, 1), (2, 2)],
            [8, 4, 2, 4, 8, 4, 2, 1, 2, 4, 2, 1], 42,
        ),
        "atkinson": (
            [(0, 1), (0, 2), (1, -1), (1, 0), (1, 1), (2, 0)],
            [1, 1, 1, 1, 1, 1], 8,
        ),
    }
    positions, weights, w_sum = kernels.get(kernel, kernels["floyd_steinberg"])

    # Error diffusion
    buf = img / 255.0
    for i in range(h):
        for j in range(w):
            old = buf[i, j]
            new = np.round(old * (n_levels - 1)) / (n_levels - 1)
            buf[i, j] = new
            error = old - new

            for (di, dj), wt in zip(positions, weights):
                ni, nj = i + di, j + dj
                if 0 <= ni < h and 0 <= nj < w:
                    buf[ni, nj] += error * wt / w_sum

    # Convert to line segments (dark pixels)
    dark = buf < 0.5
    lines = []
    for row in range(0, h, row_skip):
        if row >= h:
            break
        padded = np.concatenate([[False], dark[row], [False]])
        diffs = np.diff(padded.astype(int))
        starts = np.where(diffs == 1)[0]
        ends = np.where(diffs == -1)[0]
        for s, e in zip(starts, ends):
            if e - s >= 2:
                lines.append(np.array([[s, row], [e - 1, row]], dtype=float))

    return Paths(lines)


def _dither(image, n_levels, sigma, dot_radius, n_circle_points,
            positions, weights, weight_sum_override=None):
    """Core error diffusion dithering with configurable kernel."""
    img = smooth(image, sigma).copy()
    h, w = img.shape

    w_sum = weight_sum_override if weight_sum_override else sum(weights)
    thresholds = np.linspace(0, 255, n_levels)[1:]

    # Error diffusion pass
    for i in range(h):
        for j in range(w):
            old_val = img[i, j]
            new_val = np.searchsorted(thresholds, old_val) * (255 / (n_levels - 1))
            img[i, j] = new_val
            error = old_val - new_val

            for (di, dj), wt in zip(positions, weights):
                ni, nj = i + di, j + dj
                if 0 <= ni < h and 0 <= nj < w:
                    img[ni, nj] += error * wt / w_sum

    # Generate dots at dark pixels
    theta = np.linspace(0, 2 * np.pi, n_circle_points + 1)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)

    lines = []
    dark_threshold = 255 / (2 * (n_levels - 1)) if n_levels > 1 else 128

    for i in range(h):
        for j in range(w):
            if img[i, j] < dark_threshold:
                circle = np.column_stack([
                    j + dot_radius * cos_t,
                    i + dot_radius * sin_t,
                ])
                lines.append(circle)

    return Paths(lines)

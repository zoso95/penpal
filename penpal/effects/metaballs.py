"""Metaball / implicit surface generators.

Sum of 1/r^2 fields from point sources, extract iso-contours as polylines.
Produces organic blobby shapes that merge and split.

All generators return Paths.
"""

from __future__ import annotations

import numpy as np

from penpal.core.paths import Paths
from penpal.gen.contours import contour_lines, _extract_contours


def metaballs(
    centers: np.ndarray | list | None = None,
    radii: np.ndarray | list | None = None,
    n_balls: int = 5,
    threshold: float = 1.0,
    n_contours: int = 1,
    x_range: tuple[float, float] = (-5, 5),
    y_range: tuple[float, float] = (-5, 5),
    resolution: int = 300,
    seed: int | None = None,
    min_length: int = 10,
) -> Paths:
    """Generate metaball iso-contours.

    Computes a scalar field as the sum of inverse-distance functions
    from multiple point sources, then extracts iso-contour lines.

    Parameters
    ----------
    centers : ndarray or list, optional
        Ball center positions, shape (N, 2). If None, random.
    radii : ndarray or list, optional
        Ball influence radii. If None, random.
    n_balls : int
        Number of balls (used if centers is None).
    threshold : float
        Iso-contour threshold. Higher = smaller blobs.
    n_contours : int
        Number of contour levels to extract around the threshold.
    x_range, y_range : tuple
        Spatial extent.
    resolution : int
        Grid resolution.
    seed : int, optional
        Random seed.
    min_length : int
        Minimum points per contour.

    Returns
    -------
    Paths
        Metaball contour polylines.
    """
    rng = np.random.default_rng(seed)

    if centers is None:
        centers = np.column_stack([
            rng.uniform(x_range[0] * 0.6, x_range[1] * 0.6, n_balls),
            rng.uniform(y_range[0] * 0.6, y_range[1] * 0.6, n_balls),
        ])
    else:
        centers = np.asarray(centers)
        n_balls = len(centers)

    if radii is None:
        radii = rng.uniform(0.5, 2.0, n_balls)
    else:
        radii = np.asarray(radii)

    # Compute scalar field
    x = np.linspace(x_range[0], x_range[1], resolution)
    y = np.linspace(y_range[0], y_range[1], resolution)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)

    for i in range(n_balls):
        cx, cy = centers[i]
        r = radii[i]
        dist_sq = (X - cx) ** 2 + (Y - cy) ** 2 + 1e-6
        Z += r ** 2 / dist_sq

    # Extract contours
    if n_contours == 1:
        levels = [threshold]
    else:
        levels = np.linspace(threshold * 0.5, threshold * 2.0, n_contours).tolist()

    lines = _extract_contours(X, Y, Z, levels, min_length)
    return Paths(lines)


def metaball_field(
    centers: np.ndarray,
    radii: np.ndarray,
    n_levels: int = 15,
    x_range: tuple[float, float] = (-5, 5),
    y_range: tuple[float, float] = (-5, 5),
    resolution: int = 300,
    min_length: int = 10,
) -> Paths:
    """Generate multiple contour levels of a metaball field.

    Creates a rich topographic map of the metaball scalar field
    with many contour levels, producing nested organic shapes.

    Parameters
    ----------
    centers : ndarray, shape (N, 2)
        Ball center positions.
    radii : ndarray, shape (N,)
        Ball influence radii.
    n_levels : int
        Number of contour levels.
    x_range, y_range : tuple
        Spatial extent.
    resolution : int
        Grid resolution.
    min_length : int
        Minimum points per contour.

    Returns
    -------
    Paths
        All contour lines across all levels.
    """
    centers = np.asarray(centers)
    radii = np.asarray(radii)

    x = np.linspace(x_range[0], x_range[1], resolution)
    y = np.linspace(y_range[0], y_range[1], resolution)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)

    for i in range(len(centers)):
        cx, cy = centers[i]
        r = radii[i]
        dist_sq = (X - cx) ** 2 + (Y - cy) ** 2 + 1e-6
        Z += r ** 2 / dist_sq

    # Log scale for better contour distribution
    Z_log = np.log1p(Z)
    levels = np.linspace(np.percentile(Z_log, 30), np.percentile(Z_log, 95), n_levels)

    lines = _extract_contours(X, Y, Z_log, levels.tolist(), min_length)
    return Paths(lines)


def animated_metaballs(
    n_balls: int = 4,
    n_frames: int = 20,
    threshold: float = 1.0,
    x_range: tuple[float, float] = (-5, 5),
    y_range: tuple[float, float] = (-5, 5),
    resolution: int = 200,
    speed: float = 0.3,
    seed: int | None = None,
) -> list[Paths]:
    """Generate animated metaball frames with moving centers.

    Each frame returns a separate Paths, suitable for layering or
    animation export.

    Parameters
    ----------
    n_balls : int
        Number of metaballs.
    n_frames : int
        Number of animation frames.
    threshold : float
        Contour threshold.
    x_range, y_range : tuple
        Spatial extent.
    resolution : int
        Grid resolution.
    speed : float
        Movement speed of the balls.
    seed : int, optional
        Random seed.

    Returns
    -------
    list of Paths
        One Paths per frame.
    """
    rng = np.random.default_rng(seed)

    centers = np.column_stack([
        rng.uniform(x_range[0] * 0.5, x_range[1] * 0.5, n_balls),
        rng.uniform(y_range[0] * 0.5, y_range[1] * 0.5, n_balls),
    ])
    velocities = rng.normal(0, speed, (n_balls, 2))
    radii = rng.uniform(0.8, 1.5, n_balls)

    frames = []
    for _ in range(n_frames):
        frame = metaballs(
            centers=centers, radii=radii, threshold=threshold,
            x_range=x_range, y_range=y_range, resolution=resolution,
        )
        frames.append(frame)

        # Update positions with bouncing
        centers += velocities
        for i in range(n_balls):
            if centers[i, 0] < x_range[0] or centers[i, 0] > x_range[1]:
                velocities[i, 0] *= -1
            if centers[i, 1] < y_range[0] or centers[i, 1] > y_range[1]:
                velocities[i, 1] *= -1

    return frames

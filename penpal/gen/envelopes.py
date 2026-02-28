"""Line envelope pattern generators.

Port of axifun/1 over x grids.ipynb — hyperbolic line envelopes,
diamond/star shapes from connecting interpolated boundary points.

All generators return Paths.
"""

from __future__ import annotations

import numpy as np

from penpal.core.paths import Paths


def hyperbolic(
    n_lines: int = 50,
    size: float = 5.0,
    quadrants: int = 4,
) -> Paths:
    """Generate hyperbolic 1/x line envelope in one or more quadrants.

    Draws lines connecting evenly-spaced points on two perpendicular axes,
    creating envelope curves that trace a hyperbola.

    Parameters
    ----------
    n_lines : int
        Number of lines per quadrant.
    size : float
        Extent from origin along each axis.
    quadrants : int
        How many quadrants to fill (1, 2, or 4).

    Returns
    -------
    Paths
        Line segments forming the envelope.
    """
    lines = []
    t = np.linspace(0, size, n_lines + 1)[1:]  # skip origin

    # Quadrant 1: lines from (0, t) to (t, 0)
    for i in range(n_lines):
        lines.append(np.array([[0, t[i]], [t[n_lines - 1 - i], 0]]))

    if quadrants >= 2:
        # Quadrant 2: mirror across y-axis
        for i in range(n_lines):
            lines.append(np.array([[0, t[i]], [-t[n_lines - 1 - i], 0]]))

    if quadrants >= 4:
        # Quadrants 3 & 4: mirror across x-axis
        for i in range(n_lines):
            lines.append(np.array([[0, -t[i]], [t[n_lines - 1 - i], 0]]))
        for i in range(n_lines):
            lines.append(np.array([[0, -t[i]], [-t[n_lines - 1 - i], 0]]))

    return Paths(lines)


def diamond(
    n_lines: int = 40,
    size: float = 5.0,
) -> Paths:
    """Generate a diamond/star pattern from four-axis line envelopes.

    Lines connect points on four semi-axes (±x, ±y), creating a
    diamond-shaped star pattern with hyperbolic envelope curves.

    Parameters
    ----------
    n_lines : int
        Number of lines per pair of axes.
    size : float
        Extent from origin.

    Returns
    -------
    Paths
        Line segments forming the diamond star.
    """
    return hyperbolic(n_lines=n_lines, size=size, quadrants=4)


def string_art(
    n_lines: int = 50,
    points_a: np.ndarray | None = None,
    points_b: np.ndarray | None = None,
    size: float = 5.0,
) -> Paths:
    """Generate string-art style line envelopes between two curves.

    Connects evenly-spaced points on curve A to reverse-ordered points
    on curve B, creating tangent envelopes of the resulting curves.

    Parameters
    ----------
    n_lines : int
        Number of connecting lines.
    points_a : ndarray, optional
        Points along first curve, shape (N, 2). Defaults to vertical line.
    points_b : ndarray, optional
        Points along second curve, shape (N, 2). Defaults to horizontal line.
    size : float
        Extent for default curves.

    Returns
    -------
    Paths
        Line segments forming the envelope.
    """
    t = np.linspace(0, 1, n_lines)

    if points_a is None:
        points_a = np.column_stack([np.zeros(n_lines), t * size])
    if points_b is None:
        points_b = np.column_stack([t * size, np.zeros(n_lines)])

    # Resample curves to n_lines points if needed
    if len(points_a) != n_lines:
        t_orig = np.linspace(0, 1, len(points_a))
        t_new = np.linspace(0, 1, n_lines)
        points_a = np.column_stack([
            np.interp(t_new, t_orig, points_a[:, 0]),
            np.interp(t_new, t_orig, points_a[:, 1]),
        ])
    if len(points_b) != n_lines:
        t_orig = np.linspace(0, 1, len(points_b))
        t_new = np.linspace(0, 1, n_lines)
        points_b = np.column_stack([
            np.interp(t_new, t_orig, points_b[:, 0]),
            np.interp(t_new, t_orig, points_b[:, 1]),
        ])

    lines = []
    for i in range(n_lines):
        j = n_lines - 1 - i
        lines.append(np.array([points_a[i], points_b[j]]))

    return Paths(lines)


def parabolic_envelope(
    n_lines: int = 60,
    size: float = 5.0,
    angle: float = 90.0,
) -> Paths:
    """Generate a parabolic envelope from two angled lines.

    Creates a set of line segments between two straight edges meeting
    at a corner, whose envelope traces a parabola.

    Parameters
    ----------
    n_lines : int
        Number of connecting lines.
    size : float
        Length of each edge.
    angle : float
        Angle between the two edges in degrees.

    Returns
    -------
    Paths
        Line segments forming the parabolic envelope.
    """
    rad = np.radians(angle)
    t = np.linspace(0, size, n_lines)

    # Edge 1: along x-axis
    # Edge 2: at angle from origin
    edge_a = np.column_stack([t, np.zeros(n_lines)])
    edge_b = np.column_stack([t * np.cos(rad), t * np.sin(rad)])

    lines = []
    for i in range(n_lines):
        j = n_lines - 1 - i
        lines.append(np.array([edge_a[i], edge_b[j]]))

    return Paths(lines)


def cardioid_envelope(
    n_lines: int = 80,
    radius: float = 3.0,
    multiplier: float = 2.0,
) -> Paths:
    """Generate a cardioid (or epicycloid) envelope inside a circle.

    Connects point i on a circle to point (i * multiplier) mod n,
    creating cardioid-like curves for multiplier=2, nephroids for 3, etc.

    Parameters
    ----------
    n_lines : int
        Number of points around the circle.
    radius : float
        Circle radius.
    multiplier : float
        Connection multiplier. 2 = cardioid, 3 = nephroid, etc.

    Returns
    -------
    Paths
        Line segments forming the envelope.
    """
    angles = np.linspace(0, 2 * np.pi, n_lines, endpoint=False)
    points = np.column_stack([radius * np.cos(angles), radius * np.sin(angles)])

    lines = []
    for i in range(n_lines):
        j = int(i * multiplier) % n_lines
        lines.append(np.array([points[i], points[j]]))

    return Paths(lines)

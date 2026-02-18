"""Hatching / parallel line fills for polygons.

Core shading primitives: shade any polygon with parallel lines at a given
angle and density.
"""

from __future__ import annotations

from typing import List

import numpy as np
from shapely.geometry import LineString, Polygon, MultiLineString

from penpal.core.paths import Paths
from penpal.core.types import Lines


def hatch_polygon(
    polygon: np.ndarray,
    angle: float = 0,
    spacing: float = 0.1,
    degrees: bool = True,
) -> Paths:
    """Fill a polygon with parallel hatch lines.

    Parameters
    ----------
    polygon : (N, 2) array
        Closed polygon vertices.
    angle : float
        Hatch line angle (0 = horizontal).
    spacing : float
        Distance between hatch lines.
    degrees : bool
        If True, angle is in degrees.

    Returns
    -------
    Paths
    """
    if degrees:
        angle = np.radians(angle)

    poly = Polygon(polygon[:, :2])
    if not poly.is_valid:
        poly = poly.buffer(0)
    if poly.is_empty:
        return Paths()

    # Get bounding box of the polygon
    minx, miny, maxx, maxy = poly.bounds
    cx = (minx + maxx) / 2
    cy = (miny + maxy) / 2
    diag = np.sqrt((maxx - minx) ** 2 + (maxy - miny) ** 2)

    # Generate parallel lines covering the bounding circle, then rotate
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    half = diag / 2

    lines = []
    n_lines = int(diag / spacing) + 1
    offsets = np.linspace(-half, half, n_lines)

    for offset in offsets:
        # Line perpendicular-offset from center, along angle direction
        px = cx + offset * (-sin_a)
        py = cy + offset * cos_a
        # Extend line along angle direction
        x1 = px - half * cos_a
        y1 = py - half * sin_a
        x2 = px + half * cos_a
        y2 = py + half * sin_a

        line = LineString([(x1, y1), (x2, y2)])
        clipped = line.intersection(poly)
        if clipped.is_empty:
            continue
        if isinstance(clipped, LineString):
            coords = np.array(clipped.coords, dtype=np.float64)
            if len(coords) >= 2:
                lines.append(coords)
        elif isinstance(clipped, MultiLineString):
            for seg in clipped.geoms:
                coords = np.array(seg.coords, dtype=np.float64)
                if len(coords) >= 2:
                    lines.append(coords)

    return Paths(lines) if lines else Paths()


def shade_polygon(
    polygon: np.ndarray,
    density: int = 15,
    angle: float = None,
    seed: int = None,
) -> Paths:
    """Shade a polygon with hatch lines at a random or specified angle.

    Parameters
    ----------
    polygon : (N, 2) array
    density : int
        Approximate number of hatch lines.
    angle : float, optional
        Hatch angle in degrees. If None, random.
    seed : int, optional
    """
    rng = np.random.default_rng(seed)
    if angle is None:
        angle = rng.uniform(0, 180)

    poly = Polygon(polygon[:, :2])
    if not poly.is_valid:
        poly = poly.buffer(0)
    if poly.is_empty:
        return Paths()

    minx, miny, maxx, maxy = poly.bounds
    diag = np.sqrt((maxx - minx) ** 2 + (maxy - miny) ** 2)
    spacing = diag / max(density, 1)

    return hatch_polygon(polygon, angle=angle, spacing=spacing)


def shade_triangle(a, b, c, num_lines: int = 10) -> Paths:
    """Shade a triangle with parallel lines from one edge to the opposite vertex.

    Degenerates to shade_quadrilateral by collapsing one edge to a point.
    """
    a, b, c = np.asarray(a), np.asarray(b), np.asarray(c)
    return shade_quadrilateral(a, a, b, c, num_lines)


def shade_quadrilateral(a1, b1, a2, b2, num_lines: int = 10) -> Paths:
    """Shade a quadrilateral by interpolating lines between two edges.

    Edge 1: a1 → b1
    Edge 2: a2 → b2
    Lines go from lerp(a1, b1, t) to lerp(a2, b2, t).
    """
    a1 = np.asarray(a1, dtype=np.float64)
    b1 = np.asarray(b1, dtype=np.float64)
    a2 = np.asarray(a2, dtype=np.float64)
    b2 = np.asarray(b2, dtype=np.float64)

    lines = []
    for i in range(num_lines + 1):
        t = i / max(num_lines, 1)
        p1 = a1 + t * (b1 - a1)
        p2 = a2 + t * (b2 - a2)
        lines.append(np.array([p1, p2], dtype=np.float64))
    return Paths(lines)


def parallel_lines(
    x0: float, y0: float, x1: float, y1: float,
    angle: float = 0, spacing: float = 0.1, degrees: bool = True,
) -> Paths:
    """Generate parallel lines covering a rectangle at a given angle."""
    polygon = np.array([
        [x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]
    ], dtype=np.float64)
    return hatch_polygon(polygon, angle=angle, spacing=spacing, degrees=degrees)

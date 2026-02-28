"""Concentric inset polygon fills via Shapely buffer.

Creates topographic/contour-style fills by repeatedly insetting
a polygon boundary. Works with any polygon shape.

All functions return Paths.
"""

from __future__ import annotations

import numpy as np
from shapely.geometry import Polygon as ShapelyPolygon, MultiPolygon

from penpal.core.paths import Paths


def dilate_polygon(
    polygon: np.ndarray,
    n_rings: int = 20,
    spacing: float | None = None,
    inward: bool = True,
) -> Paths:
    """Fill a polygon with concentric inset (or outset) rings.

    Parameters
    ----------
    polygon : ndarray, shape (N, 2)
        Polygon vertices.
    n_rings : int
        Number of concentric rings.
    spacing : float, optional
        Distance between rings. If None, auto-computed to fill the shape.
    inward : bool
        If True, rings go inward (shrink). If False, outward (grow).

    Returns
    -------
    Paths
        Concentric polygon rings.
    """
    poly = ShapelyPolygon(polygon)
    if not poly.is_valid:
        poly = poly.buffer(0)

    if spacing is None:
        # Estimate based on polygon size
        minx, miny, maxx, maxy = poly.bounds
        max_dim = max(maxx - minx, maxy - miny)
        spacing = max_dim / (2 * n_rings)

    lines = []
    # Original boundary
    coords = np.array(poly.exterior.coords)
    lines.append(coords)

    sign = -1 if inward else 1
    for i in range(1, n_rings + 1):
        offset = sign * spacing * i
        buffered = poly.buffer(offset)

        if buffered.is_empty:
            break

        _extract_boundaries(buffered, lines)

    return Paths(lines)


def dilate_rect(
    x0: float, y0: float, x1: float, y1: float,
    n_rings: int = 20,
    spacing: float | None = None,
) -> Paths:
    """Fill a rectangle with concentric inset rings.

    Parameters
    ----------
    x0, y0 : float
        Lower-left corner.
    x1, y1 : float
        Upper-right corner.
    n_rings : int
        Number of rings.
    spacing : float, optional
        Distance between rings. Auto-computed if None.

    Returns
    -------
    Paths
        Concentric rectangular rings.
    """
    polygon = np.array([
        [x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]
    ])
    return dilate_polygon(polygon, n_rings, spacing, inward=True)


def dilate_circle(
    center: tuple[float, float] = (0, 0),
    radius: float = 5.0,
    n_rings: int = 20,
    n_points: int = 100,
    spacing: float | None = None,
) -> Paths:
    """Fill a circle with concentric inset rings.

    Parameters
    ----------
    center : tuple
        Circle center.
    radius : float
        Circle radius.
    n_rings : int
        Number of rings.
    n_points : int
        Points per circle.
    spacing : float, optional
        Distance between rings. Auto-computed if None.

    Returns
    -------
    Paths
        Concentric circles.
    """
    if spacing is None:
        spacing = radius / n_rings

    theta = np.linspace(0, 2 * np.pi, n_points + 1)
    lines = []
    cx, cy = center

    for i in range(n_rings):
        r = radius - i * spacing
        if r <= 0:
            break
        ring = np.column_stack([cx + r * np.cos(theta), cy + r * np.sin(theta)])
        lines.append(ring)

    return Paths(lines)


def multi_dilate(
    polygon: np.ndarray,
    n_rings: int = 10,
    spacing: float | None = None,
    alternating: bool = False,
) -> list[Paths]:
    """Fill polygon with inset rings, returning each ring as separate Paths.

    Useful for assigning different colors/layers to each ring level.

    Parameters
    ----------
    polygon : ndarray, shape (N, 2)
        Polygon vertices.
    n_rings : int
        Number of rings.
    spacing : float, optional
        Ring spacing.
    alternating : bool
        If True, return two groups (even/odd rings) for two-color effects.

    Returns
    -------
    list of Paths
        Each ring as a separate Paths, or two groups if alternating.
    """
    poly = ShapelyPolygon(polygon)
    if not poly.is_valid:
        poly = poly.buffer(0)

    if spacing is None:
        minx, miny, maxx, maxy = poly.bounds
        max_dim = max(maxx - minx, maxy - miny)
        spacing = max_dim / (2 * n_rings)

    rings = []
    for i in range(n_rings):
        offset = -spacing * i
        buffered = poly.buffer(offset)
        if buffered.is_empty:
            break

        ring_lines = []
        _extract_boundaries(buffered, ring_lines)
        rings.append(Paths(ring_lines))

    if alternating:
        even = Paths([l for i, p in enumerate(rings) if i % 2 == 0 for l in p.lines])
        odd = Paths([l for i, p in enumerate(rings) if i % 2 == 1 for l in p.lines])
        return [even, odd]

    return rings


def _extract_boundaries(geom, lines):
    """Extract boundary coordinates from a Shapely geometry."""
    if isinstance(geom, MultiPolygon):
        for p in geom.geoms:
            _extract_boundaries(p, lines)
    elif hasattr(geom, 'exterior'):
        coords = np.array(geom.exterior.coords)
        if len(coords) >= 3:
            lines.append(coords)
        for interior in geom.interiors:
            coords = np.array(interior.coords)
            if len(coords) >= 3:
                lines.append(coords)

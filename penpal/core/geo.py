"""Spatial operations: clip, intersect, containment.

Numpy in, numpy out. Shapely is the hidden backend.
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np
from shapely.geometry import LineString, MultiLineString, Polygon, box

from penpal.core.types import Lines


def _lines_to_shapely(lines: Lines) -> List[LineString]:
    """Convert Lines to list of Shapely LineStrings."""
    result = []
    for line in lines:
        if len(line) >= 2:
            result.append(LineString(line[:, :2]))
    return result


def _shapely_to_lines(geom) -> Lines:
    """Convert Shapely geometry back to Lines."""
    if geom.is_empty:
        return []
    if isinstance(geom, LineString):
        coords = np.array(geom.coords, dtype=np.float64)
        return [coords] if len(coords) >= 2 else []
    if isinstance(geom, MultiLineString):
        result = []
        for ls in geom.geoms:
            coords = np.array(ls.coords, dtype=np.float64)
            if len(coords) >= 2:
                result.append(coords)
        return result
    # For GeometryCollection or other types
    result = []
    if hasattr(geom, "geoms"):
        for g in geom.geoms:
            result.extend(_shapely_to_lines(g))
    return result


def clip(lines: Lines, polygon: np.ndarray) -> Lines:
    """Clip lines to a polygon boundary. polygon is (M, 2) array of vertices."""
    poly = Polygon(polygon[:, :2])
    result = []
    for ls in _lines_to_shapely(lines):
        clipped = ls.intersection(poly)
        result.extend(_shapely_to_lines(clipped))
    return result


def clip_rect(lines: Lines, xmin: float, ymin: float, xmax: float, ymax: float) -> Lines:
    """Clip lines to an axis-aligned rectangle."""
    rect = box(xmin, ymin, xmax, ymax)
    result = []
    for ls in _lines_to_shapely(lines):
        clipped = ls.intersection(rect)
        result.extend(_shapely_to_lines(clipped))
    return result


def intersect_lines(lines_a: Lines, lines_b: Lines) -> Lines:
    """Return the intersection of two line collections."""
    from shapely.ops import unary_union

    a = unary_union(_lines_to_shapely(lines_a))
    b = unary_union(_lines_to_shapely(lines_b))
    result = a.intersection(b)
    return _shapely_to_lines(result)


def contains_points(polygon: np.ndarray, points: np.ndarray) -> np.ndarray:
    """Test which points are inside a polygon. Returns boolean array."""
    from shapely import contains_xy

    poly = Polygon(polygon[:, :2])
    return contains_xy(poly, points[:, 0], points[:, 1])

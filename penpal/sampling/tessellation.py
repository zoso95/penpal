"""Voronoi and Delaunay tessellation wrappers.

Returns polygon/triangle data ready for shading.
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np
from scipy.spatial import Voronoi, Delaunay


def voronoi(
    points: np.ndarray,
    bounds: Tuple[float, float, float, float] = None,
) -> List[np.ndarray]:
    """Compute Voronoi regions clipped to bounds.

    Parameters
    ----------
    points : (N, 2) array
        Generator points.
    bounds : (xmin, ymin, xmax, ymax), optional
        Clipping rectangle. If None, uses point extent + margin.

    Returns
    -------
    List of (M_i, 2) arrays — each a closed polygon (vertices of one Voronoi cell).
    Only finite, bounded regions are returned.
    """
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union

    if bounds is None:
        margin = max(points[:, 0].ptp(), points[:, 1].ptp()) * 0.1
        bounds = (
            points[:, 0].min() - margin,
            points[:, 1].min() - margin,
            points[:, 0].max() + margin,
            points[:, 1].max() + margin,
        )

    xmin, ymin, xmax, ymax = bounds
    clip_box = box(xmin, ymin, xmax, ymax)

    # Add mirror points to handle boundary cells
    mirrored = _mirror_points(points, bounds)
    all_pts = np.vstack([points, mirrored])

    vor = Voronoi(all_pts)

    regions = []
    for i in range(len(points)):  # only original points
        region_idx = vor.point_region[i]
        vertex_indices = vor.regions[region_idx]
        if -1 in vertex_indices or len(vertex_indices) == 0:
            continue
        verts = vor.vertices[vertex_indices]
        try:
            poly = Polygon(verts)
            clipped = poly.intersection(clip_box)
            if clipped.is_empty or clipped.area < 1e-10:
                continue
            if hasattr(clipped, 'exterior'):
                coords = np.array(clipped.exterior.coords, dtype=np.float64)
                regions.append(coords)
        except Exception:
            continue

    return regions


def _mirror_points(points: np.ndarray, bounds) -> np.ndarray:
    """Mirror points across bounds edges for clean Voronoi at boundaries."""
    xmin, ymin, xmax, ymax = bounds
    mirrored = []
    for p in points:
        x, y = p
        mirrored.append([2 * xmin - x, y])
        mirrored.append([2 * xmax - x, y])
        mirrored.append([x, 2 * ymin - y])
        mirrored.append([x, 2 * ymax - y])
    return np.array(mirrored, dtype=np.float64)


def delaunay(points: np.ndarray) -> List[np.ndarray]:
    """Compute Delaunay triangulation.

    Returns
    -------
    List of (4, 2) arrays — each a closed triangle (3 vertices + repeated first).
    """
    tri = Delaunay(points)
    triangles = []
    for simplex in tri.simplices:
        verts = points[simplex]
        # Close the triangle
        closed = np.vstack([verts, verts[0:1]])
        triangles.append(closed)
    return triangles


def voronoi_edges(
    points: np.ndarray,
    bounds: Tuple[float, float, float, float] = None,
) -> List[np.ndarray]:
    """Return Voronoi cell edges as line segments (for outline drawing).

    Returns list of (2, 2) arrays — each a line segment.
    """
    regions = voronoi(points, bounds)
    edges = []
    for region in regions:
        for i in range(len(region) - 1):
            edges.append(region[i:i+2].copy())
    return edges

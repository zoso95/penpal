"""Mirror slicing — nested zoom / Droste effect.

Creates recursive zoom effects by showing the same art at multiple scales,
clipped to nested boundary shapes (concentric circles or rectangles).

    from penpal.symmetry import mirror_slice

    droste = mirror_slice(art, center=(0,0), n_levels=5,
                          outer_r=4.0, inner_r=0.5, zoom_factor=1.8)
"""

from __future__ import annotations

import numpy as np

from penpal.core.paths import Paths
from penpal.core.types import Lines


def mirror_slice(
    paths: Paths,
    center=(0, 0),
    radii: list = None,
    n_levels: int = 5,
    outer_r: float = 4.0,
    inner_r: float = 0.5,
    zoom_factor: float = 1.5,
    zoom_center=None,
    draw_boundaries: bool = True,
    boundary_points: int = 128,
) -> Paths:
    """Circular nested zoom (Droste effect with concentric circle boundaries).

    Parameters
    ----------
    paths : Paths
        The art to recursively zoom into.
    center : tuple
        Center of the nesting circles.
    radii : list, optional
        Explicit circle radii from outer to inner. Overrides n_levels.
    n_levels : int
        Number of nesting levels (if radii not given).
    outer_r, inner_r : float
        Outermost and innermost radii (if radii not given).
    zoom_factor : float
        Scale multiplier per level. Level k is scaled by zoom_factor^k.
    zoom_center : tuple, optional
        Center of the zoom transform. Defaults to center.
    draw_boundaries : bool
        If True, include circle outlines in the output.
    boundary_points : int
        Number of points per boundary circle.
    """
    if radii is None:
        radii = list(np.geomspace(outer_r, inner_r, n_levels))
    if zoom_center is None:
        zoom_center = center

    result = Paths()

    for k in range(len(radii)):
        # Scale art by zoom_factor^k centered on zoom_center
        zoomed = paths.scale(zoom_factor ** k, center=zoom_center)

        if k < len(radii) - 1:
            # Clip to annular region between radii[k] and radii[k+1]
            region = _annulus(center, radii[k], radii[k + 1], boundary_points)
        else:
            # Innermost level: clip to full circle (no hole)
            region = _circle_shapely(center, radii[k], boundary_points)

        clipped = Paths(_clip_to_region(zoomed.lines, region))
        result = result + clipped

    if draw_boundaries:
        from penpal.gen.curves import circle
        for r in radii:
            result = result + circle(center=center, radius=r,
                                     num_points=boundary_points)

    return result


def mirror_slice_rect(
    paths: Paths,
    center=(0, 0),
    sizes: list = None,
    n_levels: int = 5,
    outer_size=(8.0, 8.0),
    inner_size=(1.0, 1.0),
    zoom_factor: float = 1.5,
    zoom_center=None,
    draw_boundaries: bool = True,
) -> Paths:
    """Rectangular nested zoom (Droste effect with nested rectangle boundaries).

    Parameters
    ----------
    paths : Paths
        The art to recursively zoom into.
    center : tuple
        Center of the nesting rectangles.
    sizes : list of (width, height), optional
        Explicit sizes from outer to inner. Overrides n_levels.
    n_levels : int
        Number of nesting levels.
    outer_size, inner_size : tuple
        (width, height) of outermost and innermost rectangles.
    zoom_factor : float
        Scale multiplier per level.
    zoom_center : tuple, optional
        Center of the zoom. Defaults to center.
    draw_boundaries : bool
        If True, include rectangle outlines.
    """
    if sizes is None:
        widths = np.geomspace(outer_size[0], inner_size[0], n_levels)
        heights = np.geomspace(outer_size[1], inner_size[1], n_levels)
        sizes = list(zip(widths, heights))
    if zoom_center is None:
        zoom_center = center

    result = Paths()

    for k in range(len(sizes)):
        zoomed = paths.scale(zoom_factor ** k, center=zoom_center)

        if k < len(sizes) - 1:
            region = _rect_annulus(center, sizes[k], sizes[k + 1])
        else:
            region = _rect_shapely(center, sizes[k])

        clipped = Paths(_clip_to_region(zoomed.lines, region))
        result = result + clipped

    if draw_boundaries:
        for w, h in sizes:
            result = result + _rect_outline(center, w, h)

    return result


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _clip_to_region(lines: Lines, shapely_geom) -> Lines:
    """Clip lines to any Shapely geometry (supports holes)."""
    from penpal.core.geo import _lines_to_shapely, _shapely_to_lines

    result = []
    for ls in _lines_to_shapely(lines):
        clipped = ls.intersection(shapely_geom)
        result.extend(_shapely_to_lines(clipped))
    return result


def _circle_coords(center, radius, n_points=128):
    """Generate circle polygon coordinates."""
    cx, cy = center
    t = np.linspace(0, 2 * np.pi, n_points + 1)
    return np.column_stack([cx + radius * np.cos(t), cy + radius * np.sin(t)])


def _circle_shapely(center, radius, n_points=128):
    """Create a Shapely Polygon for a circle."""
    from shapely.geometry import Polygon
    return Polygon(_circle_coords(center, radius, n_points))


def _annulus(center, outer_r, inner_r, n_points=128):
    """Create a Shapely annular polygon (circle with hole)."""
    from shapely.geometry import Polygon
    outer = Polygon(_circle_coords(center, outer_r, n_points))
    inner = Polygon(_circle_coords(center, inner_r, n_points))
    return outer.difference(inner)


def _rect_coords(center, width, height):
    """Generate rectangle polygon coordinates."""
    cx, cy = center
    hw, hh = width / 2, height / 2
    return np.array([
        [cx - hw, cy - hh], [cx + hw, cy - hh],
        [cx + hw, cy + hh], [cx - hw, cy + hh],
        [cx - hw, cy - hh],
    ], dtype=np.float64)


def _rect_shapely(center, size):
    """Create a Shapely Polygon for a rectangle."""
    from shapely.geometry import Polygon
    return Polygon(_rect_coords(center, size[0], size[1]))


def _rect_annulus(center, outer_size, inner_size):
    """Create a Shapely rectangle with rectangular hole."""
    outer = _rect_shapely(center, outer_size)
    inner = _rect_shapely(center, inner_size)
    return outer.difference(inner)


def _rect_outline(center, width, height):
    """Generate rectangle outline as Paths."""
    return Paths([_rect_coords(center, width, height)])

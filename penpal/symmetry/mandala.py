"""Radial symmetry: cyclic (C_n) and dihedral (D_n) groups.

Common in mandala and rosette plotter art patterns.

    from penpal.symmetry import cyclic, dihedral

    # 6-fold snowflake symmetry
    mandala = dihedral(wedge_art, n=6, center=(0, 0))
"""

from __future__ import annotations

import numpy as np

from penpal.core.paths import Paths


def cyclic(paths: Paths, n: int, center=(0, 0)) -> Paths:
    """Apply n-fold rotational symmetry (cyclic group C_n).

    Rotates the input paths by 360/n degrees n times, combining all copies.

    Parameters
    ----------
    paths : Paths
        The "wedge" to replicate.
    n : int
        Number of rotational copies (e.g., 6 for hexagonal).
    center : tuple
        Center of rotation.
    """
    from penpal.core.transforms import rotate

    result = Paths()
    step = 360.0 / n
    for i in range(n):
        result = result + paths.transform(rotate(i * step, center=center))
    return result


def dihedral(paths: Paths, n: int, center=(0, 0),
             reflection_angle: float = 0) -> Paths:
    """Apply dihedral symmetry D_n (n rotations + n reflections).

    Reflects paths across a line through center at reflection_angle,
    then applies n-fold rotation to both original and reflected copies.
    Produces 2*n copies.

    Parameters
    ----------
    paths : Paths
        Fundamental domain (a wedge of angle pi/n).
    n : int
        Order of the dihedral group.
    center : tuple
        Center of symmetry.
    reflection_angle : float
        Angle of the first mirror line, in degrees.
    """
    from penpal.core.transforms import reflect

    reflected = paths.transform(reflect(reflection_angle, point=center))
    both = paths + reflected
    return cyclic(both, n, center=center)


def radial_repeat(paths: Paths, n: int, center=(0, 0),
                  clip_wedge: bool = False,
                  inner_r: float = 0, outer_r: float = None) -> Paths:
    """Repeat paths radially with optional clipping to a wedge/annulus.

    If clip_wedge=True, clips the input to a sector of angle 2*pi/n
    before replicating. Optionally bounded by inner_r and outer_r.

    Parameters
    ----------
    paths : Paths
        Input art.
    n : int
        Number of repetitions.
    center : tuple
        Center of rotation.
    clip_wedge : bool
        If True, clip to fundamental wedge before replicating.
    inner_r, outer_r : float
        Annular bounds (only used if clip_wedge=True).
    """
    if clip_wedge:
        wedge = _wedge_polygon(center, n, inner_r, outer_r)
        paths = paths.clip(wedge)
    return cyclic(paths, n, center=center)


def _wedge_polygon(center, n, inner_r=0, outer_r=None, num_arc_pts=64):
    """Build a sector polygon for clipping: from angle 0 to 2*pi/n."""
    cx, cy = center
    angle = 2 * np.pi / n

    if outer_r is None:
        outer_r = 1e6  # effectively infinite

    t_outer = np.linspace(0, angle, num_arc_pts)
    outer_pts = np.column_stack([
        cx + outer_r * np.cos(t_outer),
        cy + outer_r * np.sin(t_outer),
    ])

    if inner_r > 0:
        t_inner = np.linspace(angle, 0, num_arc_pts)
        inner_pts = np.column_stack([
            cx + inner_r * np.cos(t_inner),
            cy + inner_r * np.sin(t_inner),
        ])
        polygon = np.vstack([outer_pts, inner_pts, outer_pts[:1]])
    else:
        polygon = np.vstack([[[cx, cy]], outer_pts, [[cx, cy]]])

    return polygon

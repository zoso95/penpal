"""Tests for penpal.symmetry.mandala."""

import numpy as np
import pytest

from penpal.core.paths import Paths
from penpal.symmetry.mandala import cyclic, dihedral, radial_repeat


def _point_paths(x, y):
    """Helper: single-point Paths at (x, y)."""
    return Paths([np.array([[x, y]])])


def _line_paths():
    """Helper: a line from (1,0) to (2,0)."""
    return Paths([np.array([[1, 0], [2, 0]])])


class TestCyclic:
    def test_identity(self):
        p = _line_paths()
        result = cyclic(p, n=1)
        assert len(result) == 1

    def test_cyclic_4_line_count(self):
        p = _line_paths()
        result = cyclic(p, n=4)
        assert len(result) == 4

    def test_cyclic_4_positions(self):
        p = _point_paths(1, 0)
        result = cyclic(p, n=4, center=(0, 0))
        points = np.array([l[0] for l in result.lines])
        expected = np.array([[1, 0], [0, 1], [-1, 0], [0, -1]])
        np.testing.assert_allclose(np.sort(points, axis=0),
                                   np.sort(expected, axis=0), atol=1e-10)

    def test_cyclic_preserves_original(self):
        p = _line_paths()
        original_pt = p.lines[0][0].copy()
        _ = cyclic(p, n=6)
        np.testing.assert_allclose(p.lines[0][0], original_pt)

    def test_cyclic_6(self):
        p = Paths([np.array([[1, 0], [1.5, 0.2]])])
        result = cyclic(p, n=6)
        assert len(result) == 6


class TestDihedral:
    def test_dihedral_1_doubles(self):
        p = _line_paths()
        result = dihedral(p, n=1)
        assert len(result) == 2

    def test_dihedral_6_produces_12(self):
        p = _line_paths()
        result = dihedral(p, n=6)
        assert len(result) == 12

    def test_dihedral_4_symmetry(self):
        """D_4 result should be invariant under 90° rotation."""
        p = _point_paths(1, 0.1)
        result = dihedral(p, n=4, center=(0, 0))
        rotated = result.rotate(90, center=(0, 0))
        # Same set of points (sorted)
        pts_orig = np.sort(np.array([l[0] for l in result.lines]), axis=0)
        pts_rot = np.sort(np.array([l[0] for l in rotated.lines]), axis=0)
        np.testing.assert_allclose(pts_orig, pts_rot, atol=1e-10)


class TestRadialRepeat:
    def test_without_clipping_equals_cyclic(self):
        p = _line_paths()
        rr = radial_repeat(p, n=4, center=(0, 0))
        cy = cyclic(p, n=4, center=(0, 0))
        assert len(rr) == len(cy)

    def test_with_clipping(self):
        # A line clearly inside the first wedge (positive x and y quadrant)
        p = Paths([np.array([[0.5, 0.1], [2, 0.5]])])
        result = radial_repeat(p, n=4, center=(0, 0),
                               clip_wedge=True, outer_r=3)
        # Should produce 4 copies (one per wedge)
        assert len(result) == 4

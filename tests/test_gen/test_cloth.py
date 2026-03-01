"""Tests for penpal.gen.cloth."""

import numpy as np
import pytest

from penpal.gen.cloth import (
    drape, drape_linear, braid, perspective_drape, cloth_fill,
    _cardinal_spline, _smooth_1d,
)
from penpal.core.paths import Paths


# --- Helper curves ---

def _line_curve(p1, p2, n=20):
    """Simple straight-line boundary curve."""
    t = np.linspace(0, 1, n).reshape(-1, 1)
    return np.asarray(p1) + t * (np.asarray(p2) - np.asarray(p1))


def _arc_curve(center, radius, start, end, n=50):
    """Arc boundary curve."""
    theta = np.linspace(start, end, n)
    return np.column_stack([
        center[0] + radius * np.cos(theta),
        center[1] + radius * np.sin(theta),
    ])


class TestCardinalSpline:
    def test_basic_output(self):
        pts = np.array([[0, 0], [1, 1], [2, 0], [3, 1]], dtype=float)
        result = _cardinal_spline(pts)
        assert len(result) > len(pts)
        assert result.shape[1] == 2

    def test_two_points(self):
        pts = np.array([[0, 0], [1, 1]], dtype=float)
        result = _cardinal_spline(pts, n_per_segment=10)
        assert len(result) == 10

    def test_single_point(self):
        pts = np.array([[0, 0]], dtype=float)
        result = _cardinal_spline(pts)
        assert len(result) == 1

    def test_passes_through_control_points(self):
        pts = np.array([[0, 0], [1, 2], [3, 1], [4, 3]], dtype=float)
        result = _cardinal_spline(pts, n_per_segment=20)
        # First and last control points should be in result
        np.testing.assert_allclose(result[0], pts[0], atol=1e-10)
        np.testing.assert_allclose(result[-1], pts[-1], atol=1e-10)


class TestSmooth1D:
    def test_identity_for_window_1(self):
        sig = np.array([1, 2, 3, 4, 5], dtype=float)
        result = _smooth_1d(sig, 1)
        np.testing.assert_array_equal(result, sig)

    def test_smoothing(self):
        sig = np.array([0, 10, 0, 10, 0], dtype=float)
        result = _smooth_1d(sig, 3)
        # Should reduce variance
        assert np.std(result) < np.std(sig)


class TestDrape:
    def test_returns_paths(self):
        a = _line_curve([0, 0], [10, 0])
        b = _line_curve([0, 2], [10, 2])
        result = drape(a, b, n_curves=20, seed=42)
        assert isinstance(result, Paths)
        assert len(result) == 20

    def test_deterministic_with_seed(self):
        a = _line_curve([0, 0], [10, 0])
        b = _line_curve([0, 2], [10, 2])
        r1 = drape(a, b, n_curves=10, seed=42)
        r2 = drape(a, b, n_curves=10, seed=42)
        for l1, l2 in zip(r1.lines, r2.lines):
            np.testing.assert_array_equal(l1, l2)

    def test_different_seeds_differ(self):
        a = _line_curve([0, 0], [10, 0])
        b = _line_curve([0, 2], [10, 2])
        r1 = drape(a, b, n_curves=5, seed=1)
        r2 = drape(a, b, n_curves=5, seed=2)
        # At least one curve should differ
        differs = any(
            not np.allclose(l1, l2)
            for l1, l2 in zip(r1.lines, r2.lines)
        )
        assert differs

    def test_no_spline(self):
        a = _line_curve([0, 0], [10, 0])
        b = _line_curve([0, 2], [10, 2])
        result = drape(a, b, n_curves=5, spline=False, seed=42)
        assert isinstance(result, Paths)
        assert len(result) == 5

    def test_curved_boundaries(self):
        a = _arc_curve([5, 0], 3, 0, np.pi)
        b = _arc_curve([5, 0], 5, 0, np.pi)
        result = drape(a, b, n_curves=15, seed=42)
        assert len(result) == 15


class TestDrapeLinear:
    def test_basic(self):
        result = drape_linear((-5, 0), (5, 0), offset=(0, 2),
                              n_curves=20, seed=42)
        assert isinstance(result, Paths)
        assert len(result) == 20

    def test_with_shrinkage(self):
        result = drape_linear((-5, 0), (5, 0), offset=(0, 2),
                              shrinkage=0.1, n_curves=10, seed=42)
        assert len(result) == 10


class TestBraid:
    def test_returns_list_of_paths(self):
        a = _line_curve([0, 0], [10, 0])
        b = _line_curve([0, 3], [10, 3])
        result = braid(a, b, n_strands=3, n_curves_per_strand=10, seed=42)
        assert isinstance(result, list)
        assert len(result) == 3
        for strand in result:
            assert isinstance(strand, Paths)
            assert len(strand) == 10

    def test_deterministic(self):
        a = _line_curve([0, 0], [10, 0])
        b = _line_curve([0, 3], [10, 3])
        r1 = braid(a, b, n_strands=2, n_curves_per_strand=5, seed=42)
        r2 = braid(a, b, n_strands=2, n_curves_per_strand=5, seed=42)
        for s1, s2 in zip(r1, r2):
            for l1, l2 in zip(s1.lines, s2.lines):
                np.testing.assert_array_equal(l1, l2)


class TestPerspectiveDrape:
    def test_returns_paths(self):
        base = _line_curve([0, 0], [10, 0], n=50)
        result = perspective_drape(base, dy=4, n_curves=20, seed=42)
        assert isinstance(result, Paths)
        assert len(result) == 20

    def test_all_2d(self):
        base = _line_curve([0, 0], [10, 0], n=50)
        result = perspective_drape(base, dy=4, n_curves=10, seed=42)
        for line in result.lines:
            assert line.shape[1] == 2

    def test_deterministic(self):
        base = _line_curve([0, 0], [10, 0], n=50)
        r1 = perspective_drape(base, dy=4, n_curves=5, seed=42)
        r2 = perspective_drape(base, dy=4, n_curves=5, seed=42)
        for l1, l2 in zip(r1.lines, r2.lines):
            np.testing.assert_array_equal(l1, l2)


class TestClothFill:
    def test_returns_paths(self):
        a = _line_curve([0, 0], [10, 0])
        b = _line_curve([0, 2], [10, 2])
        result = cloth_fill(a, b, n_curves=15)
        assert isinstance(result, Paths)
        # n_curves + 2 boundaries
        assert len(result) == 17

    def test_cosine_easing(self):
        a = _line_curve([0, 0], [10, 0])
        b = _line_curve([0, 2], [10, 2])
        result = cloth_fill(a, b, n_curves=10, easing="cosine")
        assert len(result) == 12

    def test_with_noise(self):
        a = _line_curve([0, 0], [10, 0])
        b = _line_curve([0, 2], [10, 2])
        result = cloth_fill(a, b, n_curves=10, noise_amp=0.1, seed=42)
        assert len(result) == 12

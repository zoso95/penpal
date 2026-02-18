"""Tests for penpal.gen.curves."""

import numpy as np
import pytest

from penpal.gen.curves import (
    circle, spiral, polygon_regular, rose, lissajous, hilbert, concentric_circles,
)
from penpal.core.paths import Paths


class TestCircle:
    def test_returns_paths(self):
        c = circle()
        assert isinstance(c, Paths)
        assert len(c) == 1

    def test_center_and_radius(self):
        c = circle(center=(5, 5), radius=2, num_points=360)
        pts = c.lines[0]
        # All points should be ~2 from center
        dists = np.sqrt((pts[:, 0] - 5) ** 2 + (pts[:, 1] - 5) ** 2)
        np.testing.assert_allclose(dists, 2.0, atol=1e-3)

    def test_closed(self):
        c = circle()
        pts = c.lines[0]
        np.testing.assert_allclose(pts[0], pts[-1], atol=1e-10)


class TestSpiral:
    def test_returns_paths(self):
        s = spiral()
        assert isinstance(s, Paths)
        assert len(s) == 1

    def test_radius_range(self):
        s = spiral(inner_r=1.0, outer_r=5.0, num_points=100)
        pts = s.lines[0]
        dists = np.sqrt(pts[:, 0] ** 2 + pts[:, 1] ** 2)
        assert dists[0] == pytest.approx(1.0, abs=0.1)
        assert dists[-1] == pytest.approx(5.0, abs=0.1)


class TestPolygonRegular:
    def test_hexagon(self):
        p = polygon_regular(n_sides=6)
        assert isinstance(p, Paths)
        assert p.lines[0].shape[0] == 7  # 6 sides + close

    def test_triangle(self):
        p = polygon_regular(n_sides=3)
        assert p.lines[0].shape[0] == 4


class TestRose:
    def test_returns_paths(self):
        r = rose(k=5)
        assert isinstance(r, Paths)
        assert len(r) == 1


class TestLissajous:
    def test_returns_paths(self):
        l = lissajous()
        assert isinstance(l, Paths)
        assert len(l) == 1


class TestHilbert:
    def test_order_2(self):
        h = hilbert(order=2)
        assert isinstance(h, Paths)
        assert h.lines[0].shape[0] == 16  # 2^2 * 2^2

    def test_fills_space(self):
        h = hilbert(order=3, size=1.0)
        pts = h.lines[0]
        assert pts[:, 0].min() >= 0
        assert pts[:, 0].max() <= 1
        assert pts[:, 1].min() >= 0
        assert pts[:, 1].max() <= 1


class TestConcentricCircles:
    def test_returns_paths(self):
        c = concentric_circles(n_rings=5)
        assert isinstance(c, Paths)
        assert len(c) == 5

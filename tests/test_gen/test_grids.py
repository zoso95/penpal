"""Tests for penpal.gen.grids."""

import numpy as np
import pytest

from penpal.gen.grids import grid, distorted_grid, barrel_distortion
from penpal.core.paths import Paths


class TestGrid:
    def test_returns_paths(self):
        g = grid()
        assert isinstance(g, Paths)

    def test_line_count(self):
        g = grid(0, 0, 2, 2, spacing=1)
        # 3 vertical + 3 horizontal = 6
        assert len(g) == 6

    def test_bounds(self):
        g = grid(0, 0, 8, 10, spacing=1)
        xmin, ymin, xmax, ymax = g.bounds()
        assert xmin == 0
        assert ymin == 0
        assert xmax == 8
        assert ymax == 10


class TestDistortedGrid:
    def test_returns_paths(self):
        g = distorted_grid(seed=42)
        assert isinstance(g, Paths)

    def test_deterministic(self):
        g1 = distorted_grid(seed=42)
        g2 = distorted_grid(seed=42)
        np.testing.assert_allclose(g1.lines[0], g2.lines[0])


class TestBarrelDistortion:
    def test_returns_paths(self):
        g = barrel_distortion()
        assert isinstance(g, Paths)

"""Tests for penpal.symmetry.wallpaper."""

import numpy as np
import pytest

from penpal.core.paths import Paths
from penpal.symmetry.wallpaper import WallpaperGroup


def _diagonal_line():
    """A simple diagonal line from origin to (0.5, 0.5)."""
    return Paths([np.array([[0.1, 0.1], [0.4, 0.4]])])


class TestLatticeClassification:
    def test_square(self):
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        assert wg.shape == "square"

    def test_rectangle(self):
        wg = WallpaperGroup((0, 0), (0, 2), (1, 0))
        assert wg.shape == "rectangle"

    def test_rhombus(self):
        wg = WallpaperGroup((0, 0), (0.5, 0.866), (0.5, -0.866))
        assert wg.shape == "rhombus"

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            WallpaperGroup((0, 0), (0, 2), (1.5, 0.5))

    def test_valid_patterns_square(self):
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        assert len(wg.valid_patterns) == 8

    def test_valid_patterns_rectangle(self):
        wg = WallpaperGroup((0, 0), (0, 2), (1, 0))
        assert "442" not in wg.valid_patterns

    def test_center(self):
        wg = WallpaperGroup((0, 0), (0, 2), (2, 0))
        np.testing.assert_allclose(wg.center, [1, 1])

    def test_with_offset_origin(self):
        wg = WallpaperGroup((5, 5), (0, 1), (1, 0))
        np.testing.assert_allclose(wg.center, [5.5, 5.5])


class TestFundamentalDomain:
    def test_domain_o_is_full_cell(self):
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        domain = wg.fundamental_domain("o")
        assert len(domain) == 4  # 4 corners

    def test_domain_442_is_quarter(self):
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        domain = wg.fundamental_domain("442")
        assert len(domain) == 4

    def test_domain_star442_is_triangle(self):
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        domain = wg.fundamental_domain("*442")
        assert len(domain) == 3  # triangle

    def test_invalid_pattern_raises(self):
        wg = WallpaperGroup((0, 0), (0, 2), (1, 0))  # rectangle
        with pytest.raises(ValueError):
            wg.fundamental_domain("442")  # not valid for rectangle

    def test_domain_inside_cell(self):
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        for pattern in wg.valid_patterns:
            domain = wg.fundamental_domain(pattern)
            assert np.all(domain >= -1e-10)
            assert np.all(domain <= 1 + 1e-10)


class TestComplete:
    def test_pattern_o(self):
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        p = _diagonal_line()
        result = wg.complete(p, "o")
        assert len(result) == 1

    def test_pattern_2222_doubles(self):
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        p = _diagonal_line()
        result = wg.complete(p, "2222")
        assert len(result) == 2

    def test_pattern_442_quadruples(self):
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        p = _diagonal_line()
        result = wg.complete(p, "442")
        assert len(result) == 4

    def test_pattern_star2222_quadruples(self):
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        p = _diagonal_line()
        result = wg.complete(p, "*2222")
        assert len(result) == 4

    def test_pattern_star442_octuples(self):
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        p = _diagonal_line()
        result = wg.complete(p, "*442")
        assert len(result) == 8

    def test_pattern_4star2_octuples(self):
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        p = _diagonal_line()
        result = wg.complete(p, "4*2")
        assert len(result) == 8

    def test_pattern_2star22_quadruples(self):
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        p = _diagonal_line()
        result = wg.complete(p, "2*22")
        assert len(result) == 4

    def test_all_square_patterns_nonempty(self):
        """Smoke test: all 8 square patterns produce non-empty output."""
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        p = _diagonal_line()
        for pattern in wg.valid_patterns:
            result = wg.complete(p, pattern)
            assert len(result) > 0, f"Pattern {pattern} produced empty output"


class TestTile:
    def test_tile_count(self):
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        p = _diagonal_line()
        cell = wg.complete(p, "o")
        tiled = wg.tile(cell, nx=3, ny=3)
        assert len(tiled) == 9  # 3x3 tiles, 1 line each

    def test_tile_with_bounds(self):
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        p = _diagonal_line()
        cell = wg.complete(p, "o")
        tiled = wg.tile(cell, nx=5, ny=5, bounds=(0, 0, 3, 3))
        # All points within bounds
        for line in tiled.lines:
            assert np.all(line[:, 0] >= -0.01)
            assert np.all(line[:, 0] <= 3.01)
            assert np.all(line[:, 1] >= -0.01)
            assert np.all(line[:, 1] <= 3.01)


class TestGenerate:
    def test_end_to_end(self):
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        # Art that spans more than the fundamental domain
        art = Paths([np.array([[0, 0], [1, 1]])])
        for pattern in wg.valid_patterns:
            result = wg.generate(art, pattern, nx=2, ny=2)
            assert len(result) > 0, f"generate() empty for {pattern}"

    def test_generate_without_clipping(self):
        wg = WallpaperGroup((0, 0), (0, 1), (1, 0))
        p = _diagonal_line()
        result = wg.generate(p, "442", nx=2, ny=2, clip_to_domain=False)
        assert len(result) > 0

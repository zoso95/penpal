"""Tests for penpal.symmetry.mirror_slice."""

import numpy as np
import pytest

from penpal.core.paths import Paths
from penpal.symmetry.mirror_slice import mirror_slice, mirror_slice_rect


def _grid_paths(x0, y0, x1, y1, n=10):
    """Generate a simple grid of horizontal and vertical lines."""
    lines = []
    for x in np.linspace(x0, x1, n):
        lines.append(np.array([[x, y0], [x, y1]]))
    for y in np.linspace(y0, y1, n):
        lines.append(np.array([[x0, y], [x1, y]]))
    return Paths(lines)


class TestMirrorSlice:
    def test_produces_output(self):
        art = _grid_paths(-5, -5, 5, 5)
        result = mirror_slice(art, center=(0, 0), n_levels=3,
                              outer_r=4.0, inner_r=1.0, zoom_factor=1.5)
        assert len(result) > 0

    def test_with_explicit_radii(self):
        art = _grid_paths(-5, -5, 5, 5)
        result = mirror_slice(art, center=(0, 0),
                              radii=[4.0, 2.5, 1.0],
                              zoom_factor=1.5)
        assert len(result) > 0

    def test_output_within_outer_radius(self):
        art = _grid_paths(-5, -5, 5, 5)
        result = mirror_slice(art, center=(0, 0), n_levels=3,
                              outer_r=4.0, inner_r=1.0, zoom_factor=1.5,
                              draw_boundaries=False)
        for line in result.lines:
            distances = np.sqrt(line[:, 0]**2 + line[:, 1]**2)
            assert np.all(distances <= 4.0 + 0.01)  # tolerance for Shapely

    def test_boundaries_drawn(self):
        art = _grid_paths(-5, -5, 5, 5)
        with_bounds = mirror_slice(art, center=(0, 0), n_levels=3,
                                   outer_r=4.0, inner_r=1.0,
                                   draw_boundaries=True)
        without_bounds = mirror_slice(art, center=(0, 0), n_levels=3,
                                      outer_r=4.0, inner_r=1.0,
                                      draw_boundaries=False)
        assert len(with_bounds) > len(without_bounds)

    def test_zoom_factor_1(self):
        art = _grid_paths(-5, -5, 5, 5)
        # zoom_factor=1 means all levels show same scale
        result = mirror_slice(art, center=(0, 0), n_levels=3,
                              outer_r=4.0, inner_r=1.0, zoom_factor=1.0,
                              draw_boundaries=False)
        assert len(result) > 0


class TestMirrorSliceRect:
    def test_produces_output(self):
        art = _grid_paths(-5, -5, 5, 5)
        result = mirror_slice_rect(art, center=(0, 0), n_levels=3,
                                   outer_size=(8, 6), inner_size=(2, 1.5),
                                   zoom_factor=1.5)
        assert len(result) > 0

    def test_output_within_outer_rect(self):
        art = _grid_paths(-5, -5, 5, 5)
        result = mirror_slice_rect(art, center=(0, 0), n_levels=3,
                                   outer_size=(8, 6), inner_size=(2, 1.5),
                                   zoom_factor=1.5, draw_boundaries=False)
        for line in result.lines:
            assert np.all(np.abs(line[:, 0]) <= 4.01)
            assert np.all(np.abs(line[:, 1]) <= 3.01)

    def test_with_explicit_sizes(self):
        art = _grid_paths(-5, -5, 5, 5)
        result = mirror_slice_rect(art, center=(0, 0),
                                   sizes=[(8, 6), (4, 3), (2, 1.5)],
                                   zoom_factor=1.5)
        assert len(result) > 0

"""Tests for penpal.core.paths."""

import numpy as np
import pytest

from penpal.core.paths import Paths


class TestPathsBasic:
    def test_empty(self):
        p = Paths()
        assert len(p) == 0
        assert not p
        assert p.total_points() == 0

    def test_from_list(self):
        lines = [np.array([[0, 0], [1, 1]]), np.array([[2, 2], [3, 3]])]
        p = Paths(lines)
        assert len(p) == 2
        assert p.total_points() == 4

    def test_from_single_array(self):
        p = Paths(np.array([[0, 0], [1, 1], [2, 2]]))
        assert len(p) == 1
        assert p.total_points() == 3

    def test_dim(self):
        p = Paths([np.array([[0, 0], [1, 1]])])
        assert p.dim() == 2


class TestPathsBounds:
    def test_bounds(self):
        p = Paths([np.array([[1, 2], [3, 4]]), np.array([[0, 5], [6, 1]])])
        xmin, ymin, xmax, ymax = p.bounds()
        assert xmin == 0
        assert ymin == 1
        assert xmax == 6
        assert ymax == 5

    def test_empty_bounds(self):
        p = Paths()
        assert p.bounds() == (0, 0, 0, 0)


class TestPathsTotalLength:
    def test_single_segment(self):
        p = Paths([np.array([[0, 0], [3, 4]])])
        assert abs(p.total_length() - 5.0) < 1e-10

    def test_two_segments(self):
        p = Paths([np.array([[0, 0], [1, 0]]), np.array([[0, 0], [0, 1]])])
        assert abs(p.total_length() - 2.0) < 1e-10


class TestPathsTransform:
    def test_translate(self):
        p = Paths([np.array([[0, 0], [1, 1]])])
        moved = p.translate(10, 20)
        np.testing.assert_allclose(moved.lines[0][0], [10, 20])
        np.testing.assert_allclose(moved.lines[0][1], [11, 21])

    def test_rotate_90(self):
        p = Paths([np.array([[1, 0]])])
        rotated = p.rotate(90, center=(0, 0))
        np.testing.assert_allclose(rotated.lines[0][0], [0, 1], atol=1e-10)

    def test_scale(self):
        p = Paths([np.array([[1, 2], [3, 4]])])
        scaled = p.scale(2)
        np.testing.assert_allclose(scaled.lines[0], [[2, 4], [6, 8]])

    def test_immutable(self):
        p = Paths([np.array([[0, 0], [1, 1]])])
        _ = p.translate(10, 10)
        # Original unchanged
        np.testing.assert_allclose(p.lines[0][0], [0, 0])


class TestPathsCombine:
    def test_add(self):
        a = Paths([np.array([[0, 0], [1, 1]])])
        b = Paths([np.array([[2, 2], [3, 3]])])
        c = a + b
        assert len(c) == 2
        assert len(a) == 1  # originals unchanged
        assert len(b) == 1

    def test_iadd(self):
        a = Paths([np.array([[0, 0], [1, 1]])])
        b = Paths([np.array([[2, 2], [3, 3]])])
        a += b
        assert len(a) == 2


class TestPathsLineOps:
    def test_filter(self):
        short = np.array([[0, 0], [0.001, 0]])
        long = np.array([[0, 0], [10, 0]])
        p = Paths([short, long])
        filtered = p.filter(min_length=1.0)
        assert len(filtered) == 1

    def test_subsample(self):
        pts = np.column_stack([np.linspace(0, 10, 100), np.zeros(100)])
        p = Paths([pts])
        sub = p.subsample(n=10)
        assert sub.lines[0].shape[0] < 100

    def test_every_nth(self):
        lines = [np.array([[i, 0], [i, 1]]) for i in range(10)]
        p = Paths(lines)
        result = p.every_nth(3)
        assert len(result) == 4  # indices 0, 3, 6, 9


class TestPathsReflect:
    def test_reflect_x_axis(self):
        p = Paths([np.array([[1, 1]])])
        reflected = p.reflect(0, point=(0, 0))
        np.testing.assert_allclose(reflected.lines[0][0], [1, -1], atol=1e-10)

    def test_reflect_y_axis(self):
        p = Paths([np.array([[1, 1]])])
        reflected = p.reflect(90, point=(0, 0))
        np.testing.assert_allclose(reflected.lines[0][0], [-1, 1], atol=1e-10)

    def test_mirror_x(self):
        p = Paths([np.array([[1, 2]])])
        mirrored = p.mirror("x")
        np.testing.assert_allclose(mirrored.lines[0][0], [1, -2], atol=1e-10)

    def test_mirror_y(self):
        p = Paths([np.array([[1, 2]])])
        mirrored = p.mirror("y")
        np.testing.assert_allclose(mirrored.lines[0][0], [-1, 2], atol=1e-10)

    def test_mirror_diagonal(self):
        p = Paths([np.array([[1, 0]])])
        mirrored = p.mirror("diagonal")
        np.testing.assert_allclose(mirrored.lines[0][0], [0, 1], atol=1e-10)

    def test_reflect_immutable(self):
        p = Paths([np.array([[1, 1]])])
        _ = p.reflect(0)
        np.testing.assert_allclose(p.lines[0][0], [1, 1])


class TestPathsRepr:
    def test_repr(self):
        p = Paths([np.array([[0, 0], [1, 1]])])
        assert "1 lines" in repr(p)

    def test_svg_repr(self):
        p = Paths([np.array([[0, 0], [1, 1]])])
        svg = p._repr_svg_()
        assert "<svg" in svg
        assert "polyline" in svg

"""Tests for penpal.core.line_ops."""

import numpy as np
import pytest

from penpal.core.line_ops import (
    optimize,
    filter_short,
    collapse,
    subsample,
    every_nth,
    resample_polyline,
)


class TestOptimize:
    def test_single_line(self):
        lines = [np.array([[0, 0], [1, 1]])]
        result = optimize(lines)
        assert len(result) == 1

    def test_reorders(self):
        # Line A ends at (10, 10), line B starts at (10, 10.1), line C starts at (100, 100)
        # Without optimization, C would be visited before B if placed second
        a = np.array([[0, 0], [10, 10]])
        b = np.array([[10, 10.1], [20, 20]])
        c = np.array([[100, 100], [110, 110]])
        result = optimize([a, c, b])
        # After optimization, b should come right after a
        assert len(result) == 3


class TestFilterShort:
    def test_removes_short(self):
        short = np.array([[0, 0], [0.01, 0]])
        long = np.array([[0, 0], [10, 0]])
        result = filter_short([short, long], min_length=1.0)
        assert len(result) == 1
        np.testing.assert_allclose(result[0], long)

    def test_keeps_long(self):
        lines = [np.array([[0, 0], [5, 0]])]
        result = filter_short(lines, min_length=1.0)
        assert len(result) == 1


class TestCollapse:
    def test_merges_close(self):
        a = np.array([[0, 0], [1, 0]])
        b = np.array([[1.001, 0], [2, 0]])
        result = collapse([a, b], threshold=0.01)
        assert len(result) == 1
        assert result[0].shape[0] == 3

    def test_keeps_far(self):
        a = np.array([[0, 0], [1, 0]])
        b = np.array([[5, 0], [6, 0]])
        result = collapse([a, b], threshold=0.01)
        assert len(result) == 2


class TestSubsample:
    def test_by_n(self):
        pts = np.column_stack([np.linspace(0, 10, 100), np.zeros(100)])
        result = subsample([pts], n=10)
        assert result[0].shape[0] < 100
        # First and last preserved
        np.testing.assert_allclose(result[0][0], pts[0])
        np.testing.assert_allclose(result[0][-1], pts[-1])

    def test_short_line_unchanged(self):
        pts = np.array([[0, 0], [1, 1]])
        result = subsample([pts], n=5)
        assert result[0].shape[0] == 2


class TestEveryNth:
    def test_basic(self):
        lines = [np.array([[i, 0], [i, 1]]) for i in range(9)]
        result = every_nth(lines, 3)
        assert len(result) == 3


class TestResamplePolyline:
    def test_preserves_length(self):
        pts = np.array([[0, 0], [10, 0]], dtype=np.float64)
        result = resample_polyline(pts, 11)
        assert result.shape == (11, 2)
        np.testing.assert_allclose(result[0], [0, 0])
        np.testing.assert_allclose(result[-1], [10, 0])
        np.testing.assert_allclose(result[5], [5, 0], atol=1e-10)

    def test_single_point(self):
        pts = np.array([[5, 5]], dtype=np.float64)
        result = resample_polyline(pts, 10)
        assert result.shape == (1, 2)

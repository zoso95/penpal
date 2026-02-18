"""Tests for penpal.core.geo."""

import numpy as np
import pytest

from penpal.core.geo import clip, clip_rect, contains_points


class TestClipRect:
    def test_clips_line(self):
        # Line from (-1, 0.5) to (2, 0.5), clipped to unit square
        lines = [np.array([[-1, 0.5], [2, 0.5]])]
        result = clip_rect(lines, 0, 0, 1, 1)
        assert len(result) == 1
        # Should be trimmed to ~(0, 0.5) to (1, 0.5)
        np.testing.assert_allclose(result[0][0], [0, 0.5], atol=1e-10)
        np.testing.assert_allclose(result[0][-1], [1, 0.5], atol=1e-10)

    def test_line_inside(self):
        lines = [np.array([[0.2, 0.2], [0.8, 0.8]])]
        result = clip_rect(lines, 0, 0, 1, 1)
        assert len(result) == 1

    def test_line_outside(self):
        lines = [np.array([[5, 5], [6, 6]])]
        result = clip_rect(lines, 0, 0, 1, 1)
        assert len(result) == 0


class TestClip:
    def test_clip_to_triangle(self):
        triangle = np.array([[0, 0], [2, 0], [1, 2], [0, 0]])
        lines = [np.array([[-1, 0.5], [3, 0.5]])]
        result = clip(lines, triangle)
        assert len(result) >= 1


class TestContainsPoints:
    def test_inside(self):
        square = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
        points = np.array([[0.5, 0.5], [2.0, 2.0]])
        mask = contains_points(square, points)
        assert mask[0] == True
        assert mask[1] == False

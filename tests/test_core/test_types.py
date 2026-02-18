"""Tests for penpal.core.types."""

import numpy as np
import pytest

from penpal.core.types import (
    validate_polyline,
    validate_lines,
    lines_dimension,
    from_segments,
    to_segments,
)


class TestValidatePolyline:
    def test_valid_2d(self):
        arr = np.array([[0, 0], [1, 1]])
        result = validate_polyline(arr)
        assert result.shape == (2, 2)
        assert result.dtype == np.float64

    def test_valid_3d(self):
        arr = np.array([[0, 0, 0], [1, 1, 1]])
        result = validate_polyline(arr)
        assert result.shape == (2, 3)

    def test_1d_point_becomes_row(self):
        arr = np.array([1.0, 2.0])
        result = validate_polyline(arr)
        assert result.shape == (1, 2)

    def test_1d_3d_point(self):
        result = validate_polyline(np.array([1, 2, 3]))
        assert result.shape == (1, 3)

    def test_bad_shape_raises(self):
        with pytest.raises(ValueError):
            validate_polyline(np.array([[1, 2, 3, 4]]))

    def test_1d_bad_length_raises(self):
        with pytest.raises(ValueError):
            validate_polyline(np.array([1, 2, 3, 4]))


class TestValidateLines:
    def test_list_of_arrays(self):
        data = [np.array([[0, 0], [1, 1]]), np.array([[2, 2], [3, 3]])]
        result = validate_lines(data)
        assert len(result) == 2

    def test_single_array(self):
        result = validate_lines(np.array([[0, 0], [1, 1]]))
        assert len(result) == 1


class TestLinesDimension:
    def test_empty(self):
        assert lines_dimension([]) == 0

    def test_2d(self):
        assert lines_dimension([np.array([[0, 0], [1, 1]])]) == 2

    def test_3d(self):
        assert lines_dimension([np.array([[0, 0, 0], [1, 1, 1]])]) == 3


class TestSegmentConversion:
    def test_roundtrip(self):
        segments = [([0, 0], [1, 1]), ([2, 2], [3, 3])]
        lines = from_segments(segments)
        assert len(lines) == 2
        assert lines[0].shape == (2, 2)

    def test_to_segments(self):
        lines = [np.array([[0, 0], [1, 1], [2, 2]])]
        segs = to_segments(lines)
        assert len(segs) == 2

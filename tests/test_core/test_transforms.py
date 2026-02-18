"""Tests for penpal.core.transforms."""

import numpy as np
import pytest

from penpal.core.transforms import (
    rotate, reflect, translate, scale,
    rotate_x, rotate_y, rotate_z, rotate_axis,
    translate3d, scale3d,
    apply,
)


class TestRotate2D:
    def test_90_degrees(self):
        m = rotate(90)
        pt = np.array([[1, 0]])
        result = apply(m, [pt])
        np.testing.assert_allclose(result[0], [[0, 1]], atol=1e-10)

    def test_with_center(self):
        m = rotate(180, center=(1, 0))
        pt = np.array([[2, 0]])
        result = apply(m, [pt])
        np.testing.assert_allclose(result[0], [[0, 0]], atol=1e-10)

    def test_radians(self):
        m = rotate(np.pi / 2, degrees=False)
        pt = np.array([[1, 0]])
        result = apply(m, [pt])
        np.testing.assert_allclose(result[0], [[0, 1]], atol=1e-10)


class TestTranslate2D:
    def test_basic(self):
        m = translate(3, 4)
        result = apply(m, [np.array([[0, 0]])])
        np.testing.assert_allclose(result[0], [[3, 4]])


class TestScale2D:
    def test_uniform(self):
        m = scale(2)
        result = apply(m, [np.array([[1, 1]])])
        np.testing.assert_allclose(result[0], [[2, 2]])

    def test_non_uniform(self):
        m = scale(2, 3)
        result = apply(m, [np.array([[1, 1]])])
        np.testing.assert_allclose(result[0], [[2, 3]])

    def test_with_center(self):
        m = scale(2, center=(1, 1))
        result = apply(m, [np.array([[2, 2]])])
        np.testing.assert_allclose(result[0], [[3, 3]])


class TestReflect2D:
    def test_reflect_x_axis(self):
        m = reflect(0)  # reflect across x axis (angle=0)
        result = apply(m, [np.array([[1, 1]])])
        np.testing.assert_allclose(result[0], [[1, -1]], atol=1e-10)


class TestComposition:
    def test_translate_then_rotate(self):
        m = rotate(90) @ translate(1, 0)
        result = apply(m, [np.array([[0, 0]])])
        np.testing.assert_allclose(result[0], [[0, 1]], atol=1e-10)


class Test3DTransforms:
    def test_rotate_x(self):
        m = rotate_x(90)
        result = apply(m, [np.array([[0, 1, 0]])])
        np.testing.assert_allclose(result[0], [[0, 0, 1]], atol=1e-10)

    def test_translate3d(self):
        m = translate3d(1, 2, 3)
        result = apply(m, [np.array([[0, 0, 0]])])
        np.testing.assert_allclose(result[0], [[1, 2, 3]])

    def test_scale3d(self):
        m = scale3d(2)
        result = apply(m, [np.array([[1, 1, 1]])])
        np.testing.assert_allclose(result[0], [[2, 2, 2]])


class TestApply:
    def test_empty(self):
        m = translate(1, 0)
        assert apply(m, []) == []

    def test_multiple_lines(self):
        m = translate(10, 0)
        lines = [np.array([[0, 0], [1, 0]]), np.array([[5, 5]])]
        result = apply(m, lines)
        assert len(result) == 2
        np.testing.assert_allclose(result[0][0], [10, 0])
        np.testing.assert_allclose(result[1][0], [15, 5])

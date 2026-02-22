"""Tests for penpal.render3d.project."""

import numpy as np
import pytest

from penpal.render3d.project import (
    look_at, perspective, project_points, project_lines, viewport_map,
)


class TestLookAt:
    def test_shape(self):
        m = look_at([0, 0, 5], [0, 0, 0], [0, 1, 0])
        assert m.shape == (4, 4)

    def test_camera_on_z_axis(self):
        """Camera at (0,0,5) looking at origin — forward is -Z."""
        m = look_at([0, 0, 5], [0, 0, 0], [0, 1, 0])
        # Origin should map to (0, 0, -5) in camera space
        p = m @ np.array([0, 0, 0, 1])
        assert abs(p[0]) < 1e-10
        assert abs(p[1]) < 1e-10
        assert p[2] < 0  # in front of camera

    def test_up_preserved(self):
        m = look_at([0, 0, 5], [0, 0, 0], [0, 1, 0])
        # World Y-up point should have positive camera Y
        p = m @ np.array([0, 1, 0, 1])
        assert p[1] > 0


class TestPerspective:
    def test_shape(self):
        m = perspective(60, 1.0, 0.1, 100)
        assert m.shape == (4, 4)

    def test_center_projects_to_origin(self):
        """A point on the view axis should project to (0,0) in NDC."""
        view = look_at([0, 0, 5], [0, 0, 0], [0, 1, 0])
        proj = perspective(60, 1.0, 0.1, 100)
        mvp = proj @ view
        ndc = project_points(np.array([[0, 0, 0]]), mvp)
        assert abs(ndc[0, 0]) < 1e-6
        assert abs(ndc[0, 1]) < 1e-6

    def test_fov_effect(self):
        """Wider FOV should produce smaller NDC coordinates for same point."""
        view = look_at([0, 0, 5], [0, 0, 0], [0, 1, 0])
        p = np.array([[1, 0, 0]])

        proj_narrow = perspective(30, 1.0, 0.1, 100)
        proj_wide = perspective(90, 1.0, 0.1, 100)

        ndc_narrow = project_points(p, proj_narrow @ view)
        ndc_wide = project_points(p, proj_wide @ view)

        # Narrower FOV → larger apparent size
        assert abs(ndc_narrow[0, 0]) > abs(ndc_wide[0, 0])


class TestProjectPoints:
    def test_shape(self):
        mvp = perspective(60, 1.0, 0.1, 100) @ look_at([0, 0, 5], [0, 0, 0], [0, 1, 0])
        pts = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
        ndc = project_points(pts, mvp)
        assert ndc.shape == (3, 2)


class TestProjectLines:
    def test_preserves_structure(self):
        mvp = perspective(60, 1.0, 0.1, 100) @ look_at([0, 0, 5], [0, 0, 0], [0, 1, 0])
        lines = [
            np.array([[0, 0, 0], [1, 0, 0]]),
            np.array([[0, 0, 0], [0, 1, 0], [0, 0, 1]]),
        ]
        result = project_lines(lines, mvp)
        assert len(result) == 2
        assert result[0].shape == (2, 2)
        assert result[1].shape == (3, 2)


class TestViewportMap:
    def test_ndc_corners(self):
        """NDC corners should map to viewport corners."""
        ndc = np.array([[-1, 1], [1, 1], [1, -1], [-1, -1]], dtype=np.float64)
        screen = viewport_map(ndc, 0, 0, 100, 100)
        # (-1,1) → top-left (0,0)
        np.testing.assert_allclose(screen[0], [0, 0], atol=1e-10)
        # (1,1) → top-right (100,0)
        np.testing.assert_allclose(screen[1], [100, 0], atol=1e-10)
        # (1,-1) → bottom-right (100,100)
        np.testing.assert_allclose(screen[2], [100, 100], atol=1e-10)
        # (-1,-1) → bottom-left (0,100)
        np.testing.assert_allclose(screen[3], [0, 100], atol=1e-10)

    def test_center_maps_to_center(self):
        ndc = np.array([[0, 0]], dtype=np.float64)
        screen = viewport_map(ndc, 10, 20, 100, 200)
        np.testing.assert_allclose(screen[0], [60, 120], atol=1e-10)

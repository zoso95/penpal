"""Tests for penpal.render3d.camera."""

import numpy as np
import pytest

from penpal.render3d.camera import Camera


class TestCamera:
    def test_default_construction(self):
        cam = Camera()
        np.testing.assert_allclose(cam.position, [0, 0, 5])
        np.testing.assert_allclose(cam.target, [0, 0, 0])
        assert cam.fov == 60

    def test_view_matrix_shape(self):
        cam = Camera()
        assert cam.view_matrix.shape == (4, 4)

    def test_projection_matrix_shape(self):
        cam = Camera()
        assert cam.projection_matrix.shape == (4, 4)

    def test_vp_is_proj_times_view(self):
        cam = Camera()
        expected = cam.projection_matrix @ cam.view_matrix
        np.testing.assert_allclose(cam.vp_matrix, expected, atol=1e-12)

    def test_forward_direction(self):
        cam = Camera(position=[0, 0, 5], target=[0, 0, 0])
        fwd = cam.forward
        # Should point toward -Z (from camera toward origin)
        assert fwd[2] < 0
        assert abs(fwd[0]) < 1e-10
        assert abs(fwd[1]) < 1e-10


class TestOrbit:
    def test_azimuth_zero_elevation_zero(self):
        """az=0, el=0 → camera on +X axis."""
        cam = Camera.orbit(target=(0, 0, 0), distance=5, azimuth=0, elevation=0)
        # Should be at (5, 0, 0)
        np.testing.assert_allclose(cam.position, [5, 0, 0], atol=1e-10)

    def test_azimuth_90_elevation_zero(self):
        """az=90, el=0 → camera on +Z axis."""
        cam = Camera.orbit(target=(0, 0, 0), distance=5, azimuth=90, elevation=0)
        np.testing.assert_allclose(cam.position, [0, 0, 5], atol=1e-10)

    def test_elevation_90(self):
        """el=90 → camera directly above."""
        cam = Camera.orbit(target=(0, 0, 0), distance=5, azimuth=0, elevation=90)
        assert cam.position[1] > 4.9  # nearly at (0, 5, 0)
        assert abs(cam.position[0]) < 0.01
        assert abs(cam.position[2]) < 0.01

    def test_distance(self):
        cam = Camera.orbit(distance=10)
        dist = np.linalg.norm(cam.position - cam.target)
        np.testing.assert_allclose(dist, 10.0, atol=1e-10)

    def test_target_offset(self):
        cam = Camera.orbit(target=(1, 2, 3), distance=5, azimuth=0, elevation=0)
        np.testing.assert_allclose(cam.position, [6, 2, 3], atol=1e-10)

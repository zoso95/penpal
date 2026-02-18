"""Tests for Mesh — composable grid warping."""

import numpy as np
import pytest

from penpal.core.mesh import Mesh
from penpal.core.paths import Paths


class TestMeshRect:
    def test_basic_shape(self):
        m = Mesh.rect(0, 0, 8, 10, rows=10, cols=12)
        assert m.shape == (11, 13)  # rows+1, cols+1 vertices
        assert m.topology == "rect"

    def test_corner_values(self):
        m = Mesh.rect(0, 0, 8, 10, rows=5, cols=5)
        assert m.x[0, 0] == pytest.approx(0)
        assert m.y[0, 0] == pytest.approx(0)
        assert m.x[-1, -1] == pytest.approx(8)
        assert m.y[-1, -1] == pytest.approx(10)

    def test_centered(self):
        m = Mesh.rect(-4, -5, 4, 5, rows=4, cols=4)
        assert m.x[0, 0] == pytest.approx(-4)
        assert m.y[0, 0] == pytest.approx(-5)


class TestMeshPolar:
    def test_basic_shape(self):
        m = Mesh.polar(rings=10, spokes=20)
        assert m.shape == (20, 11)  # spokes, rings+1
        assert m.topology == "polar"

    def test_center(self):
        m = Mesh.polar(center=(3, 4), inner_r=0, outer_r=2, rings=5, spokes=8)
        # Inner ring should be at center
        np.testing.assert_allclose(
            np.mean(m.x[:, 0]), 3, atol=0.01
        )
        np.testing.assert_allclose(
            np.mean(m.y[:, 0]), 4, atol=0.01
        )

    def test_outer_radius(self):
        m = Mesh.polar(center=(0, 0), outer_r=5, rings=10, spokes=20)
        r = np.sqrt(m.x[:, -1]**2 + m.y[:, -1]**2)
        np.testing.assert_allclose(r, 5.0, atol=1e-10)


class TestWarps:
    def test_warp_returns_new_mesh(self):
        m = Mesh.rect(0, 0, 1, 1, rows=5, cols=5)
        m2 = m.warp(lambda x, y: (np.zeros_like(x), np.zeros_like(y)))
        assert m2 is not m
        np.testing.assert_array_equal(m2.x, m.x)

    def test_warp_displaces(self):
        m = Mesh.rect(0, 0, 1, 1, rows=5, cols=5)
        m2 = m.warp(lambda x, y: (np.ones_like(x) * 0.5, np.zeros_like(y)))
        np.testing.assert_allclose(m2.x, m.x + 0.5)
        np.testing.assert_array_equal(m2.y, m.y)

    def test_warp_noise_deterministic(self):
        m = Mesh.rect(0, 0, 1, 1, rows=5, cols=5)
        m1 = m.warp_noise(amplitude=0.1, seed=42)
        m2 = m.warp_noise(amplitude=0.1, seed=42)
        np.testing.assert_array_equal(m1.x, m2.x)
        np.testing.assert_array_equal(m1.y, m2.y)

    def test_warp_noise_changes_positions(self):
        m = Mesh.rect(0, 0, 1, 1, rows=5, cols=5)
        m2 = m.warp_noise(amplitude=0.3, seed=7)
        assert not np.allclose(m.x, m2.x)

    def test_warp_noise_amplitude_scales(self):
        m = Mesh.rect(0, 0, 4, 4, rows=10, cols=10)
        m_small = m.warp_noise(amplitude=0.1, seed=1)
        m_large = m.warp_noise(amplitude=1.0, seed=1)
        diff_small = np.max(np.abs(m_small.x - m.x))
        diff_large = np.max(np.abs(m_large.x - m.x))
        assert diff_large > diff_small

    def test_warp_radial_barrel(self):
        m = Mesh.rect(-1, -1, 1, 1, rows=4, cols=4)
        m2 = m.warp_radial(center=(0, 0), strength=0.5)
        # Barrel pushes outward — corners should be farther from center
        r_orig = np.sqrt(m.x**2 + m.y**2)
        r_warped = np.sqrt(m2.x**2 + m2.y**2)
        # Non-center vertices should move outward
        mask = r_orig > 0.1
        assert np.all(r_warped[mask] >= r_orig[mask] - 1e-10)

    def test_warp_radial_pincushion(self):
        m = Mesh.rect(-1, -1, 1, 1, rows=4, cols=4)
        m2 = m.warp_radial(center=(0, 0), strength=-0.5)
        r_orig = np.sqrt(m.x**2 + m.y**2)
        r_warped = np.sqrt(m2.x**2 + m2.y**2)
        mask = r_orig > 0.1
        assert np.all(r_warped[mask] <= r_orig[mask] + 1e-10)

    def test_twist(self):
        m = Mesh.polar(center=(0, 0), outer_r=2, rings=5, spokes=20)
        m2 = m.twist(np.pi / 4)
        # Outer ring should be rotated more than inner ring
        assert m2.topology == "polar"
        assert not np.allclose(m.x, m2.x)

    def test_jitter_deterministic(self):
        m = Mesh.rect(0, 0, 1, 1, rows=5, cols=5)
        m1 = m.jitter(amount=0.1, seed=42)
        m2 = m.jitter(amount=0.1, seed=42)
        np.testing.assert_array_equal(m1.x, m2.x)

    def test_jitter_pin_edges(self):
        m = Mesh.rect(0, 0, 1, 1, rows=5, cols=5)
        m2 = m.jitter(amount=0.1, seed=42, pin_edges=True)
        # Boundary should be unchanged
        np.testing.assert_array_equal(m2.x[0, :], m.x[0, :])
        np.testing.assert_array_equal(m2.x[-1, :], m.x[-1, :])
        np.testing.assert_array_equal(m2.x[:, 0], m.x[:, 0])
        np.testing.assert_array_equal(m2.x[:, -1], m.x[:, -1])

    def test_jitter_no_pin(self):
        m = Mesh.rect(0, 0, 1, 1, rows=5, cols=5)
        m2 = m.jitter(amount=0.5, seed=42, pin_edges=False)
        # Edges should have changed
        assert not np.allclose(m2.x[0, :], m.x[0, :])


class TestChaining:
    def test_chain_warps(self):
        m = (Mesh.rect(0, 0, 4, 4, rows=10, cols=10)
             .warp_noise(amplitude=0.2, seed=1)
             .warp_radial(strength=0.1)
             .jitter(amount=0.05, seed=2))
        assert m.shape == (11, 11)

    def test_polar_chain(self):
        m = (Mesh.polar(center=(0, 0), outer_r=3, rings=10, spokes=20)
             .warp_noise(amplitude=0.2, seed=1)
             .twist(0.5))
        assert m.topology == "polar"


class TestToPaths:
    def test_rect_to_paths(self):
        m = Mesh.rect(0, 0, 1, 1, rows=3, cols=3)
        p = m.to_paths()
        assert isinstance(p, Paths)
        # 4 rows + 4 cols = 8 lines
        assert len(p) == 8

    def test_rect_smooth(self):
        m = Mesh.rect(0, 0, 1, 1, rows=5, cols=5)
        p = m.to_paths(smooth=True, points_per_line=50)
        assert isinstance(p, Paths)
        # Each smooth line should have 50 points
        for line in p.lines:
            assert line.shape[0] == 50

    def test_polar_to_paths(self):
        m = Mesh.polar(rings=5, spokes=10)
        p = m.to_paths()
        assert isinstance(p, Paths)
        # 6 rings + 10 spokes = 16 lines
        assert len(p) == 16

    def test_polar_smooth(self):
        m = Mesh.polar(rings=5, spokes=10)
        p = m.to_paths(smooth=True, points_per_line=80)
        assert isinstance(p, Paths)
        assert len(p) > 0

    def test_empty_mesh(self):
        m = Mesh(np.array([[0]]), np.array([[0]]))
        p = m.to_paths()
        assert isinstance(p, Paths)


class TestCopyRepr:
    def test_copy(self):
        m = Mesh.rect(0, 0, 1, 1, rows=3, cols=3)
        m2 = m.copy()
        m2.x[0, 0] = 999
        assert m.x[0, 0] != 999

    def test_repr(self):
        m = Mesh.rect(0, 0, 1, 1, rows=3, cols=3)
        assert "4x4" in repr(m)
        assert "rect" in repr(m)

    def test_repr_polar(self):
        m = Mesh.polar(rings=5, spokes=10)
        assert "polar" in repr(m)

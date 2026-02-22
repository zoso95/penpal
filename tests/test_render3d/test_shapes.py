"""Tests for penpal.render3d.shapes."""

import numpy as np
import pytest

from penpal.render3d.shapes import Face3D, Mesh3D, TextureSpec, Wireframe


class TestTextureSpec:
    def test_defaults(self):
        ts = TextureSpec()
        assert ts.style == 'hatch'
        assert ts.angle == 45
        assert ts.draw_boundary is True


class TestFace3D:
    def test_normal_ccw(self):
        """CCW winding in XY plane → normal in +Z."""
        verts = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
        face = Face3D(verts)
        n = face.normal()
        assert n[2] > 0.99  # +Z

    def test_normal_unit(self):
        verts = np.array([[0, 0, 0], [2, 0, 0], [2, 2, 0]])
        face = Face3D(verts)
        n = face.normal()
        np.testing.assert_allclose(np.linalg.norm(n), 1.0, atol=1e-12)

    def test_centroid(self):
        verts = np.array([[0, 0, 0], [2, 0, 0], [2, 2, 0], [0, 2, 0]])
        face = Face3D(verts)
        np.testing.assert_allclose(face.centroid(), [1, 1, 0])

    def test_generate_texture_hatch(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
        face = Face3D(verts, texture=TextureSpec(style='hatch', spacing=0.3))
        lines = face.generate_texture_lines()
        assert len(lines) > 0
        # All lines should be 3D (N, 3)
        for line in lines:
            assert line.shape[1] == 3
            # All Z values should be 0 (face is in XY plane)
            np.testing.assert_allclose(line[:, 2], 0, atol=1e-10)

    def test_generate_texture_none(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
        face = Face3D(verts, texture=TextureSpec(style='none', draw_boundary=False))
        lines = face.generate_texture_lines()
        assert len(lines) == 0

    def test_generate_texture_boundary_only(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
        face = Face3D(verts, texture=TextureSpec(style='none', draw_boundary=True))
        lines = face.generate_texture_lines()
        assert len(lines) == 1  # just the boundary

    def test_generate_texture_crosshatch(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
        face = Face3D(verts, texture=TextureSpec(style='crosshatch', spacing=0.3))
        lines = face.generate_texture_lines()
        # Crosshatch should produce more lines than plain hatch
        face_hatch = Face3D(verts, texture=TextureSpec(style='hatch', spacing=0.3))
        hatch_lines = face_hatch.generate_texture_lines()
        assert len(lines) > len(hatch_lines)

    def test_transform(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
        face = Face3D(verts)
        # Translate by (1, 2, 3)
        m = np.eye(4)
        m[:3, 3] = [1, 2, 3]
        new_face = face.transform(m)
        np.testing.assert_allclose(new_face.vertices[0], [1, 2, 3])


class TestMesh3D:
    def test_box_face_count(self):
        mesh = Mesh3D.box()
        assert len(mesh.faces) == 6

    def test_box_outward_normals(self):
        """All box face normals should point outward from center."""
        mesh = Mesh3D.box(size=2, center=(0, 0, 0))
        for face in mesh.faces:
            centroid = face.centroid()
            n = face.normal()
            # Normal should be roughly aligned with centroid direction
            assert np.dot(n, centroid) > 0

    def test_box_per_face_texture(self):
        mesh = Mesh3D.box(
            face_textures={'front': TextureSpec(style='crosshatch')},
        )
        # At least one face should have crosshatch
        styles = [f.texture.style for f in mesh.faces]
        assert 'crosshatch' in styles

    def test_plane_single_face(self):
        mesh = Mesh3D.plane()
        assert len(mesh.faces) == 1

    def test_plane_normal_axis(self):
        mesh_y = Mesh3D.plane(normal_axis='y')
        n = mesh_y.faces[0].normal()
        assert abs(n[1]) > 0.99

        mesh_z = Mesh3D.plane(normal_axis='z')
        n = mesh_z.faces[0].normal()
        assert abs(n[2]) > 0.99

    def test_transform(self):
        mesh = Mesh3D.box()
        m = np.eye(4)
        m[:3, 3] = [10, 0, 0]
        new_mesh = mesh.transform(m)
        assert len(new_mesh.faces) == 6
        # All centroids should be near x=10
        for face in new_mesh.faces:
            assert abs(face.centroid()[0] - 10) < 1


class TestWireframe:
    def test_basic(self):
        wf = Wireframe([
            np.array([[0, 0, 0], [1, 0, 0]]),
            np.array([[0, 0, 0], [0, 1, 0]]),
        ])
        assert len(wf.lines) == 2

    def test_transform(self):
        wf = Wireframe([np.array([[0, 0, 0], [1, 0, 0]])])
        m = np.eye(4)
        m[:3, 3] = [5, 0, 0]
        new_wf = wf.transform(m)
        np.testing.assert_allclose(new_wf.lines[0][0], [5, 0, 0])

"""Tests for penpal.render3d.scene."""

import numpy as np
import pytest

from penpal.core.drawing import Drawing
from penpal.render3d.camera import Camera
from penpal.render3d.scene import Scene
from penpal.render3d.shapes import Face3D, Mesh3D, TextureSpec, Wireframe


@pytest.fixture
def cam():
    return Camera.orbit(distance=5, azimuth=30, elevation=30)


class TestSceneBasic:
    def test_render_returns_drawing(self, cam):
        scene = Scene()
        scene.add(Mesh3D.box())
        result = scene.render(cam)
        assert isinstance(result, Drawing)

    def test_render_has_lines(self, cam):
        scene = Scene()
        scene.add(Mesh3D.box())
        d = scene.render(cam)
        total_lines = sum(len(l.lines) for l in d.layers)
        assert total_lines > 0

    def test_empty_scene(self, cam):
        scene = Scene()
        d = scene.render(cam)
        assert len(d.layers) == 0

    def test_chaining(self):
        scene = Scene()
        result = scene.add(Mesh3D.box())
        assert result is scene


class TestBackfaceCulling:
    def test_culling_reduces_faces(self, cam):
        scene = Scene()
        scene.add(Mesh3D.box())

        d_cull = scene.render(cam, cull_backfaces=True)
        d_no_cull = scene.render(cam, cull_backfaces=False)

        cull_lines = sum(len(l.lines) for l in d_cull.layers)
        no_cull_lines = sum(len(l.lines) for l in d_no_cull.layers)

        # Without culling should have more (or equal) lines
        assert no_cull_lines >= cull_lines


class TestHiddenLineRemoval:
    def test_hidden_lines_show(self, cam):
        """hidden_lines='show' should render without clipping."""
        scene = Scene()
        scene.add(Mesh3D.box())
        d = scene.render(cam, hidden_lines='show')
        total = sum(len(l.lines) for l in d.layers)
        assert total > 0

    def test_occluded_face_has_fewer_lines(self):
        """A face behind another should have some lines clipped."""
        # Front face at z=1, back face at z=-1
        front = Face3D(
            np.array([[-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]]),
            texture=TextureSpec(style='none', draw_boundary=True),
        )
        back = Face3D(
            np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1]]),
            texture=TextureSpec(style='none', draw_boundary=True),
        )

        cam = Camera(position=[0, 0, 5], target=[0, 0, 0])

        scene_show = Scene([front, back])
        d_show = scene_show.render(cam, hidden_lines='show')

        scene_remove = Scene([front, back])
        d_remove = scene_remove.render(cam, hidden_lines='remove')

        show_lines = sum(len(l.lines) for l in d_show.layers)
        remove_lines = sum(len(l.lines) for l in d_remove.layers)

        # With removal, the back face boundary should be clipped
        # so fewer total lines (or same if fully occluded)
        assert remove_lines <= show_lines


class TestWireframeRendering:
    def test_wireframe_renders(self, cam):
        scene = Scene()
        scene.add(Wireframe([
            np.array([[0, 0, 0], [1, 0, 0]]),
            np.array([[0, 0, 0], [0, 1, 0]]),
        ], layer='axes'))
        d = scene.render(cam)
        assert any(l.name == 'axes' for l in d.layers)

    def test_wireframe_with_faces(self, cam):
        scene = Scene()
        scene.add(Mesh3D.box())
        scene.add(Wireframe([np.array([[0, 0, 0], [2, 0, 0]])], layer='axes'))
        d = scene.render(cam)
        layer_names = [l.name for l in d.layers]
        assert 'default' in layer_names
        assert 'axes' in layer_names


class TestMultiLayer:
    def test_per_face_layers(self):
        """With no backface culling, per-face layers should all appear."""
        scene = Scene()
        scene.add(Mesh3D.box(
            face_layers={'front': 'pen1', 'top': 'pen2', 'right': 'pen1'},
        ))
        cam = Camera.orbit(distance=5, azimuth=30, elevation=30)
        d = scene.render(cam, cull_backfaces=False, hidden_lines='show')
        layer_names = [l.name for l in d.layers]
        assert 'pen1' in layer_names
        assert 'pen2' in layer_names


class TestRepr:
    def test_repr(self):
        scene = Scene()
        scene.add(Mesh3D.box())
        scene.add(Wireframe([np.array([[0, 0, 0], [1, 0, 0]])]))
        r = repr(scene)
        assert 'Mesh3D' in r
        assert 'Wireframe' in r

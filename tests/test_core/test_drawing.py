"""Tests for Drawing and Layer."""

import numpy as np
import pytest

from penpal.core.drawing import Drawing
from penpal.core.layer import Layer, LayerStyle
from penpal.core.paths import Paths


class TestDrawing:
    def test_create(self):
        d = Drawing(8, 10)
        assert d.width == 8
        assert d.height == 10
        assert d.units == "in"
        assert d.show_grid is True

    def test_layer_create(self):
        d = Drawing(8, 10)
        lay = d.layer("test", color="red")
        assert lay.name == "test"
        assert lay.style.color == "red"
        assert len(d.layers) == 1

    def test_layer_get_existing(self):
        d = Drawing(8, 10)
        d.layer("test", color="red")
        lay = d.layer("test")
        assert lay.style.color == "red"

    def test_layer_update_style(self):
        d = Drawing(8, 10)
        d.layer("test", color="red")
        d.layer("test", color="blue")
        assert d.layer("test").style.color == "blue"

    def test_layer_order(self):
        d = Drawing(8, 10)
        d.layer("a")
        d.layer("b")
        d.layer("c")
        assert [l.name for l in d.layers] == ["a", "b", "c"]

    def test_add_lines(self):
        d = Drawing(8, 10)
        lines = Paths([np.array([[0, 0], [1, 1]])])
        d.layer("test").add(lines)
        assert len(d.layer("test")) == 1

    def test_add_raw_array(self):
        d = Drawing(8, 10)
        d.layer("test").add(np.array([[0, 0], [1, 1]]))
        assert len(d.layer("test")) == 1

    def test_flatten(self):
        d = Drawing(8, 10)
        d.layer("a").add(Paths([np.array([[0, 0], [1, 1]])]))
        d.layer("b").add(Paths([np.array([[2, 2], [3, 3]])]))
        merged = d.flatten()
        assert len(merged) == 2

    def test_repr(self):
        d = Drawing(8, 10)
        d.layer("test")
        assert "8x10" in repr(d)
        assert "test" in repr(d)


class TestDrawingSVG:
    def test_repr_svg(self):
        d = Drawing(8, 10)
        d.layer("test").add(Paths([np.array([[0, 0], [1, 1]])]))
        svg = d._repr_svg_()
        assert "<svg" in svg
        assert 'inkscape:label="test"' in svg

    def test_grid_in_svg(self):
        d = Drawing(8, 10, show_grid=True)
        svg = d._repr_svg_()
        assert 'id="grid"' in svg

    def test_no_grid(self):
        d = Drawing(8, 10, show_grid=False)
        svg = d._repr_svg_()
        assert 'id="grid"' not in svg


class TestLayer:
    def test_create(self):
        lay = Layer("test", color="red", linewidth=0.3)
        assert lay.name == "test"
        assert lay.style.color == "red"
        assert lay.style.linewidth == 0.3

    def test_add_returns_self(self):
        lay = Layer("test")
        result = lay.add(Paths([np.array([[0, 0], [1, 1]])]))
        assert result is lay

    def test_lines_property(self):
        lay = Layer("test")
        lay.add(Paths([np.array([[0, 0], [1, 1]])]))
        assert len(lay.lines) == 1


class TestLayerStyle:
    def test_defaults(self):
        s = LayerStyle()
        assert s.color == "black"
        assert s.linewidth == 0.5
        assert s.alpha == 1.0

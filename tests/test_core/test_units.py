"""Tests for penpal.core.units."""

import pytest

from penpal.core.units import to_inches, from_inches, convert


class TestToInches:
    def test_inches(self):
        assert to_inches(1, "in") == 1.0

    def test_mm(self):
        assert abs(to_inches(25.4, "mm") - 1.0) < 1e-10

    def test_cm(self):
        assert abs(to_inches(2.54, "cm") - 1.0) < 1e-10

    def test_pt(self):
        assert abs(to_inches(72, "pt") - 1.0) < 1e-10

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            to_inches(1, "furlongs")


class TestConvert:
    def test_mm_to_cm(self):
        assert abs(convert(10, "mm", "cm") - 1.0) < 1e-10

    def test_in_to_mm(self):
        assert abs(convert(1, "in", "mm") - 25.4) < 1e-10

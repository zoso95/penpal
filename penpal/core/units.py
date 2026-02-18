"""Physical unit conversion for plotter art.

All internal calculations use the user's chosen unit (typically inches).
This module provides conversion factors between units.
"""

from __future__ import annotations

# Conversion factors TO inches
_TO_INCHES = {
    "in": 1.0,
    "inch": 1.0,
    "inches": 1.0,
    "mm": 1.0 / 25.4,
    "cm": 1.0 / 2.54,
    "pt": 1.0 / 72.0,
    "px": 1.0 / 96.0,
}


def to_inches(value: float, from_unit: str) -> float:
    """Convert a value from the given unit to inches."""
    key = from_unit.lower().strip()
    if key not in _TO_INCHES:
        raise ValueError(f"Unknown unit '{from_unit}'. Known: {list(_TO_INCHES.keys())}")
    return value * _TO_INCHES[key]


def from_inches(value: float, to_unit: str) -> float:
    """Convert a value from inches to the given unit."""
    key = to_unit.lower().strip()
    if key not in _TO_INCHES:
        raise ValueError(f"Unknown unit '{to_unit}'. Known: {list(_TO_INCHES.keys())}")
    return value / _TO_INCHES[key]


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert between any two supported units."""
    return from_inches(to_inches(value, from_unit), to_unit)

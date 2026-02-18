"""Core type definitions for penpal.

Polyline = np.ndarray with shape (N, D) where D is 2 or 3.
Lines = List[np.ndarray], each element a Polyline.
"""

from __future__ import annotations

from typing import List, Union

import numpy as np

# Type aliases
Polyline = np.ndarray  # shape (N, D), dtype float64
Lines = List[np.ndarray]  # each element is (N_i, D)


def validate_polyline(arr: np.ndarray) -> np.ndarray:
    """Ensure arr is a valid polyline: 2D array with 2 or 3 columns."""
    arr = np.asarray(arr, dtype=np.float64)
    if arr.ndim == 1:
        if arr.shape[0] in (2, 3):
            arr = arr.reshape(1, -1)
        else:
            raise ValueError(f"1D array must have 2 or 3 elements, got {arr.shape[0]}")
    if arr.ndim != 2 or arr.shape[1] not in (2, 3):
        raise ValueError(
            f"Polyline must be shape (N, 2) or (N, 3), got {arr.shape}"
        )
    return arr


def validate_lines(data: Union[Lines, np.ndarray]) -> Lines:
    """Validate and normalize line data to Lines format."""
    if isinstance(data, np.ndarray):
        if data.ndim == 2 and data.shape[1] in (2, 3):
            return [validate_polyline(data)]
        raise ValueError(f"Single array must be (N, 2) or (N, 3), got {data.shape}")
    return [validate_polyline(line) for line in data]


def lines_dimension(lines: Lines) -> int:
    """Return the dimensionality (2 or 3) of lines. 0 if empty."""
    if not lines:
        return 0
    return lines[0].shape[1]


def from_segments(segments) -> Lines:
    """Convert [(pt_a, pt_b), ...] to Lines format."""
    return [np.array([a, b], dtype=np.float64) for a, b in segments]


def to_segments(lines: Lines):
    """Convert Lines to list of (pt_a, pt_b) segment pairs."""
    segments = []
    for line in lines:
        for i in range(len(line) - 1):
            segments.append((line[i], line[i + 1]))
    return segments

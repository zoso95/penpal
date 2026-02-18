"""Paths — the core manipulable line collection.

This is the workhorse type. Generators produce Paths, you manipulate
them freely, then add to a Layer when ready to render.
All mutation methods return new Paths (immutable pattern).
"""

from __future__ import annotations

from typing import List, Union

import numpy as np

from penpal.core.types import Lines, validate_lines, lines_dimension


class Paths:
    """A collection of polylines with manipulation methods."""

    def __init__(self, lines: Union[Lines, np.ndarray] = None):
        if lines is None:
            self.lines: Lines = []
        else:
            self.lines = validate_lines(lines)

    # --- Transforms (return new Paths) ---

    def transform(self, matrix: np.ndarray) -> Paths:
        """Apply a homogeneous transform matrix."""
        from penpal.core.transforms import apply

        return Paths(apply(matrix, self.lines))

    def translate(self, dx: float, dy: float) -> Paths:
        """Translate all lines."""
        from penpal.core.transforms import translate

        return self.transform(translate(dx, dy))

    def rotate(self, angle: float, center=None, degrees: bool = True) -> Paths:
        """Rotate all lines."""
        from penpal.core.transforms import rotate

        return self.transform(rotate(angle, center=center, degrees=degrees))

    def scale(self, sx: float, sy: float = None, center=None) -> Paths:
        """Scale all lines."""
        from penpal.core.transforms import scale

        return self.transform(scale(sx, sy, center=center))

    # --- Spatial ops (return new Paths) ---

    def clip(self, polygon: np.ndarray) -> Paths:
        """Clip to a polygon boundary."""
        from penpal.core.geo import clip

        return Paths(clip(self.lines, polygon))

    def clip_rect(self, xmin: float, ymin: float, xmax: float, ymax: float) -> Paths:
        """Clip to an axis-aligned rectangle."""
        from penpal.core.geo import clip_rect

        return Paths(clip_rect(self.lines, xmin, ymin, xmax, ymax))

    # --- Line processing (return new Paths) ---

    def optimize(self) -> Paths:
        """Reorder lines to minimize pen-lift travel."""
        from penpal.core.line_ops import optimize

        return Paths(optimize(self.lines))

    def filter(self, min_length: float) -> Paths:
        """Remove lines shorter than min_length."""
        from penpal.core.line_ops import filter_short

        return Paths(filter_short(self.lines, min_length))

    def collapse(self, threshold: float) -> Paths:
        """Merge nearby endpoints into continuous polylines."""
        from penpal.core.line_ops import collapse

        return Paths(collapse(self.lines, threshold))

    def subsample(self, n: int = None, frac: float = None) -> Paths:
        """Subsample points from each polyline."""
        from penpal.core.line_ops import subsample

        return Paths(subsample(self.lines, n=n, frac=frac))

    def every_nth(self, n: int) -> Paths:
        """Keep only every nth line."""
        from penpal.core.line_ops import every_nth

        return Paths(every_nth(self.lines, n))

    # --- Combine ---

    def __add__(self, other: Paths) -> Paths:
        """Concatenate two Paths."""
        if not isinstance(other, Paths):
            return NotImplemented
        return Paths(self.lines + other.lines)

    def __iadd__(self, other: Paths) -> Paths:
        if not isinstance(other, Paths):
            return NotImplemented
        self.lines.extend(other.lines)
        return self

    def __len__(self) -> int:
        return len(self.lines)

    def __iter__(self):
        return iter(self.lines)

    def __bool__(self) -> bool:
        return len(self.lines) > 0

    # --- Info ---

    def bounds(self) -> tuple:
        """Return (xmin, ymin, xmax, ymax)."""
        if not self.lines:
            return (0, 0, 0, 0)
        all_pts = np.vstack(self.lines)
        return (
            float(all_pts[:, 0].min()),
            float(all_pts[:, 1].min()),
            float(all_pts[:, 0].max()),
            float(all_pts[:, 1].max()),
        )

    def total_length(self) -> float:
        """Sum of arc lengths of all polylines."""
        total = 0.0
        for line in self.lines:
            if len(line) >= 2:
                diffs = np.diff(line, axis=0)
                total += float(np.sum(np.sqrt(np.sum(diffs**2, axis=1))))
        return total

    def total_points(self) -> int:
        """Total number of points across all polylines."""
        return sum(len(line) for line in self.lines)

    def dim(self) -> int:
        """Return dimensionality: 2 or 3. 0 if empty."""
        return lines_dimension(self.lines)

    # --- Display ---

    def _repr_svg_(self) -> str:
        """Notebook-friendly SVG preview."""
        if not self.lines:
            return "<svg></svg>"
        xmin, ymin, xmax, ymax = self.bounds()
        pad = max(xmax - xmin, ymax - ymin) * 0.05
        vx, vy = xmin - pad, ymin - pad
        vw, vh = (xmax - xmin) + 2 * pad, (ymax - ymin) + 2 * pad
        width = min(400, max(100, int(vw * 72)))
        height = int(width * vh / vw) if vw > 0 else 100

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" height="{height}" '
            f'viewBox="{vx} {vy} {vw} {vh}">'
            f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" fill="white"/>'
        ]
        for line in self.lines:
            pts = " ".join(f"{x:.4f},{y:.4f}" for x, y in line[:, :2])
            parts.append(
                f'<polyline points="{pts}" fill="none" stroke="black" '
                f'stroke-width="{vw * 0.003:.4f}"/>'
            )
        parts.append("</svg>")
        return "\n".join(parts)

    def __repr__(self) -> str:
        n = len(self.lines)
        pts = self.total_points()
        return f"Paths({n} lines, {pts} points)"

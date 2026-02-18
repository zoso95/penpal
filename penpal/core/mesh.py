"""Mesh — a 2D grid of vertices that can be warped and rendered as lines.

A Mesh is a structured grid of (rows, cols) vertices. You create one from
a rect or polar layout, apply warps, then convert to Paths for rendering.

All warp methods return new Mesh objects (immutable pattern).
"""

from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.interpolate import CubicSpline

from penpal.core.paths import Paths


class Mesh:
    """A structured 2D grid of vertices.

    x, y are 2D arrays of shape (n_rows, n_cols) — the vertex positions.
    topology describes how to connect them: 'rect' or 'polar'.
    """

    def __init__(self, x: np.ndarray, y: np.ndarray, topology: str = "rect"):
        self.x = np.asarray(x, dtype=np.float64)
        self.y = np.asarray(y, dtype=np.float64)
        self.topology = topology  # 'rect' or 'polar' (polar wraps rows)

    @property
    def shape(self):
        return self.x.shape

    def copy(self) -> Mesh:
        return Mesh(self.x.copy(), self.y.copy(), self.topology)

    # --- Constructors ---

    @classmethod
    def rect(cls, x0: float, y0: float, x1: float, y1: float,
             rows: int = 40, cols: int = 40) -> Mesh:
        """Rectangular grid."""
        xs = np.linspace(x0, x1, cols + 1)
        ys = np.linspace(y0, y1, rows + 1)
        xg, yg = np.meshgrid(xs, ys)
        return cls(xg, yg, topology="rect")

    @classmethod
    def polar(cls, center=(0, 0), inner_r: float = 0,
              outer_r: float = 1.0, rings: int = 20, spokes: int = 40) -> Mesh:
        """Polar grid (concentric rings + radial spokes).

        Rows = spokes (angular), Cols = rings (radial).
        The row dimension wraps around (closed rings).
        """
        cx, cy = center
        radii = np.linspace(inner_r, outer_r, rings + 1)
        angles = np.linspace(0, 2 * np.pi, spokes + 1)[:-1]  # don't duplicate 0/2pi
        rg, ag = np.meshgrid(radii, angles)
        xg = cx + rg * np.cos(ag)
        yg = cy + rg * np.sin(ag)
        return cls(xg, yg, topology="polar")

    # --- Warps (return new Mesh) ---

    def warp(self, func: Callable, pin_edges: bool = False) -> Mesh:
        """Apply arbitrary warp: func(x, y) -> (dx, dy).

        func receives the full x, y arrays and returns displacement arrays.

        pin_edges : bool
            If True, boundary vertices are not displaced.
            For rect: first/last row and column stay fixed.
            For polar: inner ring (col 0) and outer ring (col -1) stay fixed.
        """
        dx, dy = func(self.x, self.y)
        if pin_edges:
            if self.topology == "rect":
                dx[0, :] = dx[-1, :] = dx[:, 0] = dx[:, -1] = 0
                dy[0, :] = dy[-1, :] = dy[:, 0] = dy[:, -1] = 0
            elif self.topology == "polar":
                # Pin inner and outer rings (first and last column)
                dx[:, 0] = dx[:, -1] = 0
                dy[:, 0] = dy[:, -1] = 0
        return Mesh(self.x + dx, self.y + dy, self.topology)

    def warp_noise(self, amplitude: float = 0.3, frequency: float = 1.0,
                   seed: int = None, pin_edges: bool = False) -> Mesh:
        """Displace vertices with simplex noise.

        Shortcut for mesh.warp(noise.simplex(...), pin_edges=pin_edges).
        For other noise types, use mesh.warp() with functions from penpal.core.noise.
        """
        from penpal.core.noise import simplex
        return self.warp(simplex(amplitude, frequency, seed), pin_edges=pin_edges)

    def warp_radial(self, center=(0, 0), strength: float = 0.3) -> Mesh:
        """Radial barrel/pincushion distortion.

        strength > 0: barrel (push outward), < 0: pincushion (pull inward).
        """
        cx, cy = center
        dx = self.x - cx
        dy = self.y - cy
        r = np.sqrt(dx**2 + dy**2)
        r_max = r.max() if r.max() > 0 else 1.0
        scale = 1 + strength * (r / r_max) ** 2
        return Mesh(cx + dx * scale, cy + dy * scale, self.topology)

    def twist(self, amount: float) -> Mesh:
        """Angular twist proportional to radius (for polar grids).

        amount is total twist in radians at the outer edge.
        """
        cx = self.x.mean()
        cy = self.y.mean()
        dx = self.x - cx
        dy = self.y - cy
        r = np.sqrt(dx**2 + dy**2)
        r_max = r.max() if r.max() > 0 else 1.0
        theta = np.arctan2(dy, dx)
        theta += amount * (r / r_max)
        return Mesh(cx + r * np.cos(theta), cy + r * np.sin(theta), self.topology)

    def jitter(self, amount: float = 0.1, seed: int = None,
               pin_edges: bool = True) -> Mesh:
        """Random Gaussian displacement of vertices.

        pin_edges: if True, boundary vertices stay fixed (rect topology only).
        """
        rng = np.random.default_rng(seed)
        dx = rng.normal(0, amount, self.x.shape)
        dy = rng.normal(0, amount, self.y.shape)
        if pin_edges and self.topology == "rect":
            dx[0, :] = dx[-1, :] = dx[:, 0] = dx[:, -1] = 0
            dy[0, :] = dy[-1, :] = dy[:, 0] = dy[:, -1] = 0
        return Mesh(self.x + dx, self.y + dy, self.topology)

    # --- Rendering ---

    def to_paths(self, smooth: bool = False, points_per_line: int = 100) -> Paths:
        """Convert mesh to drawable Paths (lines through rows and columns).

        Parameters
        ----------
        smooth : bool
            If True, fit cubic splines through grid points for smooth curves.
        points_per_line : int
            Points per spline when smooth=True.
        """
        lines = []
        n_rows, n_cols = self.shape

        if self.topology == "polar":
            lines.extend(self._polar_to_lines(smooth, points_per_line))
        else:
            lines.extend(self._rect_to_lines(smooth, points_per_line))

        return Paths(lines) if lines else Paths()

    def _rect_to_lines(self, smooth, ppl):
        lines = []
        n_rows, n_cols = self.shape

        if smooth and n_cols >= 4:
            t = np.linspace(0, 1, n_cols)
            t_fine = np.linspace(0, 1, ppl)
            # Horizontal lines
            for i in range(n_rows):
                cs_x = CubicSpline(t, self.x[i, :])
                cs_y = CubicSpline(t, self.y[i, :])
                lines.append(np.column_stack([cs_x(t_fine), cs_y(t_fine)]))
            # Vertical lines
            t = np.linspace(0, 1, n_rows)
            for j in range(n_cols):
                cs_x = CubicSpline(t, self.x[:, j])
                cs_y = CubicSpline(t, self.y[:, j])
                lines.append(np.column_stack([cs_x(t_fine), cs_y(t_fine)]))
        else:
            for i in range(n_rows):
                lines.append(np.column_stack([self.x[i, :], self.y[i, :]]))
            for j in range(n_cols):
                lines.append(np.column_stack([self.x[:, j], self.y[:, j]]))

        return lines

    def _polar_to_lines(self, smooth, ppl):
        lines = []
        n_spokes, n_rings = self.shape

        if smooth:
            # Rings (closed curves — wrap around)
            for j in range(n_rings):
                ring_x = np.concatenate([self.x[:, j], self.x[:1, j]])
                ring_y = np.concatenate([self.y[:, j], self.y[:1, j]])
                t = np.linspace(0, 1, len(ring_x))
                t_fine = np.linspace(0, 1, ppl + 1)
                try:
                    cs_x = CubicSpline(t, ring_x, bc_type='periodic')
                    cs_y = CubicSpline(t, ring_y, bc_type='periodic')
                    lines.append(np.column_stack([cs_x(t_fine), cs_y(t_fine)]))
                except Exception:
                    lines.append(np.column_stack([ring_x, ring_y]))

            # Spokes (radial lines)
            if n_rings >= 4:
                t = np.linspace(0, 1, n_rings)
                t_fine = np.linspace(0, 1, ppl)
                for i in range(n_spokes):
                    cs_x = CubicSpline(t, self.x[i, :])
                    cs_y = CubicSpline(t, self.y[i, :])
                    lines.append(np.column_stack([cs_x(t_fine), cs_y(t_fine)]))
            else:
                for i in range(n_spokes):
                    lines.append(np.column_stack([self.x[i, :], self.y[i, :]]))
        else:
            for j in range(n_rings):
                ring_x = np.concatenate([self.x[:, j], self.x[:1, j]])
                ring_y = np.concatenate([self.y[:, j], self.y[:1, j]])
                lines.append(np.column_stack([ring_x, ring_y]))
            for i in range(n_spokes):
                lines.append(np.column_stack([self.x[i, :], self.y[i, :]]))

        return lines

    def __repr__(self):
        return f"Mesh({self.shape[0]}x{self.shape[1]}, topology='{self.topology}')"

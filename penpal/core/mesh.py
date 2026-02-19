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

    # --- Spatial transforms (return new Mesh) ---

    def translate(self, dx: float, dy: float) -> Mesh:
        """Translate all vertices."""
        return Mesh(self.x + dx, self.y + dy, self.topology)

    def rotate(self, angle: float, center=None, degrees: bool = True) -> Mesh:
        """Rotate all vertices around a center point.

        angle : float
            Rotation angle (degrees by default).
        center : (cx, cy), optional
            Center of rotation. Defaults to mesh centroid.
        """
        if degrees:
            angle = np.radians(angle)
        if center is None:
            cx, cy = self.x.mean(), self.y.mean()
        else:
            cx, cy = center
        dx = self.x - cx
        dy = self.y - cy
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        nx = cx + dx * cos_a - dy * sin_a
        ny = cy + dx * sin_a + dy * cos_a
        return Mesh(nx, ny, self.topology)

    def scale(self, sx: float, sy: float = None, center=None) -> Mesh:
        """Scale all vertices from a center point.

        sx, sy : float
            Scale factors. If sy is None, uniform scale.
        center : (cx, cy), optional
            Center of scaling. Defaults to mesh centroid.
        """
        if sy is None:
            sy = sx
        if center is None:
            cx, cy = self.x.mean(), self.y.mean()
        else:
            cx, cy = center
        nx = cx + (self.x - cx) * sx
        ny = cy + (self.y - cy) * sy
        return Mesh(nx, ny, self.topology)

    def mirror(self, axis: str = 'x', center=None) -> Mesh:
        """Mirror/reflect across an axis.

        axis : 'x' (flip horizontally) or 'y' (flip vertically).
        """
        if center is None:
            cx, cy = self.x.mean(), self.y.mean()
        else:
            cx, cy = center
        if axis == 'x':
            return Mesh(2 * cx - self.x, self.y.copy(), self.topology)
        else:
            return Mesh(self.x.copy(), 2 * cy - self.y, self.topology)

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

    def warp_radial_noise(self, amplitude: float = 0.5,
                          freq_angular: float = 2.0, freq_radial: float = 0.3,
                          center=None, seed: int = None,
                          pin_edges: bool = True) -> Mesh:
        """Displace vertices radially by angle-coherent noise.

        Unlike warp_noise (which pushes x/y independently), this pushes each
        vertex in/out along the radial direction. The noise is evaluated based
        on (theta, r) so adjacent rings follow the same angular bumps.

        This is the right warp for concentric ring patterns — rings don't cross,
        spacing is preserved, and the overall shape stays centered.

        Parameters
        ----------
        amplitude : float
            Max radial displacement in drawing units.
        freq_angular : float
            Angular noise frequency — how many bumps per revolution.
            Higher = more crinkly, lower = broad gentle waves.
        freq_radial : float
            Radial noise frequency — how much the pattern changes from
            ring to ring. Low = all rings have similar shape (coherent).
            High = rings diverge.
        center : (cx, cy), optional
            Center point. Defaults to mesh centroid.
        seed : int, optional
            For reproducibility.
        pin_edges : bool
            If True (default), inner and outer rings stay fixed.
        """
        from opensimplex import OpenSimplex

        rng = np.random.default_rng(seed)
        noise = OpenSimplex(seed=int(rng.integers(0, 2**31)))

        if center is None:
            cx, cy = self.x.mean(), self.y.mean()
        else:
            cx, cy = center

        dx = self.x - cx
        dy = self.y - cy
        r = np.sqrt(dx**2 + dy**2)
        theta = np.arctan2(dy, dx)

        # Noise based on (theta, r) — angular coherence across rings
        dr = np.zeros_like(r)
        for i in range(self.x.shape[0]):
            for j in range(self.x.shape[1]):
                dr[i, j] = noise.noise2(
                    theta[i, j] * freq_angular,
                    r[i, j] * freq_radial,
                ) * amplitude

        # Smooth taper near inner/outer edges so rings don't cross boundary
        if pin_edges:
            r_min = r.min()
            r_max = r.max()
            r_range = r_max - r_min if r_max > r_min else 1.0
            # Normalized distance from edges: 0 at boundary, 1 in middle
            t = (r - r_min) / r_range  # 0..1
            taper = np.clip(t * 5, 0, 1) * np.clip((1 - t) * 5, 0, 1)
            dr *= taper

        # Apply radial displacement
        new_r = r + dr
        # Prevent negative radii
        new_r = np.maximum(new_r, 0)
        new_x = cx + new_r * np.cos(theta)
        new_y = cy + new_r * np.sin(theta)
        return Mesh(new_x, new_y, self.topology)

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

    def warp_flow(self, field: Callable, steps: int = 50,
                  step_size: float = 0.01, momentum: float = 0.0,
                  pin_edges: bool = False) -> Mesh:
        """Advect vertices along a flow field.

        Each vertex is pushed through the field for `steps` iterations,
        producing coherent, flow-aligned distortion.

        Parameters
        ----------
        field : callable
            (x, y) -> angle in radians (same as flow.trace fields).
        steps : int
            Number of advection steps per vertex.
        step_size : float
            Distance per step.
        momentum : float (0 to <1)
            Velocity smoothing (0 = pure Euler, 0.95 = smooth sweeping).
        pin_edges : bool
            If True, boundary vertices stay fixed.
        """
        nx = self.x.copy()
        ny = self.y.copy()
        vx = np.zeros_like(nx)
        vy = np.zeros_like(ny)

        for step in range(steps):
            for i in range(nx.shape[0]):
                for j in range(nx.shape[1]):
                    angle = field(nx[i, j], ny[i, j])
                    tvx = np.cos(angle) * step_size
                    tvy = np.sin(angle) * step_size
                    if momentum > 0 and step > 0:
                        vx[i, j] = momentum * vx[i, j] + (1 - momentum) * tvx
                        vy[i, j] = momentum * vy[i, j] + (1 - momentum) * tvy
                    else:
                        vx[i, j], vy[i, j] = tvx, tvy
                    nx[i, j] += vx[i, j]
                    ny[i, j] += vy[i, j]

        if pin_edges:
            if self.topology == "rect":
                nx[0, :], nx[-1, :] = self.x[0, :], self.x[-1, :]
                nx[:, 0], nx[:, -1] = self.x[:, 0], self.x[:, -1]
                ny[0, :], ny[-1, :] = self.y[0, :], self.y[-1, :]
                ny[:, 0], ny[:, -1] = self.y[:, 0], self.y[:, -1]
            elif self.topology == "polar":
                nx[:, 0], nx[:, -1] = self.x[:, 0], self.x[:, -1]
                ny[:, 0], ny[:, -1] = self.y[:, 0], self.y[:, -1]

        return Mesh(nx, ny, self.topology)

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

    # --- Individual curve extraction ---

    def rings(self, smooth: bool = True, points_per_ring: int = 120) -> list:
        """Extract individual rings as smooth curves (polar topology).

        Returns a list of np.ndarray, one per ring (column of the mesh).
        Each is a closed curve. Useful for assigning rings to different layers/colors.
        """
        n_spokes, n_rings = self.shape
        curves = []
        for j in range(n_rings):
            ring_x = np.concatenate([self.x[:, j], self.x[:1, j]])
            ring_y = np.concatenate([self.y[:, j], self.y[:1, j]])
            if smooth and n_spokes >= 4:
                t = np.linspace(0, 1, len(ring_x))
                t_fine = np.linspace(0, 1, points_per_ring + 1)
                try:
                    cs_x = CubicSpline(t, ring_x, bc_type='periodic')
                    cs_y = CubicSpline(t, ring_y, bc_type='periodic')
                    curves.append(np.column_stack([cs_x(t_fine), cs_y(t_fine)]))
                    continue
                except Exception:
                    pass
            curves.append(np.column_stack([ring_x, ring_y]))
        return curves

    def spokes(self, smooth: bool = True, points_per_spoke: int = 100) -> list:
        """Extract individual spokes as smooth curves (polar topology).

        Returns a list of np.ndarray, one per spoke (row of the mesh).
        Each is a radial line from inner to outer ring.
        """
        n_spokes, n_rings = self.shape
        curves = []
        for i in range(n_spokes):
            if smooth and n_rings >= 4:
                t = np.linspace(0, 1, n_rings)
                t_fine = np.linspace(0, 1, points_per_spoke)
                cs_x = CubicSpline(t, self.x[i, :])
                cs_y = CubicSpline(t, self.y[i, :])
                curves.append(np.column_stack([cs_x(t_fine), cs_y(t_fine)]))
            else:
                curves.append(np.column_stack([self.x[i, :], self.y[i, :]]))
        return curves

    def rows(self, smooth: bool = True, points_per_row: int = 100) -> list:
        """Extract individual rows as smooth curves (rect topology).

        Returns a list of np.ndarray, one per horizontal grid line.
        """
        n_rows, n_cols = self.shape
        curves = []
        for i in range(n_rows):
            if smooth and n_cols >= 4:
                t = np.linspace(0, 1, n_cols)
                t_fine = np.linspace(0, 1, points_per_row)
                cs_x = CubicSpline(t, self.x[i, :])
                cs_y = CubicSpline(t, self.y[i, :])
                curves.append(np.column_stack([cs_x(t_fine), cs_y(t_fine)]))
            else:
                curves.append(np.column_stack([self.x[i, :], self.y[i, :]]))
        return curves

    def cols(self, smooth: bool = True, points_per_col: int = 100) -> list:
        """Extract individual columns as smooth curves (rect topology).

        Returns a list of np.ndarray, one per vertical grid line.
        """
        n_rows, n_cols = self.shape
        curves = []
        for j in range(n_cols):
            if smooth and n_rows >= 4:
                t = np.linspace(0, 1, n_rows)
                t_fine = np.linspace(0, 1, points_per_col)
                cs_x = CubicSpline(t, self.x[:, j])
                cs_y = CubicSpline(t, self.y[:, j])
                curves.append(np.column_stack([cs_x(t_fine), cs_y(t_fine)]))
            else:
                curves.append(np.column_stack([self.x[:, j], self.y[:, j]]))
        return curves

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

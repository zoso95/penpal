"""Wallpaper groups — periodic tilings with crystallographic symmetries.

Ported from gpyplotter's WallpaperGroup class. Supports 8 patterns for
square/rectangular lattices using orbifold notation.

    from penpal.symmetry import WallpaperGroup

    wg = WallpaperGroup(origin=(0, 0), b1=(0, 1), b2=(1, 0))
    domain = wg.fundamental_domain('*442')
    art = some_generator(domain)
    tiled = wg.generate(art, '*442', nx=8, ny=8)
"""

from __future__ import annotations

import numpy as np

from penpal.core.paths import Paths


class WallpaperGroup:
    """Wallpaper group symmetry for periodic tilings.

    Defines a lattice cell via origin + two basis vectors, classifies the
    lattice shape, and provides methods to fill the cell with symmetry
    operations and tile it across a grid.

    Parameters
    ----------
    origin : array-like
        Origin corner of the lattice cell.
    b1 : array-like
        First basis vector (conventionally "vertical").
    b2 : array-like
        Second basis vector (conventionally "horizontal").
    """

    PATTERNS = {
        "square": ["o", "2222", "*2222", "442", "4*2", "*442", "2*22", "22x"],
        "rectangle": ["o", "2222", "*2222", "22x"],
        "rhombus": ["o", "2222"],
    }

    def __init__(self, origin, b1, b2):
        self.origin = np.asarray(origin, dtype=np.float64)
        self.b1 = np.asarray(b1, dtype=np.float64)
        self.b2 = np.asarray(b2, dtype=np.float64)

        dp = float(np.dot(self.b1, self.b2))
        l1 = float(np.linalg.norm(self.b1))
        l2 = float(np.linalg.norm(self.b2))

        EPS = 1e-9
        orthogonal = abs(dp) < EPS
        equal_length = abs(l1 - l2) < EPS

        if equal_length and orthogonal:
            self.shape = "square"
        elif orthogonal:
            self.shape = "rectangle"
        elif equal_length:
            self.shape = "rhombus"
        else:
            raise ValueError(
                f"Unsupported lattice: |b1|={l1:.4f}, |b2|={l2:.4f}, "
                f"dot={dp:.4f}. Need square, rectangle, or rhombus."
            )

        self.corners = np.array([
            self.origin,
            self.origin + self.b2,
            self.origin + self.b1 + self.b2,
            self.origin + self.b1,
        ])
        self.center = self.origin + 0.5 * (self.b1 + self.b2)
        self.valid_patterns = self.PATTERNS.get(self.shape, ["o"])

    @property
    def cell_polygon(self) -> np.ndarray:
        """Closed polygon for the unit cell."""
        return np.vstack([self.corners, self.corners[:1]])

    def fundamental_domain(self, pattern: str) -> np.ndarray:
        """Return the fundamental domain polygon for the given pattern.

        Parameters
        ----------
        pattern : str
            Orbifold notation: 'o', '2222', '*2222', '442', '4*2',
            '*442', '2*22', '22x'.

        Returns
        -------
        np.ndarray
            (M, 2) polygon vertices of the fundamental domain.
        """
        self._validate_pattern(pattern)

        o = self.origin
        b1, b2 = self.b1, self.b2
        center = self.center

        if pattern == "o":
            return self.corners.copy()
        elif pattern == "2222":
            if self.shape == "rhombus":
                return np.array([o, o + b2, o + b2 + b1])
            else:
                return np.array([o, o + b2, o + b2 + b1 / 2, o + b1 / 2])
        elif pattern == "*2222":
            return np.array([o, o + b2 / 2, o + b2 / 2 + b1 / 2, o + b1 / 2])
        elif pattern == "442":
            return np.array([o, o + b2 / 2, center, o + b1 / 2])
        elif pattern == "4*2":
            return np.array([o + b2 / 2, center, o + b1 / 2])
        elif pattern == "*442":
            return np.array([o, o + b2 / 2, center])
        elif pattern == "2*22":
            return np.array([o, o + b2, center])
        elif pattern == "22x":
            return np.array([o + b2 / 2, o + b2 + b1 / 2, o + b1 / 2])
        else:
            raise ValueError(f"Unknown pattern: {pattern!r}")

    def complete(self, paths: Paths, pattern: str) -> Paths:
        """Apply symmetry operations to fill one cell from the fundamental domain.

        Parameters
        ----------
        paths : Paths
            Art inside the fundamental domain.
        pattern : str
            Orbifold notation pattern name.

        Returns
        -------
        Paths
            Completed cell with all symmetry copies.
        """
        transforms = self._symmetry_transforms(pattern)
        all_lines = []
        for matrix in transforms:
            all_lines.extend(paths.transform(matrix).lines)
        result = Paths(all_lines)

        # Glide reflection patterns can produce geometry outside the cell
        if pattern in ("22x",):
            result = result.clip(self.cell_polygon)

        return result

    def tile(self, cell: Paths, nx: int = 3, ny: int = 3,
             bounds=None) -> Paths:
        """Tile a completed cell across a grid via translation.

        Parameters
        ----------
        cell : Paths
            A completed cell (output of complete()).
        nx, ny : int
            Number of repetitions in b2 and b1 directions.
        bounds : tuple, optional
            (xmin, ymin, xmax, ymax) — clip the tiled result.
        """
        all_lines = []
        for i in range(nx):
            for j in range(ny):
                offset = i * self.b2 + j * self.b1
                translated = cell.translate(float(offset[0]), float(offset[1]))
                all_lines.extend(translated.lines)
        result = Paths(all_lines)
        if bounds is not None:
            result = result.clip_rect(*bounds)
        return result

    def generate(self, paths: Paths, pattern: str,
                 nx: int = 3, ny: int = 3,
                 bounds=None,
                 clip_to_domain: bool = True) -> Paths:
        """Convenience: clip to domain + complete + tile in one call.

        Parameters
        ----------
        paths : Paths
            Input art (doesn't need to be pre-clipped).
        pattern : str
            Orbifold notation.
        nx, ny : int
            Tile repetitions.
        bounds : tuple, optional
            Clip result to bounding box.
        clip_to_domain : bool
            If True, clip paths to fundamental domain before symmetry.
        """
        if clip_to_domain:
            domain = self.fundamental_domain(pattern)
            domain_closed = np.vstack([domain, domain[:1]])
            paths = paths.clip(domain_closed)

        cell = self.complete(paths, pattern)
        return self.tile(cell, nx, ny, bounds=bounds)

    def _validate_pattern(self, pattern: str):
        """Check that the pattern is valid for this lattice shape."""
        if pattern not in self.valid_patterns:
            raise ValueError(
                f"Pattern {pattern!r} not valid for {self.shape} lattice. "
                f"Valid: {self.valid_patterns}"
            )

    def _symmetry_transforms(self, pattern: str) -> list:
        """Return list of 3x3 matrices that fill the cell from fundamental domain."""
        from penpal.core.transforms import rotate, reflect, translate

        self._validate_pattern(pattern)

        o = self.origin
        b1, b2 = self.b1, self.b2
        center = self.center
        I = np.eye(3)

        if pattern == "o":
            return [I]

        elif pattern == "2222":
            return [I, rotate(180, center=center)]

        elif pattern == "*2222":
            mid_b2 = o + b2 / 2
            mid_b1 = o + b1 / 2
            return [
                I,
                reflect(90, point=mid_b2),   # vertical mirror
                reflect(0, point=mid_b1),     # horizontal mirror
                rotate(180, center=center),
            ]

        elif pattern == "442":
            return [rotate(i * 90, center=center) for i in range(4)]

        elif pattern == "4*2":
            mid_b2 = o + b2 / 2
            base = [I, reflect(135, point=mid_b2)]
            transforms = []
            for i in range(4):
                rot = rotate(i * 90, center=center)
                for b in base:
                    transforms.append(rot @ b)
            return transforms

        elif pattern == "*442":
            mid_b2 = o + b2 / 2
            base = [I, reflect(90, point=mid_b2)]
            transforms = []
            for i in range(4):
                rot = rotate(i * 90, center=center)
                for b in base:
                    transforms.append(rot @ b)
            return transforms

        elif pattern == "2*22":
            ref1 = [I, reflect(45, point=o)]
            transforms = list(ref1)
            for r in ref1:
                transforms.append(reflect(135, point=center) @ r)
            return transforms

        elif pattern == "22x":
            mid_b2 = o + b2 / 2
            flip = reflect(0, point=mid_b2)
            g1_offset = b1 / 2 + b2 / 2
            g2_offset = b1 / 2 - b2 / 2
            glide1 = translate(float(g1_offset[0]), float(g1_offset[1])) @ flip
            glide2 = translate(float(g2_offset[0]), float(g2_offset[1])) @ flip
            bottom = [I, glide1, glide2]
            rot180 = rotate(180, center=center)
            return bottom + [rot180 @ b for b in bottom]

        raise ValueError(f"Unknown pattern: {pattern!r}")

    def __repr__(self):
        return (f"WallpaperGroup(shape={self.shape!r}, "
                f"patterns={self.valid_patterns})")

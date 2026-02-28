"""Strange attractor generators.

Includes both random matrix attractors (from the old dynamic system notebooks)
and classic named attractors (Lorenz, Rossler, etc).

All generators return Paths.
"""

from __future__ import annotations

import numpy as np

from penpal.core.paths import Paths


def random_attractor(
    n_steps: int = 10000,
    dt: float = 0.15,
    seed: int | None = None,
    n_funcs: int = 6,
) -> Paths:
    """Generate a random strange attractor via nonlinear matrix iteration.

    Creates a 2D trajectory by iterating:
        V = [F1*x, F2*x]  (element-wise)
        VP = sin(V)^P
        dx = M @ VP

    where F1, F2 are random frequency vectors, P are random powers (1 or 2),
    and M is a random mixing matrix.

    Parameters
    ----------
    n_steps : int
        Number of iteration steps.
    dt : float
        Time step size. Smaller = smoother, larger = more chaotic.
    seed : int, optional
        Random seed for reproducibility.
    n_funcs : int
        Number of nonlinear basis functions (default 6).

    Returns
    -------
    Paths
        Single polyline tracing the attractor.
    """
    rng = np.random.default_rng(seed)

    dim = 3
    F1 = rng.uniform(-2, 2, size=dim)
    F2 = rng.uniform(-2, 2, size=dim)
    P = rng.choice([1, 2], size=n_funcs)
    M = rng.uniform(-1, 1, size=(2, n_funcs))

    x = rng.uniform(-0.1, 0.1, size=dim)
    points = np.empty((n_steps, 2))

    for i in range(n_steps):
        v1 = F1 * x
        v2 = F2 * x
        v = np.concatenate([v1, v2])[:n_funcs]
        vp = np.sign(np.sin(v)) * np.abs(np.sin(v)) ** P
        dx = M @ vp
        x[:2] += dt * dx
        x[2] += dt
        points[i] = x[:2]

        if np.any(np.abs(x[:2]) > 100):
            points = points[:i]
            break

    if len(points) < 2:
        return Paths()

    return Paths([points])


def lorenz(
    n_steps: int = 10000,
    dt: float = 0.005,
    sigma: float = 10.0,
    rho: float = 28.0,
    beta: float = 8 / 3,
    x0: tuple = (1.0, 1.0, 1.0),
    projection: str = "xz",
) -> Paths:
    """Generate a Lorenz attractor trajectory.

    Parameters
    ----------
    n_steps : int
        Number of integration steps.
    dt : float
        Time step for Euler integration.
    sigma, rho, beta : float
        Lorenz system parameters.
    x0 : tuple
        Initial condition (x, y, z).
    projection : str
        Which 2D projection to use: 'xy', 'xz', or 'yz'.

    Returns
    -------
    Paths
        Single polyline tracing the attractor in 2D projection.
    """
    points = np.empty((n_steps, 3))
    x, y, z = x0

    for i in range(n_steps):
        points[i] = [x, y, z]
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        x += dt * dx
        y += dt * dy
        z += dt * dz

    proj_map = {"xy": (0, 1), "xz": (0, 2), "yz": (1, 2)}
    a, b = proj_map.get(projection, (0, 2))
    return Paths([points[:, [a, b]]])


def rossler(
    n_steps: int = 20000,
    dt: float = 0.01,
    a: float = 0.2,
    b: float = 0.2,
    c: float = 5.7,
    x0: tuple = (1.0, 1.0, 0.0),
    projection: str = "xy",
) -> Paths:
    """Generate a Rossler attractor trajectory.

    Parameters
    ----------
    n_steps : int
        Number of integration steps.
    dt : float
        Time step for Euler integration.
    a, b, c : float
        Rossler system parameters.
    x0 : tuple
        Initial condition (x, y, z).
    projection : str
        Which 2D projection to use: 'xy', 'xz', or 'yz'.

    Returns
    -------
    Paths
        Single polyline tracing the attractor in 2D projection.
    """
    points = np.empty((n_steps, 3))
    x, y, z = x0

    for i in range(n_steps):
        points[i] = [x, y, z]
        dx = -y - z
        dy = x + a * y
        dz = b + z * (x - c)
        x += dt * dx
        y += dt * dy
        z += dt * dz

    proj_map = {"xy": (0, 1), "xz": (0, 2), "yz": (1, 2)}
    ai, bi = proj_map.get(projection, (0, 1))
    return Paths([points[:, [ai, bi]]])


def clifford(
    n_steps: int = 100000,
    a: float = -1.4,
    b: float = 1.6,
    c: float = 1.0,
    d: float = 0.7,
    x0: tuple = (0.1, 0.1),
) -> Paths:
    """Generate a Clifford attractor.

    Iterates: x' = sin(a*y) + c*cos(a*x), y' = sin(b*x) + d*cos(b*y)

    Parameters
    ----------
    n_steps : int
        Number of iteration steps.
    a, b, c, d : float
        Clifford attractor parameters.
    x0 : tuple
        Initial condition (x, y).

    Returns
    -------
    Paths
        Single polyline tracing the attractor.
    """
    points = np.empty((n_steps, 2))
    x, y = x0

    for i in range(n_steps):
        points[i] = [x, y]
        x_new = np.sin(a * y) + c * np.cos(a * x)
        y_new = np.sin(b * x) + d * np.cos(b * y)
        x, y = x_new, y_new

    return Paths([points])


def de_jong(
    n_steps: int = 100000,
    a: float = -2.24,
    b: float = 0.43,
    c: float = -0.65,
    d: float = -2.43,
    x0: tuple = (0.1, 0.1),
) -> Paths:
    """Generate a Peter de Jong attractor.

    Iterates: x' = sin(a*y) - cos(b*x), y' = sin(c*x) - cos(d*y)

    Parameters
    ----------
    n_steps : int
        Number of iteration steps.
    a, b, c, d : float
        De Jong attractor parameters.
    x0 : tuple
        Initial condition (x, y).

    Returns
    -------
    Paths
        Single polyline tracing the attractor.
    """
    points = np.empty((n_steps, 2))
    x, y = x0

    for i in range(n_steps):
        points[i] = [x, y]
        x_new = np.sin(a * y) - np.cos(b * x)
        y_new = np.sin(c * x) - np.cos(d * y)
        x, y = x_new, y_new

    return Paths([points])


def bedhead(
    n_steps: int = 100000,
    a: float = -0.81,
    b: float = -0.92,
    x0: tuple = (1.0, 1.0),
) -> Paths:
    """Generate a Bedhead attractor.

    Iterates: x' = sin(x*y/b)*y + cos(a*x-y), y' = x + sin(y)/b

    Parameters
    ----------
    n_steps : int
        Number of iteration steps.
    a, b : float
        Bedhead attractor parameters.
    x0 : tuple
        Initial condition (x, y).

    Returns
    -------
    Paths
        Single polyline tracing the attractor.
    """
    points = np.empty((n_steps, 2))
    x, y = x0

    for i in range(n_steps):
        points[i] = [x, y]
        x_new = np.sin(x * y / b) * y + np.cos(a * x - y)
        y_new = x + np.sin(y) / b
        x, y = x_new, y_new

    return Paths([points])

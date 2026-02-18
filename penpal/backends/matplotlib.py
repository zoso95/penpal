"""Matplotlib rendering backend for Drawing."""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

if TYPE_CHECKING:
    from penpal.core.drawing import Drawing


def render(drawing: Drawing, ax=None, figsize=None, grid=None, **kwargs):
    """Render a Drawing using matplotlib.

    Parameters
    ----------
    drawing : Drawing
    ax : matplotlib Axes, optional
    figsize : tuple, optional — defaults to (width, height) from drawing
    grid : bool, optional — override drawing.show_grid
    """
    if figsize is None:
        figsize = (drawing.width, drawing.height)

    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)
    else:
        fig = ax.figure

    show_grid = grid if grid is not None else drawing.show_grid

    # Draw grid lines first (behind everything)
    if show_grid:
        _draw_grid(ax, drawing.width, drawing.height)

    # Draw each layer
    for layer in drawing.layers:
        if not layer.lines:
            continue
        segments = [line[:, :2] for line in layer.lines]
        lc = LineCollection(
            segments,
            colors=layer.style.color,
            linewidths=layer.style.linewidth,
            alpha=layer.style.alpha,
            zorder=2,
        )
        ax.add_collection(lc)

    ax.set_xlim(0, drawing.width)
    ax.set_ylim(0, drawing.height)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xlabel(drawing.units)
    ax.set_ylabel(drawing.units)

    plt.tight_layout()
    return fig, ax


def _draw_grid(ax, width, height):
    """Draw reference grid lines."""
    # Light grid every 1 unit
    for x in np.arange(0, width + 0.01, 1):
        ax.axvline(x, color="#e0e0e0", linewidth=0.3, zorder=0)
    for y in np.arange(0, height + 0.01, 1):
        ax.axhline(y, color="#e0e0e0", linewidth=0.3, zorder=0)
    # Heavier grid every 5 units
    for x in np.arange(0, width + 0.01, 5):
        ax.axvline(x, color="#c0c0c0", linewidth=0.6, zorder=0)
    for y in np.arange(0, height + 0.01, 5):
        ax.axhline(y, color="#c0c0c0", linewidth=0.6, zorder=0)
    # Border
    ax.plot(
        [0, width, width, 0, 0],
        [0, 0, height, height, 0],
        color="#999999",
        linewidth=1.0,
        zorder=0,
    )

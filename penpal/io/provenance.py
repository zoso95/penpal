"""Provenance — capture and save the source code + metadata that produced a drawing.

When you call drawing.save('output/piece.svg'), provenance automatically creates:

    output/piece.svg              # The artwork
    output/piece_provenance.json  # Metadata (timestamp, git hash, layer info, params)
    output/piece_source.py        # Copy of the generating script (or notebook cells)

This makes every output reproducible — you can always find the exact code
and parameters that produced a given piece.
"""

from __future__ import annotations

import datetime
import inspect
import json
import os
import shutil
import subprocess
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from penpal.core.drawing import Drawing


def capture_provenance(drawing: Drawing,
                       params: Dict[str, Any] = None) -> dict:
    """Build a provenance metadata dict for a drawing.

    Parameters
    ----------
    drawing : Drawing
        The drawing being saved.
    params : dict, optional
        User-specified parameters to record (seeds, densities, etc.).

    Returns
    -------
    dict
        Provenance metadata ready for JSON serialization.
    """
    import penpal

    meta = {
        "created": datetime.datetime.now().isoformat(),
        "penpal_version": penpal.__version__,
        "python_version": _python_version(),
        "git_hash": _git_hash(),
        "git_dirty": _git_dirty(),
        "drawing": {
            "width": drawing.width,
            "height": drawing.height,
            "units": drawing.units,
            "center": drawing.center,
            "layers": [
                {
                    "name": layer.name,
                    "color": layer.style.color,
                    "linewidth": layer.style.linewidth,
                    "num_lines": len(layer.paths),
                    "total_points": sum(len(l) for l in layer.paths.lines),
                }
                for layer in drawing.layers
            ],
        },
    }

    if params:
        meta["params"] = params

    return meta


def capture_source() -> Optional[str]:
    """Capture the source code of the calling script or notebook.

    Walks the call stack to find the outermost user script (not penpal internals).
    For .py files, reads the file. For notebooks, captures cell sources via
    IPython if available.

    Returns
    -------
    str or None
        Source code text, or None if it can't be captured.
    """
    # Try notebook first
    nb_source = _capture_notebook_source()
    if nb_source:
        return nb_source

    # Walk the stack to find the user's script
    script_path = _find_caller_script()
    if script_path and os.path.isfile(script_path):
        with open(script_path, "r") as f:
            return f.read()

    return None


def save_provenance(drawing: Drawing, svg_path: str,
                    params: Dict[str, Any] = None):
    """Save provenance files alongside an SVG.

    Creates:
        {base}_provenance.json — metadata
        {base}_source.py — source code (if capturable)

    Parameters
    ----------
    drawing : Drawing
        The drawing being saved.
    svg_path : str
        Path to the SVG file (used to derive provenance file paths).
    params : dict, optional
        User-specified parameters to include in metadata.
    """
    base = svg_path.rsplit(".svg", 1)[0] if svg_path.endswith(".svg") else svg_path

    # Save metadata JSON
    meta = capture_provenance(drawing, params=params)
    json_path = f"{base}_provenance.json"
    with open(json_path, "w") as f:
        json.dump(meta, f, indent=2, default=str)

    # Save source code
    source = capture_source()
    if source:
        source_path = f"{base}_source.py"
        with open(source_path, "w") as f:
            f.write(source)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _python_version() -> str:
    import sys
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def _git_hash() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()[:12]
    except Exception:
        pass
    return None


def _git_dirty() -> Optional[bool]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return len(result.stdout.strip()) > 0
    except Exception:
        pass
    return None


def _find_caller_script() -> Optional[str]:
    """Walk the call stack to find the outermost .py file that isn't penpal."""
    penpal_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidate = None

    for frame_info in inspect.stack():
        filepath = frame_info.filename
        # Skip penpal internals, builtins, and interactive prompts
        if not filepath or filepath.startswith("<"):
            continue
        abs_path = os.path.abspath(filepath)
        if abs_path.startswith(penpal_dir):
            continue
        # Skip site-packages
        if "site-packages" in abs_path:
            continue
        candidate = abs_path

    return candidate


def _capture_notebook_source() -> Optional[str]:
    """Try to capture notebook cell sources from IPython/Jupyter."""
    try:
        ip = get_ipython()  # noqa: F821 — only exists in IPython/Jupyter
        cells = ip.history_manager.input_hist_parsed
        if not cells:
            return None

        # Build a script from all executed cells
        parts = []
        for i, cell in enumerate(cells):
            if not cell.strip():
                continue
            parts.append(f"# --- Cell {i} ---")
            parts.append(cell.rstrip())
            parts.append("")

        return "\n".join(parts) if parts else None
    except NameError:
        # Not in IPython/Jupyter
        return None
    except Exception:
        return None

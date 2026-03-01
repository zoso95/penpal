"""Auto-downloading image datasets for testing CV techniques.

Downloads and caches datasets locally on first use. Default cache
directory is ~/.penpal/datasets/.
"""

from __future__ import annotations

import os
import tarfile
import urllib.request
from pathlib import Path

import numpy as np

_DEFAULT_CACHE = Path.home() / ".penpal" / "datasets"

# Registry of known datasets
_DATASETS = {
    "dtd": {
        "url": "https://www.robots.ox.ac.uk/~vgg/data/dtd/download/dtd-r1.0.1.tar.gz",
        "subdir": "dtd/images",
        "description": "Describable Textures Dataset — 5640 images, 47 categories",
    },
}


def get_dataset_path(
    name: str = "dtd",
    cache_dir: str | Path | None = None,
) -> Path:
    """Get the local path to a dataset, downloading if needed.

    Parameters
    ----------
    name : str
        Dataset name (currently: 'dtd').
    cache_dir : path, optional
        Override default cache directory (~/.penpal/datasets/).

    Returns
    -------
    Path
        Directory containing the dataset images.
    """
    if name not in _DATASETS:
        raise ValueError(f"Unknown dataset '{name}'. Available: {list(_DATASETS.keys())}")

    info = _DATASETS[name]
    cache = Path(cache_dir) if cache_dir else _DEFAULT_CACHE
    dataset_dir = cache / name

    # Check if already extracted
    images_dir = cache / info["subdir"]
    if images_dir.exists() and any(images_dir.iterdir()):
        return images_dir

    # Download
    cache.mkdir(parents=True, exist_ok=True)
    tar_path = cache / f"{name}.tar.gz"

    if not tar_path.exists():
        print(f"Downloading {name} ({info['description']})...")
        print(f"  URL: {info['url']}")
        print(f"  Saving to: {tar_path}")
        urllib.request.urlretrieve(info["url"], tar_path, _progress_hook)
        print()  # newline after progress

    # Extract
    print(f"Extracting {name}...")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=cache)
    print(f"Done. Images at: {images_dir}")

    # Clean up tarball
    tar_path.unlink()

    return images_dir


def list_categories(name: str = "dtd", **kwargs) -> list[str]:
    """List available image categories in a dataset.

    Parameters
    ----------
    name : str
        Dataset name.

    Returns
    -------
    list of str
        Sorted category names.
    """
    path = get_dataset_path(name, **kwargs)
    return sorted(d.name for d in path.iterdir() if d.is_dir())


def list_images(
    name: str = "dtd",
    category: str | None = None,
    **kwargs,
) -> list[Path]:
    """List image file paths in a dataset.

    Parameters
    ----------
    name : str
        Dataset name.
    category : str, optional
        Filter to a specific category. If None, returns all.

    Returns
    -------
    list of Path
        Image file paths.
    """
    path = get_dataset_path(name, **kwargs)
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}

    if category:
        cat_dir = path / category
        if not cat_dir.exists():
            raise ValueError(
                f"Category '{category}' not found. "
                f"Available: {list_categories(name, **kwargs)}"
            )
        return sorted(p for p in cat_dir.iterdir() if p.suffix.lower() in exts)

    return sorted(p for p in path.rglob("*") if p.suffix.lower() in exts)


def load_random(
    name: str = "dtd",
    category: str | None = None,
    grayscale: bool = True,
    seed: int | None = None,
    **kwargs,
) -> tuple[np.ndarray, Path]:
    """Load a random image from a dataset.

    Parameters
    ----------
    name : str
        Dataset name.
    category : str, optional
        Filter to a specific category.
    grayscale : bool
        Convert to grayscale.
    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    (image, path) : tuple
        The loaded image array and its file path.
    """
    from penpal.cv.image import load

    images = list_images(name, category, **kwargs)
    if not images:
        raise RuntimeError(f"No images found in dataset '{name}'")

    rng = np.random.default_rng(seed)
    path = images[rng.integers(len(images))]
    return load(str(path), grayscale=grayscale), path


def _progress_hook(block_num, block_size, total_size):
    """Simple download progress display."""
    downloaded = block_num * block_size
    if total_size > 0:
        pct = min(100, downloaded * 100 // total_size)
        mb = downloaded / 1024 / 1024
        total_mb = total_size / 1024 / 1024
        print(f"\r  {mb:.0f}/{total_mb:.0f} MB ({pct}%)", end="", flush=True)

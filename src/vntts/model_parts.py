"""Utilities for splitting and merging large model files."""

from __future__ import annotations

import hashlib
from pathlib import Path

CHUNK_SIZE_BYTES = 80 * 1024 * 1024
DEFAULT_CHUNK_SIZE_MB = CHUNK_SIZE_BYTES // (1024 * 1024)


def _part_sort_key(path: Path) -> tuple[int, str]:
    suffix = path.suffix
    if suffix.startswith(".part"):
        tail = suffix.removeprefix(".part")
        if tail.isdigit():
            return int(tail), path.name
    name = path.name
    if ".part" in name:
        tail = name.rsplit(".part", 1)[-1]
        if tail.isdigit():
            return int(tail), name
    return 10**9, path.name


def find_part_files(target_file: str | Path) -> list[Path]:
    """Find part files for *target_file*.

    Supports both naming styles:
    - ``<target>.part1`` (e.g. ``banmai.onnx.part1``)
    - ``<stem>.part1`` (e.g. ``banmai.part1`` for ``banmai.onnx``)
    """
    target = Path(target_file)
    candidates = list(target.parent.glob(f"{target.name}.part*"))
    if not candidates and target.suffix:
        candidates = list(target.parent.glob(f"{target.stem}.part*"))
    return sorted(candidates, key=_part_sort_key)


def merge_parts_to_file(
    target_file: str | Path,
    *,
    overwrite: bool = False,
    expected_sha256: str | None = None,
) -> Path | None:
    """Merge split model parts into *target_file* if possible.

    Returns merged file path if merging happened, otherwise ``None``.
    """
    target = Path(target_file)
    if target.exists() and not overwrite:
        return None

    part_files = find_part_files(target)
    if not part_files:
        return None

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as merged:
        for part in part_files:
            with part.open("rb") as src:
                for chunk in iter(lambda: src.read(1024 * 1024), b""):
                    merged.write(chunk)

    if expected_sha256 is not None:
        actual_sha256 = compute_sha256(target)
        if actual_sha256 != expected_sha256.lower():
            target.unlink(missing_ok=True)
            raise ValueError(
                f"Checksum mismatch for {target}: "
                f"expected {expected_sha256}, got {actual_sha256}"
            )
    return target


def merge_all_parts_in_dir(model_dir: str | Path) -> list[Path]:
    """Merge every part-set in *model_dir* where full file is missing."""
    root = Path(model_dir)
    merged: list[Path] = []
    for part in sorted(root.glob("*.part*"), key=_part_sort_key):
        if ".part" not in part.name:
            continue
        base_name = part.name.rsplit(".part", 1)[0]

        if base_name.endswith(".onnx"):
            target = root / base_name
        else:
            # For convention like banmai.part1 => banmai.onnx
            target = root / f"{base_name}.onnx"

        if target.exists():
            continue

        result = merge_parts_to_file(target)
        if result is not None:
            merged.append(result)
    return merged


def split_file(
    source_file: str | Path,
    output_dir: str | Path | None = None,
    chunk_size_mb: int = DEFAULT_CHUNK_SIZE_MB,
    use_stem_only: bool = True,
) -> list[Path]:
    """Split *source_file* into numbered `.partN` chunks."""
    source = Path(source_file)
    if not source.is_file():
        raise FileNotFoundError(f"Source file not found: {source}")

    chunk_size = chunk_size_mb * 1024 * 1024
    out_dir = Path(output_dir) if output_dir else source.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    prefix = source.stem if use_stem_only else source.name

    created: list[Path] = []
    with source.open("rb") as src:
        index = 1
        while True:
            data = src.read(chunk_size)
            if not data:
                break
            part_path = out_dir / f"{prefix}.part{index:03d}"
            part_path.write_bytes(data)
            created.append(part_path)
            index += 1

    if not created:
        raise RuntimeError(f"No part created from source file: {source}")
    return created


def compute_sha256(file_path: str | Path) -> str:
    """Return SHA256 hash for *file_path*."""
    path = Path(file_path)
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def resolve_model_dir(
    model_dir: str | Path | None = None,
    default_subdir: str = "banmai",
) -> Path:
    """Resolve model directory path, checking multiple locations.

    Searches in order:
    1. User-provided path (if exists)
    2. Package installation directory (`vntts/models/<default_subdir>`)
    3. Relative path from current working directory (`models/<default_subdir>`)
    4. Raises error if not found

    Parameters
    ----------
    model_dir : str | Path | None
        Explicit model directory path. If None, uses default search.
    default_subdir : str
        Default subdirectory name (e.g., "banmai" or "asr/sherpa-onnx-...")

    Returns
    -------
    Path
        Resolved model directory path

    Raises
    ------
    FileNotFoundError
        If model directory not found in any location
    """
    # If user provided explicit path, use it
    if model_dir is not None:
        path = Path(model_dir)
        if path.is_dir():
            return path
        # User provided invalid path - error out
        raise FileNotFoundError(f"Model directory not found: {path}")

    # Try Package Installation Directory
    # Models are installed alongside the vntts package
    package_dir = Path(__file__).parent.parent / "models" / default_subdir
    if package_dir.is_dir():
        return package_dir

    # Try Current Working Directory (development)
    cwd_dir = Path.cwd() / "models" / default_subdir
    if cwd_dir.is_dir():
        return cwd_dir

    # Try relative to parent of package (for editable installs)
    proj_dir = Path(__file__).parent.parent.parent / "models" / default_subdir
    if proj_dir.is_dir():
        return proj_dir

    # Not found anywhere
    raise FileNotFoundError(
        f"Model directory not found for '{default_subdir}'.\n"
        f"Searched:\n"
        f"  1. {package_dir}\n"
        f"  2. {cwd_dir}\n"
        f"  3. {proj_dir}\n"
        f"Please provide explicit path via model_dir parameter or ensure "
        f"models are in the package directory."
    )

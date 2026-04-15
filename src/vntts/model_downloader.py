"""Utilities for downloading and preparing model assets."""

from __future__ import annotations

import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Final
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import zipfile

DEFAULT_MODELS_URL: Final[str] = (
    "https://github.com/Devhub-Solutions/VNTTS/releases/download/"
    "untagged-8615407a8a6bd4bb7ace/models.zip"
)
DEFAULT_MODELS_ROOT: Final[str] = "models"
DEFAULT_DOWNLOAD_TIMEOUT_SECONDS: Final[float] = 120.0
DEFAULT_MAX_RETRIES: Final[int] = 3
CHUNK_SIZE: Final[int] = 1024 * 1024


def _log(message: str) -> None:
    if os.getenv("VNTTS_MODEL_DOWNLOAD_LOG", "1") != "0":
        print(f"[vntts-models] {message}")


def _models_root() -> Path:
    configured = os.getenv("VNTTS_MODELS_DIR", DEFAULT_MODELS_ROOT)
    return Path(configured).expanduser().resolve()


def _models_url() -> str:
    return os.getenv("VNTTS_MODELS_URL", DEFAULT_MODELS_URL)


def _download_timeout() -> float:
    raw = os.getenv("VNTTS_MODEL_DOWNLOAD_TIMEOUT_SECONDS")
    if not raw:
        return DEFAULT_DOWNLOAD_TIMEOUT_SECONDS
    try:
        return float(raw)
    except ValueError:
        return DEFAULT_DOWNLOAD_TIMEOUT_SECONDS


def _max_retries() -> int:
    raw = os.getenv("VNTTS_MODEL_DOWNLOAD_RETRIES")
    if not raw:
        return DEFAULT_MAX_RETRIES
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_MAX_RETRIES


def _stream_download_with_resume(url: str, destination: Path) -> None:
    partial = destination.with_suffix(destination.suffix + ".part")
    total_size: int | None = None

    for attempt in range(1, _max_retries() + 1):
        try:
            existing_size = partial.stat().st_size if partial.exists() else 0
            headers = {"User-Agent": "vntts-model-downloader/1.0"}
            if existing_size > 0:
                headers["Range"] = f"bytes={existing_size}-"

            request = Request(url, headers=headers)
            with urlopen(request, timeout=_download_timeout()) as response:
                status = getattr(response, "status", None)
                accept_ranges = response.headers.get("Accept-Ranges", "")
                content_range = response.headers.get("Content-Range")
                content_length = response.headers.get("Content-Length")

                mode = "ab" if existing_size > 0 and status == 206 else "wb"
                if mode == "wb" and existing_size > 0:
                    _log("Server did not honor Range request; restarting download")
                    existing_size = 0

                if content_range:
                    # e.g. "bytes 100-999/1000"
                    total_part = content_range.split("/")[-1]
                    if total_part.isdigit():
                        total_size = int(total_part)
                elif content_length and content_length.isdigit():
                    total_size = existing_size + int(content_length)

                downloaded = existing_size
                last_report = time.time()
                with partial.open(mode) as out:
                    while True:
                        chunk = response.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        out.write(chunk)
                        downloaded += len(chunk)

                        now = time.time()
                        if now - last_report >= 1:
                            if total_size:
                                pct = (downloaded / total_size) * 100
                                _log(f"Downloading models.zip: {pct:.1f}%")
                            else:
                                _log(f"Downloading models.zip: {downloaded} bytes")
                            last_report = now

                if total_size and partial.stat().st_size != total_size:
                    raise IOError(
                        "Downloaded size mismatch "
                        f"({partial.stat().st_size} != {total_size})"
                    )

                partial.replace(destination)
                return

        except (URLError, HTTPError, TimeoutError, OSError) as exc:
            if attempt >= _max_retries():
                raise RuntimeError(
                    f"Failed to download models after {attempt} attempts"
                ) from exc
            sleep_s = min(2**attempt, 10)
            _log(f"Download attempt {attempt} failed ({exc}); retrying in {sleep_s}s")
            time.sleep(sleep_s)


def _safe_extract(zip_path: Path, dest_dir: Path) -> None:
    with zipfile.ZipFile(zip_path, "r") as zf:
        bad_file = zf.testzip()
        if bad_file is not None:
            raise RuntimeError(f"Zip integrity check failed at {bad_file}")

        for member in zf.infolist():
            extracted_path = (dest_dir / member.filename).resolve()
            if not str(extracted_path).startswith(str(dest_dir.resolve())):
                raise RuntimeError(f"Unsafe path detected in zip: {member.filename}")

        zf.extractall(dest_dir)


def download_and_prepare_models() -> Path:
    """Ensure models exist locally; download and extract if missing.

    Environment variables
    ---------------------
    - ``VNTTS_MODELS_DIR``: root directory where models are stored.
    - ``VNTTS_MODELS_URL``: URL for ``models.zip``.
    - ``VNTTS_MODEL_DOWNLOAD_TIMEOUT_SECONDS``: network timeout.
    - ``VNTTS_MODEL_DOWNLOAD_RETRIES``: retry attempts.
    - ``VNTTS_MODEL_DOWNLOAD_LOG``: set ``0`` to disable progress logs.
    """
    models_root = _models_root()
    if models_root.is_dir() and any(models_root.iterdir()):
        return models_root

    models_root.parent.mkdir(parents=True, exist_ok=True)
    url = _models_url()

    with tempfile.TemporaryDirectory(prefix="vntts-models-") as tmp_dir:
        temp_zip = Path(tmp_dir) / "models.zip"

        _log(f"Models not found at {models_root}; downloading from {url}")
        _stream_download_with_resume(url, temp_zip)

        temp_extract_dir = Path(tmp_dir) / "extract"
        temp_extract_dir.mkdir(parents=True, exist_ok=True)
        _safe_extract(temp_zip, temp_extract_dir)

        candidate_root = temp_extract_dir
        nested_models = temp_extract_dir / "models"
        if nested_models.is_dir() and any(nested_models.iterdir()):
            candidate_root = nested_models

        if models_root.exists():
            shutil.rmtree(models_root)
        shutil.move(str(candidate_root), str(models_root))

        _log(f"Models prepared in {models_root}")

    return models_root

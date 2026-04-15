from __future__ import annotations

import io
from pathlib import Path
import zipfile

from vntts.model_downloader import download_and_prepare_models


def _build_zip_bytes() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("models/banmai/banmai.onnx", b"dummy")
        zf.writestr("models/banmai/banmai.onnx.json", "{}")
        zf.writestr("models/asr/sherpa-onnx-zipformer-vi-2025-04-20/tokens.txt", "a")
    return buf.getvalue()


class _FakeResponse:
    def __init__(self, payload: bytes):
        self._io = io.BytesIO(payload)
        self.headers = {"Content-Length": str(len(payload))}
        self.status = 200

    def read(self, size: int = -1) -> bytes:
        return self._io.read(size)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_download_and_prepare_models_idempotent(tmp_path, monkeypatch):
    models_root = tmp_path / "models"
    monkeypatch.setenv("VNTTS_MODELS_DIR", str(models_root))

    call_count = {"n": 0}

    def _fake_urlopen(request, timeout):
        _ = request, timeout
        call_count["n"] += 1
        return _FakeResponse(_build_zip_bytes())

    monkeypatch.setattr("vntts.model_downloader.urlopen", _fake_urlopen)

    first = download_and_prepare_models()
    second = download_and_prepare_models()

    assert first == models_root
    assert second == models_root
    assert call_count["n"] == 1
    assert (models_root / "banmai" / "banmai.onnx").is_file()


def test_download_retries_and_cleans_partial(tmp_path, monkeypatch):
    models_root = tmp_path / "models"
    monkeypatch.setenv("VNTTS_MODELS_DIR", str(models_root))
    monkeypatch.setenv("VNTTS_MODEL_DOWNLOAD_RETRIES", "2")

    state = {"n": 0}

    def _flaky_urlopen(request, timeout):
        _ = request, timeout
        state["n"] += 1
        if state["n"] == 1:
            raise OSError("temporary network issue")
        return _FakeResponse(_build_zip_bytes())

    monkeypatch.setattr("vntts.model_downloader.urlopen", _flaky_urlopen)

    result = download_and_prepare_models()

    assert result == models_root
    assert state["n"] == 2
    assert (models_root / "asr" / "sherpa-onnx-zipformer-vi-2025-04-20" / "tokens.txt").is_file()


def test_resume_download_uses_partial_file(tmp_path, monkeypatch):
    full_payload = _build_zip_bytes()
    split_at = 50

    class _RangeResponse(_FakeResponse):
        pass

    def _resume_urlopen(request, timeout):
        _ = timeout
        range_header = request.headers.get("Range")
        assert range_header == f"bytes={split_at}-"
        resp = _RangeResponse(full_payload[split_at:])
        resp.status = 206
        resp.headers = {
            "Content-Range": f"bytes {split_at}-{len(full_payload)-1}/{len(full_payload)}",
            "Content-Length": str(len(full_payload) - split_at),
            "Accept-Ranges": "bytes",
        }
        return resp

    monkeypatch.setattr("vntts.model_downloader.urlopen", _resume_urlopen)

    from vntts import model_downloader as md

    zip_target = tmp_path / "manual.zip"
    partial = zip_target.with_suffix(zip_target.suffix + ".part")
    partial.write_bytes(full_payload[:split_at])

    md._stream_download_with_resume("https://example.invalid/models.zip", zip_target)

    assert zip_target.read_bytes() == full_payload

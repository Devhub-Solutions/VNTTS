"""Tests for model split/merge helpers."""

from pathlib import Path

import pytest

from vntts.model_parts import compute_sha256, merge_parts_to_file, split_file


def test_split_file_uses_zero_padded_part_names(tmp_path: Path):
    source = tmp_path / "banmai.onnx"
    source.write_bytes(b"a" * (1024 * 1024 * 2 + 10))

    parts = split_file(source, chunk_size_mb=1)

    assert [p.name for p in parts] == [
        "banmai.part001",
        "banmai.part002",
        "banmai.part003",
    ]
    assert all(p.exists() for p in parts)


def test_merge_parts_with_checksum_verification(tmp_path: Path):
    source = tmp_path / "banmai.onnx"
    original = b"hello-world"
    source.write_bytes(original)
    checksum = compute_sha256(source)
    source.unlink()

    (tmp_path / "banmai.part001").write_bytes(b"hello-")
    (tmp_path / "banmai.part002").write_bytes(b"world")

    merged = merge_parts_to_file(source, expected_sha256=checksum)
    assert merged == source
    assert source.read_bytes() == original


def test_merge_parts_raises_on_checksum_mismatch(tmp_path: Path):
    target = tmp_path / "banmai.onnx"
    (tmp_path / "banmai.part001").write_bytes(b"abc")

    with pytest.raises(ValueError, match="Checksum mismatch"):
        merge_parts_to_file(target, expected_sha256="0" * 64)

    assert not target.exists()

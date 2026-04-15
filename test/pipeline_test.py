#!/usr/bin/env python3
"""End-to-end TTS->STT pipeline smoke test for Vietnamese models."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vntts import STT, TTS


def run_pipeline(
    text: str = "Xin chào, đây là bài kiểm tra hệ thống VNTTS.",
    output_wav: Path = Path("test/output_pipeline.wav"),
) -> str:
    tts = TTS(model_dir="models/banmai", model_name="banmai")
    stt = STT(model_dir="models/asr/sherpa-onnx-zipformer-vi-2025-04-20")

    output_wav.parent.mkdir(parents=True, exist_ok=True)
    tts.speak(text=text, output=output_wav)
    return stt.recognize_from_file(output_wav)


def main() -> None:
    text = "Xin chào, đây là bài kiểm tra hệ thống VNTTS."
    result = run_pipeline(text=text)
    print("Input :", text)
    print("STT   :", result)


if __name__ == "__main__":
    main()

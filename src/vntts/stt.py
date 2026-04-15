"""Speech-to-Text module using sherpa-onnx."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union
import wave

import numpy as np
import sherpa_onnx

from vntts.model_parts import merge_all_parts_in_dir


class STT:
    """Speech-to-Text wrapper around sherpa-onnx offline recognizer.

    Parameters
    ----------
    lang : str
        Language code for API compatibility.
    model_dir : str | Path | None
        Path to the cloned sherpa-onnx model directory.
    provider : str
        ONNX execution provider (default: ``"cpu"``).
    num_threads : int
        Number of inference threads.
    """

    def __init__(
        self,
        lang: str = "vi-VN",
        model_dir: Optional[Union[str, Path]] = None,
        provider: str = "cpu",
        num_threads: int = 1,
    ) -> None:
        self.lang = lang
        self.model_dir = Path(
            model_dir
            or "models/asr/sherpa-onnx-zipformer-vi-2025-04-20"
        )
        self.provider = provider
        self.num_threads = num_threads
        self._recognizer = None

    @staticmethod
    def _read_wave(wave_filename: Union[str, Path]) -> tuple[np.ndarray, int]:
        with wave.open(str(wave_filename), "rb") as f:
            if f.getnchannels() != 1:
                raise ValueError("Only mono WAV is supported")
            if f.getsampwidth() != 2:
                raise ValueError("Only 16-bit PCM WAV is supported")
            num_samples = f.getnframes()
            samples = f.readframes(num_samples)
            samples_int16 = np.frombuffer(samples, dtype=np.int16)
            samples_float32 = samples_int16.astype(np.float32) / 32768.0
            return samples_float32, f.getframerate()

    def _pick_model_file(self, pattern: str, prefer_int8: bool = False) -> Path:
        candidates = sorted(self.model_dir.glob(pattern))
        if not candidates:
            raise FileNotFoundError(
                f"Model file not found in {self.model_dir}: pattern '{pattern}'"
            )
        if prefer_int8:
            for c in candidates:
                if ".int8." in c.name:
                    return c
        return candidates[0]

    def _get_recognizer(self):
        if self._recognizer is not None:
            return self._recognizer

        merge_all_parts_in_dir(self.model_dir)

        tokens = self.model_dir / "tokens.txt"
        if not tokens.is_file():
            raise FileNotFoundError(f"tokens.txt not found in {self.model_dir}")

        # Try to find encoder, decoder, joiner with pattern matching
        # Zipformer models often have 'encoder-epoch-X-avg-Y.onnx' format
        encoder = self._pick_model_file("encoder*.onnx", prefer_int8=True)
        decoder = self._pick_model_file("decoder*.onnx")
        joiner = self._pick_model_file("joiner*.onnx", prefer_int8=True)

        self._recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=str(encoder),
            decoder=str(decoder),
            joiner=str(joiner),
            tokens=str(tokens),
            num_threads=self.num_threads,
            provider=self.provider,
        )
        return self._recognizer

    def recognize_from_file(
        self,
        audio_path: Union[str, Path],
        language: Optional[str] = None,
    ) -> str:
        """Recognize speech from an audio file.

        Parameters
        ----------
        audio_path : str | Path
            Path to a mono 16-bit PCM WAV file.
        language : str | None
            Kept for API compatibility (not used by offline model).

        Returns
        -------
        str
            The recognized text.

        Raises
        ------
        FileNotFoundError
            If *audio_path* does not exist.
        ValueError
            If audio format is not mono 16-bit PCM WAV.
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        _ = language or self.lang
        recognizer = self._get_recognizer()
        stream = recognizer.create_stream()
        samples, sample_rate = self._read_wave(audio_path)
        stream.accept_waveform(sample_rate, samples)
        recognizer.decode_stream(stream)
        return stream.result.text.strip()

    def recognize_from_microphone(
        self,
        language: Optional[str] = None,
        timeout: Optional[float] = None,
        phrase_time_limit: Optional[float] = None,
    ) -> str:
        """Microphone recognition is not supported in offline mode."""
        _ = language, timeout, phrase_time_limit
        raise NotImplementedError(
            "Microphone recognition is not implemented for ONNX offline mode. "
            "Please record to WAV and call recognize_from_file()."
        )

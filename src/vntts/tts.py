"""Text-to-Speech module using local Piper ONNX models."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Union

from piper import PiperVoice
from piper.config import SynthesisConfig

from vntts.model_parts import merge_parts_to_file, resolve_model_dir


class TTS:
    """Text-to-Speech wrapper around local Piper ONNX models.

    Parameters
    ----------
    lang : str
        Language folder (default: ``"vi"``).
    model_dir : str | Path | None
        Directory containing `.onnx` and `.onnx.json` model pairs.
    model_name : str | None
        Optional model base name to select from `model_dir`.
    use_cuda : bool
        Whether to use CUDA for inference.
    """

    def __init__(
        self,
        lang: str = "vi",
        model_dir: Union[str, Path, None] = None,
        model_name: str | None = None,
        use_cuda: bool = False,
    ) -> None:
        self.lang = lang
        # Resolve model directory with smart fallbacks
        if model_dir is not None:
            # User provided explicit path
            self.model_dir = Path(model_dir)
        else:
            # Try to find models directory
            # First try "banmai" (the included model), then fall back to language folder
            try:
                self.model_dir = resolve_model_dir(None, default_subdir="banmai")
            except FileNotFoundError:
                # Fall back to language-based directory
                lang_dir = f"tts-model/{lang}"
                try:
                    self.model_dir = resolve_model_dir(None, default_subdir=lang_dir)
                except FileNotFoundError:
                    # Last resort: use the old relative path (may not exist)
                    self.model_dir = Path(f"models/{lang_dir}")

        self.model_name = model_name
        self.use_cuda = use_cuda
        self._voice: PiperVoice | None = None
        self._loaded_model_name: str | None = None

    def _resolve_model_name(self) -> str:
        if self.model_name:
            model = self.model_name
            model_path = self.model_dir / f"{model}.onnx"
            merge_parts_to_file(model_path)
            config_path = self.model_dir / f"{model}.onnx.json"
            if model_path.is_file() and config_path.is_file():
                return model
            raise FileNotFoundError(
                f"Model pair not found: {model_path} and {config_path}"
            )

        for cfg in self.model_dir.glob("*.onnx.json"):
            merge_parts_to_file(self.model_dir / cfg.name.removesuffix(".json"))

        candidates = sorted(p.stem for p in self.model_dir.glob("*.onnx"))
        for model in candidates:
            if (self.model_dir / f"{model}.onnx.json").is_file():
                return model
        raise FileNotFoundError(
            "No valid model pair found. Expected files: "
            "{model}.onnx and {model}.onnx.json in "
            f"{self.model_dir}"
        )

    def _load_voice(self) -> PiperVoice:
        model_name = self._resolve_model_name()
        if self._voice is not None and self._loaded_model_name == model_name:
            return self._voice

        model_path = self.model_dir / f"{model_name}.onnx"
        config_path = self.model_dir / f"{model_name}.onnx.json"
        self._voice = PiperVoice.load(
            model_path=model_path,
            config_path=config_path,
            use_cuda=self.use_cuda,
        )
        self._loaded_model_name = model_name
        return self._voice

    def speak(
        self,
        text: str,
        output: Union[str, Path],
        slow: bool = False,
    ) -> Path:
        """Convert *text* to speech and save to an audio file.

        Parameters
        ----------
        text : str
            The text to convert to speech.
        output : str | Path
            Destination file path (WAV format).
        slow : bool
            If ``True``, generate with slower speed.

        Returns
        -------
        Path
            The path to the saved audio file.
        """
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)

        voice = self._load_voice()
        syn_config = SynthesisConfig(length_scale=1.25 if slow else None)
        with output.open("wb") as f:
            import wave

            with wave.open(f, "wb") as wav_file:
                voice.synthesize_wav(text=text, wav_file=wav_file, syn_config=syn_config)
        return output

    def speak_to_bytes(self, text: str, slow: bool = False) -> bytes:
        """Convert *text* to speech and return raw WAV bytes.

        Parameters
        ----------
        text : str
            The text to convert to speech.
        slow : bool
            If ``True``, the speech is generated at a slower speed.

        Returns
        -------
        bytes
            WAV audio data.
        """
        voice = self._load_voice()
        syn_config = SynthesisConfig(length_scale=1.25 if slow else None)
        buf = io.BytesIO()
        import wave

        with wave.open(buf, "wb") as wav_file:
            voice.synthesize_wav(text=text, wav_file=wav_file, syn_config=syn_config)
        return buf.getvalue()

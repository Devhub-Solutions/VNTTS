"""Text-to-Speech module using Piper ONNX models downloaded from GitHub Releases."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Union

from piper import PiperVoice
from piper.config import SynthesisConfig

from vntts.model_downloader import download_and_prepare_models
from vntts.model_parts import merge_parts_to_file


class TTS:
    """Text-to-Speech wrapper around Piper ONNX models.

    When *model_dir* is ``None``, models are automatically downloaded from
    GitHub Releases on first use.

    Parameters
    ----------
    lang : str
        Language folder (default: ``"vi"``).
    model_dir : str | Path | None
        Directory containing `.onnx` and `.onnx.json` model pairs.
        If ``None``, models are downloaded automatically.
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
        if model_dir is not None:
            self.model_dir = Path(model_dir)
        else:
            models_root = download_and_prepare_models()
            preferred_dir = models_root / "banmai"
            if preferred_dir.is_dir():
                self.model_dir = preferred_dir
            else:
                # Backward-compatible layout support
                lang_dir = models_root / "tts-model" / lang
                if lang_dir.is_dir():
                    self.model_dir = lang_dir
                else:
                    raise FileNotFoundError(
                        f"TTS model directory not found. Expected "
                        f"'{preferred_dir}' or '{lang_dir}' after download. "
                        f"Verify the models zip at the configured URL."
                    )

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

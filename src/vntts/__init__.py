"""VNTTS - Vietnamese Text-to-Speech and Speech-to-Text library."""

from vntts.tts import TTS
from vntts.stt import STT
from vntts.model_downloader import download_and_prepare_models

__version__ = "0.1.0"
__all__ = ["TTS", "STT", "download_and_prepare_models"]

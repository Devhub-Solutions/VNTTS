"""Text-to-Speech module using gTTS."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Union

from gtts import gTTS


class TTS:
    """Text-to-Speech wrapper around gTTS.

    Parameters
    ----------
    lang : str
        Language code for speech synthesis (default: ``"vi"`` for Vietnamese).
    """

    def __init__(self, lang: str = "vi") -> None:
        self.lang = lang

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
            Destination file path (MP3 format).
        slow : bool
            If ``True``, the speech is generated at a slower speed.

        Returns
        -------
        Path
            The path to the saved audio file.
        """
        output = Path(output)
        tts = gTTS(text=text, lang=self.lang, slow=slow)
        tts.save(str(output))
        return output

    def speak_to_bytes(self, text: str, slow: bool = False) -> bytes:
        """Convert *text* to speech and return raw MP3 bytes.

        Parameters
        ----------
        text : str
            The text to convert to speech.
        slow : bool
            If ``True``, the speech is generated at a slower speed.

        Returns
        -------
        bytes
            MP3 audio data.
        """
        tts = gTTS(text=text, lang=self.lang, slow=slow)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        return buf.getvalue()

"""Speech-to-Text module using SpeechRecognition."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

import speech_recognition as sr


class STT:
    """Speech-to-Text wrapper around the SpeechRecognition library.

    Parameters
    ----------
    lang : str
        Language code for speech recognition (default: ``"vi-VN"`` for
        Vietnamese).
    """

    def __init__(self, lang: str = "vi-VN") -> None:
        self.lang = lang
        self.recognizer = sr.Recognizer()

    def recognize_from_file(
        self,
        audio_path: Union[str, Path],
        language: Optional[str] = None,
    ) -> str:
        """Recognize speech from an audio file.

        Parameters
        ----------
        audio_path : str | Path
            Path to the audio file (WAV, FLAC, AIFF, or AIFF-C).
        language : str | None
            Override the default language for this call.

        Returns
        -------
        str
            The recognized text.

        Raises
        ------
        FileNotFoundError
            If *audio_path* does not exist.
        speech_recognition.UnknownValueError
            If speech could not be understood.
        speech_recognition.RequestError
            If there was an issue with the recognition service.
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        lang = language or self.lang

        with sr.AudioFile(str(audio_path)) as source:
            audio_data = self.recognizer.record(source)

        return self.recognizer.recognize_google(audio_data, language=lang)

    def recognize_from_microphone(
        self,
        language: Optional[str] = None,
        timeout: Optional[float] = None,
        phrase_time_limit: Optional[float] = None,
    ) -> str:
        """Recognize speech from the microphone.

        Parameters
        ----------
        language : str | None
            Override the default language for this call.
        timeout : float | None
            Maximum seconds to wait for speech to start.
        phrase_time_limit : float | None
            Maximum seconds for the phrase to last.

        Returns
        -------
        str
            The recognized text.

        Raises
        ------
        speech_recognition.UnknownValueError
            If speech could not be understood.
        speech_recognition.RequestError
            If there was an issue with the recognition service.
        """
        lang = language or self.lang

        with sr.Microphone() as source:
            audio_data = self.recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit,
            )

        return self.recognizer.recognize_google(audio_data, language=lang)

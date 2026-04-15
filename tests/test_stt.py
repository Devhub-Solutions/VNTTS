"""Unit tests for the STT module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vntts.stt import STT


class TestSTTInit:
    def test_default_language(self):
        stt = STT()
        assert stt.lang == "vi-VN"

    def test_custom_language(self):
        stt = STT(lang="en-US")
        assert stt.lang == "en-US"

    def test_recognizer_created(self):
        stt = STT()
        assert stt.recognizer is not None


class TestSTTRecognizeFromFile:
    def test_file_not_found(self):
        stt = STT()
        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            stt.recognize_from_file("/nonexistent/audio.wav")

    @patch("vntts.stt.sr.AudioFile")
    def test_recognize_from_file(self, mock_audio_file, tmp_path):
        # Create a dummy file so the existence check passes
        audio = tmp_path / "test.wav"
        audio.write_bytes(b"fake")

        mock_source = MagicMock()
        mock_audio_file.return_value.__enter__ = MagicMock(return_value=mock_source)
        mock_audio_file.return_value.__exit__ = MagicMock(return_value=False)

        stt = STT()
        stt.recognizer = MagicMock()
        stt.recognizer.recognize_google.return_value = "xin chào"

        result = stt.recognize_from_file(audio)

        assert result == "xin chào"
        stt.recognizer.record.assert_called_once_with(mock_source)
        stt.recognizer.recognize_google.assert_called_once()

    @patch("vntts.stt.sr.AudioFile")
    def test_recognize_with_custom_language(self, mock_audio_file, tmp_path):
        audio = tmp_path / "test.wav"
        audio.write_bytes(b"fake")

        mock_source = MagicMock()
        mock_audio_file.return_value.__enter__ = MagicMock(return_value=mock_source)
        mock_audio_file.return_value.__exit__ = MagicMock(return_value=False)

        stt = STT()
        stt.recognizer = MagicMock()
        stt.recognizer.recognize_google.return_value = "hello"

        stt.recognize_from_file(audio, language="en-US")

        stt.recognizer.recognize_google.assert_called_once_with(
            stt.recognizer.record.return_value, language="en-US"
        )

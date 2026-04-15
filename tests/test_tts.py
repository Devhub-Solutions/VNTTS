"""Unit tests for the TTS module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from vntts.tts import TTS


class TestTTSInit:
    def test_default_language(self):
        tts = TTS()
        assert tts.lang == "vi"

    def test_custom_language(self):
        tts = TTS(lang="en")
        assert tts.lang == "en"


class TestTTSSpeak:
    @patch("vntts.tts.gTTS")
    def test_speak_saves_file(self, mock_gtts_cls, tmp_path):
        mock_instance = MagicMock()
        mock_gtts_cls.return_value = mock_instance

        tts = TTS()
        output = tmp_path / "output.mp3"
        result = tts.speak("xin chào", output)

        mock_gtts_cls.assert_called_once_with(text="xin chào", lang="vi", slow=False)
        mock_instance.save.assert_called_once_with(str(output))
        assert result == output

    @patch("vntts.tts.gTTS")
    def test_speak_slow(self, mock_gtts_cls, tmp_path):
        mock_instance = MagicMock()
        mock_gtts_cls.return_value = mock_instance

        tts = TTS()
        output = tmp_path / "output.mp3"
        tts.speak("xin chào", output, slow=True)

        mock_gtts_cls.assert_called_once_with(text="xin chào", lang="vi", slow=True)

    @patch("vntts.tts.gTTS")
    def test_speak_returns_path_object(self, mock_gtts_cls, tmp_path):
        mock_gtts_cls.return_value = MagicMock()

        tts = TTS()
        result = tts.speak("hello", str(tmp_path / "out.mp3"))
        assert isinstance(result, Path)


class TestTTSSpeakToBytes:
    @patch("vntts.tts.gTTS")
    def test_speak_to_bytes_returns_bytes(self, mock_gtts_cls):
        mock_instance = MagicMock()
        mock_instance.write_to_fp.side_effect = lambda fp: fp.write(b"fake-audio")
        mock_gtts_cls.return_value = mock_instance

        tts = TTS()
        result = tts.speak_to_bytes("xin chào")

        assert isinstance(result, bytes)
        assert result == b"fake-audio"
        mock_gtts_cls.assert_called_once_with(text="xin chào", lang="vi", slow=False)

"""Unit tests for the TTS module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vntts.tts import TTS



class TestTTSInit:
    @patch("vntts.tts.download_and_prepare_models")
    def test_default_language(self, mock_download):
        mock_download.return_value = Path(__file__).resolve().parent.parent / "src" / "vntts" / "models"
        tts = TTS()
        assert tts.lang == "vi"

    @patch("vntts.tts.download_and_prepare_models")
    def test_custom_language(self, mock_download):
        mock_download.return_value = Path(__file__).resolve().parent.parent / "src" / "vntts" / "models"
        tts = TTS(lang="en")
        assert tts.lang == "en"


class TestTTSSpeak:
    def test_missing_model_pair(self, tmp_path):
        tts = TTS(model_dir=tmp_path)
        with pytest.raises(FileNotFoundError, match="No valid model pair found"):
            tts.speak("xin chào", tmp_path / "out.wav")

    @patch("vntts.tts.PiperVoice.load")
    def test_speak_saves_file(self, mock_load, tmp_path):
        (tmp_path / "demo.onnx").write_bytes(b"x")
        (tmp_path / "demo.onnx.json").write_text("{}")

        mock_voice = MagicMock()

        def _write_audio(text, wav_file, syn_config):
            _ = text, syn_config
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(b"\x00\x00" * 10)

        mock_voice.synthesize_wav.side_effect = _write_audio
        mock_load.return_value = mock_voice

        tts = TTS(model_dir=tmp_path, model_name="demo")
        output = tmp_path / "output.wav"
        result = tts.speak("xin chào", output)

        assert result == output
        assert output.exists()
        mock_load.assert_called_once()
        mock_voice.synthesize_wav.assert_called_once()

    @patch("vntts.tts.PiperVoice.load")
    def test_speak_returns_path_object(self, mock_load, tmp_path):
        (tmp_path / "demo.onnx").write_bytes(b"x")
        (tmp_path / "demo.onnx.json").write_text("{}")
        mock_voice = MagicMock()

        def _write_audio(text, wav_file, syn_config):
            _ = text, syn_config
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(b"\x00\x00" * 10)

        mock_voice.synthesize_wav.side_effect = _write_audio
        mock_load.return_value = mock_voice

        tts = TTS(model_dir=tmp_path, model_name="demo")
        result = tts.speak("hello", str(tmp_path / "out.wav"))
        assert isinstance(result, Path)




    @patch("vntts.tts.PiperVoice.load")
    def test_auto_merge_parts_for_named_model(self, mock_load, tmp_path):
        (tmp_path / "demo.part1").write_bytes(b"abc")
        (tmp_path / "demo.part2").write_bytes(b"def")
        (tmp_path / "demo.onnx.json").write_text("{}")

        mock_voice = MagicMock()

        def _write_audio(text, wav_file, syn_config):
            _ = text, syn_config
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(b"\x00\x00" * 10)

        mock_voice.synthesize_wav.side_effect = _write_audio
        mock_load.return_value = mock_voice

        tts = TTS(model_dir=tmp_path, model_name="demo")
        output = tmp_path / "output.wav"
        tts.speak("xin chào", output)

        assert (tmp_path / "demo.onnx").read_bytes() == b"abcdef"

class TestTTSSpeakToBytes:
    @patch("vntts.tts.PiperVoice.load")
    def test_speak_to_bytes_returns_bytes(self, mock_load, tmp_path):
        (tmp_path / "demo.onnx").write_bytes(b"x")
        (tmp_path / "demo.onnx.json").write_text("{}")

        mock_voice = MagicMock()

        def _write_audio(text, wav_file, syn_config):
            _ = text, syn_config
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(b"\x00\x00" * 10)

        mock_voice.synthesize_wav.side_effect = _write_audio
        mock_load.return_value = mock_voice

        tts = TTS(model_dir=tmp_path, model_name="demo")
        result = tts.speak_to_bytes("xin chào")

        assert isinstance(result, bytes)
        assert result.startswith(b"RIFF")

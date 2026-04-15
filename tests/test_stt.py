"""Unit tests for the STT module."""

from unittest.mock import MagicMock, patch
import wave

import pytest

from vntts.stt import STT


def _create_test_wav(path):
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.writeframes(b"\x00\x00" * 160)


class TestSTTInit:
    def test_default_language(self):
        stt = STT()
        assert stt.lang == "vi-VN"

    def test_custom_language(self):
        stt = STT(lang="en-US")
        assert stt.lang == "en-US"


class TestSTTRecognizeFromFile:
    def test_file_not_found(self):
        stt = STT()
        with pytest.raises(
            FileNotFoundError, match=r"Audio file not found: /nonexistent/audio\.wav"
        ):
            stt.recognize_from_file("/nonexistent/audio.wav")

    def test_missing_model_tokens(self, tmp_path):
        audio = tmp_path / "test.wav"
        _create_test_wav(audio)
        stt = STT(model_dir=tmp_path)
        with pytest.raises(FileNotFoundError, match=r"tokens\.txt not found"):
            stt.recognize_from_file(audio)

    @patch("vntts.stt.sherpa_onnx.OfflineRecognizer.from_transducer")
    def test_recognize_from_file(self, mock_from_transducer, tmp_path):
        audio = tmp_path / "test.wav"
        _create_test_wav(audio)

        (tmp_path / "tokens.txt").write_text("a")
        (tmp_path / "encoder.int8.onnx").write_bytes(b"x")
        (tmp_path / "decoder.onnx").write_bytes(b"x")
        (tmp_path / "joiner.int8.onnx").write_bytes(b"x")

        mock_stream = MagicMock()
        mock_stream.result.text = "xin chào"
        mock_recognizer = MagicMock()
        mock_recognizer.create_stream.return_value = mock_stream
        mock_from_transducer.return_value = mock_recognizer

        stt = STT(model_dir=tmp_path)
        result = stt.recognize_from_file(audio)

        assert result == "xin chào"
        mock_from_transducer.assert_called_once()
        mock_recognizer.decode_stream.assert_called_once_with(mock_stream)



    @patch("vntts.stt.sherpa_onnx.OfflineRecognizer.from_transducer")
    def test_auto_merge_model_parts_before_loading(self, mock_from_transducer, tmp_path):
        audio = tmp_path / "test.wav"
        _create_test_wav(audio)

        (tmp_path / "tokens.txt").write_text("a")
        (tmp_path / "encoder.int8.part1").write_bytes(b"enc")
        (tmp_path / "decoder.part1").write_bytes(b"dec")
        (tmp_path / "joiner.int8.part1").write_bytes(b"join")

        mock_stream = MagicMock()
        mock_stream.result.text = "xin chào"
        mock_recognizer = MagicMock()
        mock_recognizer.create_stream.return_value = mock_stream
        mock_from_transducer.return_value = mock_recognizer

        stt = STT(model_dir=tmp_path)
        result = stt.recognize_from_file(audio)

        assert result == "xin chào"
        assert (tmp_path / "encoder.int8.onnx").read_bytes() == b"enc"
        assert (tmp_path / "decoder.onnx").read_bytes() == b"dec"
        assert (tmp_path / "joiner.int8.onnx").read_bytes() == b"join"

    def test_microphone_not_supported(self):
        stt = STT()
        with pytest.raises(NotImplementedError, match="Microphone recognition"):
            stt.recognize_from_microphone()

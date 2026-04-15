# VNTTS

Vietnamese Text-to-Speech and Speech-to-Text library for Python 3.10 – 3.12.

## Installation

```bash
pip install vntts
```

## Quick Start

### Text-to-Speech

```python
from vntts import TTS

tts = TTS(
    model_dir="models/tts-model/vi",  # contains {model}.onnx + {model}.onnx.json
    model_name="calmwoman3688",       # optional, auto-picks first valid pair if omitted
)
tts.speak("Xin chào", "output.wav")

# Get raw WAV bytes
audio_bytes = tts.speak_to_bytes("Xin chào")
```

### Speech-to-Text

```python
from vntts import STT

stt = STT(
    model_dir="models/asr/sherpa-onnx-zipformer-vi-2025-04-20"
)
text = stt.recognize_from_file("audio.wav")
print(text)
```

## Model setup

- STT: clone model to `models/asr/`:
  - `git clone https://huggingface.co/csukuangfj/sherpa-onnx-zipformer-vi-2025-04-20 models/asr/sherpa-onnx-zipformer-vi-2025-04-20`
- TTS: place model pairs in `models/tts-model/{lang}/`:
  - `{model}.onnx`
  - `{model}.onnx.json`
  - Giọng Ban Mai (NghiTTS): [Tải tại đây](https://drive.google.com/drive/folders/1f_pCpvgqfvO4fdNKM7WS4zTuXC0HBskL)

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

[MIT](LICENSE)

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

tts = TTS()  # default language: Vietnamese
tts.speak("Xin chào", "output.mp3")

# Get raw audio bytes
audio_bytes = tts.speak_to_bytes("Xin chào")
```

### Speech-to-Text

```python
from vntts import STT

stt = STT()  # default language: vi-VN
text = stt.recognize_from_file("audio.wav")
print(text)
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

[MIT](LICENSE)
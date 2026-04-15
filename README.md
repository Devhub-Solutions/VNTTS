# VNTTS

Dự án tích hợp **Vietnamese Text-to-Speech (TTS)** và **Speech-to-Text (STT)**:

- **TTS**: [`nghitts`](https://github.com/nghimestudio/nghitts) / Piper-compatible ONNX (giọng Banmai)
- **STT**: [`sherpa-onnx-zipformer-vi-2025-04-20`](https://huggingface.co/csukuangfj/sherpa-onnx-zipformer-vi-2025-04-20)

## Cấu trúc dự án

```text
VNTTS/
  src/vntts/
    __init__.py
    tts.py
    stt.py
    model_downloader.py   # Downloads models from GitHub Releases
    model_parts.py        # Helpers for split/merge model files
  scripts/
    split_model.py
    merge_model.py
  tests/
  README.md
```

## Cài đặt

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Model Loading

Models are **automatically downloaded** from GitHub Releases on first use.
When `TTS()` or `STT()` is instantiated without an explicit `model_dir`,
the library:

1. Checks if the models directory exists (default: `./models`)
2. If not, downloads `models.zip` from the configured GitHub Release URL
3. Extracts the zip and removes the archive
4. Subsequent runs skip the download (idempotent)

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `VNTTS_MODELS_DIR` | Root directory for models | `models` |
| `VNTTS_MODELS_URL` | URL for `models.zip` | *(GitHub Release)* |
| `VNTTS_MODEL_DOWNLOAD_TIMEOUT_SECONDS` | Network timeout | `120` |
| `VNTTS_MODEL_DOWNLOAD_RETRIES` | Retry attempts | `3` |
| `VNTTS_MODEL_DOWNLOAD_LOG` | Set `0` to disable logs | `1` |

### Explicit Model Directory

You can also provide your own model directory:

```python
from vntts import TTS, STT

tts = TTS(model_dir="/path/to/tts/models")
stt = STT(model_dir="/path/to/stt/models")
```

## Testing

```bash
pytest
```

## Building

```bash
python -m build
```

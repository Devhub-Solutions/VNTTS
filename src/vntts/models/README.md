# Model Storage

This directory is a placeholder. Models are **automatically downloaded** from
GitHub Releases at runtime the first time `TTS()` or `STT()` is instantiated.

## How it works

1. On first use, `download_and_prepare_models()` downloads `models.zip` from
   the configured GitHub Release URL.
2. The zip is extracted into the models root directory (default: `./models`).
3. Subsequent runs detect the existing directory and skip the download.

## Expected layout after download

```text
models/
  banmai/
    banmai.onnx
    banmai.onnx.json
  asr/
    sherpa-onnx-zipformer-vi-2025-04-20/
      encoder-epoch-12-avg-8.onnx (or .int8.onnx)
      decoder-epoch-12-avg-8.onnx
      joiner-epoch-12-avg-8.onnx (or .int8.onnx)
      tokens.txt
      bpe.model
```

## Environment variables

| Variable | Description | Default |
|---|---|---|
| `VNTTS_MODELS_DIR` | Root directory for models | `models` |
| `VNTTS_MODELS_URL` | URL for `models.zip` | *(GitHub Release)* |
| `VNTTS_MODEL_DOWNLOAD_TIMEOUT_SECONDS` | Network timeout | `120` |
| `VNTTS_MODEL_DOWNLOAD_RETRIES` | Retry attempts | `3` |
| `VNTTS_MODEL_DOWNLOAD_LOG` | Set `0` to disable logs | `1` |


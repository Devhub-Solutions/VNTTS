# VNTTS

Dự án tích hợp **Vietnamese Text-to-Speech (TTS)** và **Speech-to-Text (STT)**:

- **TTS**: [`nghitts`](https://github.com/nghimestudio/nghitts) / Piper-compatible ONNX (giọng Banmai)
- **STT**: [`sherpa-onnx-zipformer-vi-2025-04-20`](https://huggingface.co/csukuangfj/sherpa-onnx-zipformer-vi-2025-04-20)

## Cấu trúc dự án

```text
VNTTS/
  models/
    banmai/
      banmai.part001
      banmai.part002
      ...
      banmai.onnx.json
    asr/
      sherpa-onnx-zipformer-vi-2025-04-20/
        encoder.int8.part001
        decoder.part001
        joiner.int8.part001
        tokens.txt
        ...
  scripts/
    split_model.py
    merge_model.py
  src/vntts/
    tts.py
    stt.py
    model_parts.py
  test/
    pipeline_test.py
  tests/
  README.md
```

## Cài đặt

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quản lý model lớn (không dùng Git LFS)

### 1) Tách model (<= 80MB mỗi part)

```bash
python scripts/split_model.py models/banmai/banmai.onnx --chunk-size-mb 80 --write-checksum
```

Mặc định script tạo theo chuẩn:

- `banmai.part001`
- `banmai.part002`
- ...

### 2) Ghép model thủ công (nếu muốn)

```bash
python scripts/merge_model.py models/banmai/banmai.onnx --verify-checksum
# hoặc merge toàn bộ trong 1 thư mục
python scripts/merge_model.py models/asr/sherpa-onnx-zipformer-vi-2025-04-20
```

## Auto-merge khi runtime (không cần user thao tác)

Khi gọi `TTS` hoặc `STT`, hệ thống tự động:

- phát hiện thiếu file `.onnx`
- tìm các file `.part*`
- ghép lại thành `.onnx` trước khi inference

Hỗ trợ cả 2 kiểu đặt tên part:

- `banmai.part001` (hoặc `banmai.part1`) -> `banmai.onnx`
- `banmai.onnx.part001` (hoặc `banmai.onnx.part1`) -> `banmai.onnx`

## Chuẩn bị model

### TTS Banmai
### STT sherpa-onnx

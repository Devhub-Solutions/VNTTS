# VNTTS

Dự án tích hợp **Vietnamese Text-to-Speech (TTS)** và **Speech-to-Text (STT)**:

- **TTS**: [`nghitts`](https://github.com/nghimestudio/nghitts) / Piper-compatible ONNX (giọng Banmai)
- **STT**: [`sherpa-onnx-zipformer-vi-2025-04-20`](https://huggingface.co/csukuangfj/sherpa-onnx-zipformer-vi-2025-04-20)

## Cấu trúc dự án

```text
VNTTS/
  models/
    banmai/
      banmai.part1
      banmai.part2
      ...
      banmai.onnx.json
    asr/
      sherpa-onnx-zipformer-vi-2025-04-20/
        encoder.int8.part1
        decoder.part1
        joiner.int8.part1
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

### 1) Tách model (<= 900MB mỗi part)

```bash
python scripts/split_model.py models/banmai/banmai.onnx --chunk-size-mb 900
```

Mặc định script tạo theo chuẩn:

- `banmai.part1`
- `banmai.part2`
- ...

### 2) Ghép model thủ công (nếu muốn)

```bash
python scripts/merge_model.py models/banmai/banmai.onnx
# hoặc merge toàn bộ trong 1 thư mục
python scripts/merge_model.py models/asr/sherpa-onnx-zipformer-vi-2025-04-20
```

## Auto-merge khi runtime (không cần user thao tác)

Khi gọi `TTS` hoặc `STT`, hệ thống tự động:

- phát hiện thiếu file `.onnx`
- tìm các file `.part*`
- ghép lại thành `.onnx` trước khi inference

Hỗ trợ cả 2 kiểu đặt tên part:

- `banmai.part1` -> `banmai.onnx`
- `banmai.onnx.part1` -> `banmai.onnx`

## Chuẩn bị model

### TTS Banmai

- `banmai.onnx` (hoặc các part `banmai.part*`)
- `banmai.onnx.json`

Nguồn tham khảo:

- https://drive.google.com/file/d/1fOL2JtI2Ej_ZGENJIahT9A30d2yuXaor/view
- https://drive.google.com/file/d/1h8KYopTBdks4bALezfBpHFfK-PB7zJ_O/view

### STT sherpa-onnx

Đặt model tại:

```text
models/asr/sherpa-onnx-zipformer-vi-2025-04-20/
```

Có thể clone trực tiếp:

```bash
git clone https://huggingface.co/csukuangfj/sherpa-onnx-zipformer-vi-2025-04-20 \
  models/asr/sherpa-onnx-zipformer-vi-2025-04-20
```

## Test pipeline TTS -> STT

```bash
python test/pipeline_test.py
```

- Input: text tiếng Việt
- Output 1: file audio WAV (`test/output_pipeline.wav`)
- Output 2: text STT nhận dạng

## Unit test

```bash
pytest
```

## Docker / đóng gói

- Dự án đã ở dạng Python package qua `pyproject.toml`.
- Có thể build Docker bằng cách copy mã nguồn + thư mục `models/` đã split vào image.
- Khi container chạy, model sẽ auto-merge trước khi suy luận.

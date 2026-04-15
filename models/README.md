# Model Storage

Thư mục này dùng để chứa model đã **split** (`.part*`) và metadata cần thiết (`.onnx.json`, `tokens.txt`, ...).

## Cấu trúc

### TTS (Text-to-Speech)
- **banmai/** - Giọng Ban Mai từ Nghi TTS
  - `banmai.part001, banmai.part002` - Model weights (split từ 60.6 MB)
  - `banmai.onnx.json` - Configuration
  - `banmai.onnx.sha256` - Checksum verification

### ASR (Speech-to-Text)  
- **asr/sherpa-onnx-zipformer-vi-2025-04-20/** - Mô hình Vietnamese Zipformer
  - `encoder-epoch-12-avg-8.part001-005` - Encoder weights (split từ 249 MB)
  - `decoder-epoch-12-avg-8.onnx` - Decoder (~5 MB)
  - `joiner-epoch-12-avg-8.onnx` - Joiner (~4 MB)
  - `tokens.txt` - Tokenizer vocabulary
  - `bpe.model` - BPE model

## Cách hoạt động

1. **Split Models**: Model lớn được chia thành các chunk 60MB để dễ quản lý và deploy
   ```bash
   python scripts/split_model.py <file> --chunk-size-mb 60 --write-checksum
   ```

2. **Auto-Merge**: Khi sử dụng library, nó tự động merge `.part*` thành `.onnx` nếu cần
   ```python
   from vntts import TTS, STT
   tts = TTS()  # Automatically merges banmai.part* → banmai.onnx
   stt = STT()  # Automatically merges encoder.part* → encoder.onnx
   ```

3. **Checksum Verification**: Tệp `.sha256` được sử dụng để xác minh tính toàn vẹn
   ```bash
   python scripts/merge_model.py <file> --verify-checksum
   ```

## Git không cần LFS

Các file `.part*` được commit trực tiếp vào git (không dùng git lfs) vì:
- Mỗi chunk < 100 MB (GitHub limit)
- Library sẽ tự động merge khi loaded
- Người dùng không cần cài github-cli hay git lfs extra

## Thêm models mới

```bash
# 1. Tải model về tới thư mục tương ứng
cd models/banmai/
wget <model-url> -O model.onnx

# 2. Split model
python ../../scripts/split_model.py model.onnx --chunk-size-mb 60 --write-checksum

# 3. Xóa file gốc
rm model.onnx

# 4. Commit
git add .
git commit -m "Add new model with split parts"
git push
```


# Model Storage

Thư mục này dùng để chứa model đã **split** (`.part*`) và metadata cần thiết (`.onnx.json`, `tokens.txt`, ...).

- Không commit file `.onnx` lớn.
- Tách model thành từng part tối đa `80 * 1024 * 1024` bytes (80MB), ví dụ `banmai.part001`.
- Runtime sẽ tự merge `.part*` thành `.onnx` khi cần.

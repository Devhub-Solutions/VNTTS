# Model Storage

Thư mục này dùng để chứa model đã **split** (`.part*`) và metadata cần thiết (`.onnx.json`, `tokens.txt`, ...).

- Không commit file `.onnx` lớn.
- Runtime sẽ tự merge `.part*` thành `.onnx` khi cần.

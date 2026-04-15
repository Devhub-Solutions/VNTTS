# Phân tích và Khắc phục Lỗi `FileNotFoundError` khi Đóng Gói SDK VNTTS

## 1. Mô tả Lỗi

Người dùng gặp lỗi `FileNotFoundError` khi cố gắng sử dụng SDK `vntts` sau khi cài đặt từ PyPI. Lỗi cụ thể là không tìm thấy các tệp mô hình `banmai.onnx` và `banmai.onnx.json` trong thư mục `models/banmai`.

```
FileNotFoundError: Model pair not found: models\banmai\banmai.onnx and models\banmai\banmai.onnx.json
```

## 2. Phân tích Nguyên nhân

Sau khi kiểm tra cấu trúc repository và các tệp cấu hình đóng gói, chúng tôi đã xác định nguyên nhân gốc rễ của vấn đề:

1.  **Cấu trúc Thư mục Mô hình:**
    *   Các tệp mô hình lớn được chia nhỏ (`.part001`, `.part002`, v.v.) và lưu trữ trong thư mục gốc `models/banmai/` (ví dụ: `/home/ubuntu/VNTTS/models/banmai/banmai.part001`).
    *   Trong thư mục `src/vntts/models/banmai/`, các tệp `banmai.onnx` và `banmai.onnx.json` tồn tại nhưng chúng là các tệp con trỏ Git LFS (chỉ có kích thước vài chục đến vài trăm byte), không phải là các tệp mô hình thực tế. Các tệp `.part` không có trong `src/vntts/models/banmai/`.

2.  **Cấu hình Đóng gói (`pyproject.toml`):**
    *   Tệp `pyproject.toml` sử dụng `setuptools` để đóng gói và có cấu hình `[tool.setuptools.package-data]` như sau:
        ```toml
        [tool.setuptools.package-data]
        vntts = [
            "models/**/*.onnx",
            "models/**/*.txt", 
            "models/**/*.json",
        ]
        ```
    *   Cấu hình này chỉ bao gồm các tệp `.onnx`, `.txt`, và `.json` từ thư mục `src/vntts/models/`. Do đó, nó chỉ bao gồm các tệp con trỏ Git LFS (`banmai.onnx`, `banmai.onnx.json`) và không bao gồm các tệp `.part` thực tế.

3.  **Logic Tải Mô hình (`tts.py` và `model_parts.py`):**
    *   Hàm `TTS._load_voice()` gọi `TTS._resolve_model_name()`, hàm này đến lượt nó gọi `merge_parts_to_file()` từ `vntts.model_parts`.
    *   Hàm `merge_parts_to_file()` được thiết kế để tìm và hợp nhất các tệp `.part*` thành tệp `.onnx` hoàn chỉnh.
    *   Tuy nhiên, vì các tệp `.part*` không được đóng gói vào SDK (do cấu hình `pyproject.toml` không bao gồm chúng), nên khi SDK được cài đặt từ PyPI, thư mục `site-packages/vntts/models/banmai/` chỉ chứa các tệp con trỏ LFS và không có các tệp `.part` để hợp nhất. Điều này dẫn đến `FileNotFoundError` khi `merge_parts_to_file()` không tìm thấy các phần để hợp nhất.

4.  **Tệp `.gitignore`:**
    *   Tệp `.gitignore` loại trừ `models/**/*.onnx`, điều này có nghĩa là các tệp `.onnx` đã hợp nhất không được theo dõi bởi Git (chỉ các tệp con trỏ LFS được theo dõi). Các tệp `.part*` thì không bị loại trừ, cho thấy chúng được dự định để đưa vào kho lưu trữ Git.

**Tóm tắt:** Vấn đề là các tệp mô hình `.part*` cần thiết để hợp nhất mô hình không được bao gồm trong gói PyPI, trong khi các tệp `.onnx` và `.onnx.json` được bao gồm lại là các tệp con trỏ Git LFS không chứa dữ liệu mô hình thực tế.

## 3. Giải pháp và Hướng dẫn Sửa lỗi

Để khắc phục lỗi này, chúng ta cần đảm bảo rằng tất cả các tệp mô hình cần thiết (bao gồm cả các tệp `.part*`) được đóng gói đúng cách vào SDK khi tạo gói phân phối cho PyPI.

Có hai cách tiếp cận chính:

### Cách 1: Bao gồm các tệp `.part*` vào gói phân phối (Được khuyến nghị)

Đây là cách tiếp cận phù hợp với thiết kế hiện tại của thư viện, nơi các mô hình được chia nhỏ và hợp nhất khi chạy. Chúng ta cần sửa đổi `pyproject.toml` để bao gồm các tệp `.part*`.

**Các bước thực hiện:**

1.  **Chỉnh sửa `pyproject.toml`:**
    Mở tệp `pyproject.toml` và cập nhật phần `[tool.setuptools.package-data]` để bao gồm các tệp `.part*`.

    *Trước khi sửa đổi:*
    ```toml
    [tool.setuptools.package-data]
    vntts = [
        "models/**/*.onnx",
        "models/**/*.txt", 
        "models/**/*.json",
    ]
    ```

    *Sau khi sửa đổi:*
    ```toml
    [tool.setuptools.package-data]
    vntts = [
        "models/**/*.onnx",
        "models/**/*.txt", 
        "models/**/*.json",
        "models/**/*.part*", # Thêm dòng này để bao gồm các tệp phần
    ]
    ```

    **Lưu ý quan trọng:** Các tệp `.part*` thực tế nằm ở thư mục gốc `models/banmai/` chứ không phải `src/vntts/models/banmai/`. Tuy nhiên, do `[tool.setuptools.packages.find]` được cấu hình với `where = ["src"]`, `setuptools` sẽ tìm kiếm `vntts` trong thư mục `src`. Do đó, các tệp mô hình cần được di chuyển vào `src/vntts/models/` để được đóng gói đúng cách.

    **Cập nhật cấu trúc thư mục:**
    Di chuyển thư mục `models/` từ gốc repository vào `src/vntts/`.
    *   **Trước:**
        ```
        VNTTS/
        ├── models/
        │   └── banmai/
        │       ├── banmai.part001
        │       └── banmai.part002
        └── src/
            └── vntts/
                └── models/ (chứa các tệp LFS pointer)
        ```
    *   **Sau:**
        ```
        VNTTS/
        └── src/
            └── vntts/
                └── models/
                    └── banmai/
                        ├── banmai.part001
                        └── banmai.part002
                        ├── banmai.onnx.json
                        └── banmai.onnx.sha256
        ```
    Sau khi di chuyển, hãy đảm bảo rằng các tệp con trỏ Git LFS trong `src/vntts/models/` được thay thế bằng các tệp `.part` thực tế và các tệp metadata liên quan.

2.  **Cập nhật `.gitignore` (tùy chọn nhưng được khuyến nghị):**
    Nếu bạn đã di chuyển các tệp `.part*` vào `src/vntts/models/`, bạn có thể muốn cập nhật `.gitignore` để phản ánh cấu trúc mới và đảm bảo các tệp `.onnx` đã hợp nhất vẫn bị bỏ qua nếu chúng được tạo cục bộ.

    *Trước khi sửa đổi:*
    ```gitignore
    models/**/*.onnx
    ```

    *Sau khi sửa đổi (nếu các tệp mô hình được di chuyển vào `src/vntts/models/`):*
    ```gitignore
    src/vntts/models/**/*.onnx
    # Hoặc giữ nguyên nếu bạn muốn bỏ qua tất cả các tệp .onnx ở bất kỳ đâu
    # models/**/*.onnx
    ```

3.  **Tạo lại gói phân phối:**
    Sau khi thực hiện các thay đổi, bạn cần tạo lại gói phân phối (`.whl` và `.tar.gz`) và tải chúng lên PyPI.

    ```bash
    # Xóa các bản dựng cũ
    rm -rf build/ dist/ *.egg-info/
    # Xây dựng lại gói
    python -m build
    # Kiểm tra gói
    twine check dist/*
    # Tải lên PyPI (đảm bảo bạn đã tăng số phiên bản trong pyproject.toml)
    twine upload dist/*
    ```

### Cách 2: Bao gồm các tệp `.onnx` đã hợp nhất trực tiếp (ít khuyến nghị hơn)

Cách này yêu cầu bạn phải hợp nhất các tệp `.part*` thành `.onnx` trước khi đóng gói và đảm bảo các tệp `.onnx` này được bao gồm trong gói. Tuy nhiên, điều này đi ngược lại với ý tưởng chia nhỏ mô hình để quản lý Git dễ dàng hơn và tự động hợp nhất khi chạy.

**Các bước thực hiện:**

1.  **Hợp nhất mô hình trước khi đóng gói:**
    Bạn sẽ cần một bước trong quy trình CI/CD hoặc cục bộ để hợp nhất các tệp `.part*` thành `.onnx` hoàn chỉnh trước khi tạo gói phân phối.

    ```bash
    # Ví dụ: Chạy script merge_model.py
    python scripts/merge_model.py models/banmai/banmai.onnx --overwrite
    ```

2.  **Chỉnh sửa `pyproject.toml`:**
    Đảm bảo `pyproject.toml` bao gồm các tệp `.onnx` đã hợp nhất. Cấu hình hiện tại của bạn đã bao gồm `"models/**/*.onnx"`, nhưng bạn cần đảm bảo rằng các tệp `.onnx` này là các tệp thực tế, không phải con trỏ LFS.

    *   **Lưu ý:** Nếu bạn chọn cách này, bạn cần đảm bảo rằng các tệp `.onnx` đã hợp nhất nằm trong `src/vntts/models/` để `setuptools` có thể tìm thấy chúng.

3.  **Cập nhật `.gitignore`:**
    Bạn sẽ cần loại bỏ `models/**/*.onnx` khỏi `.gitignore` để các tệp `.onnx` đã hợp nhất được theo dõi bởi Git và được đưa vào gói phân phối.

    *Trước khi sửa đổi:*
    ```gitignore
    models/**/*.onnx
    ```

    *Sau khi sửa đổi:*
    ```gitignore
    # models/**/*.onnx # Comment hoặc xóa dòng này
    ```

4.  **Tạo lại gói phân phối:**
    Tương tự như Cách 1, tạo lại gói và tải lên PyPI.

## 4. Khuyến nghị

Chúng tôi **khuyến nghị sử dụng Cách 1** (bao gồm các tệp `.part*` và di chuyển thư mục `models` vào `src/vntts/`) vì nó phù hợp với kiến trúc hiện tại của thư viện, nơi các mô hình được chia nhỏ để quản lý Git và tự động hợp nhất khi tải. Điều này cũng giúp giữ kích thước repository nhỏ hơn nếu bạn không muốn lưu trữ các tệp `.onnx` lớn trực tiếp trong Git.

## 5. Các bước Tiếp theo

1.  **Di chuyển thư mục `models`:** Di chuyển thư mục `models` từ gốc repository vào `src/vntts/`.
2.  **Cập nhật `pyproject.toml`:** Thêm `"models/**/*.part*"` vào phần `[tool.setuptools.package-data]`.
3.  **Kiểm tra lại `.gitignore`:** Đảm bảo rằng `src/vntts/models/**/*.onnx` (hoặc `models/**/*.onnx` nếu bạn không muốn chỉ định đường dẫn cụ thể) được bỏ qua để tránh đưa các tệp con trỏ LFS vào gói.
4.  **Tăng số phiên bản:** Cập nhật số phiên bản trong `pyproject.toml`.
5.  **Tạo và tải lên gói mới:** Chạy `python -m build` và sau đó `twine upload dist/*`.

Sau khi thực hiện các bước này, SDK của bạn sẽ được đóng gói với tất cả các tệp mô hình cần thiết và lỗi `FileNotFoundError` sẽ được khắc phục.

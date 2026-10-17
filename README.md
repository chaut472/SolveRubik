# HỆ THỐNG GIẢI RUBIK 3x3 BẰNG NHẬN DIỆN QUA CAMERA (PYTHON)

Dự án phần mềm hoàn chỉnh nhận diện 6 mặt khối Rubik 3x3 theo thời gian thực qua webcam máy tính, phân loại màu sắc bằng không gian màu HSV & CIELAB, kiểm tra tính hợp lệ toán học, tìm chuỗi nước đi tối ưu bằng thuật toán hai giai đoạn **Kociemba (Two-Phase Algorithm)** và trực quan hóa hướng dẫn giải từng bước trên giao diện desktop hiện đại **PySide6**.

---

## 1. Tổng Quan Kiến Trúc 8 Thành Phần

Hệ thống được thiết kế theo mô hình phân tầng hướng đối tượng (Modular Layered Architecture), gồm 8 thành phần độc lập:

1. **Giao diện người dùng (GUI - PySide6)**: Bố cục trực quan chia đôi (khung camera thời gian thực và mô hình 2D trải phẳng), hiển thị nước đi lớn kèm hướng dẫn tiếng Việt.
2. **Quản lý Camera (OpenCV Stream)**: Chạy trên luồng độc lập (`QThread`), tối ưu DirectShow trên Windows, tốc độ ổn định 30 FPS, hỗ trợ chuyển đổi webcam.
3. **Phát hiện lưới & Phân loại màu (Vision & Color Detection)**: Khung định vị 3x3 ROI, lọc nhiễu vùng biên, phân loại màu kết hợp HSV và khoảng cách CIELAB $\Delta E$.
4. **Mô hình hóa khối Rubik (Cube State & Modeling)**: Quản lý 54 ô (stickers), chuẩn hóa ký hiệu quốc tế $U, R, F, D, L, B$, mô phỏng chính xác các phép xoay mặt ($R, U, F, D, L, B, R', R2...$).
5. **Bộ kiểm tra tính hợp lệ (Validator)**: Phát hiện sớm lỗi quét trùng tâm, thiếu/thừa màu (mỗi màu phải có đúng 9 ô), ô chưa nhận diện và các lỗi xoay góc/lật cạnh cơ học.
6. **Thuật toán giải (Kociemba Two-Phase Algorithm)**: Giải Rubik tối ưu trong phạm vi 20-22 nước đi, tích hợp sẵn bản Pure-Python độc lập (không yêu cầu cài đặt trình biên dịch C++).
7. **Trực quan hóa & Trình phát bước giải (Visualization & Player)**:
   - Mô hình 2D phẳng (`CubeNetWidget`) chữ thập chuẩn quốc tế.
   - Trình điều khiển bước giải (`StepGuideController`): Phát tự động, Tạm dừng, Bước tiếp, Bước trước, Nhảy tới bước bất kỳ, Thanh trượt tốc độ.
   - Bảng cọ vẽ palette cho phép click sửa màu trực tiếp trên mô hình 54 ô nếu webcam bị chóa sáng.
8. **Kiểm thử tự động & Đóng gói (Testing & Packaging)**: Bộ kiểm thử tự động `pytest` kiểm tra 100% logic cốt lõi; hướng dẫn đóng gói `.exe` bằng `PyInstaller`.

---

## 2. Cấu Trúc Thư Mục Dự Án

```
d:\Đồ Án\RUBIK\
├── main.py                     # Điểm khởi chạy ứng dụng chính (PySide6)
├── requirements.txt            # Danh sách thư viện phụ thuộc
├── pytest.ini                  # Cấu hình kiểm thử tự động
├── README.md                   # Tài liệu hướng dẫn & kỹ thuật
│
├── rubik_solver/
│   ├── __init__.py
│   │
│   ├── camera/                 # Thành phần 2: Quản lý Webcam
│   │   ├── __init__.py
│   │   └── camera_stream.py    # QThread đọc webcam, điều phối FPS, DirectShow backend
│   │
│   ├── vision/                 # Thành phần 3: Xử lý ảnh & Nhận diện màu
│   │   ├── __init__.py
│   │   ├── color_detector.py   # Phân loại màu (HSV + khoảng cách CIELAB)
│   │   ├── grid_detector.py    # Lưới định vị 3x3, trích xuất 9 ô và vẽ overlay
│   │   └── calibrator.py       # Quản lý hồ sơ cấu hình màu sắc
│   │
│   ├── cube/                   # Thành phần 4 & 5: Mô hình & Kiểm tra hợp lệ
│   │   ├── __init__.py
│   │   ├── constants.py        # Quy ước ký hiệu (U, R, F, D, L, B), mã màu Hex
│   │   ├── cube_state.py       # Quản lý 54 ô, mô phỏng xoay mặt, chuyển đổi chuỗi
│   │   └── validator.py        # Kiểm tra 6 tâm duy nhất, đủ 9 ô/màu
│   │
│   ├── solver/                 # Thành phần 6: Thuật toán giải Kociemba
│   │   ├── __init__.py
│   │   ├── kociemba_solver.py  # Wrapper gọi Kociemba, dịch lỗi sang tiếng Việt
│   │   ├── move_formatter.py   # Phân tích cú pháp, đảo bước, mô tả tiếng Việt
│   │   └── pykociemba/         # Động cơ Two-Phase Kociemba Pure-Python
│   │
│   ├── visualization/          # Thành phần 7: Hiển thị & Trình phát
│   │   ├── __init__.py
│   │   ├── cube_net_2d.py      # Widget 2D trải phẳng 6 mặt Rubik tương tác
│   │   └── step_guide.py       # Bộ điều khiển bước giải (Play, Next, Prev, Speed)
│   │
│   └── ui/                     # Thành phần 1: Giao diện PySide6
│       ├── __init__.py
│       ├── main_window.py      # Cửa sổ chính tích hợp toàn bộ hệ thống
│       ├── video_widget.py     # Widget camera HUD với hướng dẫn quét
│       ├── manual_dialog.py    # Hộp thoại bảng vẽ palette sửa màu thủ công
│       └── styles.py           # Bảng định kiểu Modern Dark Theme QSS
│
└── tests/                      # Thành phần 8: Bộ kiểm thử tự động
    ├── __init__.py
    ├── test_cube_state.py      # Kiểm tra các phép xoay mặt (R, U, Sexy Move cycle)
    ├── test_validator.py       # Kiểm tra phát hiện lỗi trùng tâm, thiếu màu
    ├── test_solver.py          # Kiểm tra giải các trạng thái xáo trộn & phát hiện Flip error
    └── test_vision.py          # Kiểm tra phân loại màu trên các ma trận ảnh mẫu
```

---

## 3. Cài Đặt & Sử Dụng

### 3.1. Yêu cầu Hệ thống
- Hệ điều hành: Windows 10/11 (hoặc Linux / macOS).
- Python: Phiên bản 3.10 trở lên (khuyên dùng Python 3.11).
- Webcam máy tính (tích hợp hoặc USB).

### 3.2. Cài đặt Thư viện
Mở PowerShell hoặc Command Prompt tại thư mục dự án:
```powershell
pip install -r requirements.txt
```

### 3.3. Chạy Kiểm Thử Tự Động
Đảm bảo toàn bộ 16 bài kiểm thử của hệ thống đều vượt qua:
```powershell
pytest
```

### 3.4. Khởi Chạy Ứng Dụng
```powershell
python main.py
```

---

## 4. Hướng Dẫn Sử Dụng Chi Tiết

### Bước 1: Quét 6 Mặt Rubik qua Camera
Khi ứng dụng mở, thanh thông báo trên video sẽ hướng dẫn bạn quét tuần tự 6 mặt theo quy ước chuẩn:
1. **Mặt 1 (U - Trắng)**: Đưa mặt Trắng vào khung lưới, mặt Xanh lá hướng xuống dưới. Bấm **📸 Chụp Mặt Này**.
2. **Mặt 2 (R - Đỏ)**: Giữ mặt Trắng ở trên, xoay khối Rubik sang Phải để đưa mặt Đỏ vào khung. Bấm **📸 Chụp Mặt Này**.
3. **Mặt 3 (F - Xanh lá)**: Tiếp tục đưa mặt Trước (Xanh lá) vào khung. Bấm **📸 Chụp Mặt Này**.
4. **Mặt 4 (D - Vàng)**: Lật mặt Dưới (Vàng) vào khung. Bấm **📸 Chụp Mặt Này**.
5. **Mặt 5 (L - Cam)**: Đưa mặt Trái (Cam) vào khung. Bấm **📸 Chụp Mặt Này**.
6. **Mặt 6 (B - Xanh dương)**: Đưa mặt Sau (Xanh dương) vào khung. Bấm **📸 Chụp Mặt Này**.

*Mẹo: Nếu phòng có ánh sáng phức tạp làm 1 ô bị bóng chóa, bạn chỉ cần click trực tiếp vào ô đó trên mô hình 2D bên phải để chọn lại màu chuẩn! Hoặc bấm **✏️ Nhập / Sửa Màu Thủ Công** để mở bảng cọ vẽ 54 ô.*

### Bước 2: Tìm Lời Giải
- Nhấn nút xanh nổi bật: **🚀 TÌM LỜI GIẢI (KOCIEMBA)**.
- Hệ thống sẽ kiểm tra tính hợp lệ toán học của khối Rubik. Nếu hợp lệ, lời giải tối ưu (thường từ 18 đến 22 bước) sẽ xuất hiện tức thì trong danh sách.

### Bước 3: Xem Hướng Dẫn Từng Bước (Solution Player)
- **Ký hiệu nước đi**: Hiển thị to, rõ ràng (ví dụ: `R'`, `U2`, `F`).
- **Giải thích tiếng Việt**: Ví dụ *"Xoay mặt Phải 90° ngược chiều kim đồng hồ (Màu Đỏ)"*.
- **Điều khiển**:
  - `◀ Bước Trước`: Quay lại bước trước (mô hình 2D sẽ xoay ngược lại).
  - `▶ Tự Động`: Tự động phát từng bước một.
  - `Bước Tiếp ▶`: Tiến tới bước tiếp theo.
  - `⏮ Về Đầu`: Đặt lại về trạng thái ban đầu để giải lại từ đầu.
  - **Thanh trượt tốc độ**: Kéo để tăng giảm thời gian giữa các bước (từ 0.4s đến 2.5s).

---

## 5. Đóng Gói Thành File Thực Thi (.exe)

Để đóng gói phần mềm thành một file chạy duy nhất trên Windows mà không cần cài đặt Python:
```powershell
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --add-data "rubik_solver/solver/pykociemba;rubik_solver/solver/pykociemba" --name "RubikSolver" main.py
```
File thực thi sẽ nằm trong thư mục `dist/RubikSolver/RubikSolver.exe`.

---

## 6. Gợi Ý Cho Báo Cáo Đồ Án Công Nghệ Thông Tin

Khi viết báo cáo hoặc thuyết trình đồ án, bạn có thể triển khai thành các chương mục như sau:
1. **Chương 1: Giới thiệu đề tài & Bài toán giải Rubik**:
   - Không gian trạng thái của Rubik 3x3: $43{,}252{,}003{,}274{,}489{,}856{,}000$ trạng thái (khoảng $4.3 \times 10^{19}$).
   - Giới hạn Chúa (God's Number): Mọi trạng thái Rubik 3x3 đều có thể giải trong tối đa 20 bước xoay (đã được chứng minh vào năm 2010).
2. **Chương 2: Xử lý hình ảnh và Nhận diện Màu sắc (Computer Vision)**:
   - Quy trình tiền xử lý khung hình webcam bằng OpenCV.
   - Kỹ thuật xác định vùng quan tâm (ROI - Region of Interest).
   - So sánh việc phân loại màu trong không gian RGB, HSV và CIELAB ($L^* a^* b^*$).
   - Kỹ thuật tính màu trung vị (median) để lọc nhiễu phản xạ ánh sáng (specular glare).
3. **Chương 3: Thuật toán Giải Kociemba (Two-Phase Algorithm)**:
   - Giai đoạn 1 (Phase 1): Đưa khối Rubik từ nhóm bất kỳ $G_0$ về nhóm con $G_1 = \langle U, D, R^2, L^2, F^2, B^2 \rangle$.
   - Giai đoạn 2 (Phase 2): Giải khối Rubik trong nhóm con $G_1$ chỉ sử dụng các phép quay mặt trên/dưới và quay 180° các mặt còn lại.
   - Bảng tra cứu cắt tỉa (Pruning Tables) để tối ưu thời gian tìm kiếm lời giải trong vòng vài phần trăm giây.
4. **Chương 4: Thiết kế & Hiện thực Hóa Phần Mềm**:
   - Sơ đồ kiến trúc 8 thành phần, sơ đồ lớp UML (Class Diagram), sơ đồ luồng hoạt động (Activity Diagram).
   - Xử lý đa luồng (`QThread`) đảm bảo trải nghiệm giao diện người dùng không bị nghẽn (UI Thread vs Video Processing Thread).
5. **Chương 5: Đánh giá, Kiểm thử & Hướng phát triển**:
   - Đánh giá độ chính xác nhận diện màu trong các điều kiện ánh sáng khác nhau.
   - Kết quả kiểm thử tự động với `pytest`.
   - Hướng phát triển: Tích hợp cánh tay robot tự động giải Rubik (Hardware Integration) hoặc mô hình 3D tương tác bằng OpenGL.

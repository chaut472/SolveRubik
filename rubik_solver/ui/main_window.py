"""
Cửa sổ chính của ứng dụng Giải Rubik bằng Camera (MainWindow).
Tích hợp toàn diện 8 thành phần: Camera, Thị giác, Mô hình, Thuật toán Kociemba,
Mô phỏng 2D và Trình phát bước giải từng bước.
"""

from typing import List, Optional
import numpy as np

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QListWidget,
    QListWidgetItem,
    QSlider,
    QMessageBox,
    QFrame,
    QStatusBar,
    QTabWidget,
)

from rubik_solver.camera.camera_stream import CameraThread
from rubik_solver.cube.constants import (
    Face,
    FACES_ORDER,
    CubeColor,
    SCAN_SEQUENCE,
    FACE_NAMES_VI,
    COLOR_NAMES_VI,
)
from rubik_solver.cube.cube_state import CubeState
from rubik_solver.cube.validator import validate_cube_state
from rubik_solver.solver.kociemba_solver import solve_cube
from rubik_solver.solver.move_formatter import StepInfo
from rubik_solver.ui.manual_dialog import (
    SingleColorPickerDialog,
    ManualCubeEditorDialog,
)
from rubik_solver.ui.video_widget import VideoWidget
from rubik_solver.visualization.cube_net_2d import CubeNetWidget
from rubik_solver.visualization.cube_3d_widget import Cube3DWidget
from rubik_solver.visualization.step_guide import StepGuideController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phần Mềm Giải Rubik 3x3 Bằng Camera (OpenCV - Kociemba)")
        self.resize(1180, 780)

        # Trạng thái dữ liệu
        self.cube_state = CubeState()
        self.current_scan_step: int = 0
        self.camera_thread: Optional[CameraThread] = None

        # Bộ điều khiển bước giải
        self.step_controller = StepGuideController(self)
        self.step_controller.step_changed.connect(self._on_step_changed)
        self.step_controller.cube_state_changed.connect(self._on_cube_updated_by_player)
        self.step_controller.playback_finished.connect(self._on_playback_finished)

        self._setup_ui()
        self._start_camera()

    def _setup_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(14)

        # ================== CỘT BÊN TRÁI: CAMERA & ĐIỀU KHIỂN QUÉT ==================
        left_panel = QFrame()
        left_panel.setProperty("class", "CardFrame")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)

        # Tiêu đề Camera
        cam_header = QLabel("1. NHẬN DIỆN CAMERA & QUÉT 6 MẶT")
        cam_header.setProperty("class", "HeaderLabel")
        left_layout.addWidget(cam_header)

        # Widget hiển thị Camera
        self.video_widget = VideoWidget(parent=self)
        left_layout.addWidget(self.video_widget, stretch=1)

        # Hàng nút điều khiển quét
        scan_btn_layout = QHBoxLayout()

        self.btn_capture_face = QPushButton("📸 Chụp Mặt Này")
        self.btn_capture_face.setProperty("class", "PrimaryButton")
        self.btn_capture_face.clicked.connect(self._capture_current_face)
        scan_btn_layout.addWidget(self.btn_capture_face)

        self.btn_rescan_face = QPushButton("🔄 Quét Lại Mặt Này")
        self.btn_rescan_face.clicked.connect(self._rescan_current_face)
        scan_btn_layout.addWidget(self.btn_rescan_face)

        self.btn_reset_scan = QPushButton("⏮ Bắt Đầu Lại Từ Mặt 1")
        self.btn_reset_scan.clicked.connect(self._reset_scan_sequence)
        scan_btn_layout.addWidget(self.btn_reset_scan)

        left_layout.addLayout(scan_btn_layout)

        # Điều khiển bật tắt camera & chuyển camera
        cam_ctrl_layout = QHBoxLayout()
        self.btn_toggle_cam = QPushButton("Tắt Camera")
        self.btn_toggle_cam.clicked.connect(self._toggle_camera)
        cam_ctrl_layout.addWidget(self.btn_toggle_cam)

        self.btn_switch_cam = QPushButton("Đổi Camera (0/1)")
        self.btn_switch_cam.clicked.connect(self._switch_camera_device)
        cam_ctrl_layout.addWidget(self.btn_switch_cam)

        self.btn_manual_edit = QPushButton("✏️ Nhập / Sửa Màu Thủ Công")
        self.btn_manual_edit.clicked.connect(self._open_manual_editor)
        cam_ctrl_layout.addWidget(self.btn_manual_edit)

        left_layout.addLayout(cam_ctrl_layout)
        root_layout.addWidget(left_panel, stretch=6)

        # ================== CỘT BÊN PHẢI: MÔ HÌNH 2D & LỜI GIẢI ==================
        right_panel = QFrame()
        right_panel.setProperty("class", "CardFrame")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(10)

        # Tiêu đề mô hình
        model_header = QLabel("2. MÔ HÌNH 54 Ô & TRÌNH PHÁT BƯỚC GIẢI")
        model_header.setProperty("class", "HeaderLabel")
        right_layout.addWidget(model_header)

        # Tab chuyển đổi giữa Mô hình 3D và Mô hình 2D
        self.tabs_view = QTabWidget()
        self.tabs_view.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #334155;
                background-color: #18191C;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #1E222A;
                color: #94A3B8;
                font-weight: 600;
                padding: 6px 14px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: #2563EB;
                color: #FFFFFF;
            }
            QTabBar::tab:hover:!selected {
                background: #334155;
                color: #E2E8F0;
            }
        """)

        # Tab 1: Mô hình 3D
        self.cube_3d = Cube3DWidget(self.cube_state, self)
        self.tabs_view.addTab(self.cube_3d, "🎮 Mô Hình 3D (Xoay 360°)")

        # Tab 2: Mô hình 2D
        self.cube_net = CubeNetWidget(self.cube_state, self)
        self.cube_net.sticker_clicked.connect(self._on_net_sticker_clicked)
        self.tabs_view.addTab(self.cube_net, "🗺️ Mô Hình 2D (Trải Phẳng)")

        right_layout.addWidget(self.tabs_view, stretch=5)

        # Thông báo trạng thái kiểm tra
        self.lbl_status = QLabel("Vui lòng quét đủ 6 mặt Rubik qua camera.")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("color: #94A3B8; font-weight: 500;")
        right_layout.addWidget(self.lbl_status)

        # Nút Giải Rubik lớn
        self.btn_solve = QPushButton("🚀 TÌM LỜI GIẢI (KOCIEMBA)")
        self.btn_solve.setProperty("class", "SuccessButton")
        self.btn_solve.clicked.connect(self._solve_rubik)
        right_layout.addWidget(self.btn_solve)

        # KHU VỰC HƯỚNG DẪN TỪNG BƯỚC (SOLUTION PLAYER)
        player_frame = QFrame()
        player_frame.setStyleSheet(
            "background-color: #1A1D24; border-radius: 8px; border: 1px solid #2C303B; padding: 6px;"
        )
        player_layout = QVBoxLayout(player_frame)

        self.lbl_big_move = QLabel("SẴN SÀNG")
        self.lbl_big_move.setProperty("class", "BigMoveLabel")
        player_layout.addWidget(self.lbl_big_move)

        self.lbl_step_desc = QLabel("Chưa có lời giải. Quét khối Rubik và nhấn nút Tìm lời giải.")
        self.lbl_step_desc.setProperty("class", "StepDescLabel")
        player_layout.addWidget(self.lbl_step_desc)

        # Thanh tiến trình
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        player_layout.addWidget(self.progress_bar)

        # Hàng nút điều khiển Player
        ctrl_row = QHBoxLayout()

        self.btn_player_reset = QPushButton("⏮ Về Đầu")
        self.btn_player_reset.clicked.connect(self.step_controller.reset)
        ctrl_row.addWidget(self.btn_player_reset)

        self.btn_player_prev = QPushButton("◀ Bước Trước")
        self.btn_player_prev.clicked.connect(self.step_controller.prev_step)
        ctrl_row.addWidget(self.btn_player_prev)

        self.btn_player_play = QPushButton("▶ Tự Động")
        self.btn_player_play.clicked.connect(self._toggle_auto_play)
        ctrl_row.addWidget(self.btn_player_play)

        self.btn_player_next = QPushButton("Bước Tiếp ▶")
        self.btn_player_next.clicked.connect(self.step_controller.next_step)
        ctrl_row.addWidget(self.btn_player_next)

        player_layout.addLayout(ctrl_row)

        # Điều chỉnh tốc độ
        speed_row = QHBoxLayout()
        speed_row.addWidget(QLabel("Tốc độ phát:"))
        self.slider_speed = QSlider(Qt.Horizontal)
        self.slider_speed.setRange(400, 2500)
        self.slider_speed.setValue(1000)
        self.slider_speed.valueChanged.connect(self._on_speed_changed)
        speed_row.addWidget(self.slider_speed)
        self.lbl_speed_val = QLabel("1.0s")
        speed_row.addWidget(self.lbl_speed_val)
        player_layout.addLayout(speed_row)

        right_layout.addWidget(player_frame, stretch=4)

        # Danh sách chuỗi nước đi
        self.list_moves = QListWidget()
        self.list_moves.itemClicked.connect(self._on_move_item_clicked)
        right_layout.addWidget(self.list_moves, stretch=2)

        root_layout.addWidget(right_panel, stretch=5)

        # Thanh trạng thái Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ứng dụng sẵn sàng.")

        # Cập nhật mặt đầu tiên cần quét
        self._update_scan_prompt()

    # ================== QUẢN LÝ CAMERA ==================

    def _start_camera(self) -> None:
        if self.camera_thread and self.camera_thread.isRunning():
            return
        self.camera_thread = CameraThread(camera_index=0, target_fps=30, parent=self)
        self.camera_thread.frame_ready.connect(self.video_widget.update_frame)
        self.camera_thread.status_changed.connect(self.status_bar.showMessage)
        self.camera_thread.error_occurred.connect(self._on_camera_error)
        self.camera_thread.start()
        self.btn_toggle_cam.setText("Tắt Camera")

    def _toggle_camera(self) -> None:
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()
            self.btn_toggle_cam.setText("Bật Camera")
            self.status_bar.showMessage("Camera đã tắt.")
        else:
            self._start_camera()

    def _switch_camera_device(self) -> None:
        if not self.camera_thread:
            return
        new_idx = 1 if self.camera_thread.camera_index == 0 else 0
        self.camera_thread.change_camera(new_idx)

    def _on_camera_error(self, err_msg: str) -> None:
        self.status_bar.showMessage(err_msg)

    # ================== QUY TRÌNH QUÉT 6 MẶT ==================

    def _update_scan_prompt(self) -> None:
        """Cập nhật giao diện chỉ dẫn quét mặt tiếp theo."""
        if self.current_scan_step < len(SCAN_SEQUENCE):
            target_face, prompt = SCAN_SEQUENCE[self.current_scan_step]
            self.video_widget.set_current_scan_face(self.current_scan_step)
            self.cube_net.set_highlighted_face(target_face)
            self.status_bar.showMessage(f"Đang chờ quét: {FACE_NAMES_VI[target_face]}")
        else:
            self.cube_net.set_highlighted_face(None)
            self.status_bar.showMessage("Đã quét đủ 6 mặt! Hãy kiểm tra và nhấn Giải Rubik.")

    def _capture_current_face(self) -> None:
        """Chụp 9 ô màu từ khung hình camera hiện tại và nạp vào mặt đang chọn."""
        if self.current_scan_step >= len(SCAN_SEQUENCE):
            QMessageBox.information(
                self, "Thông báo", "Bạn đã quét đủ cả 6 mặt. Hãy nhấn nút 'Tìm lời giải'!"
            )
            return

        target_face, _ = SCAN_SEQUENCE[self.current_scan_step]
        detected_colors = self.video_widget.get_latest_colors()

        # Kiểm tra nếu ô chưa nhận diện được
        if any(c == CubeColor.UNKNOWN for c in detected_colors):
            QMessageBox.warning(
                self,
                "Ảnh không rõ",
                "Chưa nhận diện rõ tất cả 9 ô. Vui lòng căn chỉnh lại vị trí Rubik trong khung lưới.",
            )
            return

        # Gán màu vào mặt
        self.cube_state.set_face(target_face, detected_colors)
        self.cube_net.set_cube_state(self.cube_state)
        self.cube_3d.set_cube_state(self.cube_state)

        # Chuyển sang mặt kế tiếp
        self.current_scan_step += 1
        if self.current_scan_step < len(SCAN_SEQUENCE):
            self._update_scan_prompt()
        else:
            self._update_scan_prompt()
            # Kiểm tra trạng thái toàn diện
            val = validate_cube_state(self.cube_state)
            if val.is_valid:
                self.lbl_status.setText("✓ Đã quét đủ 6 mặt và hợp lệ! Sẵn sàng giải.")
                self.lbl_status.setStyleSheet("color: #4ADE80; font-weight: bold;")
            else:
                self.lbl_status.setText(f"⚠ {val.message}")
                self.lbl_status.setStyleSheet("color: #F87171; font-weight: bold;")

    def _rescan_current_face(self) -> None:
        """Quét lại mặt vừa quét gần nhất nếu người dùng thấy màu chưa chuẩn."""
        if self.current_scan_step > 0:
            self.current_scan_step -= 1
            self._update_scan_prompt()

    def _reset_scan_sequence(self) -> None:
        """Bắt đầu lại chu kỳ quét 6 mặt từ đầu."""
        self.current_scan_step = 0
        self.cube_state.reset_to_solved()
        self.cube_net.set_cube_state(self.cube_state)
        self.cube_3d.set_cube_state(self.cube_state)
        self._update_scan_prompt()
        self.lbl_status.setText("Đã đặt lại chu kỳ quét từ Mặt Trên (Trắng).")

    # ================== CHỈNH SỬA THỦ CÔNG ==================

    def _on_net_sticker_clicked(self, face: Face, index: int) -> None:
        """Khi click vào 1 ô trên lưới 2D, mở dialog đổi màu ô đó."""
        cur_color = self.cube_state.get_sticker(face, index)
        dlg = SingleColorPickerDialog(face, index, cur_color, self)
        if dlg.exec():
            self.cube_state.set_sticker(face, index, dlg.selected_color)
            self.cube_net.set_cube_state(self.cube_state)
            self.cube_3d.set_cube_state(self.cube_state)
            val = validate_cube_state(self.cube_state)
            if val.is_valid:
                self.lbl_status.setText("✓ Trạng thái Rubik hợp lệ!")
                self.lbl_status.setStyleSheet("color: #4ADE80;")
            else:
                self.lbl_status.setText(f"⚠ {val.message}")
                self.lbl_status.setStyleSheet("color: #F87171;")

    def _open_manual_editor(self) -> None:
        """Mở bảng vẽ 54 ô thủ công toàn màn hình."""
        dlg = ManualCubeEditorDialog(self.cube_state, self)
        if dlg.exec():
            self.cube_state = dlg.get_cube_state()
            self.cube_net.set_cube_state(self.cube_state)
            self.cube_3d.set_cube_state(self.cube_state)
            val = validate_cube_state(self.cube_state)
            if val.is_valid:
                self.lbl_status.setText("✓ Trạng thái thủ công hợp lệ! Sẵn sàng giải.")
                self.lbl_status.setStyleSheet("color: #4ADE80;")
            else:
                self.lbl_status.setText(f"⚠ {val.message}")
                self.lbl_status.setStyleSheet("color: #F87171;")

    # ================== TÌM LỜI GIẢI KOCIEMBA ==================

    def _solve_rubik(self) -> None:
        """Gọi thuật toán Kociemba để tìm lời giải."""
        success, moves, msg = solve_cube(self.cube_state)
        if not success:
            QMessageBox.critical(self, "Không thể giải", f"Lỗi: {msg}")
            self.lbl_status.setText(f"Lỗi: {msg}")
            self.lbl_status.setStyleSheet("color: #EF4444; font-weight: bold;")
            return

        if len(moves) == 0:
            QMessageBox.information(
                self, "Hoàn thành", "Khối Rubik này đã ở trạng thái hoàn thành (0 bước xoay)!"
            )
            return

        self.lbl_status.setText(f"✓ {msg}")
        self.lbl_status.setStyleSheet("color: #38BDF8; font-weight: bold;")

        # Nạp vào danh sách ListWidget
        self.list_moves.clear()
        for idx, m in enumerate(moves, start=1):
            item = QListWidgetItem(f"Bước {idx:02d}:  {m}")
            self.list_moves.addItem(item)

        # Nạp vào StepGuideController
        self.cube_3d.set_cube_state(self.cube_state)
        self.step_controller.load_solution(self.cube_state, moves)
        self.progress_bar.setValue(0)

    # ================== TRÌNH PHÁT BƯỚC GIẢI (SOLUTION PLAYER) ==================

    @Slot(object, int, int)
    def _on_step_changed(self, step_info: Optional[StepInfo], current_idx: int, total_steps: int) -> None:
        if total_steps == 0:
            return

        # Cập nhật thanh tiến trình
        pct = int((current_idx / total_steps) * 100)
        self.progress_bar.setValue(pct)

        # Highlight dòng tương ứng trong list_moves
        if 0 <= current_idx < self.list_moves.count():
            self.list_moves.setCurrentRow(current_idx)

        cur_cube = self.step_controller.current_cube or self.cube_state

        # Hiển thị nước đi lớn
        if step_info:
            self.lbl_big_move.setText(step_info.move)
            self.lbl_step_desc.setText(step_info.get_full_text())

            # Kích hoạt diễn hoạt xoay 3D mượt mà
            speed_val = self.slider_speed.value()
            anim_duration = max(180, int(speed_val * 0.55))
            self.cube_3d.animate_move(step_info.move, anim_duration, cur_cube)
        else:
            self.cube_3d.set_cube_state(cur_cube)
            if current_idx >= total_steps:
                self.lbl_big_move.setText("HOÀN THÀNH")
                self.lbl_step_desc.setText("🎉 Chúc mừng! Khối Rubik đã được giải hoàn tất.")
            else:
                self.lbl_big_move.setText("BẮT ĐẦU")
                self.lbl_step_desc.setText("Nhấn 'Bước Tiếp' hoặc 'Tự Động' để bắt đầu giải.")

    @Slot(CubeState)
    def _on_cube_updated_by_player(self, cube: CubeState) -> None:
        self.cube_net.set_cube_state(cube)

    def _toggle_auto_play(self) -> None:
        self.step_controller.toggle_play()
        if self.step_controller.is_playing:
            self.btn_player_play.setText("⏸ Tạm Dừng")
        else:
            self.btn_player_play.setText("▶ Tự Động")

    def _on_playback_finished(self) -> None:
        self.btn_player_play.setText("▶ Tự Động")

    def _on_speed_changed(self, val: int) -> None:
        sec = val / 1000.0
        self.lbl_speed_val.setText(f"{sec:.1f}s")
        self.step_controller.set_speed(val)

    def _on_move_item_clicked(self, item: QListWidgetItem) -> None:
        row = self.list_moves.row(item)
        if row >= 0:
            self.step_controller.jump_to_step(row)

    def closeEvent(self, event) -> None:
        """Dọn dẹp luồng camera an toàn trước khi đóng ứng dụng."""
        if self.camera_thread:
            self.camera_thread.stop()
        event.accept()

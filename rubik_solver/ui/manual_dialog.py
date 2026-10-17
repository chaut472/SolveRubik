"""
Hộp thoại chỉnh sửa và nhập màu thủ công (Manual Input & Palette Dialog).
Cho phép người dùng chọn màu từ bảng palette để tô trực tiếp lên mô hình 54 ô.
"""

from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QButtonGroup,
    QMessageBox,
    QFrame,
)

from rubik_solver.cube.constants import (
    Face,
    CubeColor,
    COLOR_HEX,
    COLOR_NAMES_VI,
    FACE_NAMES_VI,
)
from rubik_solver.cube.cube_state import CubeState
from rubik_solver.cube.validator import validate_cube_state
from rubik_solver.visualization.cube_net_2d import CubeNetWidget


class SingleColorPickerDialog(QDialog):
    """Hộp thoại popup nhỏ để đổi màu 1 ô vừa được click."""

    def __init__(self, face: Face, index: int, current_color: CubeColor, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Đổi màu - {FACE_NAMES_VI[face]} [Ô {index + 1}]")
        self.setFixedSize(340, 220)
        self.selected_color = current_color

        layout = QVBoxLayout(self)

        info_label = QLabel(
            f"Chọn màu mới cho ô số {index + 1} ({FACE_NAMES_VI[face]}):"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #38BDF8;")
        layout.addWidget(info_label)

        # 6 nút màu xếp 2 hàng x 3 cột
        btn_layout = QVBoxLayout()
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()

        colors = [
            CubeColor.WHITE, CubeColor.YELLOW, CubeColor.GREEN,
            CubeColor.BLUE, CubeColor.RED, CubeColor.ORANGE
        ]

        for i, color in enumerate(colors):
            btn = QPushButton(COLOR_NAMES_VI[color])
            hex_c = COLOR_HEX[color]
            text_c = "#000000" if color in (CubeColor.WHITE, CubeColor.YELLOW) else "#FFFFFF"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {hex_c};
                    color: {text_c};
                    font-weight: bold;
                    font-size: 13px;
                    border: 2px solid #1E222A;
                    border-radius: 6px;
                    padding: 10px;
                }}
                QPushButton:hover {{
                    border: 2px solid #FFFFFF;
                }}
            """)
            btn.clicked.connect(lambda _, c=color: self._choose_color(c))

            if i < 3:
                row1.addWidget(btn)
            else:
                row2.addWidget(btn)

        btn_layout.addLayout(row1)
        btn_layout.addLayout(row2)
        layout.addLayout(btn_layout)

    def _choose_color(self, color: CubeColor) -> None:
        self.selected_color = color
        self.accept()


class ManualCubeEditorDialog(QDialog):
    """Hộp thoại bảng vẽ toàn diện: chọn màu cọ vẽ rồi click tô màu lên mô hình 2D."""

    def __init__(self, cube_state: CubeState, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chỉnh sửa trạng thái Rubik 54 ô thủ công")
        self.resize(700, 560)
        self.cube = cube_state.clone()
        self.brush_color: CubeColor = CubeColor.WHITE

        self._setup_ui()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        title = QLabel("BẢNG ĐIỀU CHỈNH TRẠNG THÁI KHỐI RUBIK")
        title.setProperty("class", "HeaderLabel")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        hint = QLabel(
            "Hướng dẫn: 1) Chọn màu cọ bên dưới. 2) Click chuột lên bất kỳ ô nào trên khối 2D để tô màu."
        )
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color: #94A3B8; font-style: italic; margin-bottom: 8px;")
        main_layout.addWidget(hint)

        # Thanh chọn cọ vẽ (Palette Bar)
        palette_frame = QFrame()
        palette_frame.setProperty("class", "CardFrame")
        palette_layout = QHBoxLayout(palette_frame)
        palette_layout.addWidget(QLabel("Cọ màu đang chọn:"))

        self.color_group = QButtonGroup(self)
        colors = [
            CubeColor.WHITE, CubeColor.YELLOW, CubeColor.GREEN,
            CubeColor.BLUE, CubeColor.RED, CubeColor.ORANGE
        ]

        for i, color in enumerate(colors):
            btn = QPushButton(COLOR_NAMES_VI[color])
            btn.setCheckable(True)
            if color == CubeColor.WHITE:
                btn.setChecked(True)

            hex_c = COLOR_HEX[color]
            text_c = "#000000" if color in (CubeColor.WHITE, CubeColor.YELLOW) else "#FFFFFF"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {hex_c};
                    color: {text_c};
                    font-weight: bold;
                    border: 2px solid #334155;
                    border-radius: 6px;
                    padding: 8px 12px;
                }}
                QPushButton:checked {{
                    border: 3px solid #38BDF8;
                }}
            """)
            btn.clicked.connect(lambda _, c=color: self._set_brush(c))
            self.color_group.addButton(btn, i)
            palette_layout.addWidget(btn)

        main_layout.addWidget(palette_frame)

        # Mô hình CubeNet 2D
        self.cube_net = CubeNetWidget(self.cube, self)
        self.cube_net.sticker_clicked.connect(self._on_sticker_clicked)
        main_layout.addWidget(self.cube_net, stretch=1)

        # Thông báo trạng thái màu sắc
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self._update_status()
        main_layout.addWidget(self.status_label)

        # Hàng nút thao tác
        action_layout = QHBoxLayout()

        btn_reset = QPushButton("Đặt lại (Đã giải)")
        btn_reset.clicked.connect(self._reset_to_solved)
        action_layout.addWidget(btn_reset)

        action_layout.addStretch()

        btn_cancel = QPushButton("Hủy bỏ")
        btn_cancel.clicked.connect(self.reject)
        action_layout.addWidget(btn_cancel)

        btn_save = QPushButton("Xác nhận & Áp dụng")
        btn_save.setProperty("class", "SuccessButton")
        btn_save.clicked.connect(self._validate_and_save)
        action_layout.addWidget(btn_save)

        main_layout.addLayout(action_layout)

    def _set_brush(self, color: CubeColor) -> None:
        self.brush_color = color

    def _on_sticker_clicked(self, face: Face, index: int) -> None:
        self.cube.set_sticker(face, index, self.brush_color)
        self.cube_net.set_cube_state(self.cube)
        self._update_status()

    def _reset_to_solved(self) -> None:
        self.cube.reset_to_solved()
        self.cube_net.set_cube_state(self.cube)
        self._update_status()

    def _update_status(self) -> None:
        val = validate_cube_state(self.cube)
        if val.is_valid:
            self.status_label.setText("✓ Trạng thái hợp lệ (Mỗi màu đủ 9 ô, 6 tâm phân biệt)")
            self.status_label.setStyleSheet("color: #4ADE80; font-weight: bold;")
        else:
            self.status_label.setText(f"⚠ {val.message}")
            self.status_label.setStyleSheet("color: #F87171;")

    def _validate_and_save(self) -> None:
        val = validate_cube_state(self.cube)
        if not val.is_valid:
            reply = QMessageBox.warning(
                self,
                "Cảnh báo trạng thái",
                f"{val.message}\n\nBạn có chắc chắn muốn lưu trạng thái này không?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        self.accept()

    def get_cube_state(self) -> CubeState:
        return self.cube

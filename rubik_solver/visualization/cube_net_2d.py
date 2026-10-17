"""
Hiển thị mô hình 2D trải phẳng 6 mặt Rubik (Cube Net 2D).
Cho phép tương tác click trực tiếp vào từng ô để kiểm tra hoặc sửa màu thủ công.
"""

from typing import Optional, Dict
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QMouseEvent
from PySide6.QtWidgets import QWidget

from rubik_solver.cube.constants import (
    Face,
    FACES_ORDER,
    CubeColor,
    COLOR_HEX,
    FACE_NAMES_VI,
)
from rubik_solver.cube.cube_state import CubeState


class CubeNetWidget(QWidget):
    # Tín hiệu khi người dùng click vào một ô cụ thể
    sticker_clicked = Signal(Face, int)

    # Bố cục lưới 6 mặt trên hệ tọa độ (row, col)
    #       [ U ]
    # [ L ] [ F ] [ R ] [ B ]
    #       [ D ]
    FACE_GRID_POS: Dict[Face, tuple[int, int]] = {
        Face.U: (0, 1),
        Face.L: (1, 0),
        Face.F: (1, 1),
        Face.R: (1, 2),
        Face.B: (1, 3),
        Face.D: (2, 1),
    }

    def __init__(self, cube: Optional[CubeState] = None, parent=None):
        super().__init__(parent)
        self.cube: CubeState = cube or CubeState()
        self.highlighted_face: Optional[Face] = None
        self.setMinimumSize(320, 240)
        self.setMouseTracking(True)

    def set_cube_state(self, cube: CubeState) -> None:
        """Cập nhật trạng thái Rubik và vẽ lại."""
        self.cube = cube
        self.update()

    def set_highlighted_face(self, face: Optional[Face]) -> None:
        """Làm nổi bật viền của mặt đang được quét hoặc thao tác."""
        self.highlighted_face = face
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Tổng số ô: 4 cột x 3 dòng mặt. Mỗi mặt gồm 3x3 ô nhỏ -> 12 x 9 ô
        # Tính kích thước ô sticker (tile_size)
        margin = 16
        avail_w = w - 2 * margin
        avail_h = h - 2 * margin

        tile_size = min(avail_w / 12.0, avail_h / 9.0)
        face_size = tile_size * 3.0

        # Căn giữa toàn bộ mô hình
        total_net_w = face_size * 4.0
        total_net_h = face_size * 3.0
        offset_x = margin + (avail_w - total_net_w) / 2.0
        offset_y = margin + (avail_h - total_net_h) / 2.0

        pen_border = QPen(QColor("#1E222A"), 1.5)
        pen_highlight = QPen(QColor("#38BDF8"), 3.0)

        font = QFont("Segoe UI", int(max(8, tile_size * 0.35)), QFont.Bold)
        painter.setFont(font)

        for face, (grid_r, grid_c) in self.FACE_GRID_POS.items():
            face_x = offset_x + grid_c * face_size
            face_y = offset_y + grid_r * face_size

            # Làm nổi bật mặt nếu được chọn
            if face == self.highlighted_face:
                painter.setPen(pen_highlight)
                painter.setBrush(Qt.NoBrush)
                painter.drawRoundedRect(
                    QRectF(face_x - 3, face_y - 3, face_size + 6, face_size + 6), 4, 4
                )

            # Vẽ 9 ô của mặt
            stickers = self.cube.get_face(face)
            for idx in range(9):
                r = idx // 3
                c = idx % 3
                tile_x = face_x + c * tile_size
                tile_y = face_y + r * tile_size

                color = stickers[idx]
                hex_color = COLOR_HEX.get(color, "#3C3F41")
                bg_color = QColor(hex_color)

                painter.setPen(pen_border)
                painter.setBrush(QBrush(bg_color))
                painter.drawRoundedRect(
                    QRectF(tile_x + 1, tile_y + 1, tile_size - 2, tile_size - 2), 3, 3
                )

                # Vẽ nhãn tên mặt ở ô tâm (idx == 4)
                if idx == 4:
                    text_color = (
                        QColor("#000000")
                        if color in (CubeColor.WHITE, CubeColor.YELLOW)
                        else QColor("#FFFFFF")
                    )
                    painter.setPen(text_color)
                    painter.drawText(
                        QRectF(tile_x, tile_y, tile_size, tile_size),
                        Qt.AlignCenter,
                        face.value,
                    )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Xử lý sự kiện click chuột để tìm ô được chọn."""
        if event.button() != Qt.LeftButton:
            return

        pos = event.position()
        mx, my = pos.x(), pos.y()

        w = self.width()
        h = self.height()
        margin = 16
        avail_w = w - 2 * margin
        avail_h = h - 2 * margin
        tile_size = min(avail_w / 12.0, avail_h / 9.0)
        face_size = tile_size * 3.0

        total_net_w = face_size * 4.0
        total_net_h = face_size * 3.0
        offset_x = margin + (avail_w - total_net_w) / 2.0
        offset_y = margin + (avail_h - total_net_h) / 2.0

        for face, (grid_r, grid_c) in self.FACE_GRID_POS.items():
            face_x = offset_x + grid_c * face_size
            face_y = offset_y + grid_r * face_size

            if face_x <= mx <= face_x + face_size and face_y <= my <= face_y + face_size:
                col = int((mx - face_x) // tile_size)
                row = int((my - face_y) // tile_size)
                if 0 <= col < 3 and 0 <= row < 3:
                    idx = row * 3 + col
                    self.sticker_clicked.emit(face, idx)
                    return

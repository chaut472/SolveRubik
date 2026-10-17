"""
Widget hiển thị luồng Camera và lớp phủ định vị lưới 3x3 (Video Widget).
Hỗ trợ hiển thị chỉ dẫn các bước quét 6 mặt trực quan trên màn hình.
"""

from typing import List, Tuple, Optional
import cv2
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from rubik_solver.cube.constants import (
    Face,
    CubeColor,
    SCAN_SEQUENCE,
    FACE_NAMES_VI,
    COLOR_HEX,
)
from rubik_solver.vision.grid_detector import GridDetector


class VideoWidget(QWidget):
    # Phát tín hiệu khi nhận diện được 9 màu của khung hình hiện tại
    colors_updated = Signal(list)

    def __init__(self, grid_detector: Optional[GridDetector] = None, parent=None):
        super().__init__(parent)
        self.grid_detector = grid_detector or GridDetector()

        self.latest_colors: List[CubeColor] = [CubeColor.UNKNOWN] * 9
        self.latest_confidences: List[float] = [0.0] * 9
        self.current_scan_index: int = 0  # 0 đến 5 tương ứng SCAN_SEQUENCE

        self._pixmap: Optional[QPixmap] = None
        self.setMinimumSize(480, 360)
        self.setStyleSheet("background-color: #0F172A; border-radius: 8px;")

    def set_current_scan_face(self, scan_idx: int) -> None:
        """Cập nhật mặt đang được yêu cầu quét (0 -> 5)."""
        self.current_scan_index = max(0, min(scan_idx, len(SCAN_SEQUENCE) - 1))
        self.update()

    def update_frame(self, frame: np.ndarray) -> None:
        """Nhận frame BGR từ CameraThread, xử lý qua GridDetector và vẽ lên QPixmap."""
        if frame is None or frame.size == 0:
            return

        colors, confs, annotated_frame = self.grid_detector.process_frame(frame)
        self.latest_colors = colors
        self.latest_confidences = confs
        self.colors_updated.emit(self.latest_colors)

        # Chuyển đổi BGR sang RGB cho QImage
        rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        self._pixmap = QPixmap.fromImage(q_img)
        self.update()

    def get_latest_colors(self) -> List[CubeColor]:
        """Lấy 9 màu nhận diện của khung hình mới nhất."""
        return list(self.latest_colors)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        if self._pixmap and not self._pixmap.isNull():
            # Scale pixmap giữ nguyên tỷ lệ khung hình
            scaled = self._pixmap.scaled(
                w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            px = (w - scaled.width()) // 2
            py = (h - scaled.height()) // 2
            painter.drawPixmap(px, py, scaled)
        else:
            # Khi camera chưa bật
            painter.setPen(QColor("#64748B"))
            painter.setFont(QFont("Segoe UI", 14))
            painter.drawText(
                0, 0, w, h, Qt.AlignCenter, "Camera đang tắt hoặc chưa kết nối..."
            )

        # Vẽ dải banner chỉ dẫn ở trên cùng
        if 0 <= self.current_scan_index < len(SCAN_SEQUENCE):
            target_face, instruction = SCAN_SEQUENCE[self.current_scan_index]
            banner_h = 42

            # Nền banner mờ đục
            painter.fillRect(0, 0, w, banner_h, QColor(15, 23, 42, 210))

            # Chữ tiêu đề mặt cần quét
            painter.setPen(QColor("#38BDF8"))
            painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
            banner_text = f"Bước {self.current_scan_index + 1}/6: {instruction}"
            painter.drawText(12, 0, w - 24, banner_h, Qt.AlignVCenter | Qt.AlignLeft, banner_text)

"""
Phát hiện và hiển thị lưới 3x3 trên khung hình camera (Grid Detector).
Trích xuất 9 ô sticker và vẽ lớp phủ định vị thời gian thực.
"""

from typing import List, Tuple, Optional
import cv2
import numpy as np

from rubik_solver.cube.constants import CubeColor, COLOR_TO_CHAR
from rubik_solver.vision.color_detector import ColorDetector

# Bảng màu BGR tương ứng cho việc vẽ OpenCV
COLOR_BGR_DRAW = {
    CubeColor.WHITE: (255, 255, 255),
    CubeColor.YELLOW: (0, 220, 240),
    CubeColor.GREEN: (0, 180, 0),
    CubeColor.BLUE: (220, 60, 0),
    CubeColor.RED: (0, 0, 220),
    CubeColor.ORANGE: (0, 120, 255),
    CubeColor.UNKNOWN: (128, 128, 128),
}


class GridDetector:
    def __init__(self, color_detector: Optional[ColorDetector] = None):
        self.color_detector = color_detector or ColorDetector()
        self.grid_scale = 0.58  # Tỷ lệ kích thước lưới so với chiều nhỏ nhất của khung hình
        self.cell_padding = 6   # Khoảng đệm giữa các ô trong lưới

    def get_grid_boxes(self, frame_w: int, frame_h: int) -> List[Tuple[int, int, int, int]]:
        """
        Tính toán tọa độ (x1, y1, x2, y2) của 9 ô vuông ở trung tâm khung hình.
        Thứ tự: hàng trên (0, 1, 2), hàng giữa (3, 4, 5), hàng dưới (6, 7, 8).
        """
        grid_size = int(min(frame_w, frame_h) * self.grid_scale)
        cell_size = grid_size // 3

        start_x = (frame_w - grid_size) // 2
        start_y = (frame_h - grid_size) // 2

        boxes = []
        for r in range(3):
            for c in range(3):
                x1 = start_x + c * cell_size + self.cell_padding
                y1 = start_y + r * cell_size + self.cell_padding
                x2 = start_x + (c + 1) * cell_size - self.cell_padding
                y2 = start_y + (r + 1) * cell_size - self.cell_padding
                boxes.append((x1, y1, x2, y2))
        return boxes

    def process_frame(
        self, frame: np.ndarray
    ) -> Tuple[List[CubeColor], List[float], np.ndarray]:
        """
        Xử lý 1 khung hình camera:
        1. Trích xuất màu của 9 ô.
        2. Vẽ lưới chỉ dẫn, mã màu và viền trạng thái lên khung hình.
        """
        annotated = frame.copy()
        h, w = frame.shape[:2]
        boxes = self.get_grid_boxes(w, h)

        detected_colors: List[CubeColor] = []
        confidences: List[float] = []

        for idx, (x1, y1, x2, y2) in enumerate(boxes):
            # Cắt ảnh vùng ô sticker
            patch = frame[y1:y2, x1:x2]
            color, conf = self.color_detector.classify_patch(patch)
            detected_colors.append(color)
            confidences.append(conf)

            # Màu viền và màu badge
            bgr = COLOR_BGR_DRAW.get(color, (128, 128, 128))
            is_center = (idx == 4)

            # Vẽ ô chữ nhật bo góc nhẹ / nét vẽ dày
            thickness = 3 if is_center else 2
            cv2.rectangle(annotated, (x1, y1), (x2, y2), bgr, thickness)

            # Vẽ chấm màu trung tâm hiển thị màu đã nhận diện
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            cv2.circle(annotated, (cx, cy), 14, bgr, -1)
            cv2.circle(annotated, (cx, cy), 14, (0, 0, 0), 1)

            # Vẽ ký tự viết tắt của màu (W, Y, G, B, R, O)
            char_code = COLOR_TO_CHAR.get(color, "?")
            text_color = (0, 0, 0) if color in (CubeColor.WHITE, CubeColor.YELLOW) else (255, 255, 255)
            cv2.putText(
                annotated,
                char_code,
                (cx - 5, cy + 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                text_color,
                2,
                cv2.LINE_AA,
            )

            # Đánh dấu ô tâm
            if is_center:
                cv2.putText(
                    annotated,
                    "TAM",
                    (cx - 15, y2 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.38,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

        return detected_colors, confidences, annotated

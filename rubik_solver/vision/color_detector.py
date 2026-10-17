"""
Phân loại màu sắc của ô Rubik (Color Detector).
Kết hợp không gian màu HSV và khoảng cách CIELAB để nhận diện chính xác 6 màu.
"""

from typing import Tuple, Dict, Any, Optional
import cv2
import numpy as np

from rubik_solver.cube.constants import CubeColor
from rubik_solver.vision.calibrator import Calibrator


class ColorDetector:
    def __init__(self, calibrator: Optional[Calibrator] = None):
        self.calibrator = calibrator or Calibrator()

    @property
    def config(self) -> Dict[str, Any]:
        return self.calibrator.config

    def classify_bgr(self, bgr_color: Tuple[int, int, int]) -> Tuple[CubeColor, float]:
        """
        Phân loại một màu BGR duy nhất sang CubeColor kèm độ tin cậy (0.0 -> 1.0).
        """
        # Tạo ảnh 1x1 pixel để chuyển không gian màu qua OpenCV
        pixel = np.uint8([[list(bgr_color)]])
        hsv_pixel = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)[0][0]
        h, s, v = int(hsv_pixel[0]), int(hsv_pixel[1]), int(hsv_pixel[2])

        white_cfg = self.config.get("white", {"max_s": 65, "min_v": 130})
        # 1. Kiểm tra màu Trắng (Saturation thấp, Value cao)
        if s <= white_cfg["max_s"] and v >= white_cfg["min_v"]:
            # Độ tin cậy cao khi S càng nhỏ và V càng cao
            conf = min(1.0, (white_cfg["max_s"] - s + 10) / (white_cfg["max_s"] + 10))
            return CubeColor.WHITE, round(conf, 2)

        # 2. Phân loại theo dải Hue
        hue_ranges = self.config.get("hue_ranges", {})
        o_range = hue_ranges.get("orange", [6, 20])
        y_range = hue_ranges.get("yellow", [21, 38])
        g_range = hue_ranges.get("green", [39, 85])
        b_range = hue_ranges.get("blue", [86, 135])
        r_low = hue_ranges.get("red_low", [0, 5])
        r_high = hue_ranges.get("red_high", [170, 180])

        if (r_low[0] <= h <= r_low[1]) or (r_high[0] <= h <= r_high[1]):
            return CubeColor.RED, 0.95
        elif o_range[0] <= h <= o_range[1]:
            return CubeColor.ORANGE, 0.90
        elif y_range[0] <= h <= y_range[1]:
            return CubeColor.YELLOW, 0.92
        elif g_range[0] <= h <= g_range[1]:
            return CubeColor.GREEN, 0.95
        elif b_range[0] <= h <= b_range[1]:
            return CubeColor.BLUE, 0.95

        # 3. Dự phòng bằng khoảng cách CIELAB nếu Hue rơi vào khoảng chuyển tiếp
        return self._classify_by_lab_distance(pixel)

    def _classify_by_lab_distance(self, pixel_bgr: np.ndarray) -> Tuple[CubeColor, float]:
        """Tính khoảng cách Euclidean trong không gian CIELAB tới 6 màu tham chiếu."""
        pixel_lab = cv2.cvtColor(pixel_bgr, cv2.COLOR_BGR2LAB)[0][0].astype(np.float32)

        lab_refs = self.config.get("lab_references", {})
        min_dist = float("inf")
        best_color = CubeColor.UNKNOWN

        for color_name, bgr_val in lab_refs.items():
            ref_bgr = np.uint8([[bgr_val]])
            ref_lab = cv2.cvtColor(ref_bgr, cv2.COLOR_BGR2LAB)[0][0].astype(np.float32)
            dist = np.linalg.norm(pixel_lab - ref_lab)
            if dist < min_dist:
                min_dist = dist
                best_color = CubeColor(color_name)

        confidence = max(0.1, 1.0 - (min_dist / 150.0))
        return best_color, round(confidence, 2)

    def classify_patch(self, patch_bgr: np.ndarray) -> Tuple[CubeColor, float]:
        """
        Trích xuất vùng trung tâm của ô ảnh (loại bỏ viền đen và ánh sáng phản chiếu)
        và tính màu trung vị đại diện.
        """
        if patch_bgr is None or patch_bgr.size == 0:
            return CubeColor.UNKNOWN, 0.0

        h, w = patch_bgr.shape[:2]
        # Lấy 50% vùng trung tâm của ô
        y1, y2 = int(h * 0.25), int(h * 0.75)
        x1, x2 = int(w * 0.25), int(w * 0.75)
        roi = patch_bgr[y1:y2, x1:x2]

        if roi.size == 0:
            roi = patch_bgr

        # Dùng median thay vì mean để loại trừ nhiễu điểm phản chiếu ánh sáng mạnh
        median_b = int(np.median(roi[:, :, 0]))
        median_g = int(np.median(roi[:, :, 1]))
        median_r = int(np.median(roi[:, :, 2]))

        return self.classify_bgr((median_b, median_g, median_r))

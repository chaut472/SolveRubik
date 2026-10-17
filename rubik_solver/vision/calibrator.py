"""
Quản lý hồ sơ cấu hình màu sắc (Color Calibrator).
Hỗ trợ lưu và nạp ngưỡng màu từ file JSON phù hợp với từng webcam và môi trường ánh sáng.
"""

import json
import os
from typing import Dict, Any


DEFAULT_CALIBRATION = {
    # Ngưỡng phát hiện White trong không gian HSV: S <= max_s và V >= min_v
    "white": {"max_s": 65, "min_v": 130},
    # Dải Hue (0 - 180 theo chuẩn OpenCV)
    "hue_ranges": {
        "orange": [6, 20],
        "yellow": [21, 38],
        "green": [39, 85],
        "blue": [86, 135],
        "red_low": [0, 5],
        "red_high": [170, 180],
    },
    # Giá trị tham chiếu chuẩn BGR cho từng màu (đo khoảng cách CIELAB khi cần)
    "lab_references": {
        "white": [240, 240, 240],
        "yellow": [20, 220, 240],
        "green": [40, 160, 20],
        "blue": [180, 70, 20],
        "red": [30, 20, 200],
        "orange": [20, 100, 240],
    },
}


class Calibrator:
    def __init__(self, config_path: str = "color_profile.json"):
        self.config_path = config_path
        self.config: Dict[str, Any] = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return dict(DEFAULT_CALIBRATION)
        return dict(DEFAULT_CALIBRATION)

    def save_config(self) -> bool:
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception:
            return False

    def reset_to_default(self) -> None:
        self.config = dict(DEFAULT_CALIBRATION)
        self.save_config()

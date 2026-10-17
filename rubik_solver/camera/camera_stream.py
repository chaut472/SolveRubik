"""
Quản lý luồng Camera bằng QThread độc lập (Camera Stream).
Đảm bảo giao diện PySide6 luôn mượt mà (60 FPS) và không bị gián đoạn khi đọc webcam.
"""

import time
from typing import Optional
import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal


class CameraThread(QThread):
    # Signals
    frame_ready = Signal(np.ndarray)
    status_changed = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, camera_index: int = 0, target_fps: int = 30, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self.target_fps = target_fps
        self._is_running = False
        self._cap: Optional[cv2.VideoCapture] = None

    def run(self) -> None:
        """Vòng lặp lấy khung hình webcam."""
        self._is_running = True
        self.status_changed.emit(f"Đang kết nối camera #{self.camera_index}...")

        # Thử mở camera với backend DirectShow trên Windows
        self._cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not self._cap.isOpened():
            # Thử mở backend mặc định
            self._cap = cv2.VideoCapture(self.camera_index)

        if not self._cap.isOpened():
            # Thử camera phụ index 1
            if self.camera_index == 0:
                self._cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
                if self._cap.isOpened():
                    self.camera_index = 1

        if not self._cap or not self._cap.isOpened():
            self.error_occurred.emit(
                f"Không thể mở camera #{self.camera_index}. Vui lòng kiểm tra kết nối webcam hoặc cấp quyền."
            )
            self._is_running = False
            return

        # Cấu hình độ phân giải phù hợp (640x480 để xử lý nhanh và ổn định)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.status_changed.emit("Camera đang hoạt động.")
        interval = 1.0 / self.target_fps

        while self._is_running:
            t0 = time.time()
            ret, frame = self._cap.read()
            if not ret or frame is None:
                self.error_occurred.emit("Mất tín hiệu từ camera.")
                break

            # Lật gương theo chiều ngang (Mirror) để người dùng điều khiển tự nhiên hơn
            frame = cv2.flip(frame, 1)

            # Phát tín hiệu frame mới cho GUI
            self.frame_ready.emit(frame)

            # Điều tiết FPS
            elapsed = time.time() - t0
            sleep_time = interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

        # Giải phóng tài nguyên camera khi thoát
        if self._cap and self._cap.isOpened():
            self._cap.release()
            self._cap = None
        self.status_changed.emit("Đã ngắt kết nối camera.")

    def stop(self) -> None:
        """Dừng luồng camera an toàn."""
        self._is_running = False
        self.wait(2000)

    def change_camera(self, new_index: int) -> None:
        """Chuyển đổi thiết bị camera."""
        self.stop()
        self.camera_index = new_index
        self.start()

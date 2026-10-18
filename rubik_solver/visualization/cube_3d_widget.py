"""
Widget hiển thị mô hình 3D tương tác của khối Rubik (Three.js WebGL & QWebEngineView).
Hỗ trợ người dùng xoay 360 độ bằng chuột, phóng to thu nhỏ và diễn hoạt xoay mặt mượt mà.
"""

import os
from typing import Optional
from PySide6.QtCore import QUrl, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings

from rubik_solver.cube.cube_state import CubeState


class Cube3DWidget(QWidget):
    def __init__(self, cube: Optional[CubeState] = None, parent=None):
        super().__init__(parent)
        self.cube: CubeState = cube or CubeState()
        self._is_page_loaded = False
        self._pending_color_str: Optional[str] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # WebEngineView chạy Three.js
        self.web_view = QWebEngineView(self)
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
        )
        layout.addWidget(self.web_view)

        # Đường dẫn tuyệt đối tới file HTML
        asset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        html_file = os.path.join(asset_dir, "rubik_3d.html")

        self.web_view.loadFinished.connect(self._on_load_finished)
        self.web_view.setUrl(QUrl.fromLocalFile(html_file))

    @Slot(bool)
    def _on_load_finished(self, ok: bool) -> None:
        self._is_page_loaded = ok
        if ok:
            # Đồng bộ trạng thái màu ban đầu
            target_str = self._pending_color_str or self.cube.to_color_string()
            self._execute_js(f"window.setCubeState('{target_str}');")
            self._pending_color_str = None

    def set_cube_state(self, cube: CubeState) -> None:
        """Cập nhật trạng thái màu 54 ô lên mô hình 3D."""
        self.cube = cube.clone()
        color_str = self.cube.to_color_string()

        if self._is_page_loaded:
            self._execute_js(f"window.setCubeState('{color_str}');")
        else:
            self._pending_color_str = color_str

    def animate_move(self, move: str, duration_ms: int = 400, target_cube: Optional[CubeState] = None) -> None:
        """Diễn hoạt xoay 1 mặt trong không gian 3D mượt mà."""
        if target_cube:
            self.cube = target_cube.clone()
            target_str = self.cube.to_color_string()
        else:
            self.cube.rotate_face(move)
            target_str = self.cube.to_color_string()

        if self._is_page_loaded:
            self._execute_js(f"window.animateMove('{move}', {duration_ms}, '{target_str}');")
        else:
            self._pending_color_str = target_str

    def reset_camera(self) -> None:
        """Đưa góc nhìn 3D về vị trí mặc định."""
        if self._is_page_loaded:
            self._execute_js("resetCameraView();")

    def _execute_js(self, script: str) -> None:
        if self.web_view and self.web_view.page():
            self.web_view.page().runJavaScript(script)

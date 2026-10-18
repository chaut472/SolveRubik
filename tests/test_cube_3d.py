"""
Kiểm thử khởi tạo và giao tiếp với widget mô hình 3D (Cube3DWidget).
"""

import os
import sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from rubik_solver.cube.cube_state import CubeState
from rubik_solver.visualization.cube_3d_widget import Cube3DWidget


def test_cube_3d_widget_init():
    app = QApplication.instance() or QApplication(sys.argv)
    cube = CubeState()
    widget = Cube3DWidget(cube)
    assert widget is not None
    assert widget.web_view is not None

    # Kiểm tra gọi các API đồng bộ trạng thái không gây ngoại lệ
    widget.set_cube_state(cube)
    widget.animate_move("R", duration_ms=200)
    widget.reset_camera()

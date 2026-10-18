"""
Kiểm thử khởi tạo và giao tiếp với widget mô hình 3D (Cube3DWidget).
"""

import os
import sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from rubik_solver.cube.cube_state import CubeState
from rubik_solver.visualization.cube_3d_widget import Cube3DWidget
from rubik_solver.visualization.step_guide import StepGuideController


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


def test_step_guide_signals_sync():
    controller = StepGuideController()
    cube = CubeState()
    cube.rotate_face("R")
    moves = ["R'", "U", "U'"]

    state_reset_called = []
    move_executed_called = []

    controller.state_reset.connect(lambda c: state_reset_called.append(c.to_color_string()))
    controller.move_executed.connect(lambda m, c: move_executed_called.append((m, c.to_color_string())))

    controller.load_solution(cube, moves)
    assert len(state_reset_called) == 1
    assert state_reset_called[0] == cube.to_color_string()

    # Bước 1: R'
    ok = controller.next_step()
    assert ok is True
    assert len(move_executed_called) == 1
    move_name, res_cube_str = move_executed_called[0]
    assert move_name == "R'"
    # Sau R', khối Rubik phải trở về trạng thái đã giải!
    solved_cube = CubeState()
    assert res_cube_str == solved_cube.to_color_string()

    # Bước lùi: Undo R' -> thực hiện R
    ok_prev = controller.prev_step()
    assert ok_prev is True
    assert len(move_executed_called) == 2
    undo_move, prev_cube_str = move_executed_called[1]
    assert undo_move == "R"
    assert prev_cube_str == cube.to_color_string()

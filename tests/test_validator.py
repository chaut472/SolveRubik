"""
Kiểm thử bộ kiểm tra tính hợp lệ của khối Rubik (Validator).
"""

from rubik_solver.cube.constants import Face, CubeColor
from rubik_solver.cube.cube_state import CubeState
from rubik_solver.cube.validator import validate_cube_state


def test_validator_solved_cube():
    cube = CubeState()
    res = validate_cube_state(cube)
    assert res.is_valid is True


def test_validator_unknown_sticker():
    cube = CubeState()
    cube.set_sticker(Face.F, 0, CubeColor.UNKNOWN)
    res = validate_cube_state(cube)
    assert res.is_valid is False
    assert "chưa xác định" in res.message


def test_validator_duplicate_center():
    cube = CubeState()
    # Biến tâm mặt F thành màu Đỏ (trùng với tâm mặt R)
    cube.set_sticker(Face.F, 4, CubeColor.RED)
    res = validate_cube_state(cube)
    assert res.is_valid is False
    assert "Lỗi tâm Rubik" in res.message


def test_validator_color_counts_imbalance():
    cube = CubeState()
    # Thay 1 ô trắng thành vàng (trắng còn 8, vàng thành 10)
    cube.set_sticker(Face.U, 0, CubeColor.YELLOW)
    res = validate_cube_state(cube)
    assert res.is_valid is False
    assert "Số lượng màu không hợp lệ" in res.message

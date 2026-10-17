"""
Kiểm thử mô hình khối Rubik 3x3 và các phép xoay mặt.
"""

import pytest
from rubik_solver.cube.constants import Face, CubeColor
from rubik_solver.cube.cube_state import CubeState


def test_cube_initial_solved():
    cube = CubeState()
    assert cube.is_solved() is True
    assert cube.get_center_color(Face.U) == CubeColor.WHITE
    assert cube.get_center_color(Face.D) == CubeColor.YELLOW
    assert cube.get_center_color(Face.F) == CubeColor.GREEN
    assert cube.get_center_color(Face.B) == CubeColor.BLUE
    assert cube.get_center_color(Face.R) == CubeColor.RED
    assert cube.get_center_color(Face.L) == CubeColor.ORANGE


def test_cube_single_rotation():
    cube = CubeState()
    cube.rotate_face("R")
    assert cube.is_solved() is False
    # R3 more times should restore solved state (R^4 = I)
    cube.rotate_face("R")
    cube.rotate_face("R")
    cube.rotate_face("R")
    assert cube.is_solved() is True


def test_cube_inverse_rotation():
    cube = CubeState()
    cube.rotate_face("U")
    assert cube.is_solved() is False
    cube.rotate_face("U'")
    assert cube.is_solved() is True

    cube.rotate_face("F2")
    assert cube.is_solved() is False
    cube.rotate_face("F2")
    assert cube.is_solved() is True


def test_cube_sexi_move_cycle():
    """Thuật toán (R U R' U') lặp lại 6 lần đưa Rubik về trạng thái ban đầu."""
    cube = CubeState()
    for _ in range(6):
        cube.apply_moves("R U R' U'")
    assert cube.is_solved() is True


def test_kociemba_string_conversion():
    cube = CubeState()
    k_str = cube.to_kociemba_string()
    assert len(k_str) == 54
    assert k_str == "U" * 9 + "R" * 9 + "F" * 9 + "D" * 9 + "L" * 9 + "B" * 9

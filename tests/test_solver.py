"""
Kiểm thử bộ giải Kociemba Two-Phase Solver.
"""

from rubik_solver.cube.cube_state import CubeState
from rubik_solver.solver.kociemba_solver import solve_cube, solve_cubestring


def test_solve_already_solved():
    cube = CubeState()
    success, moves, msg = solve_cube(cube)
    assert success is True
    assert len(moves) == 0


def test_solve_scrambled_and_verify():
    cube = CubeState()
    scramble = "R U R' U' F2 D L2 B2"
    cube.apply_moves(scramble)
    assert cube.is_solved() is False

    success, moves, msg = solve_cube(cube)
    assert success is True
    assert len(moves) > 0

    # Áp dụng lời giải vào khối Rubik đã xáo trộn
    cube.apply_moves(moves)
    assert cube.is_solved() is True


def test_solve_complex_scramble():
    cube = CubeState()
    scramble = "R U R' U' F2 D L2 B2 U2 F' L' D2 R B' U"
    cube.apply_moves(scramble)
    assert cube.is_solved() is False

    success, moves, msg = solve_cube(cube)
    assert success is True
    assert len(moves) > 0

    # Xác minh sau khi quay chuỗi giải thì Rubik về đúng trạng thái hoàn thành
    cube.apply_moves(moves)
    assert cube.is_solved() is True


def test_solve_flipped_edge_error():
    """Lật 1 viên cạnh tại chỗ tạo ra Flip Error (không thể giải)."""
    # Lấy chuỗi khối đã giải và tráo đổi 2 mặt của viên cạnh UF:
    # Mặt U ô số 7 (UF) và Mặt F ô số 1 (FU)
    # Trong chuỗi: U là 0..8 (U[7] là index 7), F là 18..26 (F[1] là index 19)
    base = list("UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB")
    base[7], base[19] = base[19], base[7]
    invalid_str = "".join(base)
    success, moves, msg = solve_cubestring(invalid_str)
    assert success is False
    assert "Flip Error" in msg or "lật" in msg

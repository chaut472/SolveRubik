"""
Bộ giải Kociemba Two-Phase (Kociemba Solver Wrapper).
Chuyển đổi trạng thái CubeState, thực thi thuật toán tìm kiếm hai giai đoạn
và xử lý các ngoại lệ toán học của khối Rubik.
"""

from typing import List, Tuple
from rubik_solver.cube.cube_state import CubeState
from rubik_solver.cube.validator import validate_cube_state
from rubik_solver.solver.move_formatter import parse_move_string
from rubik_solver.solver.pykociemba import search

KOCIEMBA_ERROR_MESSAGES_VI = {
    "Error 1": "Không có đúng 9 ô của mỗi màu.",
    "Error 2": "Lỗi cấu trúc cạnh: Không tìm đủ 12 viên cạnh duy nhất.",
    "Error 3": "Lỗi lật cạnh (Flip Error): Có 1 viên cạnh bị lật ngược. (Khối Rubik bị tháo lắp sai cơ học hoặc quét sai màu).",
    "Error 4": "Lỗi cấu trúc góc: Không tìm đủ 8 viên góc duy nhất.",
    "Error 5": "Lỗi bẻ góc (Twist Error): Có 1 viên góc bị xoay tại chỗ. (Khối Rubik đã bị vặn/bẻ góc hoặc quét sai màu).",
    "Error 6": "Lỗi chẵn lẻ (Parity Error): Cần tráo đổi 2 góc hoặc 2 cạnh. (Khối Rubik không thể giải ở trạng thái vật lý này).",
    "Error 7": "Không tìm thấy lời giải trong số bước cho phép.",
    "Error 8": "Quá thời gian tìm kiếm lời giải (Timeout).",
}


def solve_cubestring(cubestring: str, max_depth: int = 24, timeout_ms: int = 2000) -> Tuple[bool, List[str], str]:
    """
    Giải Rubik từ chuỗi 54 ký tự URFDLB bằng thuật toán Kociemba.
    
    Returns:
        (thành công, danh sách nước đi, thông báo kết quả/lỗi)
    """
    cubestring = cubestring.strip()
    if len(cubestring) != 54:
        return False, [], f"Độ dài chuỗi Rubik không hợp lệ ({len(cubestring)}/54 ký tự)."

    # Nếu Rubik đã giải xong (UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB)
    solved_str = "U" * 9 + "R" * 9 + "F" * 9 + "D" * 9 + "L" * 9 + "B" * 9
    if cubestring == solved_str:
        return True, [], "Khối Rubik đã ở trạng thái hoàn thành (0 bước xoay)!"

    try:
        raw_solution = search.Search().solution(cubestring, max_depth, timeout_ms, False).strip()
    except Exception as e:
        return False, [], f"Lỗi không xác định khi giải: {str(e)}"

    for err_code, err_vi in KOCIEMBA_ERROR_MESSAGES_VI.items():
        if raw_solution.startswith(err_code):
            return False, [], err_vi

    moves = parse_move_string(raw_solution)
    return True, moves, f"Tìm thấy lời giải thành công ({len(moves)} bước)!"


def solve_cube(cube: CubeState, max_depth: int = 24, timeout_ms: int = 2000) -> Tuple[bool, List[str], str]:
    """
    Kiểm tra trạng thái khối Rubik và tìm lời giải tối ưu.
    
    Returns:
        (thành công, danh sách nước đi, thông báo kết quả/lỗi)
    """
    # 1. Kiểm tra sơ bộ tính hợp lệ
    val_res = validate_cube_state(cube)
    if not val_res.is_valid:
        return False, [], val_res.message

    # 2. Kiểm tra nếu đã hoàn thành
    if cube.is_solved():
        return True, [], "Khối Rubik đã ở trạng thái hoàn thành!"

    # 3. Chuyển đổi sang định dạng Kociemba 54 ký tự
    try:
        k_str = cube.to_kociemba_string()
    except Exception as e:
        return False, [], f"Không thể chuẩn hóa Rubik sang chuỗi Kociemba: {str(e)}"

    # 4. Tìm kiếm lời giải
    return solve_cubestring(k_str, max_depth=max_depth, timeout_ms=timeout_ms)

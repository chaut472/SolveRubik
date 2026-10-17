"""
Mô hình hóa trạng thái khối Rubik 3x3 (CubeState).
Quản lý 54 ô (stickers), các phép xoay mặt và chuyển đổi định dạng.
"""

from __future__ import annotations
import copy
from typing import Dict, List, Optional, Tuple

from rubik_solver.cube.constants import (
    Face,
    FACES_ORDER,
    CubeColor,
    COLOR_TO_CHAR,
    CHAR_TO_COLOR,
    STANDARD_CENTER_COLORS,
)


class CubeState:
    """
    Biểu diễn trạng thái của khối Rubik 3x3 với 6 mặt.
    Mỗi mặt gồm danh sách 9 ô màu (index 0 đến 8 theo thứ tự hàng ngang từ trái sang phải, trên xuống dưới).
    Ô số 4 luôn là ô tâm của mặt.
    """

    def __init__(self, faces: Optional[Dict[Face, List[CubeColor]]] = None):
        if faces is not None:
            self._faces: Dict[Face, List[CubeColor]] = {
                face: list(faces[face]) for face in FACES_ORDER
            }
        else:
            self.reset_to_solved()

    def reset_to_solved(self) -> None:
        """Khởi tạo Rubik về trạng thái chuẩn hoàn chỉnh (đã giải)."""
        self._faces = {
            face: [STANDARD_CENTER_COLORS[face]] * 9 for face in FACES_ORDER
        }

    def get_face(self, face: Face) -> List[CubeColor]:
        """Lấy danh sách 9 màu của mặt."""
        return list(self._faces[face])

    def set_face(self, face: Face, colors: List[CubeColor]) -> None:
        """Gán toàn bộ 9 màu cho một mặt."""
        if len(colors) != 9:
            raise ValueError(f"Mỗi mặt phải có đúng 9 ô màu, nhận được {len(colors)}")
        self._faces[face] = list(colors)

    def set_sticker(self, face: Face, index: int, color: CubeColor) -> None:
        """Cập nhật màu của 1 ô cụ thể trên mặt."""
        if not (0 <= index < 9):
            raise IndexError(f"Chỉ số ô phải từ 0 đến 8, nhận được {index}")
        self._faces[face][index] = color

    def get_sticker(self, face: Face, index: int) -> CubeColor:
        """Lấy màu của 1 ô cụ thể trên mặt."""
        return self._faces[face][index]

    def get_center_color(self, face: Face) -> CubeColor:
        """Lấy màu ô tâm (vị trí 4) của mặt."""
        return self._faces[face][4]

    def to_color_string(self) -> str:
        """
        Xuất chuỗi 54 ký tự màu theo thứ tự chuẩn U, R, F, D, L, B.
        Ví dụ: WWWWWWWWWRRRRRRRRRGGGGGGGGGYYYYYYYYYOOOOOOOOOBBBBBBBBB
        """
        res = []
        for face in FACES_ORDER:
            for color in self._faces[face]:
                res.append(COLOR_TO_CHAR.get(color, "?"))
        return "".join(res)

    def from_color_string(self, s: str) -> None:
        """Nạp trạng thái Rubik từ chuỗi 54 ký tự màu."""
        s = s.strip().upper()
        if len(s) != 54:
            raise ValueError(f"Chuỗi màu Rubik phải có độ dài 54, nhận được {len(s)}")
        for f_idx, face in enumerate(FACES_ORDER):
            chunk = s[f_idx * 9 : (f_idx + 1) * 9]
            self._faces[face] = [CHAR_TO_COLOR.get(c, CubeColor.UNKNOWN) for c in chunk]

    def to_kociemba_string(self) -> str:
        """
        Chuyển đổi trạng thái sang chuỗi 54 ký tự chuẩn Kociemba (U, R, F, D, L, B).
        Kociemba yêu cầu mỗi ký tự biểu thị mặt đích của ô đó, xác định thông qua ô tâm.
        """
        center_map: Dict[CubeColor, str] = {}
        for face in FACES_ORDER:
            c = self.get_center_color(face)
            center_map[c] = face.value

        k_chars = []
        for face in FACES_ORDER:
            for color in self._faces[face]:
                if color not in center_map:
                    raise ValueError(
                        f"Màu {color.value} không khớp với bất kỳ tâm nào trong 6 mặt!"
                    )
                k_chars.append(center_map[color])
        return "".join(k_chars)

    def is_solved(self) -> bool:
        """Kiểm tra khối Rubik đã ở trạng thái hoàn thành hay chưa."""
        for face in FACES_ORDER:
            center = self.get_center_color(face)
            if any(c != center for c in self._faces[face]):
                return False
        return True

    def clone(self) -> CubeState:
        """Tạo bản sao độc lập của trạng thái Rubik hiện tại."""
        return CubeState(self._faces)

    # ================== MÔ PHỎNG XOAY KHỐI RUBIK ==================

    @staticmethod
    def _rotate_matrix_cw(stickers: List[CubeColor]) -> List[CubeColor]:
        """Xoay ma trận 3x3 của một mặt 90 độ theo chiều kim đồng hồ."""
        # 0 1 2       6 3 0
        # 3 4 5  -->  7 4 1
        # 6 7 8       8 5 2
        return [
            stickers[6], stickers[3], stickers[0],
            stickers[7], stickers[4], stickers[1],
            stickers[8], stickers[5], stickers[2],
        ]

    @staticmethod
    def _rotate_matrix_ccw(stickers: List[CubeColor]) -> List[CubeColor]:
        """Xoay ma trận 3x3 của một mặt 90 độ ngược chiều kim đồng hồ."""
        return [
            stickers[2], stickers[5], stickers[8],
            stickers[1], stickers[4], stickers[7],
            stickers[0], stickers[3], stickers[6],
        ]

    @staticmethod
    def _rotate_matrix_180(stickers: List[CubeColor]) -> List[CubeColor]:
        """Xoay ma trận 3x3 180 độ."""
        return stickers[::-1]

    def rotate_face(self, move: str) -> None:
        """
        Thực hiện một nước đi chuẩn (ví dụ: 'R', 'R\'', 'R2', 'U', 'U\'', 'U2', ...).
        Cập nhật cả mặt được xoay và các mép kề trên 4 mặt lân cận.
        """
        move = move.strip()
        if not move:
            return

        base_face = move[0].upper()
        modifier = move[1:] if len(move) > 1 else ""

        if base_face not in ("U", "R", "F", "D", "L", "B"):
            raise ValueError(f"Nước đi không hợp lệ: {move}")

        times = 1
        if modifier == "'":
            times = 3
        elif modifier == "2":
            times = 2
        elif modifier != "":
            raise ValueError(f"Ký hiệu biến thể không hợp lệ: {move}")

        for _ in range(times):
            self._rotate_single_cw(Face(base_face))

    def _rotate_single_cw(self, face: Face) -> None:
        """Xoay 90 độ cùng chiều kim đồng hồ cho 1 mặt cơ sở."""
        # 1. Xoay 9 ô trên chính mặt đó
        self._faces[face] = self._rotate_matrix_cw(self._faces[face])

        # 2. Xoay 3 ô kề trên 4 mặt lân cận
        f = self._faces
        if face == Face.U:
            # Ảnh hưởng: B(0,1,2) -> R(0,1,2) -> F(0,1,2) -> L(0,1,2) -> B(0,1,2)
            tmp = [f[Face.B][0], f[Face.B][1], f[Face.B][2]]
            f[Face.B][0], f[Face.B][1], f[Face.B][2] = f[Face.L][0], f[Face.L][1], f[Face.L][2]
            f[Face.L][0], f[Face.L][1], f[Face.L][2] = f[Face.F][0], f[Face.F][1], f[Face.F][2]
            f[Face.F][0], f[Face.F][1], f[Face.F][2] = f[Face.R][0], f[Face.R][1], f[Face.R][2]
            f[Face.R][0], f[Face.R][1], f[Face.R][2] = tmp

        elif face == Face.D:
            # Ảnh hưởng: F(6,7,8) -> R(6,7,8) -> B(6,7,8) -> L(6,7,8) -> F(6,7,8)
            tmp = [f[Face.F][6], f[Face.F][7], f[Face.F][8]]
            f[Face.F][6], f[Face.F][7], f[Face.F][8] = f[Face.L][6], f[Face.L][7], f[Face.L][8]
            f[Face.L][6], f[Face.L][7], f[Face.L][8] = f[Face.B][6], f[Face.B][7], f[Face.B][8]
            f[Face.B][6], f[Face.B][7], f[Face.B][8] = f[Face.R][6], f[Face.R][7], f[Face.R][8]
            f[Face.R][6], f[Face.R][7], f[Face.R][8] = tmp

        elif face == Face.R:
            # Ảnh hưởng: U(2,5,8) -> B(6,3,0) -> D(2,5,8) -> F(2,5,8) -> U(2,5,8)
            tmp = [f[Face.U][2], f[Face.U][5], f[Face.U][8]]
            f[Face.U][2], f[Face.U][5], f[Face.U][8] = f[Face.F][2], f[Face.F][5], f[Face.F][8]
            f[Face.F][2], f[Face.F][5], f[Face.F][8] = f[Face.D][2], f[Face.D][5], f[Face.D][8]
            f[Face.D][2], f[Face.D][5], f[Face.D][8] = f[Face.B][6], f[Face.B][3], f[Face.B][0]
            f[Face.B][6], f[Face.B][3], f[Face.B][0] = tmp

        elif face == Face.L:
            # Ảnh hưởng: U(0,3,6) -> F(0,3,6) -> D(0,3,6) -> B(8,5,2) -> U(0,3,6)
            tmp = [f[Face.U][0], f[Face.U][3], f[Face.U][6]]
            f[Face.U][0], f[Face.U][3], f[Face.U][6] = f[Face.B][8], f[Face.B][5], f[Face.B][2]
            f[Face.B][8], f[Face.B][5], f[Face.B][2] = f[Face.D][0], f[Face.D][3], f[Face.D][6]
            f[Face.D][0], f[Face.D][3], f[Face.D][6] = f[Face.F][0], f[Face.F][3], f[Face.F][6]
            f[Face.F][0], f[Face.F][3], f[Face.F][6] = tmp

        elif face == Face.F:
            # Ảnh hưởng: U(6,7,8) -> R(0,3,6) -> D(2,1,0) -> L(8,5,2) -> U(6,7,8)
            tmp = [f[Face.U][6], f[Face.U][7], f[Face.U][8]]
            f[Face.U][6], f[Face.U][7], f[Face.U][8] = f[Face.L][8], f[Face.L][5], f[Face.L][2]
            f[Face.L][8], f[Face.L][5], f[Face.L][2] = f[Face.D][2], f[Face.D][1], f[Face.D][0]
            f[Face.D][2], f[Face.D][1], f[Face.D][0] = f[Face.R][0], f[Face.R][3], f[Face.R][6]
            f[Face.R][0], f[Face.R][3], f[Face.R][6] = tmp

        elif face == Face.B:
            # Ảnh hưởng: U(2,1,0) -> L(0,3,6) -> D(6,7,8) -> R(8,5,2) -> U(2,1,0)
            tmp = [f[Face.U][2], f[Face.U][1], f[Face.U][0]]
            f[Face.U][2], f[Face.U][1], f[Face.U][0] = f[Face.R][8], f[Face.R][5], f[Face.R][2]
            f[Face.R][8], f[Face.R][5], f[Face.R][2] = f[Face.D][6], f[Face.D][7], f[Face.D][8]
            f[Face.D][6], f[Face.D][7], f[Face.D][8] = f[Face.L][0], f[Face.L][3], f[Face.L][6]
            f[Face.L][0], f[Face.L][3], f[Face.L][6] = tmp

    def apply_moves(self, moves: List[str] | str) -> None:
        """Thực hiện một chuỗi các nước đi (cách nhau bởi khoảng trắng hoặc list)."""
        if isinstance(moves, str):
            move_list = moves.strip().split()
        else:
            move_list = moves
        for m in move_list:
            self.rotate_face(m)

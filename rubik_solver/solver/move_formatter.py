"""
Định dạng, diễn giải và xử lý các chuỗi nước đi chuẩn (Move Formatter).
Cung cấp giải thích chi tiết bằng tiếng Việt cho từng bước xoay.
"""

from typing import Dict, List, Optional
from rubik_solver.cube.constants import Face, FACE_NAMES_VI, CubeColor, COLOR_NAMES_VI
from rubik_solver.cube.cube_state import CubeState

MOVE_DESCRIPTIONS_VI: Dict[str, str] = {
    "U": "Xoay MẶT TRÊN 90° cùng chiều kim đồng hồ",
    "U'": "Xoay MẶT TRÊN 90° ngược chiều kim đồng hồ",
    "U2": "Xoay MẶT TRÊN 180°",
    "D": "Xoay MẶT DƯỚI 90° cùng chiều kim đồng hồ",
    "D'": "Xoay MẶT DƯỚI 90° ngược chiều kim đồng hồ",
    "D2": "Xoay MẶT DƯỚI 180°",
    "R": "Xoay MẶT PHẢI 90° cùng chiều kim đồng hồ",
    "R'": "Xoay MẶT PHẢI 90° ngược chiều kim đồng hồ",
    "R2": "Xoay MẶT PHẢI 180°",
    "L": "Xoay MẶT TRÁI 90° cùng chiều kim đồng hồ",
    "L'": "Xoay MẶT TRÁI 90° ngược chiều kim đồng hồ",
    "L2": "Xoay MẶT TRÁI 180°",
    "F": "Xoay MẶT TRƯỚC 90° cùng chiều kim đồng hồ",
    "F'": "Xoay MẶT TRƯỚC 90° ngược chiều kim đồng hồ",
    "F2": "Xoay MẶT TRƯỚC 180°",
    "B": "Xoay MẶT SAU 90° cùng chiều kim đồng hồ",
    "B'": "Xoay MẶT SAU 90° ngược chiều kim đồng hồ",
    "B2": "Xoay MẶT SAU 180°",
}


class StepInfo:
    """Thông tin chi tiết của 1 bước giải."""

    def __init__(
        self,
        step_number: int,
        total_steps: int,
        move: str,
        face: Face,
        description: str,
        center_color: Optional[CubeColor] = None,
    ):
        self.step_number = step_number
        self.total_steps = total_steps
        self.move = move
        self.face = face
        self.description = description
        self.center_color = center_color

    def get_full_text(self) -> str:
        color_hint = ""
        if self.center_color:
            c_name = COLOR_NAMES_VI.get(self.center_color, "")
            color_hint = f" (Màu {c_name})"
        return f"Bước {self.step_number}/{self.total_steps}: {self.move} - {self.description}{color_hint}"


def parse_move_string(moves_str: str) -> List[str]:
    """Tách chuỗi nước đi thành danh sách các ký hiệu chuẩn."""
    if not moves_str:
        return []
    return [m.strip() for m in moves_str.strip().split() if m.strip()]


def invert_move(move: str) -> str:
    """Trả về nước đi đảo ngược (undo)."""
    move = move.strip()
    if not move:
        return ""
    base = move[0]
    mod = move[1:] if len(move) > 1 else ""
    if mod == "":
        return base + "'"
    elif mod == "'":
        return base
    elif mod == "2":
        return base + "2"
    return move


def get_step_info_list(moves: List[str], cube: Optional[CubeState] = None) -> List[StepInfo]:
    """Tạo danh sách StepInfo hoàn chỉnh cho toàn bộ lời giải."""
    total = len(moves)
    steps = []
    for i, m in enumerate(moves, start=1):
        base_face_char = m[0].upper()
        face = Face(base_face_char)
        desc = MOVE_DESCRIPTIONS_VI.get(m, f"Xoay {m}")
        center_color = cube.get_center_color(face) if cube else None
        steps.append(
            StepInfo(
                step_number=i,
                total_steps=total,
                move=m,
                face=face,
                description=desc,
                center_color=center_color,
            )
        )
    return steps

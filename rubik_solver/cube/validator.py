"""
Bộ kiểm tra tính hợp lệ của trạng thái Rubik 3x3 (Validator).
Phát hiện sớm các lỗi nhập sai, quét thiếu, trùng tâm hoặc mất cân bằng màu sắc.
"""

from typing import Dict, Optional, Tuple
from collections import Counter

from rubik_solver.cube.constants import (
    Face,
    FACES_ORDER,
    CubeColor,
    COLOR_NAMES_VI,
    FACE_NAMES_VI,
)
from rubik_solver.cube.cube_state import CubeState


class ValidationResult:
    def __init__(self, is_valid: bool, message: str = "", details: Optional[Dict] = None):
        self.is_valid = is_valid
        self.message = message
        self.details = details or {}

    def __bool__(self) -> bool:
        return self.is_valid


def validate_cube_state(cube: CubeState) -> ValidationResult:
    """
    Kiểm tra toàn diện tính hợp lệ của khối Rubik trước khi chuyển cho thuật toán giải.
    
    Các bước kiểm tra:
    1. Kiểm tra có ô chưa nhận diện (UNKNOWN).
    2. Kiểm tra tính duy nhất của 6 ô tâm (không được trùng màu tâm giữa các mặt).
    3. Kiểm tra số lượng sticker của từng màu (mỗi màu phải có đúng 9 ô).
    """
    # 1. Kiểm tra ô UNKNOWN
    unknown_locations = []
    for face in FACES_ORDER:
        for idx in range(9):
            if cube.get_sticker(face, idx) == CubeColor.UNKNOWN:
                unknown_locations.append((face, idx))

    if unknown_locations:
        first_face, first_idx = unknown_locations[0]
        return ValidationResult(
            is_valid=False,
            message=(
                f"Có {len(unknown_locations)} ô chưa xác định được màu. "
                f"Ví dụ: {FACE_NAMES_VI[first_face]}, ô số {first_idx + 1}. "
                "Vui lòng quét lại hoặc chỉnh sửa thủ công."
            ),
            details={"unknown_count": len(unknown_locations), "locations": unknown_locations},
        )

    # 2. Kiểm tra 6 ô tâm
    centers: Dict[Face, CubeColor] = {face: cube.get_center_color(face) for face in FACES_ORDER}
    center_colors = list(centers.values())
    if len(set(center_colors)) != 6:
        # Tìm màu tâm bị trùng
        counts = Counter(center_colors)
        dup_colors = [c for c, count in counts.items() if count > 1]
        dup_names = [COLOR_NAMES_VI.get(c, c.value) for c in dup_colors]
        return ValidationResult(
            is_valid=False,
            message=(
                f"Lỗi tâm Rubik: Trùng màu tâm ({', '.join(dup_names)}). "
                "6 mặt Rubik bắt buộc phải có 6 màu tâm khác nhau. Vui lòng quét lại các mặt bị trùng."
            ),
            details={"centers": centers, "duplicate_colors": dup_colors},
        )

    # 3. Kiểm tra số lượng mỗi màu (mỗi màu đúng 9 ô)
    color_counts: Dict[CubeColor, int] = {c: 0 for c in CubeColor if c != CubeColor.UNKNOWN}
    for face in FACES_ORDER:
        for idx in range(9):
            c = cube.get_sticker(face, idx)
            if c in color_counts:
                color_counts[c] += 1

    errors = []
    for c, count in color_counts.items():
        if count != 9:
            c_name = COLOR_NAMES_VI.get(c, c.value)
            errors.append(f"Màu {c_name}: {count} ô (cần đúng 9)")

    if errors:
        return ValidationResult(
            is_valid=False,
            message="Số lượng màu không hợp lệ:\n" + "\n".join(errors),
            details={"counts": color_counts},
        )

    return ValidationResult(is_valid=True, message="Trạng thái Rubik hợp lệ và sẵn sàng giải.")

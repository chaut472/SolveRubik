"""
Hằng số và quy ước chuẩn cho khối Rubik 3x3.
"""

from enum import Enum
from typing import Dict, List, Tuple


class Face(str, Enum):
    U = "U"  # Up (Trên)
    R = "R"  # Right (Phải)
    F = "F"  # Front (Trước)
    D = "D"  # Down (Dưới)
    L = "L"  # Left (Trái)
    B = "B"  # Back (Sau)


FACES_ORDER: List[Face] = [Face.U, Face.R, Face.F, Face.D, Face.L, Face.B]

FACE_NAMES_VI: Dict[Face, str] = {
    Face.U: "Mặt Trên (Up)",
    Face.R: "Mặt Phải (Right)",
    Face.F: "Mặt Trước (Front)",
    Face.D: "Mặt Dưới (Down)",
    Face.L: "Mặt Trái (Left)",
    Face.B: "Mặt Sau (Back)",
}


class CubeColor(str, Enum):
    WHITE = "white"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    RED = "red"
    ORANGE = "orange"
    UNKNOWN = "unknown"


# Mã màu viết tắt quy ước (W, Y, G, B, R, O)
COLOR_TO_CHAR: Dict[CubeColor, str] = {
    CubeColor.WHITE: "W",
    CubeColor.YELLOW: "Y",
    CubeColor.GREEN: "G",
    CubeColor.BLUE: "B",
    CubeColor.RED: "R",
    CubeColor.ORANGE: "O",
    CubeColor.UNKNOWN: "?",
}

CHAR_TO_COLOR: Dict[str, CubeColor] = {
    v: k for k, v in COLOR_TO_CHAR.items() if k != CubeColor.UNKNOWN
}

# Tên màu hiển thị tiếng Việt
COLOR_NAMES_VI: Dict[CubeColor, str] = {
    CubeColor.WHITE: "Trắng",
    CubeColor.YELLOW: "Vàng",
    CubeColor.GREEN: "Xanh lá",
    CubeColor.BLUE: "Xanh dương",
    CubeColor.RED: "Đỏ",
    CubeColor.ORANGE: "Cam",
    CubeColor.UNKNOWN: "Chưa xác định",
}

# Bảng mã màu Hex hiển thị trực quan (theo chuẩn phối màu Rubik quốc tế)
COLOR_HEX: Dict[CubeColor, str] = {
    CubeColor.WHITE: "#FFFFFF",
    CubeColor.YELLOW: "#FFD500",
    CubeColor.GREEN: "#009B48",
    CubeColor.BLUE: "#0046AD",
    CubeColor.RED: "#B71234",
    CubeColor.ORANGE: "#FF5800",
    CubeColor.UNKNOWN: "#3C3F41",
}

# Màu tâm chuẩn mặc định theo phối màu Western BOY (Blue-Orange-Yellow)
STANDARD_CENTER_COLORS: Dict[Face, CubeColor] = {
    Face.U: CubeColor.WHITE,
    Face.R: CubeColor.RED,
    Face.F: CubeColor.GREEN,
    Face.D: CubeColor.YELLOW,
    Face.L: CubeColor.ORANGE,
    Face.B: CubeColor.BLUE,
}

# Thứ tự hướng dẫn xoay mặt khi người dùng đưa Rubik vào camera:
# 1. Mặt U (Trắng ở trên, Xanh lá ở trước)
# 2. Xoay khối Rubik xuống để quét mặt R (Đỏ)
# 3. Tiếp tục xoay để quét F, D, L, B
SCAN_SEQUENCE: List[Tuple[Face, str]] = [
    (Face.U, "Đưa MẶT TRÊN (Trắng) vào camera, mặt Trước (Xanh lá) hướng xuống"),
    (Face.R, "Xoay mặt sang MẶT PHẢI (Đỏ) vào camera, mặt Trên (Trắng) giữ hướng trên"),
    (Face.F, "Xoay mặt sang MẶT TRƯỚC (Xanh lá) vào camera, mặt Trên (Trắng) giữ hướng trên"),
    (Face.D, "Xoay lật sang MẶT DƯỚI (Vàng) vào camera, mặt Trước (Xanh lá) hướng lên"),
    (Face.L, "Xoay sang MẶT TRÁI (Cam) vào camera, mặt Trên (Trắng) giữ hướng trên"),
    (Face.B, "Xoay sang MẶT SAU (Xanh dương) vào camera, mặt Trên (Trắng) giữ hướng trên"),
]

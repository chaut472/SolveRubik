"""
Điểm khởi chạy chính của Phần mềm Giải Rubik 3x3 Bằng Camera.
"""

import sys
import os

# Đảm bảo thư mục gốc dự án luôn nằm trong sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from rubik_solver.ui.main_window import MainWindow
from rubik_solver.ui.styles import APP_STYLESHEET


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("RubikSolverAI")
    app.setOrganizationName("DoAnCNTT")
    app.setStyleSheet(APP_STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

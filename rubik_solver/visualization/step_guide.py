"""
Bộ điều khiển trình phát bước giải (Step Guide Controller).
Hỗ trợ tiến, lùi, tạm dừng, tự động phát và cập nhật trạng thái mô hình Rubik sau mỗi nước đi.
"""

from typing import List, Optional
from PySide6.QtCore import QObject, Signal, QTimer

from rubik_solver.cube.cube_state import CubeState
from rubik_solver.solver.move_formatter import (
    StepInfo,
    get_step_info_list,
    invert_move,
)


class StepGuideController(QObject):
    # Tín hiệu phát đi khi bước thay đổi: (StepInfo hiện tại, bước hiện tại [1-based], tổng bước)
    step_changed = Signal(object, int, int)
    cube_state_changed = Signal(CubeState)
    playback_finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initial_cube: Optional[CubeState] = None
        self.current_cube: Optional[CubeState] = None
        self.moves: List[str] = []
        self.step_info_list: List[StepInfo] = []
        self.current_index: int = 0  # 0 đến len(moves)

        # Timer tự động phát
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_step)
        self.playback_interval_ms: int = 1000

    def load_solution(self, initial_cube: CubeState, moves: List[str]) -> None:
        """Nạp trạng thái ban đầu và chuỗi nước đi."""
        self.pause()
        self.initial_cube = initial_cube.clone()
        self.current_cube = initial_cube.clone()
        self.moves = list(moves)
        self.step_info_list = get_step_info_list(self.moves, self.initial_cube)
        self.current_index = 0

        self._emit_current_state()

    @property
    def total_steps(self) -> int:
        return len(self.moves)

    @property
    def is_playing(self) -> bool:
        return self.timer.isActive()

    def set_speed(self, interval_ms: int) -> None:
        """Điều chỉnh tốc độ tự động phát (ms)."""
        self.playback_interval_ms = interval_ms
        if self.is_playing:
            self.timer.setInterval(self.playback_interval_ms)

    def next_step(self) -> bool:
        """Thực hiện bước tiếp theo."""
        if self.current_index >= self.total_steps:
            self.pause()
            self.playback_finished.emit()
            return False

        move = self.moves[self.current_index]
        self.current_cube.rotate_face(move)
        self.current_index += 1

        self._emit_current_state()

        if self.current_index >= self.total_steps:
            self.pause()
            self.playback_finished.emit()
        return True

    def prev_step(self) -> bool:
        """Quay lại bước trước (áp dụng nước đi đảo)."""
        if self.current_index <= 0:
            return False

        self.current_index -= 1
        move = self.moves[self.current_index]
        inv = invert_move(move)
        self.current_cube.rotate_face(inv)

        self._emit_current_state()
        return True

    def reset(self) -> None:
        """Đưa khối Rubik về trạng thái ban đầu trước khi giải."""
        self.pause()
        if self.initial_cube:
            self.current_cube = self.initial_cube.clone()
        self.current_index = 0
        self._emit_current_state()

    def play(self) -> None:
        """Bắt đầu tự động phát."""
        if self.current_index >= self.total_steps:
            self.reset()
        self.timer.start(self.playback_interval_ms)

    def pause(self) -> None:
        """Tạm dừng tự động phát."""
        if self.timer.isActive():
            self.timer.stop()

    def toggle_play(self) -> None:
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def jump_to_step(self, target_step_index: int) -> None:
        """Nhảy trực tiếp đến bước chỉ định (0 đến total_steps)."""
        target_step_index = max(0, min(target_step_index, self.total_steps))
        self.reset()
        for _ in range(target_step_index):
            self.next_step()

    def _emit_current_state(self) -> None:
        step_info = None
        if 0 <= self.current_index < self.total_steps:
            step_info = self.step_info_list[self.current_index]

        self.step_changed.emit(step_info, self.current_index, self.total_steps)
        if self.current_cube:
            self.cube_state_changed.emit(self.current_cube.clone())

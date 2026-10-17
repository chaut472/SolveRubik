"""
Kiểm thử module nhận diện thị giác (Vision & Color Detection).
"""

import numpy as np
from rubik_solver.cube.constants import CubeColor
from rubik_solver.vision.color_detector import ColorDetector
from rubik_solver.vision.grid_detector import GridDetector


def test_color_detector_synthetic_colors():
    detector = ColorDetector()

    # BGR format
    white_patch = np.full((50, 50, 3), (250, 250, 250), dtype=np.uint8)
    yellow_patch = np.full((50, 50, 3), (20, 230, 250), dtype=np.uint8)
    green_patch = np.full((50, 50, 3), (20, 200, 20), dtype=np.uint8)
    blue_patch = np.full((50, 50, 3), (220, 80, 20), dtype=np.uint8)
    red_patch = np.full((50, 50, 3), (20, 20, 220), dtype=np.uint8)
    orange_patch = np.full((50, 50, 3), (20, 130, 250), dtype=np.uint8)

    assert detector.classify_patch(white_patch)[0] == CubeColor.WHITE
    assert detector.classify_patch(yellow_patch)[0] == CubeColor.YELLOW
    assert detector.classify_patch(green_patch)[0] == CubeColor.GREEN
    assert detector.classify_patch(blue_patch)[0] == CubeColor.BLUE
    assert detector.classify_patch(red_patch)[0] == CubeColor.RED
    assert detector.classify_patch(orange_patch)[0] == CubeColor.ORANGE


def test_grid_detector_boxes():
    grid = GridDetector()
    boxes = grid.get_grid_boxes(640, 480)
    assert len(boxes) == 9

    # Kiểm tra các ô không bị chồng lấn và có kích thước dương
    for x1, y1, x2, y2 in boxes:
        assert x2 > x1
        assert y2 > y1
        assert 0 <= x1 < 640
        assert 0 <= y1 < 480


def test_grid_detector_process_frame():
    grid = GridDetector()
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    detected_colors, confs, annotated = grid.process_frame(dummy_frame)

    assert len(detected_colors) == 9
    assert len(confs) == 9
    assert annotated.shape == dummy_frame.shape

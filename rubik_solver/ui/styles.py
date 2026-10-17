"""
Bảng định kiểu QSS giao diện hiện đại (Modern Dark Theme).
Được thiết kế chuyên nghiệp cho ứng dụng đồ án Công nghệ thông tin.
"""

APP_STYLESHEET = """
QMainWindow {
    background-color: #18191C;
    color: #F0F2F5;
    font-family: "Segoe UI", Arial, sans-serif;
}

QWidget {
    color: #E2E8F0;
    font-size: 13px;
}

/* Card Container */
QFrame.CardFrame {
    background-color: #23252B;
    border: 1px solid #32353E;
    border-radius: 10px;
    padding: 12px;
}

/* Tiêu đề nhóm */
QLabel.HeaderLabel {
    font-size: 15px;
    font-weight: bold;
    color: #60A5FA;
    padding-bottom: 6px;
    border-bottom: 1px solid #334155;
}

QLabel.BigMoveLabel {
    font-size: 38px;
    font-weight: 900;
    color: #38BDF8;
    background-color: #0F172A;
    border: 2px solid #0284C7;
    border-radius: 8px;
    padding: 8px 16px;
    qproperty-alignment: AlignCenter;
}

QLabel.StepDescLabel {
    font-size: 14px;
    color: #F8FAFC;
    padding: 6px;
    qproperty-alignment: AlignCenter;
}

/* Nút bấm tiêu chuẩn */
QPushButton {
    background-color: #334155;
    color: #FFFFFF;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 600;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #475569;
    border-color: #64748B;
}

QPushButton:pressed {
    background-color: #1E293B;
}

QPushButton:disabled {
    background-color: #1E222A;
    color: #64748B;
    border-color: #272C35;
}

/* Nút chính nổi bật (Primary Action) */
QPushButton.PrimaryButton {
    background-color: #2563EB;
    border: 1px solid #3B82F6;
    color: #FFFFFF;
    font-size: 14px;
    padding: 10px 18px;
}

QPushButton.PrimaryButton:hover {
    background-color: #1D4ED8;
}

QPushButton.SuccessButton {
    background-color: #16A34A;
    border: 1px solid #22C55E;
    color: #FFFFFF;
    font-size: 14px;
    font-weight: bold;
    padding: 10px 18px;
}

QPushButton.SuccessButton:hover {
    background-color: #15803D;
}

QPushButton.DangerButton {
    background-color: #DC2626;
    border: 1px solid #EF4444;
    color: #FFFFFF;
}

QPushButton.DangerButton:hover {
    background-color: #B91C1C;
}

/* Thanh tiến trình */
QProgressBar {
    border: 1px solid #334155;
    border-radius: 5px;
    background-color: #0F172A;
    text-align: center;
    color: #FFFFFF;
    font-weight: bold;
    height: 18px;
}

QProgressBar::chunk {
    background-color: #3B82F6;
    border-radius: 4px;
}

/* Danh sách bước đi */
QListWidget {
    background-color: #1E222A;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 4px;
    color: #E2E8F0;
}

QListWidget::item {
    padding: 6px 10px;
    border-radius: 4px;
    margin-bottom: 2px;
}

QListWidget::item:hover {
    background-color: #2E3440;
}

QListWidget::item:selected {
    background-color: #1D4ED8;
    color: #FFFFFF;
    font-weight: bold;
}

/* Hộp thoại thông báo & thanh cuộn */
QScrollBar:vertical {
    border: none;
    background-color: #18191C;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #475569;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #64748B;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #334155;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #38BDF8;
    border: 1px solid #0284C7;
    width: 14px;
    margin: -4px 0;
    border-radius: 7px;
}
"""

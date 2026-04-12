from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QStyle, QStyleOption
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter


class Header(QWidget):
    """
    Application header bar.
    Height: 64 px | Padding: 0 24 px
    Left: burger button 32x32 | Right: app title
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("header")
        self.setFixedHeight(64)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(0)

        # ── Burger button ──────────────────────────────────────
        self.burger_btn = QPushButton("☰")
        self.burger_btn.setObjectName("burgerButton")
        self.burger_btn.setFixedSize(32, 32)
        self.burger_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.burger_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.burger_btn)

        layout.addStretch()

        # ── App title ──────────────────────────────────────────
        self.title_label = QLabel("ИНДУСТРИАЛЬНЫЙ МАНИПУЛЯТОР")
        self.title_label.setObjectName("headerTitle")
        layout.addWidget(self.title_label)

    # QSS background-color requires paintEvent override on plain QWidget
    def paintEvent(self, event) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

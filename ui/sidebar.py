from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QStyle, QStyleOption
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter

_MENU_ITEMS = [
    "Главная",
    "Управление",
    "Мониторинг",
    "Настройки",
    "Журнал",
]


class Sidebar(QWidget):
    """
    Left navigation sidebar.
    Width: 240 px | Padding: 24 px | Item spacing: 16 px
    Item height: 40 px | Item padding: 0 12 px | border-radius: 8 px
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        for text in _MENU_ITEMS:
            btn = QPushButton(text)
            btn.setObjectName("sidebarItem")
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            layout.addWidget(btn)

    # QSS background-color requires paintEvent override on plain QWidget
    def paintEvent(self, event) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

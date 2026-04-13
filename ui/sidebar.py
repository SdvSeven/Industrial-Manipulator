from __future__ import annotations
import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QStyle, QStyleOption,
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QPainter

from components.sidebar_item import SidebarItem

# ── Media directory (resolved relative to this file) ──────────
_MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "media")

_MENU_ITEMS: list[tuple[str, str]] = [
    ("Главная",    os.path.join(_MEDIA, "main.png")),
    ("Управление", os.path.join(_MEDIA, "control.png")),
    ("Настройки",  os.path.join(_MEDIA, "settings.png")),
    ("Журнал",     os.path.join(_MEDIA, "logs.png")),
]


class Sidebar(QWidget):
    """
    Left navigation panel — always visible, never toggleable.

    Width    : 240 px
    Padding  : 24 px all sides
    Spacing  : 16 px between items
    Bottom   : semi-transparent info block (content TBD)

    Signals
    -------
    item_clicked(str): emitted with the menu item label on click.
    """

    item_clicked = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self._items: dict[str, SidebarItem] = {}

        for name, icon_path in _MENU_ITEMS:
            item = SidebarItem(name, icon_path, self)
            item.clicked.connect(self._on_item_clicked)
            self._items[name] = item
            layout.addWidget(item)

        # Default active item
        self._active: str = "Главная"
        self._items["Главная"].setChecked(True)

        # ── Bottom block ───────────────────────────────────────
        layout.addStretch(1)

        bottom = QFrame(self)
        bottom.setObjectName("sidebarBottomBlock")
        bottom.setMinimumHeight(88)
        layout.addWidget(bottom)

    # ── Public API ─────────────────────────────────────────────

    def set_active(self, name: str) -> None:
        if name in self._items:
            if self._active and self._active in self._items:
                self._items[self._active].setChecked(False)
            self._active = name
            self._items[name].setChecked(True)

    @property
    def items(self) -> dict[str, SidebarItem]:
        return self._items

    # ── Internal ───────────────────────────────────────────────

    def _on_item_clicked(self, name: str) -> None:
        self.set_active(name)
        self.item_clicked.emit(name)

    def paintEvent(self, event) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

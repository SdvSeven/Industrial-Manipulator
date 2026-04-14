from __future__ import annotations
import os

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStyle, QStyleOption
from PySide6.QtCore import Signal
from PySide6.QtGui import QPainter

from components.sidebar_item import SidebarItem
from components.sidebar_info import SidebarInfoBlock

_MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "media")

_MENU_ITEMS: list[tuple[str, str]] = [
    ("Главная",    os.path.join(_MEDIA, "main.png")),
    ("Управление", os.path.join(_MEDIA, "control.png")),
    ("Настройки",  os.path.join(_MEDIA, "settings.png")),
    ("Журнал",     os.path.join(_MEDIA, "logs.png")),
]

# Pages that require authentication (§3.2)
_AUTH_REQUIRED: frozenset[str] = frozenset({"Управление", "Настройки", "Журнал"})


class Sidebar(QWidget):
    """
    Left navigation panel — always visible.

    Signals
    -------
    item_clicked(str): menu item label on click.

    Public attributes
    -----------------
    info_block: SidebarInfoBlock — real-time state display
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
        self._active: str = "Главная"

        for name, icon_path in _MENU_ITEMS:
            item = SidebarItem(name, icon_path, self)
            item.clicked.connect(self._on_item_clicked)
            self._items[name] = item
            layout.addWidget(item)

        self._items["Главная"].setChecked(True)

        layout.addStretch(1)

        # ── SystemInfoBlock ────────────────────────────────────
        self.info_block = SidebarInfoBlock(self)
        layout.addWidget(self.info_block)

    # ── Public API ─────────────────────────────────────────────

    def set_active(self, name: str) -> None:
        if name not in self._items:
            return
        if self._active in self._items:
            self._items[self._active].setChecked(False)
        self._active = name
        self._items[name].setChecked(True)

    def set_auth_state(self, is_authenticated: bool) -> None:
        """Dim lock-required items when not authenticated."""
        for name in _AUTH_REQUIRED:
            item = self._items.get(name)
            if item:
                item.setProperty("locked", not is_authenticated)
                item.style().unpolish(item)
                item.style().polish(item)

    @property
    def items(self) -> dict[str, SidebarItem]:
        return self._items

    # ── Internal ───────────────────────────────────────────────

    def _on_item_clicked(self, name: str) -> None:
        self.item_clicked.emit(name)

    def paintEvent(self, event) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

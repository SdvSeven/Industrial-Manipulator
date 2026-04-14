from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QMenu, QPushButton,
    QStyle, QStyleOption, QWidget,
)


class Header(QWidget):
    """
    Application header bar.
    Height: 64 px | Padding: 0 24 px

    Layout:
        LEFT : app title
        RIGHT: [UserMenuButton]  OR  [login_btn]  [reg_btn]

    Signals
    -------
    logout_requested: emitted when user clicks «Выйти» in dropdown
    """

    logout_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("header")
        self.setFixedHeight(64)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(0)

        # ── Left: app title ────────────────────────────────────
        self.title_label = QLabel("ИНДУСТРИАЛЬНЫЙ МАНИПУЛЯТОР")
        self.title_label.setObjectName("headerTitle")
        layout.addWidget(self.title_label)
        layout.addStretch()

        # ── Right: authenticated state — dropdown button ───────
        self._user_menu_btn = QPushButton()
        self._user_menu_btn.setObjectName("userMenuBtn")
        self._user_menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._user_menu_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._user_menu_btn.hide()

        _menu = QMenu(self._user_menu_btn)
        _menu.setObjectName("userDropdownMenu")
        _logout_action = _menu.addAction("Выйти")
        _logout_action.triggered.connect(self.logout_requested)
        self._user_menu_btn.setMenu(_menu)
        layout.addWidget(self._user_menu_btn)
        layout.addSpacing(16)

        # ── Right: unauthenticated state — login / register ────
        self.login_btn = QPushButton("Вход")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.login_btn)
        layout.addSpacing(8)

        self.reg_btn = QPushButton("Регистрация")
        self.reg_btn.setObjectName("registerBtn")
        self.reg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reg_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.reg_btn)

    # ── Public API ─────────────────────────────────────────────

    def show_user(self, name: str) -> None:
        self._user_menu_btn.setText(f"{name}  ▼")
        self._user_menu_btn.show()
        self.login_btn.hide()
        self.reg_btn.hide()

    def show_auth_buttons(self) -> None:
        self._user_menu_btn.hide()
        self.login_btn.show()
        self.reg_btn.show()

    def paintEvent(self, event) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

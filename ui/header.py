from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QStyle, QStyleOption,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter


class Header(QWidget):
    """
    Application header bar.
    Height: 64 px | Padding: 0 24 px

    Layout:
        LEFT : app title (fixed position)
        RIGHT: [user_label]  OR  [login_btn]  [reg_btn]
    """

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

        # ── Right: auth area ───────────────────────────────────

        # Shown when authenticated
        self.user_label = QLabel()
        self.user_label.setObjectName("userLabel")
        self.user_label.hide()
        layout.addWidget(self.user_label)
        layout.addSpacing(16)

        # Shown when NOT authenticated
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
        self.user_label.setText(name)
        self.user_label.show()
        self.login_btn.hide()
        self.reg_btn.hide()

    def show_auth_buttons(self) -> None:
        self.user_label.hide()
        self.login_btn.show()
        self.reg_btn.show()

    def paintEvent(self, event) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

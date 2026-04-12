"""
Composite widgets.

Layout rules: only QVBoxLayout / QHBoxLayout. No .move(), no absolute coords.
"""

import os
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QVBoxLayout, QWidget,
)

from components import (
    BurgerButton, ConnectButton, GhostButton, GlassPanel, GlassSidebar,
    LogoBadge, MenuItemButton, PrimaryButton, UserChip,
)


# ─────────── Header ───────────

class Header(GlassPanel):
    """
    Fixed-height 72px glass bar.
    Layout: [burger] · stretch · [auth zone]
    Auth zone has two states:
      - guest  → [Войти] [Регистрация]
      - logged → [user chip] [Выйти]
    """
    menuToggled = Signal()
    loginRequested = Signal()
    registerRequested = Signal()
    logoutRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(72)

        root = QHBoxLayout(self)
        root.setContentsMargins(16, 0, 20, 0)
        root.setSpacing(12)

        # Left
        self.burger = BurgerButton()
        self.burger.clicked.connect(self.menuToggled)
        root.addWidget(self.burger, 0, Qt.AlignVCenter)

        root.addStretch(1)

        # Right — guest widgets
        self._login_btn = GhostButton("Войти")
        self._login_btn.clicked.connect(self.loginRequested)

        self._register_btn = PrimaryButton("Регистрация")
        self._register_btn.clicked.connect(self.registerRequested)

        # Right — logged widgets
        self._user_chip = UserChip("")
        self._user_chip.hide()

        self._logout_btn = GhostButton("Выйти")
        self._logout_btn.clicked.connect(self.logoutRequested)
        self._logout_btn.hide()

        root.addWidget(self._user_chip, 0, Qt.AlignVCenter)
        root.addWidget(self._login_btn, 0, Qt.AlignVCenter)
        root.addWidget(self._register_btn, 0, Qt.AlignVCenter)
        root.addWidget(self._logout_btn, 0, Qt.AlignVCenter)

    def set_user(self, full_name: str, authenticated: bool):
        if authenticated and full_name:
            # show first name only to keep header clean
            first = full_name.split()[0] if full_name.split() else full_name
            self._user_chip.setText(first)
            self._user_chip.show()
            self._logout_btn.show()
            self._login_btn.hide()
            self._register_btn.hide()
        else:
            self._user_chip.hide()
            self._logout_btn.hide()
            self._login_btn.show()
            self._register_btn.show()


# ─────────── Sidebar ───────────

class Sidebar(GlassSidebar):
    """Overlay sidebar with 4 menu items."""
    itemClicked = Signal(str)

    _ITEMS = [
        ("Главная",     "home"),
        ("Организация", "org"),
        ("Инструкция",  "help"),
        ("Соглашение",  "terms"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(280)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 28, 20, 28)
        lay.setSpacing(8)

        for text, key in self._ITEMS:
            btn = MenuItemButton(text)
            btn.clicked.connect(lambda _=False, k=key: self.itemClicked.emit(k))
            lay.addWidget(btn)

        lay.addStretch(1)


# ─────────── Home page (logo + connect button) ───────────

class HomePage(QWidget):
    connectClicked = Signal()

    def __init__(self, logo_path: str = "", parent=None):
        super().__init__(parent)
        self._logo_path = logo_path
        self._build()

    def _build(self):
        from components import GlassCard  # local import to avoid cycle noise

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.card = GlassCard()
        self.card.setFixedSize(440, 480)

        card_lay = QVBoxLayout(self.card)
        card_lay.setContentsMargins(48, 56, 48, 56)
        card_lay.setSpacing(0)

        self.logo = self._make_logo()
        self.connect_btn = ConnectButton()
        self.connect_btn.clicked.connect(self.connectClicked)

        card_lay.addStretch(1)
        card_lay.addWidget(self.logo, 0, Qt.AlignHCenter)
        card_lay.addSpacing(56)
        card_lay.addWidget(self.connect_btn, 0, Qt.AlignHCenter)
        card_lay.addStretch(1)

        outer.addStretch(1)
        outer.addWidget(self.card)
        outer.addStretch(1)

    def _make_logo(self) -> QLabel:
        if self._logo_path and os.path.exists(self._logo_path):
            lbl = QLabel()
            pix = QPixmap(self._logo_path).scaled(
                140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation,
            )
            lbl.setPixmap(pix)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedSize(140, 140)
            return lbl
        return LogoBadge()


# ─────────── Stub page («В разработке») ───────────

class StubPage(QWidget):
    """Shown after successful «Подключиться» click."""
    backClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        from components import GlassCard

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = GlassCard()
        card.setFixedSize(520, 420)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(56, 56, 56, 56)
        lay.setSpacing(0)

        icon = QLabel("⚙")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(
            "font-size: 64px; color: #6366F1; background: transparent;"
        )

        t = QLabel("В разработке")
        t.setObjectName("stubTitle")
        t.setAlignment(Qt.AlignCenter)

        hint = QLabel("Эта секция появится в следующей версии")
        hint.setObjectName("stubHint")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)

        back = GhostButton("← Назад в меню")
        back.clicked.connect(self.backClicked)

        lay.addStretch(1)
        lay.addWidget(icon)
        lay.addSpacing(20)
        lay.addWidget(t)
        lay.addSpacing(8)
        lay.addWidget(hint)
        lay.addStretch(1)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(back)
        btn_row.addStretch(1)
        lay.addLayout(btn_row)

        outer.addStretch(1)
        outer.addWidget(card)
        outer.addStretch(1)

"""
MainWindow — glass gradient background, header, stacked content, sidebar overlay.

Layout (strict QVBox/QHBox, main UI only):

QMainWindow
└── central  (QVBoxLayout, margins 20, spacing 24)
    ├── Header              (fixed 72)
    └── QStackedWidget      (stretch)
        ├── HomePage        (logo + Connect)
        └── StubPage        («В разработке» + Back)

Overlays (children of `central`, positioned in resizeEvent,
raised above the stack — this is NOT absolute UI positioning, it's
the standard Qt overlay pattern for slide-in menus):
    - Backdrop  (dim layer, click to close)
    - Sidebar   (280px, slides in from left via QPropertyAnimation)
    - Toast     («Требуется вход» — 2.5s auto-hide)
"""

import os
from PySide6.QtCore import (
    Qt, QEasingCurve, QPoint, QPropertyAnimation, QRect, QTimer, Signal, Slot,
)
from PySide6.QtGui import (
    QBrush, QColor, QLinearGradient, QPainter, QRadialGradient,
)
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QMainWindow, QStackedWidget, QVBoxLayout, QWidget,
)

from dialogs import InfoDialog, LoginDialog, RegisterDialog
from state import AppState
from styles import APP_STYLE
from widgets import Header, HomePage, Sidebar, StubPage


SIDEBAR_WIDTH = 280
ANIM_MS = 320


# ─────────── Backdrop ───────────

class Backdrop(QWidget):
    clicked = Signal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background: rgba(13, 18, 30, 0.28);")
        self.hide()

    def mousePressEvent(self, e):
        self.clicked.emit()
        super().mousePressEvent(e)


# ─────────── Main window ───────────

class MainWindow(QMainWindow):
    def __init__(self, logo_path: str = ""):
        super().__init__()
        self.setWindowTitle("")
        self.setMinimumSize(1100, 740)
        self.resize(1200, 780)
        self.setStyleSheet(APP_STYLE)

        self._logo_path = logo_path
        self._sidebar_open = False
        self._anim = None
        self._shake_anim = None

        self.state = AppState()
        self.state.userChanged.connect(self._refresh_user)

        self._build()
        self._refresh_user()

    # ── Background painting: gradient + soft colored blobs ──
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()

        g = QLinearGradient(0, 0, 0, r.height())
        g.setColorAt(0.0, QColor("#E8EEFB"))
        g.setColorAt(0.5, QColor("#EDE7FB"))
        g.setColorAt(1.0, QColor("#FCE9EF"))
        p.fillRect(r, QBrush(g))

        b1 = QRadialGradient(r.width() * 0.15, r.height() * 0.20, r.width() * 0.45)
        b1.setColorAt(0.0, QColor(99, 102, 241, 120))
        b1.setColorAt(1.0, QColor(99, 102, 241, 0))
        p.fillRect(r, QBrush(b1))

        b2 = QRadialGradient(r.width() * 0.85, r.height() * 0.85, r.width() * 0.50)
        b2.setColorAt(0.0, QColor(168, 85, 247, 110))
        b2.setColorAt(1.0, QColor(168, 85, 247, 0))
        p.fillRect(r, QBrush(b2))

        b3 = QRadialGradient(r.width() * 0.75, r.height() * 0.25, r.width() * 0.35)
        b3.setColorAt(0.0, QColor(244, 114, 182, 90))
        b3.setColorAt(1.0, QColor(244, 114, 182, 0))
        p.fillRect(r, QBrush(b3))

        p.end()

    # ── Build ──
    def _build(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)

        root = QVBoxLayout(self.central)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(24)

        # Header
        self.header = Header()
        self.header.menuToggled.connect(self._toggle_sidebar)
        self.header.loginRequested.connect(self._open_login)
        self.header.registerRequested.connect(self._open_register)
        self.header.logoutRequested.connect(self._logout)
        root.addWidget(self.header)

        # Stacked content
        self.stack = QStackedWidget()

        self.home_page = HomePage(self._logo_path)
        self.home_page.connectClicked.connect(self._on_connect)

        self.stub_page = StubPage()
        self.stub_page.backClicked.connect(self._go_home)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.stub_page)

        root.addWidget(self.stack, 1)

        # ── Overlays ──
        self.backdrop = Backdrop(self.central)
        self.backdrop.clicked.connect(self._toggle_sidebar)

        self.sidebar = Sidebar(self.central)
        self.sidebar.itemClicked.connect(self._on_menu_item)

        # Toast (hidden by default)
        self.toast = QLabel("Требуется вход", self.central)
        self.toast.setObjectName("toast")
        self.toast.setAlignment(Qt.AlignCenter)
        self.toast.adjustSize()
        self.toast.hide()
        self._toast_timer = QTimer(self)
        self._toast_timer.setSingleShot(True)
        self._toast_timer.timeout.connect(self.toast.hide)

        self._place_overlays(opened=False)
        self.backdrop.raise_()
        self.sidebar.raise_()
        self.toast.raise_()

    # ── Overlay positioning ──
    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._place_overlays(opened=self._sidebar_open)
        self._place_toast()

    def _place_overlays(self, opened: bool):
        if not hasattr(self, "sidebar"):
            return
        w = self.central.width()
        h = self.central.height()

        self.backdrop.setGeometry(0, 0, w, h)

        top = 20 + 72 + 24  # root top margin + header height + spacing
        bottom_inset = 20
        sb_h = max(100, h - top - bottom_inset)
        sb_x = 20 if opened else -SIDEBAR_WIDTH - 40
        self.sidebar.setGeometry(sb_x, top, SIDEBAR_WIDTH, sb_h)

    def _place_toast(self):
        if not hasattr(self, "toast"):
            return
        self.toast.adjustSize()
        w = self.central.width()
        h = self.central.height()
        x = (w - self.toast.width()) // 2
        y = h - self.toast.height() - 40
        self.toast.move(x, y)

    # ── Sidebar ──
    @Slot()
    def _toggle_sidebar(self):
        self._sidebar_open = not self._sidebar_open

        if self._anim:
            self._anim.stop()

        top = 20 + 72 + 24
        sb_h = max(100, self.central.height() - top - 20)
        start = self.sidebar.geometry()
        end_x = 20 if self._sidebar_open else -SIDEBAR_WIDTH - 40
        end = QRect(end_x, top, SIDEBAR_WIDTH, sb_h)

        self._anim = QPropertyAnimation(self.sidebar, b"geometry", self)
        self._anim.setDuration(ANIM_MS)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.start()

        if self._sidebar_open:
            self.backdrop.show()
            self.backdrop.raise_()
            self.sidebar.raise_()
        else:
            self.backdrop.hide()

    # ── Navigation ──
    @Slot()
    def _go_home(self):
        self.stack.setCurrentWidget(self.home_page)

    # ── Auth ──
    @Slot()
    def _open_login(self):
        dlg = LoginDialog(self)
        dlg.authenticated.connect(lambda name: self.state.login(name))
        dlg.exec()

    @Slot()
    def _open_register(self):
        dlg = RegisterDialog(self)
        dlg.registered.connect(
            lambda fn, org, em, ph: self.state.register(fn, org, em, ph)
        )
        dlg.exec()

    @Slot()
    def _logout(self):
        self.state.logout()
        self._go_home()

    @Slot()
    def _refresh_user(self):
        u = self.state.user
        self.header.set_user(u.full_name, u.is_authenticated)

    # ── Connect ──
    @Slot()
    def _on_connect(self):
        if not self.state.user.is_authenticated:
            self._flash_locked()
            return
        self.stack.setCurrentWidget(self.stub_page)

    def _flash_locked(self):
        # Shake the connect button
        btn = self.home_page.connect_btn
        origin = btn.pos()

        if self._shake_anim:
            self._shake_anim.stop()

        self._shake_anim = QPropertyAnimation(btn, b"pos", self)
        self._shake_anim.setDuration(340)
        self._shake_anim.setLoopCount(1)
        self._shake_anim.setKeyValueAt(0.0,  origin)
        self._shake_anim.setKeyValueAt(0.15, origin + QPoint(-10, 0))
        self._shake_anim.setKeyValueAt(0.30, origin + QPoint( 10, 0))
        self._shake_anim.setKeyValueAt(0.45, origin + QPoint(-8,  0))
        self._shake_anim.setKeyValueAt(0.60, origin + QPoint( 8,  0))
        self._shake_anim.setKeyValueAt(0.80, origin + QPoint(-4,  0))
        self._shake_anim.setKeyValueAt(1.0,  origin)
        self._shake_anim.start()

        # Toast
        self._place_toast()
        self.toast.show()
        self.toast.raise_()
        self._toast_timer.start(2500)

    # ── Menu items ──
    _INFO = {
        "org": (
            "Организация",
            "ООО «ИндуСтрой»\n\n"
            "Контактное лицо: Иван Иванов\n"
            "Email: ivan.ivanov@example.com\n\n"
            "Организация авторизована для использования данного ПО.",
        ),
        "help": (
            "Инструкция",
            "1. Зарегистрируйтесь или войдите в систему.\n"
            "2. Нажмите «Подключиться» для перехода к рабочей области.\n"
            "3. Управление устройством доступно после авторизации.\n\n"
            "Данная версия — демонстрационный прототип.",
        ),
        "terms": (
            "Пользовательское соглашение",
            "1. ПО предоставляется «как есть».\n"
            "2. Реальное взаимодействие с оборудованием недоступно в данной версии.\n"
            "3. Данные сеанса хранятся только в оперативной памяти.\n"
            "4. Использование осуществляется на усмотрение пользователя.",
        ),
    }

    @Slot(str)
    def _on_menu_item(self, key: str):
        # Close sidebar on any click
        if self._sidebar_open:
            self._toggle_sidebar()

        if key == "home":
            self._go_home()
            return
        if key in self._INFO:
            title, text = self._INFO[key]
            InfoDialog(title, text, self).exec()

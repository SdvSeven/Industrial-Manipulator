from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QDialog

from services.app_state import AppState
from ui.dialogs import LoginDialog, RegisterDialog
from ui.header import Header
from ui.sidebar import Sidebar
from ui.dashboard import Dashboard

_CSS_CONNECTED    = "color: #22c55e; font-size: 14px; background: transparent;"
_CSS_DISCONNECTED = ""   # falls back to QSS #statusLabel rule


class MainWindow(QMainWindow):
    """
    Root application window — 1920×1080.

    Responsibilities
    ----------------
    • Owns AppState (single source of truth).
    • Wires all signals in one place (_connect_signals).
    • Delegates state mutations to AppState business methods.
    • Pushes state changes into the UI via update_*_ui().
    • No business logic inside widget classes.

    Layout (top → bottom)
    ----------------------
    Header (64 px)
    Body: Sidebar (240 px) | Dashboard (stretch)
      Dashboard owns DeviceBar (440 px, content column only)
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Индустриальный Манипулятор")
        self.resize(1920, 1080)

        self._state = AppState()

        # ── Central widget ─────────────────────────────────────
        root = QWidget()
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Header ────────────────────────────────────────────
        self.header = Header()
        root_layout.addWidget(self.header)

        # ── Body: sidebar + content ────────────────────────────
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self.sidebar = Sidebar()
        body_layout.addWidget(self.sidebar)

        self.dashboard = Dashboard()
        body_layout.addWidget(self.dashboard, 1)

        root_layout.addWidget(body, 1)

        # ── Wire signals ───────────────────────────────────────
        self._connect_signals()

    # ══════════════════════════════════════════════════════════
    # Signal wiring
    # ══════════════════════════════════════════════════════════

    def _connect_signals(self) -> None:
        self.header.login_btn.clicked.connect(self._on_login_clicked)
        self.header.reg_btn.clicked.connect(self._on_register_clicked)
        self.dashboard.connect_image.clicked.connect(self._on_connect_clicked)
        self.sidebar.item_clicked.connect(self._on_nav_item)

    # ══════════════════════════════════════════════════════════
    # Handlers
    # ══════════════════════════════════════════════════════════

    def _on_connect_clicked(self) -> None:
        self._state.toggle_connection()
        self.update_status_ui()

    def _on_login_clicked(self) -> None:
        dlg = LoginDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            login, _ = dlg.credentials()
            self._state.login(login)
            self.update_auth_ui()

    def _on_register_clicked(self) -> None:
        dlg = RegisterDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, email = dlg.credentials()
            self._state.register(name, email)
            self.update_auth_ui()

    def _on_nav_item(self, name: str) -> None:
        self.setWindowTitle(f"Индустриальный Манипулятор — {name}")
        self.dashboard.show_page("control" if name == "Управление" else "main")

    # ══════════════════════════════════════════════════════════
    # UI update methods  (state → UI)
    # ══════════════════════════════════════════════════════════

    def update_status_ui(self) -> None:
        if self._state.is_connected:
            self.dashboard.status_label.setText("● ПОДКЛЮЧЕНО")
            self.dashboard.status_label.setStyleSheet(_CSS_CONNECTED)
        else:
            self.dashboard.status_label.setText("● НЕ ПОДКЛЮЧЕНО")
            self.dashboard.status_label.setStyleSheet(_CSS_DISCONNECTED)

    def update_auth_ui(self) -> None:
        if self._state.is_authenticated:
            self.header.show_user(self._state.display_name)
        else:
            self.header.show_auth_buttons()

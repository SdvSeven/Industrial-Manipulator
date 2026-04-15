from __future__ import annotations

from PySide6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget

from ui.views.home_view import HomeView
from ui.views.control_view import ControlView
from ui.views.settings_view import SettingsView
from ui.views.logs_view import LogsView
from services.app_state import AppState

_PAGE_INDEX = {"main": 0, "control": 1, "settings": 2, "logs": 3}


class Dashboard(QWidget):
    """
    Central content area — QStackedWidget with 4 pages.

    Pages
    -----
    0 — HomeView     ("main")
    1 — ControlView  ("control")
    2 — SettingsView ("settings")
    3 — LogsView     ("logs")

    Public attributes
    -----------------
    home     : HomeView
    control  : ControlView
    settings : SettingsView
    logs     : LogsView

    Public methods
    --------------
    show_page(name: str)   — "main" | "control" | "settings" | "logs"
    bind_state(AppState)   — wire SettingsView to AppState
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("contentArea")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._stack = QStackedWidget()
        root.addWidget(self._stack)

        self.home     = HomeView()
        self.control  = ControlView()
        self.settings = SettingsView()
        self.logs     = LogsView()

        self._stack.addWidget(self.home)      # 0
        self._stack.addWidget(self.control)   # 1
        self._stack.addWidget(self.settings)  # 2
        self._stack.addWidget(self.logs)      # 3

        self._stack.setCurrentIndex(0)
        self._current_page = "main"

    # ── Public API ─────────────────────────────────────────────

    def bind_state(self, state: AppState) -> None:
        self.settings.bind_state(state)
        # BUG#7: share the same deque — eliminates the duplicate copy in LogsView
        self.logs.bind_log_entries(state.log_entries)

    def show_page(self, name: str) -> None:
        idx = _PAGE_INDEX.get(name, 0)

        # Stop camera when leaving control page
        if self._current_page == "control" and name != "control":
            self.control.stop_camera()

        self._stack.setCurrentIndex(idx)
        self._current_page = name

        # Start camera when entering control page
        if name == "control":
            self.control.start_camera()

    @property
    def current_page(self) -> str:
        return self._current_page

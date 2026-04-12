from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout

from ui.header import Header
from ui.sidebar import Sidebar
from ui.dashboard import Dashboard


class MainWindow(QMainWindow):
    """
    Root application window — 1920×1080.
    Layout (top-to-bottom):
        Header  (64 px fixed height)
        Body:
            Sidebar  (240 px fixed width) | Content area (stretch)
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Индустриальный Манипулятор")
        self.resize(1920, 1080)

        # ── Central widget ─────────────────────────────────────
        root_widget = QWidget()
        self.setCentralWidget(root_widget)

        root_layout = QVBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Header ────────────────────────────────────────────
        self.header = Header()
        root_layout.addWidget(self.header)

        # ── Body (sidebar + content) ──────────────────────────
        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self.sidebar = Sidebar()
        body_layout.addWidget(self.sidebar)

        self.dashboard = Dashboard()
        body_layout.addWidget(self.dashboard, 1)   # stretch=1 → fills remaining width

        root_layout.addWidget(body_widget, 1)      # stretch=1 → fills below header

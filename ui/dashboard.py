from __future__ import annotations

from PySide6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget

from components.camera_view import CameraView
from ui.views.home_view import HomeView


class Dashboard(QWidget):
    """
    Central content area.  Two pages via QStackedWidget:

      Page 0 — HomeView   : DeviceBar + connect image + status label
      Page 1 — CameraView : full-area webcam with mediapipe hands

    Public attributes (delegated from HomeView)
    -------------------------------------------
    connect_image : _ClickableImage  — emits clicked()
    status_label  : QLabel
    device_bar    : DeviceBar

    Public methods
    --------------
    show_page(name: str)  — "main" | "control"
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("contentArea")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._stack = QStackedWidget()
        root.addWidget(self._stack)

        # Page 0
        self._home = HomeView()
        self._stack.addWidget(self._home)

        # Page 1
        self._camera_view = CameraView()
        self._stack.addWidget(self._camera_view)

        self._stack.setCurrentIndex(0)

        # Delegate public attributes
        self.connect_image = self._home.connect_image
        self.status_label = self._home.status_label
        self.device_bar = self._home.device_bar

    # ── Public API ─────────────────────────────────────────────

    def show_page(self, name: str) -> None:
        """Switch between pages and manage the camera lifecycle."""
        if name == "control":
            self._stack.setCurrentIndex(1)
            self._camera_view.start()
        else:
            self._camera_view.stop()
            self._stack.setCurrentIndex(0)

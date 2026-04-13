from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from services.camera_worker import CameraWorker


class CameraView(QWidget):
    """
    Full-area webcam view with mediapipe hand landmark overlay.

    Call start() when the view becomes visible,
    call stop() when navigating away — releases the camera.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("cameraView")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._feed = QLabel("Нет сигнала")
        self._feed.setObjectName("cameraFeed")
        self._feed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._feed.setMinimumSize(1, 1)   # allow shrinking
        layout.addWidget(self._feed)

        self._worker: CameraWorker | None = None

    # ── Public API ─────────────────────────────────────────────

    def start(self) -> None:
        """Open the camera and start streaming processed frames."""
        if self._worker is not None:
            return
        self._worker = CameraWorker(self)
        self._worker.frame_ready.connect(self._on_frame)
        self._worker.start()

    def stop(self) -> None:
        """Stop streaming and release the camera."""
        if self._worker is None:
            return
        self._worker.stop()
        self._worker.wait(3000)
        self._worker.deleteLater()
        self._worker = None
        self._feed.setPixmap(QPixmap())
        self._feed.setText("Нет сигнала")

    # ── Slots ──────────────────────────────────────────────────

    def _on_frame(self, img: QImage) -> None:
        """Scale the incoming frame to fill the label, keep aspect ratio."""
        pm = QPixmap.fromImage(img).scaled(
            self._feed.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._feed.setPixmap(pm)

    # ── Cleanup ────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        self.stop()
        super().closeEvent(event)

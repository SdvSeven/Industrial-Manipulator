from __future__ import annotations

import os
import subprocess
import sys

from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QBrush, QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout, QLabel, QPushButton,
    QVBoxLayout, QWidget,
)

from components.device_bar import DeviceBar
from models.device_status import DeviceStatus
from models.system_state import SystemState

_MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "media")
_IMG_MAX_W = 400
_IMG_MAX_H = 400

# ── Image paths per state ──────────────────────────────────────
_STATE_IMAGES = {
    SystemState.IDLE:       os.path.join(_MEDIA, "connect.png"),
    SystemState.CONNECTING: os.path.join(_MEDIA, "connect.png"),
    SystemState.RUNNING:    os.path.join(_MEDIA, "green_connect.png"),
    SystemState.ERROR:      os.path.join(_MEDIA, "red_connect.png"),
}
_STATE_LABEL_TEXT = {
    SystemState.IDLE:       "▶  НАЖМИТЕ ДЛЯ ПОДКЛЮЧЕНИЯ",
    SystemState.CONNECTING: "●  ПОДКЛЮЧЕНИЕ...",
    SystemState.RUNNING:    "●  ПОДКЛЮЧЕНО",
    SystemState.ERROR:      "⚠  ОШИБКА",
}
_STATE_LABEL_CSS = {
    SystemState.IDLE:       "color: #e2e8f0;",
    SystemState.CONNECTING: "color: #eab308;",
    SystemState.RUNNING:    "color: #22c55e;",
    SystemState.ERROR:      "color: #ef4444;",
}


# ──────────────────────────────────────────────────────────────
class _ClickableImage(QLabel):
    """QLabel with hover opacity animation and click signal."""

    clicked = Signal()

    def __init__(self, pixmap: QPixmap, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setPixmap(pixmap)
        self.setFixedSize(pixmap.size())
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._effect = QGraphicsOpacityEffect(self)
        self._effect.setOpacity(0.90)
        self.setGraphicsEffect(self._effect)

        self._anim = QPropertyAnimation(self._effect, b"opacity", self)
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def _animate(self, target: float) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._effect.opacity())
        self._anim.setEndValue(target)
        self._anim.start()

    def set_pixmap_scaled(self, pm: QPixmap) -> None:
        self.setPixmap(pm)
        self.setFixedSize(pm.size())

    def enterEvent(self, event) -> None:
        self._animate(1.0); super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._animate(0.90); super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._animate(0.65)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._animate(1.0)
            self.clicked.emit()
        super().mouseReleaseEvent(event)


# ──────────────────────────────────────────────────────────────
class HomeView(QWidget):
    """
    Main home screen.

    Public attributes
    -----------------
    connect_image : _ClickableImage — emits clicked()
    status_label  : QLabel
    device_bar    : DeviceBar

    Public methods
    --------------
    update_state(state: SystemState)
    update_devices(devices: DeviceStatus)
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("mainPage")

        # Pre-load all state images
        self._pixmaps: dict[SystemState, QPixmap] = {}
        for state, path in _STATE_IMAGES.items():
            self._pixmaps[state] = self._load_image(path, state)

        outer_v = QVBoxLayout(self)
        outer_v.setContentsMargins(0, 0, 0, 0)
        outer_v.setSpacing(0)
        outer_v.addStretch(1)

        outer_h = QHBoxLayout()
        outer_h.setContentsMargins(0, 0, 0, 0)
        outer_h.setSpacing(0)
        outer_h.addStretch(1)

        inner = QWidget()
        inner.setObjectName("dashboardInner")
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)
        inner_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Device bar
        self.device_bar = DeviceBar()
        self.device_bar.setFixedWidth(440)
        inner_layout.addWidget(self.device_bar, 0, Qt.AlignmentFlag.AlignHCenter)
        inner_layout.addSpacing(16)

        # Connect image
        self.connect_image = _ClickableImage(
            self._pixmaps[SystemState.IDLE], inner
        )
        inner_layout.addWidget(self.connect_image, 0, Qt.AlignmentFlag.AlignHCenter)
        inner_layout.addSpacing(24)

        # Status label
        self.status_label = QLabel(_STATE_LABEL_TEXT[SystemState.IDLE])
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner_layout.addWidget(self.status_label, 0, Qt.AlignmentFlag.AlignHCenter)

        outer_h.addWidget(inner)
        outer_h.addStretch(1)

        outer_v.addLayout(outer_h)
        outer_v.addStretch(1)

        # ── Restart button — bottom-right of content area ──────
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(0, 0, 24, 16)
        bottom_bar.addStretch(1)

        self._restart_btn = QPushButton("Перезапуск")
        self._restart_btn.setObjectName("restartBtn")
        self._restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._restart_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._restart_btn.clicked.connect(self._on_restart)

        # Icon to the right of text
        restart_icon_path = os.path.join(_MEDIA, "reboot.png")
        if os.path.exists(restart_icon_path):
            from PySide6.QtGui import QIcon
            self._restart_btn.setIcon(QIcon(restart_icon_path))
            from PySide6.QtCore import QSize
            self._restart_btn.setIconSize(QSize(16, 16))
            self._restart_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        bottom_bar.addWidget(self._restart_btn)
        outer_v.addLayout(bottom_bar)

    # ── Public API ─────────────────────────────────────────────

    def update_state(self, state: SystemState) -> None:
        """Update image, status label text and color."""
        self.connect_image.set_pixmap_scaled(self._pixmaps[state])
        self.status_label.setText(_STATE_LABEL_TEXT[state])
        base_css = "font-size: 14px; background: transparent;"
        self.status_label.setStyleSheet(
            _STATE_LABEL_CSS[state] + base_css
        )

    def update_devices(self, devices: DeviceStatus) -> None:
        self.device_bar.update_status(devices)

    # ── Restart ────────────────────────────────────────────────

    @staticmethod
    def _on_restart() -> None:
        from PySide6.QtWidgets import QApplication
        subprocess.Popen([sys.executable] + sys.argv)
        QApplication.instance().quit()

    # ── Image helpers ──────────────────────────────────────────

    def _load_image(self, path: str, state: SystemState) -> QPixmap:
        if os.path.exists(path):
            pm = QPixmap(path)
            if not pm.isNull():
                return pm.scaled(
                    _IMG_MAX_W, _IMG_MAX_H,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
        return self._placeholder_pixmap(state)

    @staticmethod
    def _placeholder_pixmap(state: SystemState) -> QPixmap:
        W, H = 240, 240
        _colors = {
            SystemState.IDLE:       "#2563eb",
            SystemState.CONNECTING: "#eab308",
            SystemState.RUNNING:    "#22c55e",
            SystemState.ERROR:      "#ef4444",
        }
        pm = QPixmap(W, H)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor("#1e293b")))
        p.setPen(QColor("#334155"))
        p.drawEllipse(8, 8, W - 16, H - 16)
        p.setPen(QColor(_colors.get(state, "#2563eb")))
        p.drawText(pm.rect(), Qt.AlignmentFlag.AlignCenter, "⏻")
        p.end()
        return pm

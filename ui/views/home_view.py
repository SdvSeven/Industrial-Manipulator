from __future__ import annotations

import os

from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QBrush, QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from components.device_bar import DeviceBar

_MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "media")
_CONNECT_PNG = os.path.join(_MEDIA, "connect.png")

_IMG_MAX_W = 400
_IMG_MAX_H = 400


# ──────────────────────────────────────────────────────────────
class _ClickableImage(QLabel):
    """QLabel that emits clicked() on left-click with hover opacity animation."""

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

    def enterEvent(self, event) -> None:
        self._animate(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._animate(0.90)
        super().leaveEvent(event)

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
    Main "home" screen: DeviceBar → clickable connect image → status label.

    Public attributes
    -----------------
    connect_image : _ClickableImage — emits clicked() when pressed
    status_label  : QLabel
    device_bar    : DeviceBar
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("mainPage")

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
        pixmap = self._load_connect_image()
        self.connect_image = _ClickableImage(pixmap, inner)
        inner_layout.addWidget(self.connect_image, 0, Qt.AlignmentFlag.AlignHCenter)
        inner_layout.addSpacing(24)

        # Status label
        self.status_label = QLabel("● НЕ ПОДКЛЮЧЕНО")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner_layout.addWidget(self.status_label, 0, Qt.AlignmentFlag.AlignHCenter)

        outer_h.addWidget(inner)
        outer_h.addStretch(1)

        outer_v.addLayout(outer_h)
        outer_v.addStretch(1)

    # ── Image helpers ──────────────────────────────────────────

    def _load_connect_image(self) -> QPixmap:
        if os.path.exists(_CONNECT_PNG):
            pm = QPixmap(_CONNECT_PNG)
            if not pm.isNull():
                return pm.scaled(
                    _IMG_MAX_W, _IMG_MAX_H,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
        return self._placeholder_pixmap()

    def _placeholder_pixmap(self) -> QPixmap:
        W, H = 240, 240
        pm = QPixmap(W, H)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor("#1e293b")))
        p.setPen(QColor("#334155"))
        p.drawEllipse(8, 8, W - 16, H - 16)
        p.setPen(QColor("#2563eb"))
        p.drawText(pm.rect(), Qt.AlignmentFlag.AlignCenter, "⏻")
        p.end()
        return pm

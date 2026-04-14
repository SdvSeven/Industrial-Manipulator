from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from models.device_status import DeviceStatus
from models.system_state import StatusIndicator

_INDICATOR_COLORS = {
    StatusIndicator.OK:           "#22c55e",
    StatusIndicator.INITIALIZING: "#eab308",
    StatusIndicator.ERROR:        "#ef4444",
}
_INDICATOR_SIZE = 10  # px, circle diameter


class _DeviceIndicator(QWidget):
    """One coloured dot + device name label."""

    def __init__(self, label: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color = QColor(_INDICATOR_COLORS[StatusIndicator.ERROR])

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._dot = QLabel()
        self._dot.setFixedSize(_INDICATOR_SIZE, _INDICATOR_SIZE)
        layout.addWidget(self._dot)

        self._lbl = QLabel(label)
        self._lbl.setObjectName("deviceBarLabel")
        layout.addWidget(self._lbl)

    def set_status(self, status: StatusIndicator) -> None:
        self._color = QColor(_INDICATOR_COLORS[status])
        self._dot.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        # Draw circle on top of the dot placeholder
        dot_pos = self._dot.mapTo(self, self._dot.rect().topLeft())
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(self._color)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(
            dot_pos.x(), dot_pos.y() + (_INDICATOR_SIZE // 4),
            _INDICATOR_SIZE, _INDICATOR_SIZE,
        )
        p.end()


class DeviceBar(QFrame):
    """
    Horizontal pill-panel with 4 device status indicators.

    Call update_status(DeviceStatus) to refresh indicators.
    """

    def __init__(self, parent: QFrame | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("deviceBar")
        self.setFixedHeight(44)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(32)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self._arduino    = _DeviceIndicator("Arduino (COM3)")
        self._camera     = _DeviceIndicator("Camera (0)")
        self._mediapipe  = _DeviceIndicator("MediaPipe")
        self._connection = _DeviceIndicator("Connection")

        for ind in (self._arduino, self._camera, self._mediapipe, self._connection):
            layout.addWidget(ind)

        layout.addStretch(1)

    def update_status(self, devices: DeviceStatus) -> None:
        self._arduino.set_status(devices.arduino)
        self._camera.set_status(devices.camera)
        self._mediapipe.set_status(devices.mediapipe)
        self._connection.set_status(devices.connection)
        self.update()

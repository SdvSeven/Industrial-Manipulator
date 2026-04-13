from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel


class DeviceBar(QFrame):
    """
    Horizontal info-panel placed between the header and the body.
    Shape: pill / half-circle (border-radius ≈ half height).
    Width stretches to fill the available area.
    Content is static for now.
    """

    def __init__(self, parent: QFrame | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("deviceBar")
        self.setFixedHeight(44)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(0)

        self._label = QLabel(
            "Подключенные устройства:  Arduino COM3  ·  Камера 0"
        )
        self._label.setObjectName("deviceBarLabel")
        self._label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._label)

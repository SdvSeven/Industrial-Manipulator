from __future__ import annotations

from PySide6.QtCore import (
    Qt, Signal, QPropertyAnimation, QEasingCurve,
)
from PySide6.QtGui import (
    QPainter, QPixmap,
)
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout, QLabel, QStyle, QStyleOption, QWidget,
)

_ICON_SIZE = 16          # px — matches 14 px font cap height
_ICON_TEXT_GAP = 10      # px — between icon and text


class SidebarItem(QWidget):
    """
    Sidebar navigation item with icon + text.

    Hover behaviour:
        • icon opacity: dim (0.55) → full (1.0)  — animated 160 ms
        • text and background: NO change on hover

    Active (checked) state:
        • container background = #1e3a8a
        • text colour = #93c5fd
        • icon opacity = 1.0 (always lit)
    """

    clicked = Signal(str)   # emits item name

    def __init__(
        self,
        name: str,
        icon_path: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._name = name
        self._checked = False

        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(_ICON_TEXT_GAP)

        # ── Icon ──────────────────────────────────────────────
        self._icon_lbl = QLabel()
        self._icon_lbl.setFixedSize(_ICON_SIZE, _ICON_SIZE)
        self._icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_lbl.setScaledContents(False)

        pm = QPixmap(icon_path)
        if not pm.isNull():
            pm = pm.scaled(
                _ICON_SIZE, _ICON_SIZE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._icon_lbl.setPixmap(pm)

        # Opacity effect applied ONLY to the icon label
        self._opacity = QGraphicsOpacityEffect(self._icon_lbl)
        self._opacity.setOpacity(0.55)
        self._icon_lbl.setGraphicsEffect(self._opacity)

        # Smooth opacity animation
        self._anim = QPropertyAnimation(self._opacity, b"opacity", self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        layout.addWidget(self._icon_lbl)

        # ── Text ──────────────────────────────────────────────
        self._text_lbl = QLabel(name)
        self._text_lbl.setObjectName("sidebarItemText")
        self._text_lbl.setStyleSheet(
            "background: transparent; color: #e2e8f0; font-size: 14px;"
        )
        layout.addWidget(self._text_lbl, 1)

    # ── Public API ─────────────────────────────────────────────

    def setChecked(self, checked: bool) -> None:
        self._checked = checked
        self._refresh_style()

    def isChecked(self) -> bool:
        return self._checked

    # ── Internal ───────────────────────────────────────────────

    def _refresh_style(self) -> None:
        if self._checked:
            self.setStyleSheet(
                "SidebarItem { background-color: #1e3a8a; border-radius: 8px; }"
            )
            self._text_lbl.setStyleSheet(
                "background: transparent; color: #93c5fd; font-size: 14px;"
            )
            self._opacity.setOpacity(1.0)
        else:
            self.setStyleSheet(
                "SidebarItem { background-color: transparent; border-radius: 8px; }"
            )
            self._text_lbl.setStyleSheet(
                "background: transparent; color: #e2e8f0; font-size: 14px;"
            )
            self._opacity.setOpacity(0.55)

    def _animate_icon(self, target: float) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._opacity.opacity())
        self._anim.setEndValue(target)
        self._anim.start()

    # ── Events ─────────────────────────────────────────────────

    def enterEvent(self, event) -> None:
        self._animate_icon(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if not self._checked:
            self._animate_icon(0.55)
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._name)
        super().mousePressEvent(event)

    # paintEvent needed so setStyleSheet background-color renders on QWidget
    def paintEvent(self, event) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

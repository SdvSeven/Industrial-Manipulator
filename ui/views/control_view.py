from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QPushButton, QSlider,
    QStyle, QStyleOption, QVBoxLayout, QWidget,
)

from components.camera_view import CameraView
from models.system_state import ControlMode


# ──────────────────────────────────────────────────────────────
class _GestureOverlay(QFrame):
    """
    Semi-transparent info box overlaid on the camera feed.
    Shows GESTURE / COMMAND / CONFIDENCE.
    Positioned absolutely by CameraContainer.resizeEvent.
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("gestureOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        self._gesture_lbl    = self._make_label("GESTURE:     —")
        self._command_lbl    = self._make_label("COMMAND:     —")
        self._confidence_lbl = self._make_label("CONFIDENCE:  —")

        layout.addWidget(self._gesture_lbl)
        layout.addWidget(self._command_lbl)
        layout.addWidget(self._confidence_lbl)
        self.adjustSize()

    def update_data(self, gesture: str, command: str, confidence: float) -> None:
        self._gesture_lbl.setText(f"GESTURE:     {gesture}")
        self._command_lbl.setText(f"COMMAND:     {command}")
        self._confidence_lbl.setText(f"CONFIDENCE:  {confidence:.2f}")

    @staticmethod
    def _make_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("overlayLabel")
        return lbl

    def paintEvent(self, event) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)


# ──────────────────────────────────────────────────────────────
class _CameraContainer(QWidget):
    """CameraView + floating GestureOverlay."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("cameraPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.camera_view = CameraView(self)
        layout.addWidget(self.camera_view)

        self._overlay = _GestureOverlay(self)
        self._overlay.raise_()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._overlay.move(16, 16)
        self._overlay.raise_()

    def update_overlay(self, gesture: str, command: str, confidence: float) -> None:
        self._overlay.update_data(gesture, command, confidence)

    def start(self) -> None:
        self.camera_view.start()

    def stop(self) -> None:
        self.camera_view.stop()


# ──────────────────────────────────────────────────────────────
class _ControlPanel(QWidget):
    """
    Right panel (30%).

    Signals
    -------
    emergency_stop_triggered
    mode_changed(str)         — "GESTURE" | "MANUAL"
    manual_command(str)       — "UP" | "DOWN" | "LEFT" | "RIGHT" | "GRAB" | "RELEASE"
    speed_changed(int)        — 0–100
    sensitivity_changed(int)  — 0–100
    """

    emergency_stop_triggered = Signal()
    mode_changed             = Signal(str)
    manual_command           = Signal(str)
    speed_changed            = Signal(int)
    sensitivity_changed      = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("controlPanel")
        self.setFixedWidth(360)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        # ── Title ──────────────────────────────────────────────
        title = QLabel("Панель управления")
        title.setObjectName("controlPanelTitle")
        root.addWidget(title)

        # ── Mode toggle ────────────────────────────────────────
        root.addWidget(self._build_mode_toggle())

        # ── Gesture info ───────────────────────────────────────
        root.addWidget(self._build_gesture_info())

        # ── Separator ─────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("controlSeparator")
        root.addWidget(sep)

        # ── Manual controls ────────────────────────────────────
        root.addWidget(self._build_manual_controls())

        # ── Speed ──────────────────────────────────────────────
        root.addWidget(self._build_slider_block(
            "Speed", 50, self.speed_changed
        ))

        # ── Sensitivity ───────────────────────────────────────
        root.addWidget(self._build_slider_block(
            "Sensitivity", 50, self.sensitivity_changed
        ))

        root.addStretch(1)

        # ── Emergency Stop (always at bottom) ─────────────────
        self._estop_btn = QPushButton("!!!  STOP  !!!")
        self._estop_btn.setObjectName("emergencyStopBtn")
        self._estop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._estop_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._estop_btn.setMinimumHeight(64)
        self._estop_btn.clicked.connect(self.emergency_stop_triggered)
        root.addWidget(self._estop_btn)

    # ── Public API ─────────────────────────────────────────────

    def update_gesture_info(self, gesture: str, stability: float) -> None:
        self._gesture_val.setText(gesture)
        self._stability_val.setText(f"{stability * 100:.0f}%")

    def set_mode(self, mode: ControlMode) -> None:
        is_gesture = mode == ControlMode.GESTURE
        self._btn_gesture.setChecked(is_gesture)
        self._btn_manual.setChecked(not is_gesture)
        self._manual_box.setEnabled(not is_gesture)
        self._refresh_mode_styles(is_gesture)

    # ── Builders ───────────────────────────────────────────────

    def _build_mode_toggle(self) -> QWidget:
        w = QWidget()
        w.setObjectName("modeToggleWidget")
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        self._btn_gesture = QPushButton("Gesture")
        self._btn_gesture.setObjectName("modeBtn")
        self._btn_gesture.setCheckable(True)
        self._btn_gesture.setChecked(True)
        self._btn_gesture.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_gesture.clicked.connect(lambda: self._on_mode_clicked("GESTURE"))

        self._btn_manual = QPushButton("Manual")
        self._btn_manual.setObjectName("modeBtn")
        self._btn_manual.setCheckable(True)
        self._btn_manual.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_manual.clicked.connect(lambda: self._on_mode_clicked("MANUAL"))

        h.addWidget(self._btn_gesture)
        h.addWidget(self._btn_manual)
        self._refresh_mode_styles(True)
        return w

    def _build_gesture_info(self) -> QWidget:
        w = QWidget()
        w.setObjectName("gestureInfoWidget")
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)

        def _row(key: str, val_attr: str) -> QLabel:
            row = QHBoxLayout()
            k_lbl = QLabel(f"{key}:")
            k_lbl.setObjectName("gestureInfoKey")
            v_lbl = QLabel("—")
            v_lbl.setObjectName("gestureInfoValue")
            row.addWidget(k_lbl)
            row.addStretch()
            row.addWidget(v_lbl)
            v.addLayout(row)
            return v_lbl

        self._gesture_val  = _row("Gesture",   "_gesture_val")
        self._stability_val = _row("Stability", "_stability_val")
        return w

    def _build_manual_controls(self) -> QGroupBox:
        self._manual_box = QGroupBox("Ручное управление")
        self._manual_box.setObjectName("manualControlsGroup")
        self._manual_box.setEnabled(False)   # disabled in GESTURE mode

        grid = QGridLayout(self._manual_box)
        grid.setSpacing(6)

        def _btn(text: str, cmd: str) -> QPushButton:
            b = QPushButton(text)
            b.setObjectName("manualBtn")
            b.setFixedSize(52, 40)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda: self.manual_command.emit(cmd))
            return b

        grid.addWidget(_btn("↑",  "UP"),      0, 1)
        grid.addWidget(_btn("←",  "LEFT"),    1, 0)
        grid.addWidget(_btn("→",  "RIGHT"),   1, 2)
        grid.addWidget(_btn("↓",  "DOWN"),    2, 1)

        grab_btn    = _btn("GRAB",    "GRAB")
        release_btn = _btn("RELEASE", "RELEASE")
        grab_btn.setFixedWidth(80)
        release_btn.setFixedWidth(80)
        grab_btn.setObjectName("manualBtnAction")
        release_btn.setObjectName("manualBtnAction")

        h = QHBoxLayout()
        h.addStretch()
        h.addWidget(grab_btn)
        h.addSpacing(8)
        h.addWidget(release_btn)
        h.addStretch()
        grid.addLayout(h, 3, 0, 1, 3)

        return self._manual_box

    def _build_slider_block(
        self, label: str, default: int, signal: Signal
    ) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)

        header = QHBoxLayout()
        lbl  = QLabel(f"{label}:")
        lbl.setObjectName("sliderLabel")
        val_lbl = QLabel(str(default))
        val_lbl.setObjectName("sliderValue")
        header.addWidget(lbl)
        header.addStretch()
        header.addWidget(val_lbl)
        v.addLayout(header)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setObjectName("controlSlider")
        slider.setRange(0, 100)
        slider.setValue(default)
        slider.valueChanged.connect(lambda x: val_lbl.setText(str(x)))
        slider.valueChanged.connect(signal)
        v.addWidget(slider)
        return w

    def _on_mode_clicked(self, mode_str: str) -> None:
        is_gesture = mode_str == "GESTURE"
        self._btn_gesture.setChecked(is_gesture)
        self._btn_manual.setChecked(not is_gesture)
        self._manual_box.setEnabled(not is_gesture)
        self._refresh_mode_styles(is_gesture)
        self.mode_changed.emit(mode_str)

    def _refresh_mode_styles(self, is_gesture: bool) -> None:
        active   = "background-color: #2563eb; color: #ffffff; border-radius: 6px;"
        inactive = "background-color: transparent; color: #94a3b8; border-radius: 6px;"
        self._btn_gesture.setStyleSheet(active   if is_gesture else inactive)
        self._btn_manual.setStyleSheet (inactive if is_gesture else active)

    def paintEvent(self, event) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)


# ──────────────────────────────────────────────────────────────
class ControlView(QWidget):
    """
    Control page: 70% CameraView + 30% ControlPanel.

    Signals
    -------
    emergency_stop_triggered
    mode_changed(str)
    manual_command(str)
    speed_changed(int)
    sensitivity_changed(int)

    Public methods
    --------------
    start_camera() / stop_camera()
    update_gesture_display(gesture, command, confidence, stability)
    set_mode(mode: ControlMode)
    """

    emergency_stop_triggered = Signal()
    mode_changed             = Signal(str)
    manual_command           = Signal(str)
    speed_changed            = Signal(int)
    sensitivity_changed      = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("controlView")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Left: camera (70%)
        self._cam = _CameraContainer()
        layout.addWidget(self._cam, 7)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.VLine)
        div.setObjectName("controlDivider")
        layout.addWidget(div)

        # Right: control panel (30%)
        self._panel = _ControlPanel()
        layout.addWidget(self._panel, 3)

        # ── Forward panel signals ──────────────────────────────
        self._panel.emergency_stop_triggered.connect(self.emergency_stop_triggered)
        self._panel.mode_changed.connect(self.mode_changed)
        self._panel.manual_command.connect(self.manual_command)
        self._panel.speed_changed.connect(self.speed_changed)
        self._panel.sensitivity_changed.connect(self.sensitivity_changed)

    # ── Public API ─────────────────────────────────────────────

    def start_camera(self) -> None:
        self._cam.start()

    def stop_camera(self) -> None:
        self._cam.stop()

    def update_gesture_display(
        self,
        gesture:    str,
        command:    str,
        confidence: float,
        stability:  float,
    ) -> None:
        self._cam.update_overlay(gesture, command, confidence)
        self._panel.update_gesture_info(gesture, stability)

    def set_mode(self, mode: ControlMode) -> None:
        self._panel.set_mode(mode)

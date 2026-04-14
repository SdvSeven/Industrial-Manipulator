from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QFrame, QStyle, QStyleOption, QVBoxLayout, QLabel, QWidget

from models.system_state import SystemState, ControlMode


class SidebarInfoBlock(QFrame):
    """
    Real-time system info block for the sidebar bottom area.

    Displays: STATE / MODE / LAST COMMAND / FPS / LATENCY
    Call update_data() from MainWindow via QTimer (200 ms).
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebarBottomBlock")
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(3)

        self._rows: dict[str, QLabel] = {}
        for key in ("STATE", "MODE", "LAST CMD", "FPS", "LATENCY"):
            lbl = QLabel(self._format(key, "—"))
            lbl.setObjectName("sidebarInfoText")
            lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(lbl)
            self._rows[key] = lbl

        self._set_defaults()

    # ── Public API ─────────────────────────────────────────────

    def update_data(
        self,
        state:    SystemState,
        mode:     ControlMode,
        last_cmd: str,
        fps:      float,
        latency:  float,
    ) -> None:
        self._rows["STATE"].setText(self._format("STATE", state.value))
        self._rows["MODE"].setText(self._format("MODE", mode.value))
        self._rows["LAST CMD"].setText(self._format("LAST CMD", last_cmd or "—"))
        self._rows["FPS"].setText(self._format("FPS", f"{fps:.0f}"))
        self._rows["LATENCY"].setText(self._format("LATENCY", f"{latency:.0f} ms"))

        # Color STATE label
        colors = {
            SystemState.IDLE:       "#94a3b8",
            SystemState.CONNECTING: "#eab308",
            SystemState.RUNNING:    "#22c55e",
            SystemState.ERROR:      "#ef4444",
        }
        self._rows["STATE"].setStyleSheet(
            f"color: {colors.get(state, '#94a3b8')};"
            "background: transparent; font-family: monospace; font-size: 11px;"
        )

    # ── Helpers ────────────────────────────────────────────────

    @staticmethod
    def _format(key: str, value: str) -> str:
        return f"{key:<9}: {value}"

    def _set_defaults(self) -> None:
        self.update_data(SystemState.IDLE, ControlMode.GESTURE, "—", 0.0, 0.0)

    def paintEvent(self, event) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

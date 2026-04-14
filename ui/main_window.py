from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QMainWindow,
    QVBoxLayout, QWidget,
)

from services.app_state import AppState
from models.system_state import SystemState, ControlMode, StatusIndicator
from models.device_status import DeviceStatus
from ui.dialogs import LoginDialog, RegisterDialog
from ui.header import Header
from ui.sidebar import Sidebar
from ui.dashboard import Dashboard

# Pages that require authentication (§3.2)
_AUTH_REQUIRED: frozenset[str] = frozenset({"Управление", "Настройки", "Журнал"})

# Sidebar label → page key mapping
_NAV_MAP: dict[str, str] = {
    "Главная":    "main",
    "Управление": "control",
    "Настройки":  "settings",
    "Журнал":     "logs",
}


class MainWindow(QMainWindow):
    """
    Root window — 1920×1080.

    Responsibilities
    ----------------
    • Owns AppState.
    • Wires ALL signals in _connect_signals().
    • Drives state machine: IDLE → CONNECTING → RUNNING / ERROR.
    • Pushes state to UI via update_*_ui() methods.
    • Auth gating for protected sidebar items.
    • Metrics update timer (200 ms).
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Индустриальный Манипулятор")
        self.resize(1920, 1080)

        self._state       = AppState()
        self._pending_nav: str | None = None   # navigation target after login

        # ── Central widget ─────────────────────────────────────
        root = QWidget()
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.header    = Header()
        root_layout.addWidget(self.header)

        body        = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self.sidebar   = Sidebar()
        body_layout.addWidget(self.sidebar)

        self.dashboard = Dashboard()
        self.dashboard.bind_state(self._state)
        body_layout.addWidget(self.dashboard, 1)

        root_layout.addWidget(body, 1)

        # ── Metrics timer (200 ms) ─────────────────────────────
        self._metrics_timer = QTimer(self)
        self._metrics_timer.setInterval(200)
        self._metrics_timer.timeout.connect(self._update_sidebar_info)
        self._metrics_timer.start()

        # ── Wire everything ────────────────────────────────────
        self._connect_signals()

        # Initial UI sync
        self.update_auth_ui()
        self.update_system_ui()

    # ══════════════════════════════════════════════════════════
    # Signal wiring
    # ══════════════════════════════════════════════════════════

    def _connect_signals(self) -> None:
        # Header
        self.header.login_btn.clicked.connect(self._on_login_clicked)
        self.header.reg_btn.clicked.connect(self._on_register_clicked)
        self.header.logout_requested.connect(self._on_logout)

        # Home page
        self.dashboard.home.connect_image.clicked.connect(
            self._on_connect_clicked
        )

        # Sidebar navigation
        self.sidebar.item_clicked.connect(self._on_nav_item)

        # Control page signals
        ctrl = self.dashboard.control
        ctrl.emergency_stop_triggered.connect(self._on_emergency_stop)
        ctrl.mode_changed.connect(self._on_mode_changed)
        ctrl.manual_command.connect(self._on_manual_command)
        ctrl.speed_changed.connect(self._on_speed_changed)
        ctrl.sensitivity_changed.connect(self._on_sensitivity_changed)

        # CameraWorker signals are wired when camera starts (via ControlView)
        # We need to tap into the camera_view's worker.
        # CameraView exposes _worker — instead, we forward through ControlView.
        # ControlView._cam.camera_view is a CameraView; we wire on start.
        # To decouple this, we connect to ControlView's internal camera signals
        # by wrapping CameraView.start/stop in ControlView, which calls worker.
        # Solution: wire after camera starts via a direct connection on the view.
        self._wire_camera_signals()

    def _wire_camera_signals(self) -> None:
        """Wire CameraWorker signals via CameraView inside ControlView."""
        cam_view = self.dashboard.control._cam.camera_view

        # We intercept the worker by monkey-patching CameraView.start
        # to wire our slots after the worker is created.
        _original_start = cam_view.start

        def _patched_start():
            _original_start()
            w = cam_view._worker
            if w is not None:
                w.gesture_detected.connect(self._on_gesture_detected)
                w.metrics_updated.connect(self._on_metrics_updated)
                w.error_occurred.connect(self._on_camera_error)

        cam_view.start = _patched_start

    # ══════════════════════════════════════════════════════════
    # Navigation
    # ══════════════════════════════════════════════════════════

    def _on_nav_item(self, name: str) -> None:
        if name in _AUTH_REQUIRED and not self._state.is_authenticated:
            self._pending_nav = name
            dlg = LoginDialog(self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                login, _ = dlg.credentials()
                self._state.login(login)
                self.update_auth_ui()
                # Navigate to originally requested page
                target = self._pending_nav
                self._pending_nav = None
                self._do_navigate(name, target)
            else:
                # Restore previously active sidebar item
                self._pending_nav = None
                self.sidebar.set_active(
                    _page_to_nav_name(self.dashboard.current_page)
                )
            return

        self._do_navigate(name)

    def _do_navigate(self, nav_name: str, override: str | None = None) -> None:
        target = override or nav_name
        page = _NAV_MAP.get(target, "main")
        self.sidebar.set_active(target)
        self.setWindowTitle(f"Индустриальный Манипулятор — {target}")
        self.dashboard.show_page(page)

    # ══════════════════════════════════════════════════════════
    # Auth handlers
    # ══════════════════════════════════════════════════════════

    def _on_login_clicked(self) -> None:
        dlg = LoginDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            login, _ = dlg.credentials()
            self._state.login(login)
            self.update_auth_ui()

    def _on_register_clicked(self) -> None:
        dlg = RegisterDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, email = dlg.credentials()
            self._state.register(name, email)
            self.update_auth_ui()

    def _on_logout(self) -> None:
        # Emergency stop before logout for safety
        self._on_emergency_stop()
        self._state.logout()
        # Return to home
        self.dashboard.show_page("main")
        self.sidebar.set_active("Главная")
        self.setWindowTitle("Индустриальный Манипулятор")
        self.update_auth_ui()
        self.update_system_ui()

    # ══════════════════════════════════════════════════════════
    # Connection state machine
    # ══════════════════════════════════════════════════════════

    def _on_connect_clicked(self) -> None:
        state = self._state.system_state
        if state == SystemState.RUNNING:
            self._state.disconnect()
            self.update_system_ui()
        elif state in (SystemState.IDLE, SystemState.ERROR):
            self._state.start_connecting()
            self.update_system_ui()
            # Simulate device check (1.5 s) — replace with real hardware probe
            QTimer.singleShot(1500, self._finish_connecting)

    def _finish_connecting(self) -> None:
        # In production: probe cv2.VideoCapture + serial port here
        self._state.finish_connecting(success=True)
        self.update_system_ui()

    # ══════════════════════════════════════════════════════════
    # Control handlers
    # ══════════════════════════════════════════════════════════

    def _on_emergency_stop(self) -> None:
        # Stop camera immediately (no wait)
        cam_view = self.dashboard.control._cam.camera_view
        if cam_view._worker is not None:
            cam_view._worker.stop()
            cam_view._worker.deleteLater()
            cam_view._worker = None

        self._state.emergency_stop()
        self.update_system_ui()
        self._push_log_entry_to_view()

    def _on_mode_changed(self, mode_str: str) -> None:
        mode = ControlMode.GESTURE if mode_str == "GESTURE" else ControlMode.MANUAL
        self._state.control_mode = mode

    def _on_manual_command(self, command: str) -> None:
        self._state.on_manual_command(command)
        self._push_log_entry_to_view()

    def _on_speed_changed(self, value: int) -> None:
        self._state.speed = value

    def _on_sensitivity_changed(self, value: int) -> None:
        self._state.sensitivity = value

    # ══════════════════════════════════════════════════════════
    # Camera worker slots
    # ══════════════════════════════════════════════════════════

    def _on_gesture_detected(
        self, gesture: str, stability: float, confidence: float
    ) -> None:
        self._state.on_gesture(gesture, stability, confidence)
        command = self._state.last_command
        self.dashboard.control.update_gesture_display(
            gesture, command, confidence, stability
        )
        self._push_log_entry_to_view()

    def _on_metrics_updated(self, fps: float, latency_ms: float) -> None:
        self._state.on_metrics(fps, latency_ms)

    def _on_camera_error(self, msg: str) -> None:
        self._state.system_state = SystemState.ERROR
        self._state.devices.camera = StatusIndicator.ERROR
        self.update_system_ui()

    # ══════════════════════════════════════════════════════════
    # UI update methods  (state → UI)
    # ══════════════════════════════════════════════════════════

    def update_auth_ui(self) -> None:
        if self._state.is_authenticated:
            self.header.show_user(self._state.display_name)
        else:
            self.header.show_auth_buttons()
        self.sidebar.set_auth_state(self._state.is_authenticated)

    def update_system_ui(self) -> None:
        """Sync all state-dependent UI: home page + sidebar info."""
        s = self._state
        self.dashboard.home.update_state(s.system_state)
        self.dashboard.home.update_devices(s.devices)

    def _update_sidebar_info(self) -> None:
        """Called by 200 ms QTimer — updates SidebarInfoBlock."""
        s = self._state
        self.sidebar.info_block.update_data(
            s.system_state,
            s.control_mode,
            s.last_command,
            s.fps,
            s.latency_ms,
        )

    def _push_log_entry_to_view(self) -> None:
        """Forward the most recent log entry to LogsView."""
        entries = self._state.log_entries
        if entries:
            self.dashboard.logs.add_entry(entries[0])


# ── Helpers ────────────────────────────────────────────────────
def _page_to_nav_name(page: str) -> str:
    _inv = {v: k for k, v in _NAV_MAP.items()}
    return _inv.get(page, "Главная")

from __future__ import annotations

import hashlib
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime

from models.user import UserProfile
from models.system_state import SystemState, ControlMode, StatusIndicator
from models.device_status import DeviceStatus

_MAX_LOGIN_ATTEMPTS = 3

_DEFAULT_GESTURE_MAP: dict[str, str] = {
    "LEFT":  "MOVE_X -10",
    "RIGHT": "MOVE_X +10",
    "UP":    "MOVE_Y +10",
    "DOWN":  "MOVE_Y -10",
    "FIST":  "GRAB",
    "OPEN":  "RELEASE",
}


@dataclass
class AppState:
    """
    Single source of truth for all runtime state.

    Mutations go through business methods only.
    UI reads public fields and calls update_*_ui() in MainWindow.
    """

    # ── Auth ───────────────────────────────────────────────────
    is_authenticated: bool = False
    user: UserProfile = field(default_factory=UserProfile)

    # ── System ────────────────────────────────────────────────
    system_state: SystemState = field(default=SystemState.IDLE)
    control_mode: ControlMode = field(default=ControlMode.GESTURE)
    devices: DeviceStatus = field(default_factory=DeviceStatus)

    # ── Real-time metrics ─────────────────────────────────────
    last_command:       str   = "—"
    last_gesture:       str   = "—"
    fps:                float = 0.0
    latency_ms:         float = 0.0
    gesture_stability:  float = 0.0
    gesture_confidence: float = 0.0

    # ── Config ────────────────────────────────────────────────
    gesture_map: dict = field(
        default_factory=lambda: dict(_DEFAULT_GESTURE_MAP)
    )
    speed:       int = 50
    sensitivity: int = 50

    # ── Log ───────────────────────────────────────────────────
    log_entries: object = field(
        default_factory=lambda: deque(maxlen=1000)
    )

    # ── Credential store (login → sha256 hex digest) ──────────
    _credentials: dict = field(
        default_factory=dict, init=False, repr=False
    )
    _login_attempts: int = field(default=0, init=False, repr=False)

    # ══════════════════════════════════════════════════════════
    # Auth methods
    # ══════════════════════════════════════════════════════════

    def login(self, login: str, password: str) -> bool:
        """Verify credentials and authenticate.

        Returns True on success.  Returns False if credentials are wrong or
        the account is locked after _MAX_LOGIN_ATTEMPTS consecutive failures.
        """
        if self._login_attempts >= _MAX_LOGIN_ATTEMPTS:
            return False
        stored = self._credentials.get(login)
        if stored is None:
            self._login_attempts += 1
            return False
        pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if pw_hash != stored:
            self._login_attempts += 1
            return False
        self._login_attempts = 0
        self.user = UserProfile(name=login, login=login)
        self.is_authenticated = True
        return True

    def register(self, name: str, email: str, password: str) -> None:
        pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        self._credentials[email] = pw_hash
        self.user = UserProfile(name=name, email=email, login=email)
        self.is_authenticated = True

    @property
    def auth_attempts_left(self) -> int:
        return max(0, _MAX_LOGIN_ATTEMPTS - self._login_attempts)

    def logout(self) -> None:
        # BUG#3: do NOT call emergency_stop() here — MainWindow already does it
        self.user = UserProfile()
        self.is_authenticated = False

    # ══════════════════════════════════════════════════════════
    # Connection state machine
    # ══════════════════════════════════════════════════════════

    def start_connecting(self) -> None:
        if self.system_state in (SystemState.IDLE, SystemState.ERROR):
            self.system_state = SystemState.CONNECTING
            self.devices = DeviceStatus(
                arduino=StatusIndicator.INITIALIZING,
                camera=StatusIndicator.INITIALIZING,
                mediapipe=StatusIndicator.INITIALIZING,
                connection=StatusIndicator.INITIALIZING,
            )

    def finish_connecting(self, success: bool = True) -> None:
        if self.system_state != SystemState.CONNECTING:
            return
        if success:
            self.system_state = SystemState.RUNNING
            self.devices = DeviceStatus(
                arduino=StatusIndicator.OK,
                camera=StatusIndicator.OK,
                mediapipe=StatusIndicator.OK,
                connection=StatusIndicator.OK,
            )
        else:
            self.system_state = SystemState.ERROR
            self.devices = DeviceStatus(
                arduino=StatusIndicator.ERROR,
                camera=StatusIndicator.ERROR,
                mediapipe=StatusIndicator.ERROR,
                connection=StatusIndicator.ERROR,
            )

    def disconnect(self) -> None:
        if self.system_state == SystemState.RUNNING:
            self.system_state = SystemState.IDLE
            self.devices = DeviceStatus()
            self.fps = 0.0
            self.latency_ms = 0.0

    def emergency_stop(self) -> None:
        if self.system_state == SystemState.RUNNING:
            self.add_log("—", "EMERGENCY_STOP", "STOP")
        self.system_state = SystemState.IDLE
        self.last_command = "EMERGENCY_STOP"

    # ══════════════════════════════════════════════════════════
    # Real-time updates
    # ══════════════════════════════════════════════════════════

    def on_gesture(self, gesture: str, stability: float, confidence: float) -> None:
        """Called from MainWindow on CameraWorker.gesture_detected signal."""
        prev_gesture = self.last_gesture
        self.last_gesture = gesture
        self.gesture_stability = stability
        self.gesture_confidence = confidence
        if self.control_mode == ControlMode.GESTURE and gesture not in ("NONE", "—"):
            cmd = self.gesture_map.get(gesture, "—")
            self.last_command = cmd
            # BUG#5: only log when gesture changes to avoid flooding the log
            if gesture != prev_gesture:
                self.add_log(gesture, cmd, "OK")

    def on_manual_command(self, command: str) -> None:
        """Called when a manual control button is pressed."""
        self.last_command = command
        self.add_log("—", command, "MANUAL")

    def on_metrics(self, fps: float, latency_ms: float) -> None:
        self.fps = fps
        self.latency_ms = latency_ms

    def add_log(self, gesture: str, command: str, status: str) -> None:
        self.log_entries.appendleft({
            "time":    datetime.now().strftime("%H:%M:%S"),
            "gesture": gesture,
            "command": command,
            "status":  status,
        })

    # ══════════════════════════════════════════════════════════
    # Derived
    # ══════════════════════════════════════════════════════════

    @property
    def display_name(self) -> str:
        return self.user.display_name

    @property
    def is_running(self) -> bool:
        return self.system_state == SystemState.RUNNING

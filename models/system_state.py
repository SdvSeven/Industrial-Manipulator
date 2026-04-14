from enum import Enum


class SystemState(Enum):
    IDLE       = "IDLE"
    CONNECTING = "CONNECTING"
    RUNNING    = "RUNNING"
    ERROR      = "ERROR"


class ControlMode(Enum):
    GESTURE = "GESTURE"
    MANUAL  = "MANUAL"


class StatusIndicator(Enum):
    OK           = "ok"            # 🟢
    INITIALIZING = "initializing"  # 🟡
    ERROR        = "error"         # 🔴

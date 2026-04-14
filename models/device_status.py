from __future__ import annotations

from dataclasses import dataclass

from .system_state import StatusIndicator


@dataclass
class DeviceStatus:
    arduino:    StatusIndicator = StatusIndicator.ERROR
    camera:     StatusIndicator = StatusIndicator.ERROR
    mediapipe:  StatusIndicator = StatusIndicator.ERROR
    connection: StatusIndicator = StatusIndicator.ERROR

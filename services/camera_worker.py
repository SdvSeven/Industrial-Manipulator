from __future__ import annotations

import time
from collections import deque

import cv2
import mediapipe as mp

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

# ── Mediapipe setup ────────────────────────────────────────────
_mp_hands       = mp.solutions.hands
_mp_draw        = mp.solutions.drawing_utils
_mp_draw_styles = mp.solutions.drawing_styles


# ── Gesture stability tracker ──────────────────────────────────
class _GestureTracker:
    """Rolling window stability: fraction of last N frames with same gesture."""

    def __init__(self, window: int = 15) -> None:
        self._history: deque[str] = deque(maxlen=window)

    def update(self, gesture: str) -> float:
        self._history.append(gesture)
        if gesture == "NONE":
            return 0.0
        count = sum(1 for g in self._history if g == gesture)
        return count / len(self._history)

    def reset(self) -> None:
        self._history.clear()


# ── Gesture classifier ─────────────────────────────────────────
def _classify_gesture(hand_lm) -> tuple[str, float]:
    """
    Classify gesture from MediaPipe landmarks.
    Returns (gesture_name, confidence).
    Supported: FIST | OPEN | LEFT | RIGHT | UP | DOWN | NONE
    """
    lm = hand_lm.landmark

    tips = [8, 12, 16, 20]   # index, middle, ring, pinky tips
    pips = [6, 10, 14, 18]   # corresponding PIP joints

    fingers_up = [lm[t].y < lm[p].y for t, p in zip(tips, pips)]
    up_count = sum(fingers_up)

    if up_count == 0:
        return "FIST", 0.90
    if up_count >= 3:
        return "OPEN", 0.90

    # Directional: hand center vs image center
    wrist   = lm[0]
    mid_mcp = lm[9]
    hand_x  = (wrist.x + mid_mcp.x) / 2
    hand_y  = (wrist.y + mid_mcp.y) / 2
    dx = hand_x - 0.5
    dy = hand_y - 0.5

    if abs(dx) > abs(dy) and abs(dx) > 0.05:
        return ("RIGHT" if dx > 0 else "LEFT"), 0.78
    if abs(dy) > abs(dx) and abs(dy) > 0.05:
        return ("DOWN" if dy > 0 else "UP"), 0.78

    return "NONE", 0.50


# ── Worker ─────────────────────────────────────────────────────
class CameraWorker(QThread):
    """
    Background thread: captures frames → MediaPipe hands →
    emits QImage, gesture data, and performance metrics.

    Signals
    -------
    frame_ready(QImage)
    hand_count_changed(int)
    gesture_detected(str, float, float)  — name, stability, confidence
    metrics_updated(float, float)        — fps, latency_ms
    error_occurred(str)                  — human-readable error
    """

    frame_ready        = Signal(QImage)
    hand_count_changed = Signal(int)
    gesture_detected   = Signal(str, float, float)
    metrics_updated    = Signal(float, float)
    error_occurred     = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._running = False
        self._last_hand_count = -1
        self._tracker = _GestureTracker(window=15)

    def stop(self) -> None:
        self._running = False

    def run(self) -> None:
        self._running = True
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            self.error_occurred.emit("Камера не найдена (index 0)")
            self._running = False
            return

        hands = _mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
        )

        frame_times: deque[float] = deque(maxlen=30)

        try:
            while self._running:
                t0 = time.monotonic()

                ok, frame = cap.read()
                if not ok:
                    self.msleep(30)
                    continue

                frame = cv2.flip(frame, 1)
                h, w = frame.shape[:2]

                rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb)

                if not self._running:
                    break

                # ── Landmarks + gesture ────────────────────────
                hand_count = 0
                gesture    = "NONE"
                confidence = 0.0

                if results.multi_hand_landmarks:
                    hand_count = len(results.multi_hand_landmarks)
                    for hand_lm in results.multi_hand_landmarks:
                        _mp_draw.draw_landmarks(
                            rgb, hand_lm,
                            _mp_hands.HAND_CONNECTIONS,
                            _mp_draw_styles.get_default_hand_landmarks_style(),
                            _mp_draw_styles.get_default_hand_connections_style(),
                        )
                    gesture, confidence = _classify_gesture(
                        results.multi_hand_landmarks[0]
                    )

                if hand_count != self._last_hand_count:
                    self._last_hand_count = hand_count
                    self.hand_count_changed.emit(hand_count)

                stability = self._tracker.update(gesture)
                if gesture != "NONE":
                    self.gesture_detected.emit(gesture, stability, confidence)

                # ── Metrics ────────────────────────────────────
                t1 = time.monotonic()
                frame_times.append(t1)
                fps = (
                    (len(frame_times) - 1) / (frame_times[-1] - frame_times[0])
                    if len(frame_times) >= 2 else 0.0
                )
                self.metrics_updated.emit(fps, (t1 - t0) * 1000)

                # ── Frame ──────────────────────────────────────
                qimg = QImage(
                    rgb.data, w, h, w * 3,
                    QImage.Format.Format_RGB888,
                ).copy()
                self.frame_ready.emit(qimg)

        finally:
            self._tracker.reset()
            hands.close()
            cap.release()

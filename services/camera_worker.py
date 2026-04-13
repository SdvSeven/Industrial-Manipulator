from __future__ import annotations

import cv2
import mediapipe as mp
import numpy as np

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

# ── Mediapipe setup (module-level, shared across instances) ───
_mp_hands = mp.solutions.hands
_mp_draw = mp.solutions.drawing_utils
_mp_draw_styles = mp.solutions.drawing_styles


class CameraWorker(QThread):
    """
    Background thread: captures frames from the default camera,
    runs mediapipe hand detection, draws landmarks, emits QImage.

    Usage
    -----
    worker = CameraWorker()
    worker.frame_ready.connect(my_slot)
    worker.start()
    ...
    worker.stop()
    worker.wait()
    """

    frame_ready = Signal(QImage)
    hand_count_changed = Signal(int)   # 0, 1, or 2 hands detected

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._running = False
        self._last_hand_count = -1

    # ── Public ─────────────────────────────────────────────────

    def stop(self) -> None:
        self._running = False

    # ── Thread entry point ─────────────────────────────────────

    def run(self) -> None:
        self._running = True
        cap = cv2.VideoCapture(0)

        hands = _mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
        )

        if not cap.isOpened():
            self._running = False

        try:
            while self._running:
                ok, frame = cap.read()
                if not ok:
                    self.msleep(30)   # brief back-off, avoid spin on bad frames
                    continue

                # Mirror horizontally for natural interaction
                frame = cv2.flip(frame, 1)
                h, w = frame.shape[:2]

                # mediapipe requires RGB
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb)

                # ── Draw landmarks ─────────────────────────────
                hand_count = 0
                if results.multi_hand_landmarks:
                    hand_count = len(results.multi_hand_landmarks)
                    for hand_lm in results.multi_hand_landmarks:
                        _mp_draw.draw_landmarks(
                            rgb,
                            hand_lm,
                            _mp_hands.HAND_CONNECTIONS,
                            _mp_draw_styles.get_default_hand_landmarks_style(),
                            _mp_draw_styles.get_default_hand_connections_style(),
                        )

                # Emit hand count change
                if hand_count != self._last_hand_count:
                    self._last_hand_count = hand_count
                    self.hand_count_changed.emit(hand_count)

                # ── Convert to QImage ──────────────────────────
                qimg = QImage(
                    rgb.data,
                    w, h,
                    w * 3,
                    QImage.Format.Format_RGB888,
                ).copy()   # .copy() detaches from numpy buffer

                self.frame_ready.emit(qimg)

        finally:
            hands.close()
            cap.release()

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFrame, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QHeaderView,
)

from services.app_state import AppState

_GESTURE_ROWS = ["LEFT", "RIGHT", "UP", "DOWN", "FIST", "OPEN"]


class SettingsView(QWidget):
    """
    Settings page with 3 blocks:
      1. Arduino (COM port, baudrate, auto-connect)
      2. Camera (index, resolution)
      3. Gesture Mapping (editable table)

    Call bind_state(AppState) after creation to sync with AppState.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("settingsView")
        self._state: AppState | None = None

        # Scroll container
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container.setObjectName("settingsContainer")
        v = QVBoxLayout(container)
        v.setContentsMargins(40, 32, 40, 32)
        v.setSpacing(24)

        page_title = QLabel("Настройки")
        page_title.setObjectName("pageTitle")
        v.addWidget(page_title)

        v.addWidget(self._build_arduino_block())
        v.addWidget(self._build_camera_block())
        v.addWidget(self._build_gesture_block())
        v.addStretch(1)

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # ── Public API ─────────────────────────────────────────────

    def bind_state(self, state: AppState) -> None:
        self._state = state
        self._load_gesture_map(state.gesture_map)

    # ── Block builders ─────────────────────────────────────────

    def _build_arduino_block(self) -> QGroupBox:
        box = QGroupBox("Arduino")
        box.setObjectName("settingsGroup")
        v = QVBoxLayout(box)
        v.setSpacing(12)

        # COM port
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("COM порт:"))
        row1.addStretch()
        self._com_combo = QComboBox()
        self._com_combo.setObjectName("settingsCombo")
        self._com_combo.addItems(["COM1", "COM3", "COM4", "COM5"])
        self._com_combo.setCurrentText("COM3")
        self._com_combo.setMinimumWidth(120)
        row1.addWidget(self._com_combo)
        v.addLayout(row1)

        # Baudrate
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Baudrate:"))
        row2.addStretch()
        self._baudrate_edit = QLineEdit("115200")
        self._baudrate_edit.setObjectName("settingsInput")
        self._baudrate_edit.setMaximumWidth(120)
        row2.addWidget(self._baudrate_edit)
        v.addLayout(row2)

        # Auto-connect
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Auto-connect:"))
        row3.addStretch()
        self._autoconnect_cb = QCheckBox()
        self._autoconnect_cb.setObjectName("settingsCheckbox")
        row3.addWidget(self._autoconnect_cb)
        v.addLayout(row3)

        return box

    def _build_camera_block(self) -> QGroupBox:
        box = QGroupBox("Камера")
        box.setObjectName("settingsGroup")
        v = QVBoxLayout(box)
        v.setSpacing(12)

        # Camera index
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Camera index:"))
        row1.addStretch()
        self._cam_index_combo = QComboBox()
        self._cam_index_combo.setObjectName("settingsCombo")
        self._cam_index_combo.addItems(["0", "1", "2"])
        self._cam_index_combo.setMinimumWidth(80)
        row1.addWidget(self._cam_index_combo)
        v.addLayout(row1)

        # Resolution
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Resolution:"))
        row2.addStretch()
        self._res_combo = QComboBox()
        self._res_combo.setObjectName("settingsCombo")
        self._res_combo.addItems(["640×480", "1280×720"])
        self._res_combo.setMinimumWidth(120)
        row2.addWidget(self._res_combo)
        v.addLayout(row2)

        return box

    def _build_gesture_block(self) -> QGroupBox:
        box = QGroupBox("Gesture Mapping")
        box.setObjectName("settingsGroup")
        v = QVBoxLayout(box)
        v.setSpacing(12)

        hint = QLabel("Редактируйте поле Command и нажмите «Сохранить».")
        hint.setObjectName("settingsHint")
        v.addWidget(hint)

        self._gesture_table = QTableWidget(len(_GESTURE_ROWS), 2)
        self._gesture_table.setObjectName("gestureTable")
        self._gesture_table.setHorizontalHeaderLabels(["Gesture", "Command"])
        self._gesture_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self._gesture_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._gesture_table.verticalHeader().hide()
        self._gesture_table.setSelectionMode(
            QTableWidget.SelectionMode.NoSelection
        )
        self._gesture_table.setEditTriggers(
            QTableWidget.EditTrigger.DoubleClicked |
            QTableWidget.EditTrigger.SelectedClicked
        )

        for row, gesture in enumerate(_GESTURE_ROWS):
            # Gesture column — read only
            g_item = QTableWidgetItem(gesture)
            g_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self._gesture_table.setItem(row, 0, g_item)
            # Command column — editable
            self._gesture_table.setItem(row, 1, QTableWidgetItem("—"))

        v.addWidget(self._gesture_table)

        # Save / Reset buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        reset_btn = QPushButton("Сбросить к defaults")
        reset_btn.setObjectName("settingsSecondaryBtn")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self._on_reset)
        btn_row.addWidget(reset_btn)

        save_btn = QPushButton("Сохранить")
        save_btn.setObjectName("settingsPrimaryBtn")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)
        v.addLayout(btn_row)

        return box

    # ── Gesture map sync ───────────────────────────────────────

    def _load_gesture_map(self, mapping: dict[str, str]) -> None:
        for row, gesture in enumerate(_GESTURE_ROWS):
            cmd = mapping.get(gesture, "—")
            self._gesture_table.item(row, 1).setText(cmd)

    def _on_save(self) -> None:
        if self._state is None:
            return
        for row, gesture in enumerate(_GESTURE_ROWS):
            cmd = self._gesture_table.item(row, 1).text().strip()
            if cmd:
                self._state.gesture_map[gesture] = cmd

    def _on_reset(self) -> None:
        from services.app_state import _DEFAULT_GESTURE_MAP
        if self._state is not None:
            self._state.gesture_map = dict(_DEFAULT_GESTURE_MAP)
        self._load_gesture_map(
            self._state.gesture_map if self._state else {}
        )

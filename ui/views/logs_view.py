from __future__ import annotations

import csv

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QFileDialog,
    QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

_COLUMNS = ("Time", "Gesture", "Command", "Status")
_STATUS_COLORS = {
    "OK":     "#22c55e",
    "MANUAL": "#60a5fa",
    "STOP":   "#ef4444",
    "ERROR":  "#ef4444",
}


class LogsView(QWidget):
    """
    Logs page: event table with time/command filters and Clear/Export CSV.

    Public methods
    --------------
    add_entry(entry: dict)   — dict with keys: time, gesture, command, status
    clear_all()
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("logsView")

        self._all_entries: list[dict] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(40, 32, 40, 24)
        root.setSpacing(16)

        # ── Page title ─────────────────────────────────────────
        page_title = QLabel("Журнал событий")
        page_title.setObjectName("pageTitle")
        root.addWidget(page_title)

        # ── Filter bar ─────────────────────────────────────────
        root.addWidget(self._build_filter_bar())

        # ── Table ──────────────────────────────────────────────
        self._table = QTableWidget(0, len(_COLUMNS))
        self._table.setObjectName("logTable")
        self._table.setHorizontalHeaderLabels(list(_COLUMNS))
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._table.verticalHeader().hide()
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self._table.setAlternatingRowColors(True)
        root.addWidget(self._table, 1)

        # ── Action buttons ─────────────────────────────────────
        root.addWidget(self._build_action_bar())

    # ── Public API ─────────────────────────────────────────────

    def bind_log_entries(self, entries) -> None:
        """Share the AppState log deque so there is a single source of truth.

        Call this once from Dashboard.bind_state() before any entries arrive.
        """
        self._all_entries = entries

    def add_entry(self, entry: dict) -> None:
        """Notify the view that a new entry was appended to the shared deque.

        The entry is already stored in AppState.log_entries; we only update
        the table display here.
        """
        if self._entry_passes_filter(entry):
            self._insert_table_row(0, entry)

    def clear_all(self) -> None:
        self._all_entries.clear()
        self._table.setRowCount(0)

    # ── Filter bar builder ─────────────────────────────────────

    def _build_filter_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("filterBar")
        h = QHBoxLayout(bar)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(12)

        h.addWidget(QLabel("Команда:"))
        self._cmd_filter = QComboBox()
        self._cmd_filter.setObjectName("filterCombo")
        self._cmd_filter.addItems([
            "Все", "MOVE_X -10", "MOVE_X +10", "MOVE_Y +10",
            "MOVE_Y -10", "GRAB", "RELEASE", "EMERGENCY_STOP",
        ])
        self._cmd_filter.currentTextChanged.connect(self._apply_filter)
        h.addWidget(self._cmd_filter)

        h.addSpacing(16)
        h.addWidget(QLabel("Статус:"))
        self._status_filter = QComboBox()
        self._status_filter.setObjectName("filterCombo")
        self._status_filter.addItems(["Все", "OK", "MANUAL", "STOP", "ERROR"])
        self._status_filter.currentTextChanged.connect(self._apply_filter)
        h.addWidget(self._status_filter)

        h.addStretch(1)
        return bar

    def _build_action_bar(self) -> QWidget:
        bar = QWidget()
        h = QHBoxLayout(bar)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(12)
        h.addStretch(1)

        clear_btn = QPushButton("Очистить")
        clear_btn.setObjectName("logClearBtn")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self.clear_all)
        h.addWidget(clear_btn)

        export_btn = QPushButton("Экспорт CSV")
        export_btn.setObjectName("logExportBtn")
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.clicked.connect(self._on_export_csv)
        h.addWidget(export_btn)

        return bar

    # ── Filter logic ───────────────────────────────────────────

    def _apply_filter(self) -> None:
        self._table.setRowCount(0)
        for entry in self._all_entries:
            if self._entry_passes_filter(entry):
                self._insert_table_row(self._table.rowCount(), entry)

    def _entry_passes_filter(self, entry: dict) -> bool:
        cmd_filter    = self._cmd_filter.currentText()
        status_filter = self._status_filter.currentText()
        if cmd_filter != "Все" and entry.get("command") != cmd_filter:
            return False
        if status_filter != "Все" and entry.get("status") != status_filter:
            return False
        return True

    def _insert_table_row(self, position: int, entry: dict) -> None:
        self._table.insertRow(position)
        values = [
            entry.get("time", ""),
            entry.get("gesture", ""),
            entry.get("command", ""),
            entry.get("status", ""),
        ]
        for col, val in enumerate(values):
            item = QTableWidgetItem(val)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if col == 3:   # status column — colored
                color = _STATUS_COLORS.get(val, "#e2e8f0")
                item.setForeground(Qt.GlobalColor.white)
                from PySide6.QtGui import QColor
                item.setBackground(QColor(color).darker(200))
            self._table.setItem(position, col, item)

    # ── CSV export ─────────────────────────────────────────────

    @staticmethod
    def _sanitize_csv_value(val: str) -> str:
        """Prefix formula-injection characters to neutralise CSV injection."""
        if val and val[0] in ("=", "+", "-", "@", "\t", "\r"):
            return "'" + val
        return val

    def _on_export_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт журнала", "logs_export.csv",
            "CSV files (*.csv)"
        )
        if not path:
            return
        # Enforce .csv extension regardless of what the dialog returned
        if not path.lower().endswith(".csv"):
            path += ".csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["time", "gesture", "command", "status"]
            )
            writer.writeheader()
            for entry in self._all_entries:
                writer.writerow({
                    k: self._sanitize_csv_value(str(v))
                    for k, v in entry.items()
                })

"""
Dialogs — frameless glass cards centered over a dimmed backdrop.

Layout: every dialog is QDialog → QVBoxLayout (0 margins) → GlassDialogCard
with its own QVBoxLayout (32px margins, explicit spacing). No absolute coords.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget,
)

from components import (
    Field, GhostButton, GlassDialogCard, PrimaryButton,
    dialog_body, field_label,
)
from data import validate_registration


# ─────────── Base ───────────

class BaseDialog(QDialog):
    def __init__(self, title_text: str, parent=None, width: int = 460):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setAlignment(Qt.AlignCenter)

        self._card = GlassDialogCard()
        self._card.setFixedWidth(width)
        outer.addWidget(self._card)

        self._lay = QVBoxLayout(self._card)
        self._lay.setContentsMargins(36, 32, 36, 32)
        self._lay.setSpacing(0)

        # Header row
        t = QLabel(title_text)
        t.setObjectName("title")

        close = GhostButton("✕")
        close.setFixedSize(38, 38)
        close.setStyleSheet(
            "QPushButton#ghost { padding: 0; min-height: 38px; font-size: 16px; }"
        )
        close.clicked.connect(self.reject)

        hdr = QHBoxLayout()
        hdr.setSpacing(12)
        hdr.addWidget(t)
        hdr.addStretch(1)
        hdr.addWidget(close)
        self._lay.addLayout(hdr)
        self._lay.addSpacing(24)

    def _add_field(self, label_text: str, field: Field):
        self._lay.addWidget(field_label(label_text))
        self._lay.addSpacing(6)
        self._lay.addWidget(field)
        self._lay.addSpacing(16)

    def _make_error(self) -> QLabel:
        lbl = QLabel("")
        lbl.setObjectName("errorMsg")
        lbl.setWordWrap(True)
        lbl.hide()
        return lbl

    def _show_error(self, lbl: QLabel, msg: str):
        lbl.setText(msg)
        lbl.show()

    def _actions(self, *buttons) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)
        row.addStretch(1)
        for b in buttons:
            row.addWidget(b)
        return row


# ─────────── Login ───────────

class LoginDialog(BaseDialog):
    authenticated = Signal(str)

    def __init__(self, parent=None):
        super().__init__("Вход", parent, width=440)
        self._build()

    def _build(self):
        self._lay.addWidget(dialog_body("Введите логин и пароль для доступа к системе"))
        self._lay.addSpacing(24)

        self._login = Field("Логин")
        self._pass = Field("Пароль", password=True)
        self._add_field("ЛОГИН", self._login)
        self._add_field("ПАРОЛЬ", self._pass)

        self._err = self._make_error()
        self._lay.addWidget(self._err)
        self._lay.addSpacing(16)

        cancel = GhostButton("Отмена")
        cancel.clicked.connect(self.reject)
        ok = PrimaryButton("Войти")
        ok.setMinimumWidth(120)
        ok.clicked.connect(self._submit)
        self._lay.addLayout(self._actions(cancel, ok))

    def _submit(self):
        login = self._login.text().strip()
        pw = self._pass.text().strip()
        if not login or not pw:
            self._show_error(self._err, "Пожалуйста, заполните все поля.")
            return
        # Stub auth — replace with real check
        self.authenticated.emit("Алексей Петров")
        self.accept()


# ─────────── Register ───────────

class RegisterDialog(BaseDialog):
    registered = Signal(str, str, str, str)

    def __init__(self, parent=None):
        super().__init__("Регистрация", parent, width=500)
        self._build()

    def _build(self):
        self._lay.addWidget(dialog_body("Создайте аккаунт для доступа к системе"))
        self._lay.addSpacing(20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setMaximumHeight(360)

        form = QWidget()
        form_lay = QVBoxLayout(form)
        form_lay.setContentsMargins(0, 0, 10, 0)
        form_lay.setSpacing(0)

        def add_row(lbl_text, field):
            form_lay.addWidget(field_label(lbl_text))
            form_lay.addSpacing(6)
            form_lay.addWidget(field)
            form_lay.addSpacing(16)

        self._fname = Field("Фамилия Имя Отчество")
        self._org = Field("Организация и филиал")
        self._email = Field("user@example.com")
        self._phone = Field("+7 (___) ___-__-__")
        self._phone.setInputMask("+7 (000) 000-00-00;_")
        self._ulogin = Field("Придумайте логин")
        self._pw = Field("Минимум 6 символов", password=True)
        self._pw2 = Field("Повторите пароль", password=True)

        add_row("ФИО", self._fname)
        add_row("ОРГАНИЗАЦИЯ", self._org)
        add_row("EMAIL", self._email)
        add_row("ТЕЛЕФОН", self._phone)
        add_row("ЛОГИН", self._ulogin)
        add_row("ПАРОЛЬ", self._pw)
        add_row("ПОДТВЕРЖДЕНИЕ", self._pw2)

        scroll.setWidget(form)
        self._lay.addWidget(scroll)

        self._agree = QCheckBox("Принимаю пользовательское соглашение")
        self._lay.addSpacing(16)
        self._lay.addWidget(self._agree)
        self._lay.addSpacing(12)

        self._err = self._make_error()
        self._lay.addWidget(self._err)
        self._lay.addSpacing(16)

        cancel = GhostButton("Отмена")
        cancel.clicked.connect(self.reject)
        ok = PrimaryButton("Зарегистрироваться")
        ok.clicked.connect(self._submit)
        self._lay.addLayout(self._actions(cancel, ok))

    def _submit(self):
        if not self._agree.isChecked():
            self._show_error(self._err, "Необходимо принять соглашение.")
            return
        valid, msg = validate_registration(
            self._fname.text().strip(), self._org.text().strip(),
            self._email.text().strip(), self._phone.text().strip(),
            self._ulogin.text().strip(), self._pw.text().strip(),
            self._pw2.text().strip(),
        )
        if not valid:
            self._show_error(self._err, msg)
            return
        self.registered.emit(
            self._fname.text().strip(), self._org.text().strip(),
            self._email.text().strip(), self._phone.text().strip(),
        )
        self.accept()


# ─────────── Info ───────────

class InfoDialog(BaseDialog):
    def __init__(self, title: str, text: str, parent=None):
        super().__init__(title, parent, width=480)
        self._lay.addWidget(dialog_body(text))
        self._lay.addSpacing(24)

        ok = PrimaryButton("Закрыть")
        ok.setMinimumWidth(120)
        ok.clicked.connect(self.accept)
        self._lay.addLayout(self._actions(ok))

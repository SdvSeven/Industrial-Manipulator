from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class _BaseAuthDialog(QDialog):
    """Shared structure for Login and Register dialogs."""

    _TITLE: str = ""
    _SUBMIT_LABEL: str = "Подтвердить"
    _WIDTH: int = 400
    _HEIGHT: int = 340

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(self._TITLE)
        self.setModal(True)
        self.setFixedSize(self._WIDTH, self._HEIGHT)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(32, 32, 32, 32)
        self._layout.setSpacing(0)

        # ── Heading ───────────────────────────────────────────
        heading = QLabel(self._TITLE)
        heading.setObjectName("dialogTitle")
        self._layout.addWidget(heading)
        self._layout.addSpacing(24)

        # ── Form fields (filled by subclass) ──────────────────
        self._build_form()

        # ── Error message ─────────────────────────────────────
        self._error_lbl = QLabel()
        self._error_lbl.setObjectName("formErrorLabel")
        self._error_lbl.setWordWrap(True)
        self._error_lbl.hide()
        self._layout.addSpacing(4)
        self._layout.addWidget(self._error_lbl)
        self._layout.addSpacing(16)

        # ── Action buttons ────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        cancel = QPushButton("Отмена")
        cancel.setObjectName("dialogCancelBtn")
        cancel.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)

        submit = QPushButton(self._SUBMIT_LABEL)
        submit.setObjectName("dialogSubmitBtn")
        submit.setCursor(Qt.CursorShape.PointingHandCursor)
        submit.clicked.connect(self._on_submit)
        btn_row.addWidget(submit)

        self._layout.addLayout(btn_row)

    # ── Helper: add a labelled text field ─────────────────────
    def _add_field(
        self,
        label_text: str,
        placeholder: str = "",
        *,
        password: bool = False,
    ) -> QLineEdit:
        lbl = QLabel(label_text)
        lbl.setObjectName("formLabel")
        self._layout.addWidget(lbl)
        self._layout.addSpacing(6)

        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        if password:
            edit.setEchoMode(QLineEdit.EchoMode.Password)
        edit.returnPressed.connect(self._on_submit)
        self._layout.addWidget(edit)
        self._layout.addSpacing(14)
        return edit

    def _show_error(self, msg: str) -> None:
        self._error_lbl.setText(msg)
        self._error_lbl.show()

    def _clear_error(self) -> None:
        self._error_lbl.setText("")
        self._error_lbl.hide()

    # ── Subclass responsibilities ──────────────────────────────
    def _build_form(self) -> None:
        raise NotImplementedError

    def _on_submit(self) -> None:
        raise NotImplementedError


# ──────────────────────────────────────────────────────────────
class LoginDialog(_BaseAuthDialog):
    _TITLE = "Вход в систему"
    _SUBMIT_LABEL = "Войти"
    _HEIGHT = 310

    def _build_form(self) -> None:
        self._login_edit = self._add_field("Логин", "Введите логин")
        self._pwd_edit = self._add_field("Пароль", "Введите пароль", password=True)

    def _on_submit(self) -> None:
        self._clear_error()
        if not self._login_edit.text().strip() or not self._pwd_edit.text():
            self._show_error("Заполните все поля")
            return
        self.accept()

    def credentials(self) -> tuple[str, str]:
        return self._login_edit.text().strip(), self._pwd_edit.text()


# ──────────────────────────────────────────────────────────────
class RegisterDialog(_BaseAuthDialog):
    _TITLE = "Регистрация"
    _SUBMIT_LABEL = "Зарегистрироваться"
    _HEIGHT = 470

    def _build_form(self) -> None:
        self._name_edit = self._add_field("Имя", "Иван Иванов")
        self._email_edit = self._add_field("Email", "user@example.com")
        self._pwd_edit = self._add_field(
            "Пароль", "Минимум 6 символов", password=True
        )
        self._confirm_edit = self._add_field(
            "Подтвердите пароль", "Повторите пароль", password=True
        )

    def _on_submit(self) -> None:
        self._clear_error()
        name = self._name_edit.text().strip()
        email = self._email_edit.text().strip()
        pwd = self._pwd_edit.text()
        confirm = self._confirm_edit.text()

        if not all([name, email, pwd, confirm]):
            self._show_error("Заполните все поля")
            return
        if "@" not in email or "." not in email.split("@")[-1]:
            self._show_error("Некорректный email")
            return
        if len(pwd) < 6:
            self._show_error("Пароль: минимум 6 символов")
            return
        if pwd != confirm:
            self._show_error("Пароли не совпадают")
            return
        self.accept()

    def credentials(self) -> tuple[str, str]:
        """Return (name, email) for the AppState.register() call."""
        return self._name_edit.text().strip(), self._email_edit.text().strip()

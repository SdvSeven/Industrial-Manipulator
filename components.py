"""Primitive widgets: glass surfaces, buttons, inputs, logo."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame, QGraphicsDropShadowEffect, QLabel, QLineEdit, QPushButton, QSizePolicy,
)


def _shadow(blur=48, dy=16, alpha=55):
    e = QGraphicsDropShadowEffect()
    e.setBlurRadius(blur)
    e.setOffset(0, dy)
    e.setColor(QColor(15, 23, 42, alpha))
    return e


# ─────────── Glass surfaces ───────────

class GlassPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glass")
        self.setGraphicsEffect(_shadow(40, 12, 40))


class GlassCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glassCard")
        self.setGraphicsEffect(_shadow(70, 24, 70))


class GlassSidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glassSidebar")
        self.setGraphicsEffect(_shadow(60, 20, 80))


class GlassDialogCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glassDialog")
        self.setGraphicsEffect(_shadow(80, 28, 90))


# ─────────── Buttons ───────────

class BurgerButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("☰", parent)
        self.setObjectName("burger")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(44, 44)


class GhostButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("ghost")
        self.setCursor(Qt.PointingHandCursor)


class PrimaryButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("primary")
        self.setCursor(Qt.PointingHandCursor)


class ConnectButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("Подключиться", parent)
        self.setObjectName("connect")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(56)
        self.setMinimumWidth(280)
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(48)
        glow.setOffset(0, 16)
        glow.setColor(QColor(99, 102, 241, 110))
        self.setGraphicsEffect(glow)


class MenuItemButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("menuItem")
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


# ─────────── Atoms ───────────

class UserChip(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("userChip")
        self.setAlignment(Qt.AlignCenter)


class LogoBadge(QLabel):
    """Circular glass badge fallback when no logo file is provided."""
    def __init__(self, parent=None):
        super().__init__("◈", parent)
        self.setObjectName("logoBadge")
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(120, 120)
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(40)
        glow.setOffset(0, 12)
        glow.setColor(QColor(99, 102, 241, 70))
        self.setGraphicsEffect(glow)


class Field(QLineEdit):
    def __init__(self, placeholder: str = "", password: bool = False, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(44)
        if password:
            self.setEchoMode(QLineEdit.EchoMode.Password)


# ─────────── Labels ───────────

def title(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("title")
    return lbl


def subtitle(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("subtitle")
    lbl.setWordWrap(True)
    return lbl


def field_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("fieldLabel")
    return lbl


def dialog_body(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("dialogBody")
    lbl.setWordWrap(True)
    return lbl

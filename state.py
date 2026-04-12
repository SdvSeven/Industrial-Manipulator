from PySide6.QtCore import QObject, Signal
from data import UserProfile


class AppState(QObject):
    userChanged = Signal()

    def __init__(self):
        super().__init__()
        self.user = UserProfile()

    def login(self, full_name: str, org: str = "", email: str = "", phone: str = ""):
        self.user = UserProfile(
            full_name=full_name, organization=org,
            email=email, phone=phone, is_authenticated=True,
        )
        self.userChanged.emit()

    def register(self, full_name: str, org: str, email: str, phone: str):
        self.login(full_name, org, email, phone)

    def logout(self):
        self.user = UserProfile()
        self.userChanged.emit()

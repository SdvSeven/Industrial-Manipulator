from __future__ import annotations

from dataclasses import dataclass, field

from models.user import UserProfile


@dataclass
class AppState:
    """
    Single source of truth for runtime application state.

    All mutations go through the business methods below so that
    MainWindow never manipulates raw fields directly.
    """

    is_connected: bool = False
    is_authenticated: bool = False
    user: UserProfile = field(default_factory=UserProfile)

    # ── Business methods ───────────────────────────────────────

    def login(self, login: str, name: str = "") -> None:
        self.user = UserProfile(name=name or login, login=login)
        self.is_authenticated = True

    def register(self, name: str, email: str) -> None:
        self.user = UserProfile(name=name, email=email, login=email)
        self.is_authenticated = True

    def logout(self) -> None:
        self.user = UserProfile()
        self.is_authenticated = False

    def toggle_connection(self) -> bool:
        """Flip connection state; return the new value."""
        self.is_connected = not self.is_connected
        return self.is_connected

    # ── Derived properties ─────────────────────────────────────

    @property
    def display_name(self) -> str:
        return self.user.display_name

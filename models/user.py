from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UserProfile:
    """Immutable-ish value object for an authenticated user."""

    name: str = ""
    login: str = ""
    email: str = ""

    # ── Validation helpers ─────────────────────────────────────

    @staticmethod
    def validate_email(email: str) -> bool:
        parts = email.strip().split("@")
        return len(parts) == 2 and "." in parts[1]

    @staticmethod
    def validate_password(pwd: str) -> bool:
        return len(pwd) >= 6

    # ── Display ────────────────────────────────────────────────

    @property
    def display_name(self) -> str:
        return self.name or self.login or self.email or ""

    def __bool__(self) -> bool:
        """Falsy when the profile is blank (unauthenticated placeholder)."""
        return bool(self.name or self.login or self.email)

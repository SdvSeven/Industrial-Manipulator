"""Pure data validation helpers."""
import re
from dataclasses import dataclass

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE = re.compile(r"^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$")


@dataclass
class UserProfile:
    full_name: str = ""
    organization: str = ""
    email: str = ""
    phone: str = ""
    is_authenticated: bool = False


def validate_email(v: str) -> bool:
    return bool(_EMAIL.match(v))


def validate_phone(v: str) -> bool:
    return bool(_PHONE.match(v))


def validate_registration(
    full_name: str, organization: str, email: str,
    phone: str, login: str, password: str, confirm: str,
) -> tuple[bool, str]:
    fields = [full_name, organization, email, phone, login, password, confirm]
    if not all(f.strip() for f in fields):
        return False, "Все поля обязательны для заполнения."
    if not validate_email(email):
        return False, "Неверный формат email."
    if not validate_phone(phone):
        return False, "Телефон: +7 (XXX) XXX-XX-XX"
    if len(password) < 6:
        return False, "Пароль — минимум 6 символов."
    if password != confirm:
        return False, "Пароли не совпадают."
    return True, ""

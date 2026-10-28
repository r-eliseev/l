"""Email как объект-значение: валидация при создании, а не при отправке."""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = ["EmailAddress", "InvalidEmail"]

_PATTERN = re.compile(r"^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$")


class InvalidEmail(ValueError):
    """Адрес не проходит проверку формата."""


@dataclass(frozen=True, slots=True)
class EmailAddress:
    """Нормализованный адрес электронной почты.

    Объект-значение: два адреса с одинаковым текстом равны; у адреса нет
    идентичности, поэтому сравнивать «это тот же клиент или другой» здесь
    неправильно — для этого нужна сущность.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not _PATTERN.match(normalized):
            raise InvalidEmail(f"Некорректный email: {self.value!r}")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value

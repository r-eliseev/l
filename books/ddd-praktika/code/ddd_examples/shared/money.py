"""Денежная сумма как объект-значение.

Источники идей:
- Eric Evans, DDD Reference (2015): «When you care only about the attributes
  and logic of an element of the model, classify it as a value object».
- Fowler, Value Object: объекты, равные по значению своих свойств.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

__all__ = ["Money", "CurrencyError"]


class CurrencyError(ValueError):
    """Операция с суммами в разных валютах запрещена."""


@dataclass(frozen=True, slots=True)
class Money:
    """Неизменяемый объект-значение: сумма в конкретной валюте.

    Иммутабельность — не украшение, а требование: объект-значение должен
    безопасно разделяться между потоками и агрегатами, кэшироваться без
    defensive copy и не иметь идентичности.
    """

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "amount", self._quantize(self.amount))
        code = self.currency.strip().upper()
        if len(code) != 3 or not code.isalpha():
            raise CurrencyError(f"Некорректный код валюты: {self.currency!r}")
        object.__setattr__(self, "currency", code)

    @staticmethod
    def _quantize(value: Decimal | int | str) -> Decimal:
        amount = Decimal(str(value))
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # --- сравнение и арифметика -------------------------------------------------

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise CurrencyError(
                f"Нельзя сравнивать или складывать суммы в разных валютах: "
                f"{self.currency} и {other.currency}"
            )

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: int | Decimal) -> "Money":
        return Money(self.amount * Decimal(str(factor)), self.currency)

    def __lt__(self, other: "Money") -> bool:
        self._assert_same_currency(other)
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        self._assert_same_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        self._assert_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        self._assert_same_currency(other)
        return self.amount >= other.amount

    # --- конструкторы ------------------------------------------------------------

    @classmethod
    def zero(cls, currency: str = "RUB") -> "Money":
        return cls(Decimal("0"), currency)

    @classmethod
    def of(cls, amount: Decimal | int | str, currency: str = "RUB") -> "Money":
        return cls(Decimal(str(amount)), currency)

    # --- форматирование ---------------------------------------------------------

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"

    def as_dict(self) -> dict[str, Any]:
        return {"amount": str(self.amount), "currency": self.currency}

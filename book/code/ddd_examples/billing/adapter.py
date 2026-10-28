"""Bounded context «Биллинг» (Billing) + Anti-Corruption Layer.

Здесь показана классическая схема: внутри компании существует старая
система биллинга с чужой моделью и чужим словарём. Мы не позволяем ей
просочиться в домен — вместо этого пишем трансляционный слой.

Fowler об Anti-Corruption Layer: «Implement a facade or adapter layer between
different subsystems that don't share the same semantics».
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Protocol

__all__ = [
    "LegacyInvoiceStatus",
    "LegacyInvoice",
    "LegacyBillingGateway",
    "BillingInvoice",
    "BillingAdapter",
]


class LegacyInvoiceStatus(Enum):
    """Словарь legacy-системы. В домене таких значений нет."""

    ISSUED = "ISSUED"
    PAID = "PAID"
    VOID = "VOID"


@dataclass(frozen=True, slots=True)
class LegacyInvoice:
    """Запись в чужом формате: поля названы как в старой базе."""

    legacy_id: str
    account_ref: str
    amount_minor: int
    currency_code: str
    status: LegacyInvoiceStatus


class LegacyBillingGateway(Protocol):
    """Порт к внешней системе. Реализация в продакшене — HTTP-клиент."""

    def fetch_invoices(self, account_ref: str) -> list[LegacyInvoice]: ...


@dataclass(frozen=True, slots=True)
class BillingInvoice:
    """Модель биллинга на нашем языке.

    Обратите внимание: здесь нет ни «amount_minor», ни статусов ISSUED/PAID.
    Есть наши понятия и наши единицы — сумма в валюте, а не в центах.
    """

    invoice_id: str
    account_id: str
    amount: Decimal
    currency: str
    is_settled: bool


class BillingAdapter:
    """Anti-Corruption Layer: переводит чужую модель в нашу.

    Правило слоя: ни одно поле legacy-системы не попадает в наш домен
    напрямую. Всё, что нужно, переводится явно, и перевод — единственное
    место, где живёт знание о чужом словаре.
    """

    def __init__(self, gateway: LegacyBillingGateway) -> None:
        self._gateway = gateway

    def invoices_for(self, account_id: str) -> list[BillingInvoice]:
        legacy_invoices = self._gateway.fetch_invoices(account_id)
        return [self._translate(invoice) for invoice in legacy_invoices]

    def _translate(self, invoice: LegacyInvoice) -> BillingInvoice:
        if invoice.account_ref != invoice.legacy_id and not invoice.legacy_id:
            raise ValueError("Некорректная запись legacy-системы")
        return BillingInvoice(
            invoice_id=f"inv-{invoice.legacy_id}",
            account_id=invoice.account_ref,
            amount=Decimal(invoice.amount_minor) / Decimal(100),
            currency=invoice.currency_code.upper(),
            is_settled=invoice.status is LegacyInvoiceStatus.PAID,
        )

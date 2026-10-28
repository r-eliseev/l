"""Модель домена: сущности, объекты-значения, агрегат и его события.

Bounded context: «Подписки» (Subscriptions).

Здесь нарочно всё в одном модуле: в реальном проекте агрегат разваливают на
файлы по типам, но держать его в одном месте — полезная привычка: сразу видно
границу транзакции и то, что именно агрегат защищает.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional

from ..shared import AggregateRoot, DomainEvent, EmailAddress, Money

__all__ = [
    "SubscriptionId",
    "CustomerId",
    "Customer",
    "SubscriptionPlan",
    "PlanTier",
    "SubscriptionStatus",
    "Subscription",
    "SubscriptionStarted",
    "SubscriptionPaused",
    "SubscriptionResumed",
    "PlanChanged",
    "SubscriptionCancelled",
    "SubscriptionError",
]


class SubscriptionError(Exception):
    """Нарушение инварианта агрегата."""


# ---------------------------------------------------------------------------
# Объекты-значения: идентичности нет, определены значениями
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SubscriptionId:
    """Идентификатор подписки — объект-значение, а не «голый» UUID.

    Обёртка даёт типобезопасность: перепутать SubscriptionId с CustomerId
    невозможно, хотя оба — строки.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("Пустой идентификатор подписки")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CustomerId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("Пустой идентификатор клиента")

    def __str__(self) -> str:
        return self.value


class PlanTier(Enum):
    """Уровень тарифа. Термин ubiquitous language этого контекста."""

    LIGHT = "light"
    RITUAL = "ritual"
    OBSESSION = "obsession"


@dataclass(frozen=True, slots=True)
class SubscriptionPlan:
    """Тариф — объект-значение: тарифы сравниваются по содержанию, а не по id."""

    code: str
    tier: PlanTier
    monthly_price: Money
    bags_per_month: int

    def __post_init__(self) -> None:
        if self.bags_per_month <= 0:
            raise ValueError("Число пакетов в месяц должно быть положительным")
        if self.monthly_price.amount <= 0:
            raise ValueError("Цена тарифа должна быть положительной")

    @property
    def is_upgrade(self) -> bool:
        return self.tier in (PlanTier.RITUAL, PlanTier.OBSESSION)


# ---------------------------------------------------------------------------
# Сущности: идентичность сохраняется во времени
# ---------------------------------------------------------------------------


@dataclass(eq=False)
class Customer:
    """Клиент — сущность: у него есть постоянная идентичность.

    Два клиента с одинаковым именем — разные клиенты. Имя может измениться,
    и клиент останется тем же самым.
    """

    id: CustomerId
    email: EmailAddress
    name: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Customer):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def rename(self, new_name: str) -> None:
        if not new_name.strip():
            raise ValueError("Имя не может быть пустым")
        self.name = new_name.strip()


class SubscriptionStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"


# ---------------------------------------------------------------------------
# Доменные события
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SubscriptionStarted(DomainEvent):
    subscription_id: SubscriptionId
    customer_id: CustomerId
    plan_code: str


@dataclass(frozen=True, slots=True)
class SubscriptionPaused(DomainEvent):
    subscription_id: SubscriptionId
    reason: str


@dataclass(frozen=True, slots=True)
class SubscriptionResumed(DomainEvent):
    subscription_id: SubscriptionId


@dataclass(frozen=True, slots=True)
class PlanChanged(DomainEvent):
    subscription_id: SubscriptionId
    old_plan_code: str
    new_plan_code: str
    effective_date: date


@dataclass(frozen=True, slots=True)
class SubscriptionCancelled(DomainEvent):
    subscription_id: SubscriptionId
    reason: str


# ---------------------------------------------------------------------------
# Агрегат
# ---------------------------------------------------------------------------


class Subscription(AggregateRoot):
    """Агрегат подписки: корень защищает инварианты целиком.

    Инварианты:
      * отменённую подписку нельзя возобновить;
      * нельзя отменить уже отменённую подписку;
      * тариф можно менять только у активной подписки;
      * пауза допустима только для активной подписки.
    """

    def __init__(
        self,
        subscription_id: SubscriptionId,
        customer: Customer,
        plan: SubscriptionPlan,
        started_on: date,
        status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
    ) -> None:
        super().__init__()
        self.id = subscription_id
        self.customer = customer
        self.plan = plan
        self.started_on = started_on
        self.status = status

    # --- чтение состояния -----------------------------------------------------

    @property
    def is_active(self) -> bool:
        return self.status is SubscriptionStatus.ACTIVE

    @property
    def is_paused(self) -> bool:
        return self.status is SubscriptionStatus.PAUSED

    @property
    def is_cancelled(self) -> bool:
        return self.status is SubscriptionStatus.CANCELLED

    # --- поведение ------------------------------------------------------------

    def pause(self, reason: str) -> None:
        if not self.is_active:
            raise SubscriptionError(
                f"Поставить на паузу можно только активную подписку, "
                f"текущий статус: {self.status.value}"
            )
        if not reason.strip():
            raise SubscriptionError("Причина паузы обязательна")
        self.status = SubscriptionStatus.PAUSED
        self._record(SubscriptionPaused(self.id, reason.strip()))

    def resume(self) -> None:
        if not self.is_paused:
            raise SubscriptionError(
                f"Возобновить можно только подписку на паузе, "
                f"текущий статус: {self.status.value}"
            )
        self.status = SubscriptionStatus.ACTIVE
        self._record(SubscriptionResumed(self.id))

    def change_plan(self, new_plan: SubscriptionPlan, effective_on: date) -> None:
        if not self.is_active:
            raise SubscriptionError(
                f"Сменить тариф можно только у активной подписки, "
                f"текущий статус: {self.status.value}"
            )
        if new_plan == self.plan:
            raise SubscriptionError("Подписка уже на этом тарифе")
        old_code = self.plan.code
        self.plan = new_plan
        self._record(PlanChanged(self.id, old_code, new_plan.code, effective_on))

    def cancel(self, reason: str) -> None:
        if self.is_cancelled:
            raise SubscriptionError("Подписка уже отменена")
        if not reason.strip():
            raise SubscriptionError("Причина отмены обязательна")
        self.status = SubscriptionStatus.CANCELLED
        self._record(SubscriptionCancelled(self.id, reason.strip()))

    @classmethod
    def start(
        cls,
        subscription_id: SubscriptionId,
        customer: Customer,
        plan: SubscriptionPlan,
        started_on: date,
    ) -> "Subscription":
        subscription = cls(subscription_id, customer, plan, started_on)
        subscription._record(
            SubscriptionStarted(subscription_id, customer.id, plan.code)
        )
        return subscription

    def __repr__(self) -> str:
        return (
            f"Subscription(id={self.id}, customer={self.customer.id}, "
            f"plan={self.plan.code}, status={self.status.value})"
        )

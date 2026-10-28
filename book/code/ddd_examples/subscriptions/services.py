"""Репозиторий агрегатов, доменный сервис и спецификация.

Bounded context: «Подписки» (Subscriptions).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Iterable, Optional, Protocol

from ..shared import Money
from .model import (
    Customer,
    CustomerId,
    PlanTier,
    Subscription,
    SubscriptionError,
    SubscriptionId,
    SubscriptionPlan,
)

__all__ = [
    "SubscriptionRepository",
    "InMemorySubscriptionRepository",
    "SubscriptionPricing",
    "CanChangePlan",
    "CanChangePlanSpec",
    "PlanCatalog",
]


class SubscriptionRepository(ABC):
    """Репозиторий даёт доступ к агрегатам на языке домена.

    Evans: «For each type of aggregate that needs global access, create a
    service that can provide the illusion of an in-memory collection of all
    objects of that aggregate's root type».
    """

    @abstractmethod
    def add(self, subscription: Subscription) -> None: ...

    @abstractmethod
    def get(self, subscription_id: SubscriptionId) -> Optional[Subscription]: ...

    @abstractmethod
    def update(self, subscription: Subscription) -> None: ...

    @abstractmethod
    def find_by_customer(self, customer_id: CustomerId) -> Iterable[Subscription]: ...


class InMemorySubscriptionRepository(SubscriptionRepository):
    """Реализация для примеров и тестов. В проде здесь будет БД."""

    def __init__(self) -> None:
        self._items: dict[SubscriptionId, Subscription] = {}

    def add(self, subscription: Subscription) -> None:
        if subscription.id in self._items:
            raise SubscriptionError(f"Подписка {subscription.id} уже существует")
        self._items[subscription.id] = subscription

    def get(self, subscription_id: SubscriptionId) -> Optional[Subscription]:
        return self._items.get(subscription_id)

    def update(self, subscription: Subscription) -> None:
        if subscription.id not in self._items:
            raise SubscriptionError(f"Подписка {subscription.id} не найдена")
        self._items[subscription.id] = subscription

    def find_by_customer(self, customer_id: CustomerId) -> Iterable[Subscription]:
        return [s for s in self._items.values() if s.customer.id == customer_id]

    def all(self) -> Iterable[Subscription]:
        return list(self._items.values())


class PlanCatalog:
    """Каталог тарифов — справочник, а не агрегат."""

    def __init__(self, plans: Iterable[SubscriptionPlan]) -> None:
        self._plans = {plan.code: plan for plan in plans}

    def get(self, code: str) -> SubscriptionPlan:
        try:
            return self._plans[code]
        except KeyError:
            raise SubscriptionError(f"Неизвестный тариф: {code!r}") from None

    def all(self) -> list[SubscriptionPlan]:
        return list(self._plans.values())

    def upgrade_options(self, current: SubscriptionPlan) -> list[SubscriptionPlan]:
        """Какие тарифы можно взять вместо текущего (улучшения и равные)."""
        order = {PlanTier.LIGHT: 0, PlanTier.RITUAL: 1, PlanTier.OBSESSION: 2}
        return [p for p in self._plans.values() if order[p.tier] >= order[current.tier]]


class SubscriptionPricing:
    """Доменный сервис: расчёт, который не принадлежит ни одной сущности.

    Evans: когда значимый процесс не является естественной обязанностью
    сущности или объекта-значения, его оформляют отдельным сервисом, имя
    которого становится частью ubiquitous language.
    """

    def prorated_charge(
        self,
        current: SubscriptionPlan,
        target: SubscriptionPlan,
        days_in_period: int,
        days_remaining: int,
    ) -> Money:
        """Доплата за смену тарифа в середине периода.

        Разница цен за оставшуюся часть периода. Если переход вниз —
        возвращаем ноль: кредит здесь не моделируем, но фиксируем решение
        в одном месте, чтобы правило не расползлось по коду.
        """
        if days_in_period <= 0:
            raise ValueError("Период должен быть положительным")
        if not 0 <= days_remaining <= days_in_period:
            raise ValueError("Оставшиеся дни вне периода")
        if target.monthly_price <= current.monthly_price:
            return Money.zero(current.monthly_price.currency)

        difference = target.monthly_price - current.monthly_price
        ratio = days_remaining / days_in_period
        return difference * ratio


class CanChangePlan(Protocol):
    """Протокол спецификации — предикат над агрегатом."""

    def is_satisfied_by(self, subscription: Subscription) -> bool: ...


class CanChangePlanSpec:
    """Спецификация: правило «тариф можно менять только у активной подписки».

    Спецификация полезна, когда одно и то же правило спрашивают в разных
    местах: UI, валидация команды, миграция данных.
    """

    def is_satisfied_by(self, subscription: Subscription) -> bool:
        return subscription.is_active

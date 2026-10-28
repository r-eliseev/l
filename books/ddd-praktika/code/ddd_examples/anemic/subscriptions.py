"""Анемичная версия той же предметной области — антипаттерн.

Fowler, Anemic Domain Model: «The basic symptom of an Anemic Domain Model is
that at first blush it looks like the real thing… The catch comes when you look
at the behavior, and you realize that there is hardly any behavior on these
objects, making them little more than bags of getters and setters».

Этот модуль нужен не для продакшена, а чтобы рядом с «живым» агрегатом
увидеть разницу. Код запускается и работает — он просто устроен хуже.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

__all__ = ["SubscriptionData", "SubscriptionService", "SubscriptionStateError"]


class SubscriptionStateError(Exception):
    """Ошибка состояния — раньше она жила внутри агрегата."""


@dataclass
class SubscriptionData:
    """Мешок с данными: идентичность есть, поведения нет."""

    subscription_id: str
    customer_id: str
    plan_code: str
    status: str = "active"
    monthly_price: float = 0.0
    bags_per_month: int = 0
    started_on: Optional[date] = None
    version: int = field(default=0)


class SubscriptionService:
    """Вся логика вынесена в сервис-объект — домен высох.

    Формально работает, тесты проходят, но:
      * правила нельзя посмотреть рядом с данными, которые они защищают;
      * инварианты можно обойти, изменив поле напрямую;
      * два сервиса легко разойдутся в трактовке одного правила.
    """

    def __init__(self) -> None:
        self._data: dict[str, SubscriptionData] = {}

    def create(self, subscription_id: str, customer_id: str, plan_code: str) -> SubscriptionData:
        data = SubscriptionData(subscription_id, customer_id, plan_code)
        self._data[subscription_id] = data
        return data

    def pause(self, subscription_id: str, reason: str) -> SubscriptionData:
        data = self._get(subscription_id)
        if data.status != "active":
            raise SubscriptionStateError("Пауза доступна только для активной подписки")
        data.status = "paused"
        data.version += 1
        return data

    def resume(self, subscription_id: str) -> SubscriptionData:
        data = self._get(subscription_id)
        if data.status != "paused":
            raise SubscriptionStateError("Возобновить можно только подписку на паузе")
        data.status = "active"
        data.version += 1
        return data

    def change_plan(self, subscription_id: str, plan_code: str) -> SubscriptionData:
        data = self._get(subscription_id)
        if data.status != "active":
            raise SubscriptionStateError("Смена тарифа доступна только для активной подписки")
        data.plan_code = plan_code
        data.version += 1
        return data

    def cancel(self, subscription_id: str, reason: str) -> SubscriptionData:
        data = self._get(subscription_id)
        if data.status == "cancelled":
            raise SubscriptionStateError("Подписка уже отменена")
        data.status = "cancelled"
        data.version += 1
        return data

    def _get(self, subscription_id: str) -> SubscriptionData:
        if subscription_id not in self._data:
            raise KeyError(subscription_id)
        return self._data[subscription_id]

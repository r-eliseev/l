"""Сценарии использования (application layer).

Приложение оркестрирует: загружает агрегат, вызывает его методы, сохраняет
результат и публикует события. Бизнес-правил здесь быть не должно — они
живут в агрегате.
"""

from __future__ import annotations

from datetime import date
from typing import Callable, Iterable, Optional

from ..shared import EventPublisher
from .model import (
    Customer,
    CustomerId,
    PlanChanged,
    Subscription,
    SubscriptionId,
    SubscriptionPlan,
)
from .services import SubscriptionPricing, SubscriptionRepository

__all__ = ["SubscriptionApplication", "SubscriptionView"]


class SubscriptionView:
    """Проекция для чтения: плоская структура, удобная для UI и API.

    Такой read-модель не является источником истины: она пересобирается из
    агрегатов или из потока событий.
    """

    def __init__(
        self,
        subscription_id: str,
        customer_id: str,
        plan_code: str,
        status: str,
        monthly_price: str,
    ) -> None:
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.plan_code = plan_code
        self.status = status
        self.monthly_price = monthly_price


class SubscriptionApplication:
    """Сценарии: подписаться, сменить тариф, поставить на паузу, отменить."""

    def __init__(
        self,
        repository: SubscriptionRepository,
        publisher: Optional[EventPublisher] = None,
        pricing: Optional[SubscriptionPricing] = None,
        id_generator: Optional[Callable[[], str]] = None,
    ) -> None:
        self._repository = repository
        self._publisher = publisher
        self._pricing = pricing or SubscriptionPricing()
        self._next_id = id_generator or (lambda: f"sub-{id(self._repository)}")

    def subscribe(
        self,
        customer: Customer,
        plan: SubscriptionPlan,
        started_on: date,
    ) -> Subscription:
        subscription_id = SubscriptionId(self._next_id())
        subscription = Subscription.start(subscription_id, customer, plan, started_on)
        self._repository.add(subscription)
        self._publish(subscription)
        return subscription

    def change_plan(
        self,
        subscription_id: SubscriptionId,
        new_plan: SubscriptionPlan,
        effective_on: date,
    ) -> Subscription:
        subscription = self._require(subscription_id)
        subscription.change_plan(new_plan, effective_on)
        self._repository.update(subscription)
        self._publish(subscription)
        return subscription

    def pause(self, subscription_id: SubscriptionId, reason: str) -> Subscription:
        subscription = self._require(subscription_id)
        subscription.pause(reason)
        self._repository.update(subscription)
        self._publish(subscription)
        return subscription

    def resume(self, subscription_id: SubscriptionId) -> Subscription:
        subscription = self._require(subscription_id)
        subscription.resume()
        self._repository.update(subscription)
        self._publish(subscription)
        return subscription

    def cancel(self, subscription_id: SubscriptionId, reason: str) -> Subscription:
        subscription = self._require(subscription_id)
        subscription.cancel(reason)
        self._repository.update(subscription)
        self._publish(subscription)
        return subscription

    def list_for_customer(self, customer_id: CustomerId) -> list[SubscriptionView]:
        return [
            SubscriptionView(
                subscription_id=str(s.id),
                customer_id=str(s.customer.id),
                plan_code=s.plan.code,
                status=s.status.value,
                monthly_price=str(s.plan.monthly_price),
            )
            for s in self._repository.find_by_customer(customer_id)
        ]

    # --- внутреннее ------------------------------------------------------------

    def _require(self, subscription_id: SubscriptionId) -> Subscription:
        subscription = self._repository.get(subscription_id)
        if subscription is None:
            raise KeyError(f"Подписка {subscription_id} не найдена")
        return subscription

    def _publish(self, subscription: Subscription) -> None:
        if self._publisher is None:
            return
        for event in subscription.pull_events():
            self._publisher.publish(event)

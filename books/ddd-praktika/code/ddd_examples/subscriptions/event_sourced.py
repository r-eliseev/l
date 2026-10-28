"""Вариант подписки, построенный на потоке событий (Event Sourcing).

Состояние не хранится — оно восстанавливается проигрыванием событий.
Каждый переход состояния записывается как факт; текущее состояние — это
свёртка всех фактов.

Fowler, Event Sourcing: «Capture all changes to an application state as a
sequence of events».
"""

from __future__ import annotations

from datetime import date
from typing import Iterable

from ..shared import DomainEvent
from ..shared.event_store import EventStore, StoredEvent
from .model import (
    Customer,
    CustomerId,
    PlanChanged,
    SubscriptionCancelled,
    SubscriptionError,
    SubscriptionId,
    SubscriptionPaused,
    SubscriptionPlan,
    SubscriptionResumed,
    SubscriptionStarted,
    SubscriptionStatus,
)

__all__ = ["EventSourcedSubscription"]


class EventSourcedSubscription:
    """Подписка, восстанавливаемая из событий.

    Обратите внимание на отсутствие сеттеров: единственный способ изменить
    состояние — применить событие. Это делает историю полной и непротиворечивой.
    """

    def __init__(self, subscription_id: SubscriptionId) -> None:
        self.id = subscription_id
        self.customer: Customer | None = None
        self.plan: SubscriptionPlan | None = None
        self.started_on: date | None = None
        self.status = SubscriptionStatus.ACTIVE

    # --- восстановление ---------------------------------------------------------

    @classmethod
    def load(
        cls,
        subscription_id: SubscriptionId,
        store: EventStore,
    ) -> "EventSourcedSubscription":
        subscription = cls(subscription_id)
        for record in store.read(str(subscription_id)):
            subscription.apply(record.event)
        return subscription

    def apply(self, event: DomainEvent) -> None:
        """Применяет событие к состоянию. Правило одно: факт меняет факт."""
        if isinstance(event, SubscriptionStarted):
            self.status = SubscriptionStatus.ACTIVE
            self.plan = _plan_from_code(event.plan_code)
        elif isinstance(event, SubscriptionPaused):
            self.status = SubscriptionStatus.PAUSED
        elif isinstance(event, SubscriptionResumed):
            self.status = SubscriptionStatus.ACTIVE
        elif isinstance(event, SubscriptionCancelled):
            self.status = SubscriptionStatus.CANCELLED
        elif isinstance(event, PlanChanged):
            self.plan = _plan_from_code(event.new_plan_code)
        # Неизвестные события игнорируются: журнал может содержать события
        # будущих версий системы, и это не повод падать.

    # --- команды ----------------------------------------------------------------

    def start(
        self,
        customer: Customer,
        plan: SubscriptionPlan,
        started_on: date,
    ) -> list[DomainEvent]:
        if self.customer is not None:
            raise SubscriptionError("Подписка уже начата")
        self.customer = customer
        self.plan = plan
        self.started_on = started_on
        event = SubscriptionStarted(self.id, customer.id, plan.code)
        self.apply(event)
        return [event]

    def pause(self, reason: str) -> list[DomainEvent]:
        if self.status is not SubscriptionStatus.ACTIVE:
            raise SubscriptionError(
                f"Поставить на паузу можно только активную подписку, "
                f"текущий статус: {self.status.value}"
            )
        event = SubscriptionPaused(self.id, reason)
        self.apply(event)
        return [event]

    def resume(self) -> list[DomainEvent]:
        if self.status is not SubscriptionStatus.PAUSED:
            raise SubscriptionError("Возобновить можно только подписку на паузе")
        event = SubscriptionResumed(self.id)
        self.apply(event)
        return [event]

    def cancel(self, reason: str) -> list[DomainEvent]:
        if self.status is SubscriptionStatus.CANCELLED:
            raise SubscriptionError("Подписка уже отменена")
        event = SubscriptionCancelled(self.id, reason)
        self.apply(event)
        return [event]

    def change_plan(self, new_plan: SubscriptionPlan, effective_on: date) -> list[DomainEvent]:
        if self.status is not SubscriptionStatus.ACTIVE:
            raise SubscriptionError("Сменить тариф можно только у активной подписки")
        if self.plan is None or new_plan == self.plan:
            raise SubscriptionError("Подписка уже на этом тарифе")
        event = PlanChanged(self.id, self.plan.code, new_plan.code, effective_on)
        self.apply(event)
        return [event]


def _plan_from_code(code: str) -> SubscriptionPlan:
    """Восстанавливает тариф по коду.

    В реальном проекте здесь обращение к справочнику тарифов: тарифы меняются,
    и их нельзя хранить в событии — в событии хранится только код.
    """
    from .model import PlanTier

    presets = {
        "light": ("light", PlanTier.LIGHT, "490", 1),
        "ritual": ("ritual", PlanTier.RITUAL, "990", 2),
        "obsession": ("obsession", PlanTier.OBSESSION, "1990", 4),
    }
    try:
        name, tier, price, bags = presets[code]
    except KeyError:
        raise SubscriptionError(f"Неизвестный тариф: {code!r}") from None
    from ..shared import Money

    return SubscriptionPlan(
        code=name, tier=tier, monthly_price=Money.of(price, "RUB"), bags_per_month=bags
    )

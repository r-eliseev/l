"""Доменные события и корень агрегата.

Событие — факт, о котором эксперты домена хотят знать. В DDD Reference
Evans определяет доменное событие как «something happened that domain experts
care about» и требует моделировать активность домена как последовательность
дискретных событий.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol

__all__ = [
    "DomainEvent",
    "AggregateRoot",
    "EventPublisher",
    "CollectingEventPublisher",
    "utc_now",
]


def utc_now() -> datetime:
    """Единая точка времени — чтобы тесты могли подменять её."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Базовый класс доменного события.

    Событие неизменяемо: это запись о прошлом.

    ``occurred_at`` объявлен keyword-only, чтобы наследники могли добавлять
    свои обязательные поля: в обычном dataclass поле со значением по
    умолчанию в базовом классе запрещает обязательные поля в наследнике.
    """

    occurred_at: datetime = field(default_factory=utc_now, kw_only=True)

    @property
    def name(self) -> str:
        return type(self).__name__


class AggregateRoot:
    """Корень агрегата: единственная точка входа в его внутренности.

    Агрегат хранит свои события до тех пор, пока их не заберут: сбор событий
    и публикация — работа инфраструктуры, а не домена.
    """

    def __init__(self) -> None:
        self._events: list[DomainEvent] = []

    def _record(self, event: DomainEvent) -> None:
        self._events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        """Забрать накопленные события и очистить буфер."""
        events = list(self._events)
        self._events.clear()
        return events

    @property
    def pending_events(self) -> tuple[DomainEvent, ...]:
        return tuple(self._events)


class EventPublisher(Protocol):
    """Порт публикации событий. Реализация живёт в инфраструктуре."""

    def publish(self, event: DomainEvent) -> None: ...


class CollectingEventPublisher:
    """Тестовая реализация: складывает события в список."""

    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self.events.append(event)

    def names(self) -> list[str]:
        return [event.name for event in self.events]

    def of_type(self, kind: type) -> list[Any]:
        return [e for e in self.events if isinstance(e, kind)]

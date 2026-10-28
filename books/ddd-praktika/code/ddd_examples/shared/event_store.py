"""Простой Event Store и шина подписок.

Минимальная инфраструктура для главы про доменные события и Event Sourcing.
Никаких внешних зависимостей — только чтобы показать идею целиком.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Protocol
from uuid import uuid4

from .events import DomainEvent

__all__ = [
    "StoredEvent",
    "EventStore",
    "InMemoryEventStore",
    "Subscriber",
    "EventBus",
    "InMemoryEventBus",
]


@dataclass(frozen=True, slots=True)
class StoredEvent:
    """Событие вместе со служебной обвязкой, как в настоящем журнале."""

    sequence: int
    stream_id: str
    event: DomainEvent


class EventStore(Protocol):
    """Порт хранилища событий."""

    def append(self, stream_id: str, events: Iterable[DomainEvent]) -> list[StoredEvent]:
        ...

    def read(self, stream_id: str) -> list[StoredEvent]:
        ...


class InMemoryEventStore:
    """Журнал событий в памяти.

    События хранятся в порядке поступления и никогда не меняются: поток
    событий — это единственный источник правды о состоянии агрегата.
    """

    def __init__(self) -> None:
        self._streams: dict[str, list[StoredEvent]] = {}
        self._sequence = 0

    def append(self, stream_id: str, events: Iterable[DomainEvent]) -> list[StoredEvent]:
        stored: list[StoredEvent] = []
        for event in events:
            self._sequence += 1
            record = StoredEvent(self._sequence, stream_id, event)
            self._streams.setdefault(stream_id, []).append(record)
            stored.append(record)
        return stored

    def read(self, stream_id: str) -> list[StoredEvent]:
        return list(self._streams.get(stream_id, []))

    def all_streams(self) -> list[str]:
        return list(self._streams)

    @property
    def total_events(self) -> int:
        return self._sequence


Subscriber = Callable[[DomainEvent], None]


class EventBus:
    """Распределяет события подписчикам."""

    def publish(self, event: DomainEvent) -> None: ...


class InMemoryEventBus:
    """Простая шина: подписчики вызываются по порядку регистрации."""

    def __init__(self) -> None:
        self._subscribers: dict[type, list[Subscriber]] = {}

    def subscribe(self, event_type: type, handler: Subscriber) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._subscribers.get(type(event), []):
            handler(event)

    def publish_all(self, events: Iterable[DomainEvent]) -> None:
        for event in events:
            self.publish(event)


def new_stream_id(prefix: str = "stream") -> str:
    """Идентификатор потока событий."""
    return f"{prefix}-{uuid4().hex[:12]}"

"""Общие элементы, разделяемые разными bounded contexts.

Внимание: модуль shared существует исключительно как учебный пример того,
как выглядит код одного домена. В реальном проекте такого «общего ядра»
между контекстами быть не должно — shared kernel оправдан лишь когда
изменения в нём согласуются между командами.
"""

from .email import EmailAddress, InvalidEmail
from .event_store import (
    EventBus,
    EventStore,
    InMemoryEventBus,
    InMemoryEventStore,
    StoredEvent,
    new_stream_id,
)
from .events import (
    AggregateRoot,
    CollectingEventPublisher,
    DomainEvent,
    EventPublisher,
    utc_now,
)
from .money import CurrencyError, Money

__all__ = [
    "AggregateRoot",
    "EventBus",
    "EventStore",
    "InMemoryEventBus",
    "InMemoryEventStore",
    "StoredEvent",
    "CollectingEventPublisher",
    "CurrencyError",
    "DomainEvent",
    "EmailAddress",
    "EventPublisher",
    "InvalidEmail",
    "Money",
    "new_stream_id",
    "utc_now",
]

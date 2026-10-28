"""Модель карты контекстов (context map) в коде.

Не библиотека, а учебная модель: она показывает, что карта контекстов —
это структура данных, которую можно хранить, проверять и обсуждать.

Названия отношений и паттернов — термины ubiquitous language стратегического
дизайна; список девяти паттернов и трёх типов отношений взят из DDD Reference
Эванса и из шпаргалки ddd-crew.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

__all__ = [
    "TeamRelationship",
    "ContextMapPattern",
    "BoundedContext",
    "ContextMap",
    "SubscriptionContext",
]


class TeamRelationship(Enum):
    """Тип отношения между двумя bounded context'ами."""

    MUTUALLY_DEPENDENT = "mutually_dependent"
    UPSTREAM_DOWNSTREAM = "upstream_downstream"
    FREE = "free"


class ContextMapPattern(Enum):
    """Девять паттернов context map."""

    OPEN_HOST_SERVICE = "open_host_service"
    SHARED_KERNEL = "shared_kernel"
    CUSTOMER_SUPPLIER = "customer_supplier"
    CONFORMIST = "conformist"
    ANTICORRUPTION_LAYER = "anticorruption_layer"
    PUBLISHED_LANGUAGE = "published_language"
    SEPARATE_WAYS = "separate_ways"
    PARTNERSHIP = "partnership"
    BIG_BALL_OF_MUD = "big_ball_of_mud"


@dataclass(frozen=True, slots=True)
class BoundedContext:
    """Ограниченный контекст: имя, команда, язык."""

    name: str
    team: str
    ubiquitous_language: tuple[str, ...] = ()

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True, slots=True)
class ContextMap:
    """Связи между контекстами."""

    upstream: BoundedContext
    downstream: BoundedContext
    relationship: TeamRelationship
    pattern: ContextMapPattern
    note: str = ""

    def describe(self) -> str:
        return (
            f"{self.upstream.name} → {self.downstream.name}: "
            f"{self.relationship.value}, {self.pattern.value}"
        )


@dataclass
class SystemMap:
    """Вся карта: контексты и связи между ними."""

    contexts: list[BoundedContext] = field(default_factory=list)
    links: list[ContextMap] = field(default_factory=list)

    def add(self, context: BoundedContext) -> None:
        self.contexts.append(context)

    def connect(self, link: ContextMap) -> None:
        self.links.append(link)

    def find(self, name: str) -> BoundedContext | None:
        for context in self.contexts:
            if context.name == name:
                return context
        return None

    def links_of(self, name: str) -> list[ContextMap]:
        return [
            link
            for link in self.links
            if link.upstream.name == name or link.downstream.name == name
        ]

    def render(self) -> str:
        """Человекочитаемый вид карты — как её обсуждают на воркшопе."""
        lines = ["Контексты:"]
        for context in self.contexts:
            language = ", ".join(context.ubiquitous_language)
            lines.append(f"  • {context.name} ({context.team}): {language}")
        lines.append("Связи:")
        for link in self.links:
            lines.append(f"  {link.describe()}")
            if link.note:
                lines.append(f"      {link.note}")
        return "\n".join(lines)


# --- учебный пример: карта кофейного сервиса -------------------------------

SUBSCRIPTION = BoundedContext(
    name="Subscriptions",
    team="команда подписок",
    ubiquitous_language=("подписка", "тариф", "уровень", "пауза", "отмена"),
)

FULFILMENT = BoundedContext(
    name="Fulfilment",
    team="команда склада",
    ubiquitous_language=("отгрузка", "партия", "остаток", "поставка"),
)

BILLING = BoundedContext(
    name="Billing",
    team="команда биллинга",
    ubiquitous_language=("счёт", "платёж", "способ оплаты", "период"),
)

LEGACY = BoundedContext(
    name="LegacyBilling",
    team="внешняя система",
    ubiquitous_language=("invoice", "amount_minor", "ISSUED", "PAID"),
)


def coffee_shop_map() -> SystemMap:
    """Карта контекстов учебного домена."""
    system = SystemMap()
    for context in (SUBSCRIPTION, FULFILMENT, BILLING, LEGACY):
        system.add(context)

    system.connect(
        ContextMap(
            upstream=BILLING,
            downstream=SUBSCRIPTION,
            relationship=TeamRelationship.UPSTREAM_DOWNSTREAM,
            pattern=ContextMapPattern.ANTICORRUPTION_LAYER,
            note="Счета приходят из legacy-системы; ACL переводит их в наши понятия.",
        )
    )
    system.connect(
        ContextMap(
            upstream=SUBSCRIPTION,
            downstream=FULFILMENT,
            relationship=TeamRelationship.UPSTREAM_DOWNSTREAM,
            pattern=ContextMapPattern.PUBLISHED_LANGUAGE,
            note="Событие SubscriptionStarted — опубликованный язык для склада.",
        )
    )
    system.connect(
        ContextMap(
            upstream=FULFILMENT,
            downstream=BILLING,
            relationship=TeamRelationship.UPSTREAM_DOWNSTREAM,
            pattern=ContextMapPattern.CONFORMIST,
            note="Биллинг принимает модель склада без изменений.",
        )
    )
    return system

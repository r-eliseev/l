"""Стратегический дизайн: карта контекстов."""

from .context_map import (
    BILLING,
    FULFILMENT,
    LEGACY,
    SUBSCRIPTION,
    BoundedContext,
    ContextMap,
    ContextMapPattern,
    SystemMap,
    TeamRelationship,
    coffee_shop_map,
)

__all__ = [
    "BILLING",
    "FULFILMENT",
    "LEGACY",
    "SUBSCRIPTION",
    "BoundedContext",
    "ContextMap",
    "ContextMapPattern",
    "SystemMap",
    "TeamRelationship",
    "coffee_shop_map",
]

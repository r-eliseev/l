"""Анемичная версия домена — для сравнения в главе об антипаттернах."""

from .demo import bypass_invariant_demo, correct_usage_demo
from .subscriptions import SubscriptionData, SubscriptionService, SubscriptionStateError

__all__ = [
    "SubscriptionData",
    "SubscriptionService",
    "SubscriptionStateError",
    "bypass_invariant_demo",
    "correct_usage_demo",
]

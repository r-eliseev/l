"""Демонстрация обхода инварианта в анемичной модели.

Книга показывает на этом примере главный дефект анемичного домена: правило
можно обойти, потому что данные меняются напрямую, а логика живёт в сервисе.
Чтобы пример был настоящим, а не псевдокодом, он оформлен как функция.
"""

from __future__ import annotations

from .subscriptions import SubscriptionData, SubscriptionService

__all__ = ["bypass_invariant_demo", "correct_usage_demo"]


def bypass_invariant_demo() -> SubscriptionData:
    """Показывает, как легко сломать правило в анемичной модели.

    Подписку отменили «неправильно»: статус выставлен напрямую, минуя
    проверки в SubscriptionService.cancel. Сервис об этом не узнает и
    продолжит считать подписку активной.
    """
    service = SubscriptionService()
    service.create("sub-1", "cust-1", "light")

    data = service._data["sub-1"]
    data.status = "cancelled"  # обход всех проверок
    return data


def correct_usage_demo() -> SubscriptionData:
    """Тот же сценарий, но через сервис: правило соблюдается.

    Повторная отмена вызовет SubscriptionStateError — сервис не даст
    перевести подписку в противоречивое состояние.
    """
    service = SubscriptionService()
    service.create("sub-1", "cust-1", "light")
    return service.cancel("sub-1", "не нужна")

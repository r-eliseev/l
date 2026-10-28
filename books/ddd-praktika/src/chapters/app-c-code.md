# Приложение В. Полный пример: структура и запуск

*Все примеры книги — это работающий пакет. Здесь его карта и команды запуска.*

## Как запустить

Нужен Python 3.11 или новее. Внешних зависимостей нет.

```bash
cd code
python -m unittest discover -s tests -v
```

Ожидаемый вывод — строка вида `OK` и число тестов (на момент написания — 50).

## Структура пакета

```
code/
  ddd_examples/
    __init__.py
    shared/                     элементы одного домена
      __init__.py
      money.py                   Money — объект-значение
      email.py                   EmailAddress — объект-значение
      events.py                  DomainEvent, AggregateRoot, шина
      event_store.py             журнал событий и шина подписок
    subscriptions/               bounded context «Подписки»
      __init__.py
      model.py                   сущности, объекты-значения, агрегат, события
      services.py                репозиторий, каталог, доменный сервис, спецификация
      application.py             сценарии и read-модель
      event_sourced.py           вариант на потоке событий
    billing/                     bounded context «Биллинг»
      __init__.py
      adapter.py                 Anti-Corruption Layer над legacy-системой
    strategic/                   стратегический дизайн
      __init__.py
      context_map.py             модель карты контекстов
    anemic/                      антипаттерн для сравнения
      __init__.py
      subscriptions.py           та же логика, но без поведения у объектов
  tests/
    test_shared.py
    test_subscriptions.py
    test_billing_and_anemic.py
    test_event_sourcing_and_strategy.py
```

## Что где искать

| Вопрос | Файл |
|---|---|
| Как выглядит объект-значение | `ddd_examples/shared/money.py` |
| Как выглядит сущность | `ddd_examples/subscriptions/model.py`, класс `Customer` |
| Как выглядит агрегат | `ddd_examples/subscriptions/model.py`, класс `Subscription` |
| Как выглядит репозиторий | `ddd_examples/subscriptions/services.py` |
| Как выглядит доменный сервис | `ddd_examples/subscriptions/services.py`, класс `SubscriptionPricing` |
| Как выглядит спецификация | `ddd_examples/subscriptions/services.py`, класс `CanChangePlanSpec` |
| Как выглядят доменные события | `ddd_examples/shared/events.py`, `ddd_examples/subscriptions/model.py` |
| Как выглядит изолирующий слой | `ddd_examples/billing/adapter.py` |
| Как выглядит карта контекстов | `ddd_examples/strategic/context_map.py` |
| Как выглядит анемичная модель | `ddd_examples/anemic/subscriptions.py` |
| Как выглядит event sourcing | `ddd_examples/subscriptions/event_sourced.py` |

## Минимальный пример целиком

Вот весь домен «Подписки» в сжатом виде — объект-значение, сущность и агрегат:

```python
@dataclass(frozen=True, slots=True)
class SubscriptionPlan:
    """Тариф — объект-значение: тарифы сравниваются по содержанию."""

    code: str
    tier: PlanTier
    monthly_price: Money
    bags_per_month: int


@dataclass(eq=False)
class Customer:
    """Клиент — сущность: у него есть постоянная идентичность."""

    id: CustomerId
    email: EmailAddress
    name: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Customer):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class Subscription(AggregateRoot):
    """Агрегат подписки: корень защищает инварианты целиком."""

    def change_plan(self, new_plan: SubscriptionPlan, effective_on: date) -> None:
        if not self.is_active:
            raise SubscriptionError(
                f"Сменить тариф можно только у активной подписки, "
                f"текущий статус: {self.status.value}"
            )
        if new_plan == self.plan:
            raise SubscriptionError("Подписка уже на этом тарифе")
        old_code = self.plan.code
        self.plan = new_plan
        self._record(PlanChanged(self.id, old_code, new_plan.code, effective_on))
```

## Упражнения с кодом

1. **Сломайте инвариант.** Добавьте в `Subscription` метод `force_cancel()`, который отменяет подписку без проверки статуса. Объясните, почему это хуже, чем проверка в `cancel()`.
2. **Сделайте объект-значение изменяемым.** Уберите `frozen=True` у `SubscriptionPlan` и посмотрите, что ломается в сравнении `new_plan == self.plan`.
3. **Сломайте единый язык.** Переименуйте `Subscription.pause` в `suspend` и `resume` в `activate` — и оцените, сколько мест в пакете придётся тронуть.
4. **Проверьте границу агрегата.** Попробуйте из сценария изменить `subscription.plan` напрямую, минуя `change_plan`. Что должно помешать этому?
5. **Замените инфраструктуру.** Напишите `InMemorySubscriptionRepository`, хранящий агрегаты в словаре по `str(id)`, — и убедитесь, что доменный код не изменился ни на строчку.
6. **Сравните две реализации.** Опишите один и тот же сценарий через `SubscriptionApplication` и через `EventSourcedSubscription` — и сравните, где проходит граница транзакции.

## Как расширить пакет

Хорошие места для эксперимента:

- **Новый тариф** — добавьте пресет в `_plan_from_code` и в `PlanCatalog`. Посмотрите, как меняется число мест, где перечислены тарифы.
- **Новый контекст** — создайте `ddd_examples/fulfilment/` с собственным понятием «отгрузка». Проверьте: не понадобились ли общие классы с «Подписками»?
- **Событие подписки** — добавьте `SubscriptionUpgraded` в `model.py`, обработайте в `EventSourcedSubscription.apply` и в подписчике шины.

## Источники

- [1] — определения паттернов, по которым построен пример.
- [3] — о том, чем отличается анемичная реализация в `ddd_examples/anemic/`.

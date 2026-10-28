"""Тесты хранилища событий, event sourcing и карты контекстов."""

import unittest
from datetime import date

from ddd_examples.shared import (
    EmailAddress,
    InMemoryEventBus,
    InMemoryEventStore,
    Money,
    new_stream_id,
)
from ddd_examples.strategic import (
    BILLING,
    SUBSCRIPTION,
    ContextMapPattern,
    TeamRelationship,
    coffee_shop_map,
)
from ddd_examples.subscriptions import (
    Customer,
    CustomerId,
    EventSourcedSubscription,
    PlanTier,
    SubscriptionError,
    SubscriptionId,
    SubscriptionPlan,
    SubscriptionStatus,
)


def make_plan(code="light", price="490", bags=1):
    return SubscriptionPlan(
        code=code,
        tier=PlanTier.LIGHT,
        monthly_price=Money.of(price, "RUB"),
        bags_per_month=bags,
    )


def make_customer():
    return Customer(CustomerId("cust-1"), EmailAddress("ira@example.com"), "Ира")


class EventStoreTests(unittest.TestCase):
    def test_события_сохраняются_в_порядке(self):
        store = InMemoryEventStore()
        subscription = EventSourcedSubscription(SubscriptionId("sub-1"))
        customer = make_customer()
        plan = make_plan()
        for event in subscription.start(customer, plan, date(2026, 3, 1)):
            store.append("sub-1", [event])

        events = store.read("sub-1")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event.name, "SubscriptionStarted")
        self.assertEqual(events[0].stream_id, "sub-1")

    def test_потоки_независимы(self):
        """Пустой append не создаёт поток: поток появляется с первым событием."""
        store = InMemoryEventStore()
        store.append("a", [])
        self.assertEqual(store.all_streams(), [])

        subscription = EventSourcedSubscription(SubscriptionId("sub-a"))
        events = subscription.start(make_customer(), make_plan(), date(2026, 3, 1))
        store.append("a", events)
        store.append("b", events)
        self.assertEqual(store.all_streams(), ["a", "b"])
        self.assertEqual(len(store.read("a")), 1)
        self.assertEqual(len(store.read("b")), 1)


class EventSourcingTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryEventStore()
        self.subscription = EventSourcedSubscription(SubscriptionId("sub-1"))
        self.customer = make_customer()
        self.plan = make_plan()

    def _apply(self, events):
        for event in events:
            self.store.append("sub-1", [event])

    def test_состояние_восстанавливается_из_событий(self):
        self._apply(self.subscription.start(self.customer, self.plan, date(2026, 3, 1)))
        self._apply(self.subscription.pause("переезд"))

        restored = EventSourcedSubscription.load(SubscriptionId("sub-1"), self.store)
        self.assertEqual(restored.status, SubscriptionStatus.PAUSED)
        self.assertEqual(restored.plan.code, "light")

    def test_история_сохраняется_полностью(self):
        self._apply(self.subscription.start(self.customer, self.plan, date(2026, 3, 1)))
        self._apply(self.subscription.pause("переезд"))
        self._apply(self.subscription.resume())
        names = [r.event.name for r in self.store.read("sub-1")]
        self.assertEqual(
            names, ["SubscriptionStarted", "SubscriptionPaused", "SubscriptionResumed"]
        )

    def test_инвариант_работает_и_здесь(self):
        self._apply(self.subscription.start(self.customer, self.plan, date(2026, 3, 1)))
        with self.assertRaises(SubscriptionError):
            self.subscription.resume()

    def test_смена_тарифа_меняет_состояние(self):
        self._apply(self.subscription.start(self.customer, self.plan, date(2026, 3, 1)))
        self._apply(
            self.subscription.change_plan(make_plan("ritual", "990", 2), date(2026, 4, 1))
        )
        restored = EventSourcedSubscription.load(SubscriptionId("sub-1"), self.store)
        self.assertEqual(restored.plan.code, "ritual")


class EventBusTests(unittest.TestCase):
    def test_подписчик_получает_событие(self):
        bus = InMemoryEventBus()
        received = []
        from ddd_examples.subscriptions import SubscriptionStarted

        bus.subscribe(SubscriptionStarted, received.append)
        event = SubscriptionStarted(SubscriptionId("sub-1"), CustomerId("cust-1"), "light")
        bus.publish(event)
        self.assertEqual(len(received), 1)


class ContextMapTests(unittest.TestCase):
    def setUp(self):
        self.system = coffee_shop_map()

    def test_контексты_зарегистрированы(self):
        self.assertIsNotNone(self.system.find("Subscriptions"))
        self.assertIsNotNone(self.system.find("Billing"))

    def test_связи_описаны(self):
        links = self.system.links_of("Billing")
        self.assertTrue(links)
        self.assertIn(
            ContextMapPattern.ANTICORRUPTION_LAYER,
            {link.pattern for link in links},
        )

    def test_отношения_в_допустимых_значениях(self):
        for link in self.system.links:
            self.assertIsInstance(link.relationship, TeamRelationship)

    def test_рендер_читаем(self):
        rendered = self.system.render()
        self.assertIn("Subscriptions", rendered)
        self.assertIn("Связи:", rendered)


if __name__ == "__main__":
    unittest.main()

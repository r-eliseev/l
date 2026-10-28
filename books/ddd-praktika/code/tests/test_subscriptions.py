"""Тесты агрегата подписки, репозитория и доменного сервиса."""

import unittest
from datetime import date

from ddd_examples.shared import CollectingEventPublisher, EmailAddress, Money
from ddd_examples.subscriptions import (
    Customer,
    CustomerId,
    PlanChanged,
    PlanCatalog,
    PlanTier,
    Subscription,
    SubscriptionApplication,
    SubscriptionError,
    SubscriptionId,
    SubscriptionPaused,
    SubscriptionPlan,
    SubscriptionPricing,
    SubscriptionStarted,
    SubscriptionStatus,
    InMemorySubscriptionRepository,
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


class AggregateTests(unittest.TestCase):
    def setUp(self):
        self.customer = make_customer()
        self.plan = make_plan()

    def test_старт_фиксирует_событие(self):
        subscription = Subscription.start(
            SubscriptionId("sub-1"), self.customer, self.plan, date(2026, 3, 1)
        )
        names = [e.name for e in subscription.pending_events]
        self.assertEqual(names, ["SubscriptionStarted"])

    def test_пауза_меняет_статус_и_пишет_событие(self):
        subscription = Subscription.start(
            SubscriptionId("sub-1"), self.customer, self.plan, date(2026, 3, 1)
        )
        subscription.pause("переезд")
        self.assertTrue(subscription.is_paused)
        self.assertIn("SubscriptionPaused", [e.name for e in subscription.pending_events])

    def test_нельзя_поставить_на_паузу_дважды(self):
        subscription = Subscription.start(
            SubscriptionId("sub-1"), self.customer, self.plan, date(2026, 3, 1)
        )
        subscription.pause("переезд")
        with self.assertRaises(SubscriptionError):
            subscription.pause("ещё раз")

    def test_нельзя_возобновить_не_паузную(self):
        subscription = Subscription.start(
            SubscriptionId("sub-1"), self.customer, self.plan, date(2026, 3, 1)
        )
        with self.assertRaises(SubscriptionError):
            subscription.resume()

    def test_нельзя_сменить_тариф_у_отменённой(self):
        subscription = Subscription.start(
            SubscriptionId("sub-1"), self.customer, self.plan, date(2026, 3, 1)
        )
        subscription.cancel("не нужен")
        with self.assertRaises(SubscriptionError):
            subscription.change_plan(make_plan("ritual", "990", 2), date(2026, 4, 1))

    def test_нельзя_отменить_дважды(self):
        subscription = Subscription.start(
            SubscriptionId("sub-1"), self.customer, self.plan, date(2026, 3, 1)
        )
        subscription.cancel("не нужен")
        with self.assertRaises(SubscriptionError):
            subscription.cancel("всё ещё не нужен")

    def test_смена_тарифа_пишет_событие(self):
        subscription = Subscription.start(
            SubscriptionId("sub-1"), self.customer, self.plan, date(2026, 3, 1)
        )
        subscription.change_plan(make_plan("ritual", "990", 2), date(2026, 4, 1))
        events = subscription.pending_events
        changed = [e for e in events if isinstance(e, PlanChanged)]
        self.assertEqual(len(changed), 1)
        self.assertEqual(changed[0].old_plan_code, "light")
        self.assertEqual(changed[0].new_plan_code, "ritual")

    def test_события_извлекаются_один_раз(self):
        subscription = Subscription.start(
            SubscriptionId("sub-1"), self.customer, self.plan, date(2026, 3, 1)
        )
        first = subscription.pull_events()
        second = subscription.pull_events()
        self.assertEqual(len(first), 1)
        self.assertEqual(second, [])

    def test_клиент_равен_себе_по_идентификатору(self):
        other = Customer(CustomerId("cust-1"), EmailAddress("other@example.com"), "Другое имя")
        self.assertEqual(self.customer, other)


class RepositoryTests(unittest.TestCase):
    def test_добавление_и_чтение(self):
        repo = InMemorySubscriptionRepository()
        subscription = Subscription.start(
            SubscriptionId("sub-1"), make_customer(), make_plan(), date(2026, 3, 1)
        )
        repo.add(subscription)
        self.assertIs(repo.get(SubscriptionId("sub-1")), subscription)

    def test_нельзя_добавить_дважды(self):
        repo = InMemorySubscriptionRepository()
        subscription = Subscription.start(
            SubscriptionId("sub-1"), make_customer(), make_plan(), date(2026, 3, 1)
        )
        repo.add(subscription)
        with self.assertRaises(SubscriptionError):
            repo.add(subscription)

    def test_поиск_по_клиенту(self):
        repo = InMemorySubscriptionRepository()
        for sid in ("sub-1", "sub-2"):
            repo.add(
                Subscription.start(
                    SubscriptionId(sid), make_customer(), make_plan(), date(2026, 3, 1)
                )
            )
        found = list(repo.find_by_customer(CustomerId("cust-1")))
        self.assertEqual(len(found), 2)


class PricingTests(unittest.TestCase):
    def setUp(self):
        self.pricing = SubscriptionPricing()

    def test_доплата_за_оставшуюся_часть_периода(self):
        charge = self.pricing.prorated_charge(
            make_plan("light", "490"), make_plan("ritual", "990", 2),
            days_in_period=30, days_remaining=15,
        )
        self.assertEqual(charge, Money.of("250.00", "RUB"))

    def test_понижение_даёт_ноль(self):
        charge = self.pricing.prorated_charge(
            make_plan("ritual", "990", 2), make_plan("light", "490"),
            days_in_period=30, days_remaining=15,
        )
        self.assertEqual(charge, Money.zero("RUB"))

    def test_некорректный_период(self):
        with self.assertRaises(ValueError):
            self.pricing.prorated_charge(
                make_plan(), make_plan("ritual", "990", 2),
                days_in_period=0, days_remaining=0,
            )


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.repo = InMemorySubscriptionRepository()
        self.publisher = CollectingEventPublisher()
        self.app = SubscriptionApplication(self.repo, self.publisher)
        self.customer = make_customer()
        self.plan = make_plan()

    def test_подписка_публикует_событие(self):
        self.app.subscribe(self.customer, self.plan, date(2026, 3, 1))
        self.assertIn("SubscriptionStarted", self.publisher.names())

    def test_сценарий_паузы(self):
        subscription = self.app.subscribe(self.customer, self.plan, date(2026, 3, 1))
        self.app.pause(subscription.id, "переезд")
        self.assertIn("SubscriptionPaused", self.publisher.names())
        self.assertEqual(
            self.repo.get(subscription.id).status, SubscriptionStatus.PAUSED
        )

    def test_проекция_для_клиента(self):
        subscription = self.app.subscribe(self.customer, self.plan, date(2026, 3, 1))
        views = self.app.list_for_customer(self.customer.id)
        self.assertEqual(len(views), 1)
        self.assertEqual(views[0].plan_code, "light")


class CatalogTests(unittest.TestCase):
    def test_неизвестный_тариф(self):
        catalog = PlanCatalog([make_plan()])
        with self.assertRaises(SubscriptionError):
            catalog.get("nope")

    def test_варианты_повышения(self):
        catalog = PlanCatalog(
            [
                make_plan("light", "490"),
                make_plan("ritual", "990", 2),
            ]
        )
        options = catalog.upgrade_options(catalog.get("light"))
        self.assertEqual({p.code for p in options}, {"light", "ritual"})


if __name__ == "__main__":
    unittest.main()

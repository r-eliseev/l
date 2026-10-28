"""Тесты Anti-Corruption Layer и анемичной версии домена."""

import unittest
from decimal import Decimal

from ddd_examples.anemic import SubscriptionService, SubscriptionStateError
from ddd_examples.billing import (
    BillingAdapter,
    LegacyInvoice,
    LegacyInvoiceStatus,
)


class FakeLegacyGateway:
    """Заглушка внешней системы."""

    def __init__(self, invoices):
        self._invoices = invoices
        self.calls: list[str] = []

    def fetch_invoices(self, account_ref):
        self.calls.append(account_ref)
        return [i for i in self._invoices if i.account_ref == account_ref]


class AntiCorruptionLayerTests(unittest.TestCase):
    def test_переводит_центы_в_рубли(self):
        gateway = FakeLegacyGateway(
            [
                LegacyInvoice(
                    legacy_id="A-1",
                    account_ref="cust-1",
                    amount_minor=125050,
                    currency_code="rub",
                    status=LegacyInvoiceStatus.PAID,
                )
            ]
        )
        adapter = BillingAdapter(gateway)
        invoices = adapter.invoices_for("cust-1")

        self.assertEqual(len(invoices), 1)
        self.assertEqual(invoices[0].amount, Decimal("1250.50"))
        self.assertEqual(invoices[0].currency, "RUB")
        self.assertTrue(invoices[0].is_settled)

    def test_наши_поля_не_совпадают_с_чужими(self):
        gateway = FakeLegacyGateway(
            [
                LegacyInvoice(
                    legacy_id="A-1",
                    account_ref="cust-1",
                    amount_minor=100,
                    currency_code="RUB",
                    status=LegacyInvoiceStatus.ISSUED,
                )
            ]
        )
        invoice = BillingAdapter(gateway).invoices_for("cust-1")[0]
        self.assertFalse(hasattr(invoice, "amount_minor"))
        self.assertFalse(hasattr(invoice, "status"))
        self.assertFalse(invoice.is_settled)

    def test_шлюз_вызван_с_нужным_аккаунтом(self):
        gateway = FakeLegacyGateway([])
        BillingAdapter(gateway).invoices_for("cust-9")
        self.assertEqual(gateway.calls, ["cust-9"])


class AnemicTests(unittest.TestCase):
    """Анемичная версия работает — и это как раз проблема."""

    def setUp(self):
        self.service = SubscriptionService()
        self.service.create("sub-1", "cust-1", "light")

    def test_работает(self):
        self.service.pause("sub-1", "переезд")
        self.assertEqual(self.service._data["sub-1"].status, "paused")

    def test_правило_все_ещё_работает(self):
        with self.assertRaises(SubscriptionStateError):
            self.service.pause("sub-1", "переезд")
            self.service.pause("sub-1", "переезд")

    def test_инвариант_можно_обойти(self):
        """Главный дефект: данные меняются напрямую, правило не знает."""
        data = self.service._data["sub-1"]
        data.status = "cancelled"  # обход всех проверок
        self.assertEqual(data.status, "cancelled")

    def test_версия_меняется_на_каждое_действие(self):
        data = self.service._data["sub-1"]
        self.assertEqual(data.version, 0)
        self.service.resume("sub-1") if False else self.service.pause("sub-1", "x")
        self.assertEqual(data.version, 1)


if __name__ == "__main__":
    unittest.main()

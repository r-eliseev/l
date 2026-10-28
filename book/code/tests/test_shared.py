"""Тесты объектов-значений: Money, EmailAddress."""

import unittest
from decimal import Decimal

from ddd_examples.shared import CurrencyError, EmailAddress, InvalidEmail, Money


class MoneyTests(unittest.TestCase):
    def test_равны_по_значению(self):
        self.assertEqual(Money.of(100, "RUB"), Money.of("100.00", "rub"))

    def test_неизменяемы(self):
        money = Money.of(100)
        with self.assertRaises(Exception):
            money.amount = Decimal("200")  # type: ignore[misc]

    def test_сложение_в_одной_валюте(self):
        total = Money.of(100, "RUB") + Money.of(50, "RUB")
        self.assertEqual(total, Money.of(150, "RUB"))

    def test_сложение_в_разных_валютах_запрещено(self):
        with self.assertRaises(CurrencyError):
            Money.of(100, "RUB") + Money.of(50, "USD")

    def test_сравнение_в_разных_валютах_запрещено(self):
        with self.assertRaises(CurrencyError):
            _ = Money.of(100, "RUB") < Money.of(50, "USD")

    def test_умножение_на_дробь(self):
        self.assertEqual(Money.of(100) * 0.5, Money.of(50))

    def test_ноль(self):
        self.assertEqual(Money.zero("RUB"), Money.of(0, "RUB"))

    def test_некорректный_код_валюты(self):
        with self.assertRaises(CurrencyError):
            Money.of(10, "RU")

    def test_округление_до_копеек(self):
        self.assertEqual(Money.of("10.005"), Money.of("10.01"))


class EmailTests(unittest.TestCase):
    def test_нормализуется(self):
        self.assertEqual(EmailAddress("  User@Example.COM ").value, "user@example.com")

    def test_некорректный_адрес(self):
        with self.assertRaises(InvalidEmail):
            EmailAddress("not-an-email")

    def test_равны_по_значению(self):
        self.assertEqual(EmailAddress("a@b.ru"), EmailAddress("A@B.RU"))


if __name__ == "__main__":
    unittest.main()

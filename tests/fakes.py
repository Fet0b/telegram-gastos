"""Implementações em memória das portas do Domain, para testes.

Não herdam de nada: satisfazem os `Protocol`s só por terem os mesmos
métodos (tipagem estrutural) — o mesmo mecanismo que a Infrastructure usa.
"""

from __future__ import annotations

from App.Domain.entities.expense import Expense
from App.Domain.value_objects.telegram_user_id import TelegramUserId


class InMemoryExpenseRepository:
    def __init__(self) -> None:
        self.expenses: list[Expense] = []

    def add(self, expense: Expense) -> None:
        self.expenses.append(expense)

    def list_by_user(self, user_id: TelegramUserId) -> list[Expense]:
        return [e for e in self.expenses if e.user_id == user_id]

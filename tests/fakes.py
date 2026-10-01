"""Implementações em memória das portas do Domain, para testes.

Não herdam de nada: satisfazem os `Protocol`s só por terem os mesmos
métodos (tipagem estrutural) — o mesmo mecanismo que a Infrastructure usa.
"""

from __future__ import annotations

from App.Domain.entities.expense import Expense
from App.Domain.entities.income import Income
from App.Domain.value_objects.entry_id import EntryId
from App.Domain.value_objects.telegram_user_id import TelegramUserId


class SequentialEntryIdGenerator:
    def __init__(self, start: int = 1) -> None:
        self._next = start

    def next_id(self) -> EntryId:
        entry_id = EntryId(self._next)
        self._next += 1
        return entry_id


class InMemoryExpenseRepository:
    def __init__(self) -> None:
        self.expenses: list[Expense] = []

    def add(self, expense: Expense) -> None:
        self.expenses.append(expense)

    def list_by_user(self, user_id: TelegramUserId) -> list[Expense]:
        return [e for e in self.expenses if e.user_id == user_id]

    def remove(self, user_id: TelegramUserId, entry_id: EntryId) -> Expense | None:
        for expense in self.expenses:
            if expense.id == entry_id and expense.user_id == user_id:
                self.expenses.remove(expense)
                return expense
        return None


class InMemoryIncomeRepository:
    def __init__(self) -> None:
        self.incomes: list[Income] = []

    def add(self, income: Income) -> None:
        self.incomes.append(income)

    def list_by_user(self, user_id: TelegramUserId) -> list[Income]:
        return [i for i in self.incomes if i.user_id == user_id]

    def remove(self, user_id: TelegramUserId, entry_id: EntryId) -> Income | None:
        for income in self.incomes:
            if income.id == entry_id and income.user_id == user_id:
                self.incomes.remove(income)
                return income
        return None

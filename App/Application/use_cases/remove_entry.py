"""Caso de uso: remover um lançamento (gasto ou ganho) pelo ID.

Como gastos e ganhos compartilham a mesma sequência de IDs, `/remover 12`
não precisa dizer o tipo: o caso de uso procura primeiro entre os gastos
e depois entre os ganhos do usuário.

Só remove lançamentos do próprio usuário. Um ID de outro usuário tem o
mesmo tratamento de um ID inexistente (EntryNotFoundError) — a resposta
não revela se o lançamento existe.
"""

from __future__ import annotations

from App.Domain.entities.expense import Expense
from App.Domain.entities.income import Income
from App.Domain.exceptions import EntryNotFoundError
from App.Domain.ports.expense_repository import ExpenseRepository
from App.Domain.ports.income_repository import IncomeRepository
from App.Domain.value_objects.entry_id import EntryId
from App.Domain.value_objects.telegram_user_id import TelegramUserId


class RemoveEntryUseCase:
    def __init__(self, expenses: ExpenseRepository, incomes: IncomeRepository) -> None:
        self._expenses = expenses
        self._incomes = incomes

    def execute(self, *, user_id: TelegramUserId, entry_id: EntryId) -> Expense | Income:
        removed_expense = self._expenses.remove(user_id, entry_id)
        if removed_expense is not None:
            return removed_expense

        removed_income = self._incomes.remove(user_id, entry_id)
        if removed_income is not None:
            return removed_income

        raise EntryNotFoundError(entry_id.value)

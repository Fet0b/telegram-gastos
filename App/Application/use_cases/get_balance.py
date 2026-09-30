"""Caso de uso: calcular o saldo de um usuário (ganhos - gastos).

O cálculo mora aqui, e não na camada de Telegram, porque "saldo" é uma
regra do negócio — se amanhã existir outra interface (um relatório, uma
API), ela reaproveita o mesmo caso de uso sem reescrever a conta.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from App.Domain.ports.expense_repository import ExpenseRepository
from App.Domain.ports.income_repository import IncomeRepository
from App.Domain.value_objects.telegram_user_id import TelegramUserId


@dataclass(frozen=True, slots=True)
class Balance:
    total_incomes: Decimal
    total_expenses: Decimal

    @property
    def balance(self) -> Decimal:
        """Pode ser negativo — gastar mais do que ganhou é justamente o que
        o usuário quer enxergar. Por isso não é um `Money` (que só aceita > 0).
        """
        return self.total_incomes - self.total_expenses


class GetBalanceUseCase:
    def __init__(self, expenses: ExpenseRepository, incomes: IncomeRepository) -> None:
        self._expenses = expenses
        self._incomes = incomes

    def execute(self, user_id: TelegramUserId) -> Balance:
        return Balance(
            total_incomes=sum(
                (i.amount.amount for i in self._incomes.list_by_user(user_id)), Decimal("0")
            ),
            total_expenses=sum(
                (e.amount.amount for e in self._expenses.list_by_user(user_id)), Decimal("0")
            ),
        )

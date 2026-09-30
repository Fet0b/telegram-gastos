"""Caso de uso: listar gastos de um usuário, em bruto ou resumido por categoria."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from App.Domain.entities.expense import Expense
from App.Domain.ports.expense_repository import ExpenseRepository
from App.Domain.value_objects.category import ExpenseCategory
from App.Domain.value_objects.telegram_user_id import TelegramUserId


@dataclass(frozen=True, slots=True)
class CategorySummary:
    category: ExpenseCategory
    total: Decimal
    percentage: Decimal


class ListExpensesUseCase:
    def __init__(self, repository: ExpenseRepository) -> None:
        self._repository = repository

    def raw(self, user_id: TelegramUserId) -> list[Expense]:
        """Gastos em ordem cronológica (mais antigo primeiro)."""
        return sorted(self._repository.list_by_user(user_id), key=lambda e: e.occurred_at)

    def summarize_by_category(self, user_id: TelegramUserId) -> list[CategorySummary]:
        """Total e % gasto por categoria, ordenado do maior para o menor total.

        Categorias sem nenhum gasto não aparecem na lista.
        """
        expenses = self._repository.list_by_user(user_id)
        if not expenses:
            return []

        totals: dict[ExpenseCategory, Decimal] = {}
        for expense in expenses:
            current = totals.get(expense.category, Decimal("0"))
            totals[expense.category] = current + expense.amount.amount

        grand_total = sum(totals.values(), Decimal("0"))
        summaries = [
            CategorySummary(
                category=category,
                total=total,
                percentage=(total / grand_total * 100).quantize(Decimal("0.1")),
            )
            for category, total in totals.items()
        ]
        return sorted(summaries, key=lambda s: s.total, reverse=True)

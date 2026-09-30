"""Fábricas de entidades para testes, com defaults razoáveis.

Cada teste só informa o que importa para ele (`make_expense(amount="30")`),
e o resto vem preenchido — deixa claro o que está sendo testado.
"""

from __future__ import annotations

from datetime import UTC, datetime

from App.Domain.entities.expense import Expense
from App.Domain.entities.income import Income
from App.Domain.value_objects.category import ExpenseCategory
from App.Domain.value_objects.entry_id import EntryId
from App.Domain.value_objects.money import Money
from App.Domain.value_objects.telegram_user_id import TelegramUserId


def make_expense(
    *,
    id: int = 1,
    user: int = 1,
    amount: str = "10",
    title: str = "mercado",
    category: ExpenseCategory = ExpenseCategory.ALIMENTACAO,
    occurred_at: datetime | None = None,
) -> Expense:
    return Expense(
        id=EntryId(id),
        user_id=TelegramUserId(user),
        amount=Money.from_text(amount),
        title=title,
        category=category,
        occurred_at=occurred_at or datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
    )


def make_income(
    *,
    id: int = 1,
    user: int = 1,
    amount: str = "1000",
    title: str = "salário",
    occurred_at: datetime | None = None,
) -> Income:
    return Income(
        id=EntryId(id),
        user_id=TelegramUserId(user),
        amount=Money.from_text(amount),
        title=title,
        occurred_at=occurred_at or datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
    )

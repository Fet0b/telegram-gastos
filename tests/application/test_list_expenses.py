from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from App.Application.use_cases.list_expenses import ListExpensesUseCase
from App.Domain.entities.expense import Expense
from App.Domain.value_objects.category import ExpenseCategory
from App.Domain.value_objects.telegram_user_id import TelegramUserId
from tests.builders import make_expense
from tests.fakes import InMemoryExpenseRepository

USER = TelegramUserId(1)


def _repository_with(*expenses: Expense) -> InMemoryExpenseRepository:
    repository = InMemoryExpenseRepository()
    for expense in expenses:
        repository.add(expense)
    return repository


def test_raw_ordena_cronologicamente_e_filtra_usuario() -> None:
    late = make_expense(id=1, occurred_at=datetime(2026, 1, 20, tzinfo=UTC))
    early = make_expense(id=2, occurred_at=datetime(2026, 1, 2, tzinfo=UTC))
    other = make_expense(id=3, user=2, occurred_at=datetime(2026, 1, 1, tzinfo=UTC))
    use_case = ListExpensesUseCase(_repository_with(late, other, early))

    assert use_case.raw(USER) == [early, late]


def test_resumo_por_categoria_com_percentual() -> None:
    use_case = ListExpensesUseCase(
        _repository_with(
            make_expense(id=1, amount="30", category=ExpenseCategory.ALIMENTACAO),
            make_expense(id=2, amount="45", category=ExpenseCategory.ALIMENTACAO),
            make_expense(id=3, amount="25", category=ExpenseCategory.LAZER),
            make_expense(id=4, user=2, amount="1000", category=ExpenseCategory.LAZER),
        )
    )

    summary = use_case.summarize_by_category(USER)

    assert [(s.category, s.total, s.percentage) for s in summary] == [
        (ExpenseCategory.ALIMENTACAO, Decimal("75.00"), Decimal("75.0")),
        (ExpenseCategory.LAZER, Decimal("25.00"), Decimal("25.0")),
    ]


def test_resumo_vazio_sem_gastos() -> None:
    assert ListExpensesUseCase(InMemoryExpenseRepository()).summarize_by_category(USER) == []

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from App.Application.use_cases.list_expenses import ListExpensesUseCase
from App.Domain.entities.expense import Expense
from App.Domain.value_objects.category import ExpenseCategory
from App.Domain.value_objects.money import Money
from App.Domain.value_objects.telegram_user_id import TelegramUserId
from tests.fakes import InMemoryExpenseRepository

USER = TelegramUserId(1)
OTHER_USER = TelegramUserId(2)


def _expense(user: TelegramUserId, amount: str, category: ExpenseCategory, day: int) -> Expense:
    return Expense(
        user_id=user,
        amount=Money.from_text(amount),
        title="x",
        category=category,
        occurred_at=datetime(2026, 1, day, tzinfo=UTC),
    )


def _repository_with(*expenses: Expense) -> InMemoryExpenseRepository:
    repository = InMemoryExpenseRepository()
    for expense in expenses:
        repository.add(expense)
    return repository


def test_raw_ordena_cronologicamente_e_filtra_usuario() -> None:
    late = _expense(USER, "10", ExpenseCategory.LAZER, day=20)
    early = _expense(USER, "5", ExpenseCategory.CASA, day=2)
    other = _expense(OTHER_USER, "99", ExpenseCategory.CASA, day=1)
    use_case = ListExpensesUseCase(_repository_with(late, other, early))

    assert use_case.raw(USER) == [early, late]


def test_resumo_por_categoria_com_percentual() -> None:
    use_case = ListExpensesUseCase(
        _repository_with(
            _expense(USER, "30", ExpenseCategory.ALIMENTACAO, day=1),
            _expense(USER, "45", ExpenseCategory.ALIMENTACAO, day=2),
            _expense(USER, "25", ExpenseCategory.LAZER, day=3),
            _expense(OTHER_USER, "1000", ExpenseCategory.LAZER, day=3),
        )
    )

    summary = use_case.summarize_by_category(USER)

    assert [(s.category, s.total, s.percentage) for s in summary] == [
        (ExpenseCategory.ALIMENTACAO, Decimal("75.00"), Decimal("75.0")),
        (ExpenseCategory.LAZER, Decimal("25.00"), Decimal("25.0")),
    ]


def test_resumo_vazio_sem_gastos() -> None:
    assert ListExpensesUseCase(InMemoryExpenseRepository()).summarize_by_category(USER) == []

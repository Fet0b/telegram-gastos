from __future__ import annotations

from datetime import UTC, datetime

from App.Application.use_cases.register_expense import RegisterExpenseUseCase
from App.Domain.value_objects.category import ExpenseCategory
from App.Domain.value_objects.entry_id import EntryId
from App.Domain.value_objects.money import Money
from App.Domain.value_objects.telegram_user_id import TelegramUserId
from tests.fakes import InMemoryExpenseRepository, SequentialEntryIdGenerator


def test_registra_e_persiste_gasto_com_id_novo() -> None:
    repository = InMemoryExpenseRepository()
    use_case = RegisterExpenseUseCase(repository, SequentialEntryIdGenerator(start=5))
    occurred_at = datetime(2026, 3, 10, 15, 30, tzinfo=UTC)

    expense = use_case.execute(
        user_id=TelegramUserId(42),
        amount=Money.from_text("12,50"),
        title="uber",
        category=ExpenseCategory.TRANSPORTE,
        occurred_at=occurred_at,
    )

    assert repository.expenses == [expense]
    assert expense.id == EntryId(5)
    assert expense.occurred_at == occurred_at

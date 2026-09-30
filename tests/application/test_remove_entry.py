from __future__ import annotations

import pytest

from App.Application.use_cases.remove_entry import RemoveEntryUseCase
from App.Domain.exceptions import EntryNotFoundError
from App.Domain.value_objects.entry_id import EntryId
from App.Domain.value_objects.telegram_user_id import TelegramUserId
from tests.builders import make_expense, make_income
from tests.fakes import InMemoryExpenseRepository, InMemoryIncomeRepository

USER = TelegramUserId(1)


def _use_case() -> tuple[RemoveEntryUseCase, InMemoryExpenseRepository, InMemoryIncomeRepository]:
    expenses = InMemoryExpenseRepository()
    incomes = InMemoryIncomeRepository()
    expenses.add(make_expense(id=1, user=1))
    incomes.add(make_income(id=2, user=1))
    expenses.add(make_expense(id=3, user=2))  # de outro usuário
    return RemoveEntryUseCase(expenses, incomes), expenses, incomes


def test_remove_gasto() -> None:
    use_case, expenses, _ = _use_case()
    removed = use_case.execute(user_id=USER, entry_id=EntryId(1))
    assert removed.id == EntryId(1)
    assert expenses.list_by_user(USER) == []


def test_remove_ganho() -> None:
    use_case, _, incomes = _use_case()
    removed = use_case.execute(user_id=USER, entry_id=EntryId(2))
    assert removed.id == EntryId(2)
    assert incomes.list_by_user(USER) == []


def test_id_inexistente() -> None:
    use_case, _, _ = _use_case()
    with pytest.raises(EntryNotFoundError):
        use_case.execute(user_id=USER, entry_id=EntryId(99))


def test_nao_remove_lancamento_de_outro_usuario() -> None:
    use_case, expenses, _ = _use_case()
    with pytest.raises(EntryNotFoundError):
        use_case.execute(user_id=USER, entry_id=EntryId(3))
    assert len(expenses.list_by_user(TelegramUserId(2))) == 1

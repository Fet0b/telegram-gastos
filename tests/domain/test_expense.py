from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from App.Domain.entities.expense import Expense
from App.Domain.exceptions import InvalidExpenseError
from App.Domain.value_objects.category import ExpenseCategory
from App.Domain.value_objects.money import Money
from App.Domain.value_objects.telegram_user_id import TelegramUserId


def _expense(**overrides: object) -> Expense:
    data: dict[str, object] = {
        "user_id": TelegramUserId(1),
        "amount": Money.from_text("10"),
        "title": "mercado",
        "category": ExpenseCategory.ALIMENTACAO,
        "occurred_at": datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
    }
    data.update(overrides)
    return Expense(**data)  # type: ignore[arg-type]


def test_cria_gasto_valido() -> None:
    assert _expense().title == "mercado"


@pytest.mark.parametrize("title", ["", "   "])
def test_rejeita_titulo_vazio(title: str) -> None:
    with pytest.raises(InvalidExpenseError):
        _expense(title=title)


def test_rejeita_data_sem_timezone() -> None:
    with pytest.raises(InvalidExpenseError):
        _expense(occurred_at=datetime(2026, 1, 1, 12, 0))


def test_e_imutavel() -> None:
    expense = _expense()
    with pytest.raises(FrozenInstanceError):
        expense.title = "outro"  # type: ignore[misc]


@pytest.mark.parametrize("value", [0, -1])
def test_telegram_user_id_rejeita_nao_positivo(value: int) -> None:
    with pytest.raises(ValueError):
        TelegramUserId(value)

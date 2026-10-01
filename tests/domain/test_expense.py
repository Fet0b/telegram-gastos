from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from App.Domain.exceptions import InvalidExpenseError
from App.Domain.value_objects.telegram_user_id import TelegramUserId
from tests.builders import make_expense


def test_cria_gasto_valido() -> None:
    expense = make_expense(id=7, title="mercado")
    assert expense.title == "mercado"
    assert expense.id.value == 7


@pytest.mark.parametrize("title", ["", "   "])
def test_rejeita_titulo_vazio(title: str) -> None:
    with pytest.raises(InvalidExpenseError):
        make_expense(title=title)


def test_rejeita_data_sem_timezone() -> None:
    with pytest.raises(InvalidExpenseError):
        make_expense(occurred_at=datetime(2026, 1, 1, 12, 0))


def test_e_imutavel() -> None:
    expense = make_expense()
    with pytest.raises(FrozenInstanceError):
        expense.title = "outro"  # type: ignore[misc]


@pytest.mark.parametrize("value", [0, -1])
def test_telegram_user_id_rejeita_nao_positivo(value: int) -> None:
    with pytest.raises(ValueError):
        TelegramUserId(value)

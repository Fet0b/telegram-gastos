from __future__ import annotations

from datetime import datetime

import pytest

from App.Domain.exceptions import InvalidIncomeError
from tests.builders import make_income


def test_cria_ganho_valido() -> None:
    income = make_income(amount="5000", title="salário setembro")
    assert income.title == "salário setembro"
    assert str(income.amount) == "R$ 5000.00"


@pytest.mark.parametrize("title", ["", "  "])
def test_rejeita_titulo_vazio(title: str) -> None:
    with pytest.raises(InvalidIncomeError):
        make_income(title=title)


def test_rejeita_data_sem_timezone() -> None:
    with pytest.raises(InvalidIncomeError):
        make_income(occurred_at=datetime(2026, 1, 1))

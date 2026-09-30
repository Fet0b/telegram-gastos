from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from App.Application.use_cases.register_income import RegisterIncomeUseCase, parse_ganho_command
from App.Domain.exceptions import InvalidMoneyAmountError
from App.Domain.value_objects.entry_id import EntryId
from App.Domain.value_objects.money import Money
from App.Domain.value_objects.telegram_user_id import TelegramUserId
from tests.fakes import InMemoryIncomeRepository, SequentialEntryIdGenerator


def test_parse_comando_completo() -> None:
    parsed = parse_ganho_command(["5000", "salário", "setembro"])
    assert parsed.amount.amount == Decimal("5000.00")
    assert parsed.title == "salário setembro"
    assert parsed.is_complete


def test_parse_so_valor_pede_titulo() -> None:
    parsed = parse_ganho_command(["150,75"])
    assert parsed.title is None
    assert not parsed.is_complete


def test_parse_nao_trata_ultima_palavra_como_categoria() -> None:
    # Ganho não tem categoria: "Lazer" aqui é só parte do título.
    assert parse_ganho_command(["100", "reembolso", "Lazer"]).title == "reembolso Lazer"


@pytest.mark.parametrize("tokens", [[], ["abc", "salário"], ["-10", "x"]])
def test_parse_valor_invalido_ou_ausente_e_erro(tokens: list[str]) -> None:
    with pytest.raises(InvalidMoneyAmountError):
        parse_ganho_command(tokens)


def test_registra_e_persiste_ganho() -> None:
    repository = InMemoryIncomeRepository()
    use_case = RegisterIncomeUseCase(repository, SequentialEntryIdGenerator(start=3))

    income = use_case.execute(
        user_id=TelegramUserId(1),
        amount=Money.from_text("5000"),
        title="salário",
        occurred_at=datetime(2026, 9, 5, 9, 0, tzinfo=UTC),
    )

    assert repository.incomes == [income]
    assert income.id == EntryId(3)

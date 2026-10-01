from __future__ import annotations

from decimal import Decimal

import pytest

from App.Application.use_cases.register_expense import parse_gasto_command
from App.Domain.exceptions import InvalidMoneyAmountError
from App.Domain.value_objects.category import ExpenseCategory


def test_comando_completo() -> None:
    parsed = parse_gasto_command(["45,90", "mercado", "do", "bairro", "Alimentação"])
    assert parsed.amount.amount == Decimal("45.90")
    assert parsed.title == "mercado do bairro"
    assert parsed.category is ExpenseCategory.ALIMENTACAO
    assert parsed.missing_fields == ()
    assert parsed.is_complete


def test_so_valor_pede_titulo_e_categoria() -> None:
    parsed = parse_gasto_command(["10"])
    assert parsed.title is None
    assert parsed.category is None
    assert parsed.missing_fields == ("título", "categoria")
    assert not parsed.is_complete


def test_valor_e_categoria_pede_titulo() -> None:
    parsed = parse_gasto_command(["10", "lazer"])
    assert parsed.title is None
    assert parsed.category is ExpenseCategory.LAZER
    assert parsed.missing_fields == ("título",)


def test_ultimo_token_desconhecido_vira_parte_do_titulo() -> None:
    # "comida" não é categoria: não assume default, pergunta de volta.
    parsed = parse_gasto_command(["30", "pizza", "comida"])
    assert parsed.title == "pizza comida"
    assert parsed.category is None
    assert parsed.missing_fields == ("categoria",)


@pytest.mark.parametrize("tokens", [[], ["abc", "pizza", "Lazer"], ["nan", "x", "Lazer"]])
def test_valor_invalido_ou_ausente_e_erro(tokens: list[str]) -> None:
    with pytest.raises(InvalidMoneyAmountError):
        parse_gasto_command(tokens)

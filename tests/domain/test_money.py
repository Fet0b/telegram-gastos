from __future__ import annotations

from decimal import Decimal

import pytest

from App.Domain.exceptions import InvalidMoneyAmountError
from App.Domain.value_objects.money import Money


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("45.90", Decimal("45.90")),
        ("45,90", Decimal("45.90")),
        ("45,9", Decimal("45.90")),
        ("10", Decimal("10.00")),
        (" 3.5 ", Decimal("3.50")),
        ("0,01", Decimal("0.01")),
    ],
)
def test_from_text_aceita_ponto_e_virgula(raw: str, expected: Decimal) -> None:
    assert Money.from_text(raw).amount == expected


def test_from_text_arredonda_para_centavos() -> None:
    assert Money.from_text("10.005").amount == Decimal("10.00")  # ROUND_HALF_EVEN


@pytest.mark.parametrize("raw", ["", "abc", "0", "-5", "0,001", "nan", "NaN", "inf", "1,000,00"])
def test_from_text_rejeita_valores_invalidos(raw: str) -> None:
    with pytest.raises(InvalidMoneyAmountError) as exc_info:
        Money.from_text(raw)
    # A mensagem mostra o que o usuário digitou, não o valor normalizado.
    assert exc_info.value.amount_raw == raw


def test_nao_usa_float() -> None:
    # 0.1 + 0.2 em float é 0.30000000000000004; em Decimal é exato.
    total = Money.from_text("0.1").amount + Money.from_text("0.2").amount
    assert total == Decimal("0.30")


def test_construtor_direto_valida_valor() -> None:
    with pytest.raises(InvalidMoneyAmountError):
        Money(Decimal("0"))
    with pytest.raises(InvalidMoneyAmountError):
        Money(Decimal("NaN"))


def test_str_formata_em_reais() -> None:
    assert str(Money.from_text("45,9")) == "R$ 45.90"

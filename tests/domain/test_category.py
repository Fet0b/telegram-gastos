from __future__ import annotations

import pytest

from App.Domain.value_objects.category import ExpenseCategory


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Alimentação", ExpenseCategory.ALIMENTACAO),
        ("alimentacao", ExpenseCategory.ALIMENTACAO),
        ("ALIMENTAÇÃO", ExpenseCategory.ALIMENTACAO),
        (" lazer ", ExpenseCategory.LAZER),
        ("Transporte", ExpenseCategory.TRANSPORTE),
        ("investimentos", ExpenseCategory.INVESTIMENTOS),
        ("casa", ExpenseCategory.CASA),
        ("assinaturas", ExpenseCategory.ASSINATURAS),
        ("outros", ExpenseCategory.OUTROS),
    ],
)
def test_from_text_ignora_caixa_e_acento(raw: str, expected: ExpenseCategory) -> None:
    assert ExpenseCategory.from_text(raw) is expected


@pytest.mark.parametrize("raw", ["", "comida", "lazeres", "invest"])
def test_from_text_retorna_none_para_categoria_desconhecida(raw: str) -> None:
    assert ExpenseCategory.from_text(raw) is None


def test_lista_de_categorias_e_fechada() -> None:
    # Se este teste quebrar, alguém mudou a lista fixa — decisão do dono do
    # projeto, ver Docs/CLAUDE.md.
    assert ExpenseCategory.values() == (
        "Transporte",
        "Lazer",
        "Investimentos",
        "Casa",
        "Alimentação",
        "Assinaturas",
        "Outros",
    )

"""Categorias fixas de gasto.

Decisão de domínio (do usuário): categorias são um conjunto fechado.
Deixar o usuário criar categorias livremente, com o tempo, tende a gerar
categorias demais e tirar o propósito de uma visualização simples de gastos.
Se precisar de uma categoria nova no futuro, ela entra aqui, revisada
conscientemente — não em tempo de execução.
"""

from __future__ import annotations

import unicodedata
from enum import Enum


class ExpenseCategory(str, Enum):
    TRANSPORTE = "Transporte"
    LAZER = "Lazer"
    INVESTIMENTOS = "Investimentos"
    CASA = "Casa"
    ALIMENTACAO = "Alimentação"
    ASSINATURAS = "Assinaturas"
    OUTROS = "Outros"

    @classmethod
    def from_text(cls, raw: str) -> ExpenseCategory | None:
        """Resolve um texto livre (case/acento-insensível) para uma categoria.

        Retorna None se não bater com nenhuma categoria — quem chama decide
        se isso é erro ou motivo para perguntar de novo ao usuário.
        """
        normalized = _normalize(raw)
        for category in cls:
            if _normalize(category.value) == normalized:
                return category
        return None

    @classmethod
    def values(cls) -> tuple[str, ...]:
        return tuple(category.value for category in cls)


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.strip().lower())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))

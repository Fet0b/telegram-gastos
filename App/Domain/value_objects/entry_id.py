"""Identificador de um lançamento (gasto ou ganho).

Gastos e ganhos compartilham a mesma sequência de IDs: o `#12` mostrado
no /gastos identifica um único lançamento, sem precisar dizer se é gasto
ou ganho — é isso que permite um `/remover 12` sem ambiguidade.

É a identidade que faz de `Expense` e `Income` *entidades* (em DDD, uma
entidade é distinguida pelo ID, não pelos atributos: dois gastos de
R$ 10 no mesmo minuto continuam sendo dois gastos diferentes).
"""

from __future__ import annotations

from dataclasses import dataclass

from App.Domain.exceptions import InvalidEntryIdError


@dataclass(frozen=True, slots=True)
class EntryId:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise InvalidEntryIdError(str(self.value))

    @classmethod
    def from_text(cls, raw: str) -> EntryId:
        """Aceita '12' ou '#12' (o formato em que o /gastos mostra o ID)."""
        text = raw.strip().removeprefix("#")
        if not text.isdigit():
            raise InvalidEntryIdError(raw)
        return cls(int(text))

    def __str__(self) -> str:
        return f"#{self.value}"

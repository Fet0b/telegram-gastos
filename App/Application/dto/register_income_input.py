"""DTOs do caso de uso RegisterIncome."""

from __future__ import annotations

from dataclasses import dataclass

from App.Domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class ParsedGanhoCommand:
    """Resultado de interpretar o texto de `/ganho <valor> <título>`.

    `title` fica None quando o usuário mandou só o valor — a camada de
    Telegram pergunta o título de volta, nunca assume um default.
    """

    amount: Money
    title: str | None

    @property
    def is_complete(self) -> bool:
        return self.title is not None

"""DTOs do caso de uso RegisterExpense."""

from __future__ import annotations

from dataclasses import dataclass, field

from App.Domain.value_objects.category import ExpenseCategory
from App.Domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class ParsedGastoCommand:
    """Resultado de interpretar o texto de `/gasto <valor> <título> <categoria>`.

    Pode vir incompleto — `missing_fields` lista o que falta, para a camada
    de Telegram decidir como perguntar de volta ao usuário. `amount` é
    obrigatório para sequer chegar até aqui (ver `parse_gasto_command`).
    """

    amount: Money
    title: str | None
    category: ExpenseCategory | None
    missing_fields: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_complete(self) -> bool:
        return not self.missing_fields

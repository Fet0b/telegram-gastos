"""Caso de uso: registrar um ganho a partir do comando /ganho.

Formato: `/ganho <valor> <título...>`. Mesma lógica posicional do /gasto,
só que sem categoria: primeiro token = valor, todo o resto = título.
"""

from __future__ import annotations

from datetime import datetime

from App.Application.dto.register_income_input import ParsedGanhoCommand
from App.Domain.entities.income import Income
from App.Domain.exceptions import InvalidMoneyAmountError
from App.Domain.ports.entry_id_generator import EntryIdGenerator
from App.Domain.ports.income_repository import IncomeRepository
from App.Domain.value_objects.money import Money
from App.Domain.value_objects.telegram_user_id import TelegramUserId


def parse_ganho_command(tokens: list[str]) -> ParsedGanhoCommand:
    """Interpreta os argumentos de `/ganho`. O valor é obrigatório."""
    if not tokens:
        raise InvalidMoneyAmountError("")

    amount = Money.from_text(tokens[0])
    title = " ".join(tokens[1:]).strip() or None
    return ParsedGanhoCommand(amount=amount, title=title)


class RegisterIncomeUseCase:
    def __init__(self, repository: IncomeRepository, id_generator: EntryIdGenerator) -> None:
        self._repository = repository
        self._id_generator = id_generator

    def execute(
        self,
        *,
        user_id: TelegramUserId,
        amount: Money,
        title: str,
        occurred_at: datetime,
    ) -> Income:
        income = Income(
            id=self._id_generator.next_id(),
            user_id=user_id,
            amount=amount,
            title=title,
            occurred_at=occurred_at,
        )
        self._repository.add(income)
        return income

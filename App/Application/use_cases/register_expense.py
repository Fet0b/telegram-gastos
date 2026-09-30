"""Caso de uso: registrar um gasto a partir do comando /gasto.

Formato esperado: `/gasto <valor> <título...> <categoria>`. O título pode
ter espaços (ex: "mercado do bairro"), então a regra de interpretação é
posicional e não por delimitador especial:

  - primeiro token  -> valor (Money)
  - último token    -> categoria (precisa bater com uma ExpenseCategory)
  - tokens do meio  -> título

Se o usuário não informar título e/ou categoria, o campo correspondente
fica None e entra em `missing_fields` — quem chama (a camada de Telegram)
decide como perguntar de volta, sem a Application precisar saber nada de
Telegram.
"""

from __future__ import annotations

from datetime import datetime

from App.Application.dto.register_expense_input import ParsedGastoCommand
from App.Domain.entities.expense import Expense
from App.Domain.exceptions import InvalidMoneyAmountError
from App.Domain.ports.expense_repository import ExpenseRepository
from App.Domain.value_objects.category import ExpenseCategory
from App.Domain.value_objects.money import Money
from App.Domain.value_objects.telegram_user_id import TelegramUserId


def parse_gasto_command(tokens: list[str]) -> ParsedGastoCommand:
    """Interpreta os argumentos de `/gasto`. Levanta InvalidMoneyAmountError
    se o primeiro token não for um valor válido — isso é sempre obrigatório.
    """
    if not tokens:
        raise InvalidMoneyAmountError("")

    amount = Money.from_text(tokens[0])
    remainder = tokens[1:]

    if not remainder:
        return ParsedGastoCommand(
            amount=amount, title=None, category=None, missing_fields=("título", "categoria")
        )

    category = ExpenseCategory.from_text(remainder[-1])
    if category is not None:
        title_tokens = remainder[:-1]
    else:
        title_tokens = remainder

    title = " ".join(title_tokens).strip() or None

    missing: list[str] = []
    if title is None:
        missing.append("título")
    if category is None:
        missing.append("categoria")

    return ParsedGastoCommand(
        amount=amount, title=title, category=category, missing_fields=tuple(missing)
    )


class RegisterExpenseUseCase:
    def __init__(self, repository: ExpenseRepository) -> None:
        self._repository = repository

    def execute(
        self,
        *,
        user_id: TelegramUserId,
        amount: Money,
        title: str,
        category: ExpenseCategory,
        occurred_at: datetime,
    ) -> Expense:
        expense = Expense(
            user_id=user_id,
            amount=amount,
            title=title,
            category=category,
            occurred_at=occurred_at,
        )
        self._repository.add(expense)
        return expense

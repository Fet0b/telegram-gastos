"""Entidade Gasto (Expense).

Um gasto registrado por um usuário autorizado: quanto, em quê, em que
categoria e quando. O "quando" é o horário da mensagem no Telegram, não o
horário em que o backend processou — evita distorção se o bot ficar
momentaneamente sem processar o lote de updates.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from App.Domain.exceptions import InvalidExpenseError
from App.Domain.value_objects.category import ExpenseCategory
from App.Domain.value_objects.entry_id import EntryId
from App.Domain.value_objects.money import Money
from App.Domain.value_objects.telegram_user_id import TelegramUserId


@dataclass(frozen=True, slots=True)
class Expense:
    id: EntryId
    user_id: TelegramUserId
    amount: Money
    title: str
    category: ExpenseCategory
    occurred_at: datetime

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise InvalidExpenseError("O título do gasto não pode ser vazio.")
        if self.occurred_at.tzinfo is None:
            raise InvalidExpenseError("occurred_at precisa ser timezone-aware.")

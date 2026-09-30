"""Entidade Ganho (Income).

Uma entrada de dinheiro na conta (salário, freelance, reembolso...).
Diferente do gasto, não tem categoria — decisão do dono do projeto:
entradas são poucas e o título já basta para identificá-las.

Mesmas regras de horário do gasto: `occurred_at` é o horário da mensagem
no Telegram, sempre timezone-aware.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from App.Domain.exceptions import InvalidIncomeError
from App.Domain.value_objects.entry_id import EntryId
from App.Domain.value_objects.money import Money
from App.Domain.value_objects.telegram_user_id import TelegramUserId


@dataclass(frozen=True, slots=True)
class Income:
    id: EntryId
    user_id: TelegramUserId
    amount: Money
    title: str
    occurred_at: datetime

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise InvalidIncomeError("O título do ganho não pode ser vazio.")
        if self.occurred_at.tzinfo is None:
            raise InvalidIncomeError("occurred_at precisa ser timezone-aware.")

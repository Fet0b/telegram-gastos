"""Porta de saída para persistência de ganhos.

Espelha `ExpenseRepository`. São portas separadas (e não um "repositório
de lançamentos" genérico) porque gasto e ganho são entidades diferentes,
com regras diferentes — o gasto tem categoria, o ganho não.
"""

from __future__ import annotations

from typing import Protocol

from App.Domain.entities.income import Income
from App.Domain.value_objects.entry_id import EntryId
from App.Domain.value_objects.telegram_user_id import TelegramUserId


class IncomeRepository(Protocol):
    def add(self, income: Income) -> None:
        """Persiste um novo ganho."""
        ...

    def list_by_user(self, user_id: TelegramUserId) -> list[Income]:
        """Retorna todos os ganhos de um usuário, em qualquer ordem."""
        ...

    def remove(self, user_id: TelegramUserId, entry_id: EntryId) -> Income | None:
        """Remove o ganho `entry_id` do usuário e o devolve, ou None."""
        ...

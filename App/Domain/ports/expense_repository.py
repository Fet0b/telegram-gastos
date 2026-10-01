"""Porta de saída para persistência de gastos.

O Domain e a Application conhecem apenas esta interface. A implementação
concreta (Excel, hoje; poderia ser um banco amanhã) vive em Infrastructure
e é injetada em tempo de execução — Domain/Application nunca importam
openpyxl nem sabem que existe uma planilha.
"""

from __future__ import annotations

from typing import Protocol

from App.Domain.entities.expense import Expense
from App.Domain.value_objects.entry_id import EntryId
from App.Domain.value_objects.telegram_user_id import TelegramUserId


class ExpenseRepository(Protocol):
    def add(self, expense: Expense) -> None:
        """Persiste um novo gasto."""
        ...

    def list_by_user(self, user_id: TelegramUserId) -> list[Expense]:
        """Retorna todos os gastos de um usuário, em qualquer ordem."""
        ...

    def remove(self, user_id: TelegramUserId, entry_id: EntryId) -> Expense | None:
        """Remove o gasto `entry_id` do usuário e o devolve.

        Retorna None se não existir um gasto com esse ID *daquele usuário*.
        """
        ...

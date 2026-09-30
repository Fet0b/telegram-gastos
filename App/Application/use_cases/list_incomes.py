"""Caso de uso: listar os ganhos de um usuário."""

from __future__ import annotations

from App.Domain.entities.income import Income
from App.Domain.ports.income_repository import IncomeRepository
from App.Domain.value_objects.telegram_user_id import TelegramUserId


class ListIncomesUseCase:
    def __init__(self, repository: IncomeRepository) -> None:
        self._repository = repository

    def raw(self, user_id: TelegramUserId) -> list[Income]:
        """Ganhos em ordem cronológica (mais antigo primeiro)."""
        return sorted(self._repository.list_by_user(user_id), key=lambda i: i.occurred_at)

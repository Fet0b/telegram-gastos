"""Porta de saída para a allowlist de usuários autorizados.

Hoje a implementação lê de variável de ambiente (ver Docs/CLAUDE.md,
seção "Permissionamento"), mas a Application só depende desta interface —
trocar para outro mecanismo de credenciais não deveria tocar em nenhum
caso de uso.
"""

from __future__ import annotations

from typing import Protocol

from App.Domain.value_objects.telegram_user_id import TelegramUserId


class AuthorizedUsersProvider(Protocol):
    def is_authorized(self, user_id: TelegramUserId) -> bool: ...

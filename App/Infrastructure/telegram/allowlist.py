"""Implementação da porta `AuthorizedUsersProvider` a partir de uma lista fixa.

A lista vem de `AUTHORIZED_USER_IDS` no `.env` (lida em `config/settings.py`)
e fica em memória durante toda a execução — mudar a allowlist exige
reiniciar o container, o que é aceitável para uso pessoal.

Note que a classe não herda de `AuthorizedUsersProvider`: basta ter o
método `is_authorized` com a mesma assinatura para cumprir o `Protocol`.
"""

from __future__ import annotations

from collections.abc import Iterable

from App.Domain.value_objects.telegram_user_id import TelegramUserId


class StaticAuthorizedUsersProvider:
    def __init__(self, user_ids: Iterable[int]) -> None:
        self._user_ids = frozenset(user_ids)

    def is_authorized(self, user_id: TelegramUserId) -> bool:
        return user_id.value in self._user_ids

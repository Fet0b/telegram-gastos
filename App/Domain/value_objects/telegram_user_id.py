"""Identificador de usuário do Telegram.

É o `from.id` do update — numérico, imutável, único por conta do Telegram.
Nunca o `username` (pode mudar) nem o `chat.id` (para grupos, é outro
número). Ver Docs/CLAUDE.md, seção "Permissionamento".
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TelegramUserId:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError(f"TelegramUserId inválido: {self.value}")

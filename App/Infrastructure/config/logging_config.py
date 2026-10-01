"""Configuração de logs, com censura de segredos.

Por que censurar em vez de só "tomar cuidado para não logar o token":
o token do bot faz parte da URL de toda chamada à Bot API
(`https://api.telegram.org/bot<TOKEN>/getUpdates`). Bibliotecas de
terceiros logam essa URL sem pedir licença — o `httpx`, usado pelo
python-telegram-bot, faz isso em nível INFO a cada requisição, e
mensagens de exceção de rede também podem carregá-la. Um formatter que
substitui o token na linha final pega todos esses casos de uma vez,
inclusive tracebacks.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable

REDACTED = "***"
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


class RedactingFormatter(logging.Formatter):
    def __init__(self, secrets: Iterable[str], fmt: str = LOG_FORMAT) -> None:
        super().__init__(fmt)
        self._secrets = tuple(secret for secret in secrets if secret)

    def format(self, record: logging.LogRecord) -> str:
        text = super().format(record)
        for secret in self._secrets:
            text = text.replace(secret, REDACTED)
        return text


def configure_logging(secrets: Iterable[str], level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(RedactingFormatter(secrets))

    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)

    # Segunda camada de defesa: o httpx loga toda requisição (com a URL que
    # contém o token) em INFO. Mesmo censurado, é ruído a cada 30s.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

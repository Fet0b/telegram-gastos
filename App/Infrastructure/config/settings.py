"""Configuração da aplicação, lida de variáveis de ambiente (`.env`).

Toda a leitura e validação de env vars acontece aqui, uma vez, na partida.
O resto do sistema recebe um `Settings` já validado e tipado — nenhuma
outra parte do código chama `os.environ` diretamente.

Falhar cedo é intencional: se o token ou a allowlist estiverem faltando,
o container para na hora com uma mensagem clara, em vez de subir e só
quebrar quando a primeira mensagem chegar.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv

DEFAULT_TIMEZONE = "America/Sao_Paulo"
DEFAULT_EXCEL_FILE_PATH = "/data/gastos.xlsx"
DEFAULT_POLLING_INTERVAL_SECONDS = 30


class ConfigurationError(Exception):
    """Configuração ausente ou inválida. A mensagem nunca inclui o token."""


@dataclass(frozen=True, slots=True)
class Settings:
    # repr=False: se alguém logar/printar o Settings, o token não aparece.
    telegram_bot_token: str = field(repr=False)
    authorized_user_ids: frozenset[int]
    timezone: ZoneInfo
    excel_file_path: Path
    polling_interval_seconds: int


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    """Lê as configurações do ambiente.

    Sem argumento, carrega o `.env` (se existir) e usa `os.environ`. Os
    testes passam um dicionário direto, sem tocar no ambiente real.
    """
    if environ is None:
        load_dotenv()
        environ = os.environ

    return Settings(
        telegram_bot_token=_required(environ, "TELEGRAM_BOT_TOKEN"),
        authorized_user_ids=_parse_user_ids(_required(environ, "AUTHORIZED_USER_IDS")),
        timezone=_parse_timezone(environ.get("TIMEZONE") or DEFAULT_TIMEZONE),
        excel_file_path=Path(environ.get("EXCEL_FILE_PATH") or DEFAULT_EXCEL_FILE_PATH),
        polling_interval_seconds=_parse_positive_int(
            "POLLING_INTERVAL_SECONDS",
            environ.get("POLLING_INTERVAL_SECONDS") or str(DEFAULT_POLLING_INTERVAL_SECONDS),
        ),
    )


def _required(environ: Mapping[str, str], key: str) -> str:
    value = (environ.get(key) or "").strip()
    if not value:
        raise ConfigurationError(f"Variável de ambiente obrigatória ausente: {key}.")
    return value


def _parse_user_ids(raw: str) -> frozenset[int]:
    """'123, 456' -> {123, 456}. Aceita espaços e vírgula sobrando no fim."""
    ids: set[int] = set()
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if not chunk.isdigit() or int(chunk) <= 0:
            raise ConfigurationError(
                f"AUTHORIZED_USER_IDS contém um valor que não é um user.id numérico: {chunk!r}."
            )
        ids.add(int(chunk))
    if not ids:
        raise ConfigurationError("AUTHORIZED_USER_IDS precisa ter pelo menos um user.id.")
    return frozenset(ids)


def _parse_timezone(raw: str) -> ZoneInfo:
    try:
        return ZoneInfo(raw.strip())
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ConfigurationError(f"TIMEZONE inválido: {raw!r}.") from exc


def _parse_positive_int(key: str, raw: str) -> int:
    try:
        value = int(raw.strip())
    except ValueError as exc:
        raise ConfigurationError(f"{key} precisa ser um número inteiro: {raw!r}.") from exc
    if value <= 0:
        raise ConfigurationError(f"{key} precisa ser maior que zero: {raw!r}.")
    return value

"""Porta de saída que emite a identidade de novos lançamentos.

Por que uma porta e não um contador no Domain: o próximo ID depende do que
já foi persistido (inclusive entre reinícios do container), então só a
persistência sabe respondê-lo. É o padrão "o repositório fornece a próxima
identidade" — a entidade já nasce com ID, nunca existe um gasto "sem ID
ainda".

Contrato: IDs são crescentes e **nunca reaproveitados**, mesmo depois de
uma remoção. Senão, remover o #12 e registrar outro gasto recriaria um
#12, e um `/remover 12` repetido apagaria o lançamento errado.
"""

from __future__ import annotations

from typing import Protocol

from App.Domain.value_objects.entry_id import EntryId


class EntryIdGenerator(Protocol):
    def next_id(self) -> EntryId: ...

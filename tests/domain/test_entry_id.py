from __future__ import annotations

import pytest

from App.Domain.exceptions import InvalidEntryIdError
from App.Domain.value_objects.entry_id import EntryId


@pytest.mark.parametrize(("raw", "expected"), [("12", 12), ("#12", 12), (" 7 ", 7)])
def test_from_text_aceita_numero_com_ou_sem_cerquilha(raw: str, expected: int) -> None:
    assert EntryId.from_text(raw) == EntryId(expected)


@pytest.mark.parametrize("raw", ["", "abc", "0", "-3", "1.5", "#"])
def test_from_text_rejeita_invalidos(raw: str) -> None:
    with pytest.raises(InvalidEntryIdError):
        EntryId.from_text(raw)


def test_str_mostra_com_cerquilha() -> None:
    assert str(EntryId(12)) == "#12"

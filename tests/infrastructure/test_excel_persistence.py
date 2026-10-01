"""Testes de integração da persistência em Excel, contra um .xlsx real em tmp_path."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from openpyxl import load_workbook

from App.Domain.value_objects.entry_id import EntryId
from App.Domain.value_objects.telegram_user_id import TelegramUserId
from App.Infrastructure.persistence.excel_entry_id_generator import ExcelEntryIdGenerator
from App.Infrastructure.persistence.excel_expense_repository import ExcelExpenseRepository
from App.Infrastructure.persistence.excel_income_repository import ExcelIncomeRepository
from App.Infrastructure.persistence.excel_workbook import (
    CONTROL_SHEET,
    EXPENSES_SHEET,
    CorruptedSpreadsheetError,
    ExcelWorkbook,
)
from tests.builders import make_expense, make_income

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
USER = TelegramUserId(1)


@pytest.fixture
def workbook(tmp_path: Path) -> ExcelWorkbook:
    return ExcelWorkbook(tmp_path / "data" / "gastos.xlsx", SAO_PAULO)


def test_planilha_inexistente_lista_vazio_sem_criar_arquivo(workbook: ExcelWorkbook) -> None:
    assert ExcelExpenseRepository(workbook).list_by_user(USER) == []
    assert not workbook.path.exists()


def test_gasto_ida_e_volta_preserva_decimal_e_timezone(workbook: ExcelWorkbook) -> None:
    repository = ExcelExpenseRepository(workbook)
    # 15:30 UTC = 12:30 em São Paulo
    occurred_at = datetime(2026, 3, 1, 15, 30, tzinfo=UTC)
    expense = make_expense(id=1, amount="0,10", occurred_at=occurred_at)
    repository.add(expense)

    [loaded] = repository.list_by_user(USER)
    assert loaded == expense  # igualdade de entidade inteira, inclusive o instante
    assert loaded.amount.amount == Decimal("0.10")

    sheet = load_workbook(workbook.path)[EXPENSES_SHEET]
    assert sheet["B2"].value == datetime(2026, 3, 1, 12, 30)  # hora local, sem fuso


def test_lista_apenas_do_usuario(workbook: ExcelWorkbook) -> None:
    repository = ExcelExpenseRepository(workbook)
    repository.add(make_expense(id=1, user=1))
    repository.add(make_expense(id=2, user=2))
    assert [e.id for e in repository.list_by_user(USER)] == [EntryId(1)]


def test_ganho_ida_e_volta(workbook: ExcelWorkbook) -> None:
    repository = ExcelIncomeRepository(workbook)
    income = make_income(id=3, amount="5000")
    repository.add(income)
    assert repository.list_by_user(USER) == [income]


def test_remove_so_do_proprio_usuario(workbook: ExcelWorkbook) -> None:
    repository = ExcelExpenseRepository(workbook)
    repository.add(make_expense(id=1, user=1))
    repository.add(make_expense(id=2, user=2))

    assert repository.remove(USER, EntryId(2)) is None  # é do usuário 2
    removed = repository.remove(USER, EntryId(1))
    assert removed is not None and removed.id == EntryId(1)
    assert repository.list_by_user(USER) == []
    assert len(repository.list_by_user(TelegramUserId(2))) == 1


def test_ids_sao_sequenciais_e_nunca_reaproveitados(workbook: ExcelWorkbook) -> None:
    ids = ExcelEntryIdGenerator(workbook)
    expenses = ExcelExpenseRepository(workbook)

    first = ids.next_id()
    expenses.add(make_expense(id=first.value))
    second = ids.next_id()
    expenses.add(make_expense(id=second.value))
    assert (first, second) == (EntryId(1), EntryId(2))

    expenses.remove(USER, second)
    assert ids.next_id() == EntryId(3)  # não volta para 2


def test_id_pula_ids_colados_manualmente_na_planilha(workbook: ExcelWorkbook) -> None:
    ExcelExpenseRepository(workbook).add(make_expense(id=50))
    assert ExcelEntryIdGenerator(workbook).next_id() == EntryId(51)


def test_aba_de_controle_fica_oculta(workbook: ExcelWorkbook) -> None:
    ExcelEntryIdGenerator(workbook).next_id()
    assert load_workbook(workbook.path)[CONTROL_SHEET].sheet_state == "hidden"


def test_nao_deixa_arquivo_temporario(workbook: ExcelWorkbook) -> None:
    ExcelExpenseRepository(workbook).add(make_expense())
    assert [p.name for p in workbook.path.parent.iterdir()] == ["gastos.xlsx"]


def test_erro_no_meio_da_escrita_nao_altera_planilha(workbook: ExcelWorkbook) -> None:
    ExcelExpenseRepository(workbook).add(make_expense(id=1))
    before = workbook.path.read_bytes()

    with pytest.raises(RuntimeError), workbook.writing() as wb:
        wb[EXPENSES_SHEET].append((2, None, 1, 1, "x", "Lazer"))
        raise RuntimeError("falha simulada")

    assert workbook.path.read_bytes() == before


def test_linha_editada_errada_aponta_aba_e_linha(workbook: ExcelWorkbook) -> None:
    ExcelExpenseRepository(workbook).add(make_expense(id=1))
    wb = load_workbook(workbook.path)
    wb[EXPENSES_SHEET]["F2"] = "Comida"  # categoria que não existe
    wb.save(workbook.path)

    with pytest.raises(CorruptedSpreadsheetError, match="Gastos.*linha 2"):
        ExcelExpenseRepository(workbook).list_by_user(USER)

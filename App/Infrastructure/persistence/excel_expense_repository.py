"""Implementação Excel da porta `ExpenseRepository`.

Traduz entre a entidade `Expense` e uma linha da aba "Gastos". Toda a
lógica de arquivo (lock, criação, save atômico) fica no `ExcelWorkbook`;
aqui mora só o mapeamento entidade <-> linha.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from App.Domain.entities.expense import Expense
from App.Domain.value_objects.category import ExpenseCategory
from App.Domain.value_objects.entry_id import EntryId
from App.Domain.value_objects.money import Money
from App.Domain.value_objects.telegram_user_id import TelegramUserId
from App.Infrastructure.persistence.excel_workbook import (
    DATE_FORMAT,
    EXPENSES_SHEET,
    MONEY_FORMAT,
    CorruptedSpreadsheetError,
    ExcelWorkbook,
    data_rows,
)


class ExcelExpenseRepository:
    def __init__(self, workbook: ExcelWorkbook) -> None:
        self._workbook = workbook

    def add(self, expense: Expense) -> None:
        with self._workbook.writing() as workbook:
            sheet = workbook[EXPENSES_SHEET]
            sheet.append(
                (
                    expense.id.value,
                    self._workbook.to_excel_datetime(expense.occurred_at),
                    expense.user_id.value,
                    # Decimal vai para o XML da planilha como texto ("45.90"),
                    # sem passar por float na escrita.
                    expense.amount.amount,
                    expense.title,
                    expense.category.value,
                )
            )
            sheet.cell(sheet.max_row, 2).number_format = DATE_FORMAT
            sheet.cell(sheet.max_row, 4).number_format = MONEY_FORMAT

    def list_by_user(self, user_id: TelegramUserId) -> list[Expense]:
        with self._workbook.reading() as workbook:
            sheet = workbook[EXPENSES_SHEET]
            return [
                expense
                for index, row in data_rows(sheet)
                if (expense := self._to_entity(index, row)).user_id == user_id
            ]

    def remove(self, user_id: TelegramUserId, entry_id: EntryId) -> Expense | None:
        with self._workbook.writing() as workbook:
            sheet = workbook[EXPENSES_SHEET]
            for index, row in data_rows(sheet):
                expense = self._to_entity(index, row)
                if expense.id == entry_id and expense.user_id == user_id:
                    sheet.delete_rows(index)
                    return expense
        return None

    def _to_entity(self, index: int, row: tuple[object, ...]) -> Expense:
        try:
            entry_id, occurred_at, user_id, amount, title, category = row[:6]
            if not isinstance(occurred_at, datetime):
                raise ValueError(f"data inválida: {occurred_at!r}")
            return Expense(
                id=EntryId(int(str(entry_id))),
                user_id=TelegramUserId(int(str(user_id))),
                # Na leitura o openpyxl devolve float/int; str() + Decimal
                # recupera o valor exato para quantias com 2 casas.
                amount=Money(Decimal(str(amount)).quantize(Decimal("0.01"))),
                title=str(title),
                category=ExpenseCategory(str(category)),
                occurred_at=self._workbook.from_excel_datetime(occurred_at),
            )
        except Exception as exc:  # qualquer falha de conversão = linha corrompida
            raise CorruptedSpreadsheetError(EXPENSES_SHEET, index, str(exc)) from exc

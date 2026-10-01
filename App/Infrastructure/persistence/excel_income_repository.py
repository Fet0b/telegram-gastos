"""Implementação Excel da porta `IncomeRepository` (aba "Ganhos").

Mesma estrutura do `ExcelExpenseRepository`, sem a coluna de categoria.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from App.Domain.entities.income import Income
from App.Domain.value_objects.entry_id import EntryId
from App.Domain.value_objects.money import Money
from App.Domain.value_objects.telegram_user_id import TelegramUserId
from App.Infrastructure.persistence.excel_workbook import (
    DATE_FORMAT,
    INCOMES_SHEET,
    MONEY_FORMAT,
    CorruptedSpreadsheetError,
    ExcelWorkbook,
    data_rows,
)


class ExcelIncomeRepository:
    def __init__(self, workbook: ExcelWorkbook) -> None:
        self._workbook = workbook

    def add(self, income: Income) -> None:
        with self._workbook.writing() as workbook:
            sheet = workbook[INCOMES_SHEET]
            sheet.append(
                (
                    income.id.value,
                    self._workbook.to_excel_datetime(income.occurred_at),
                    income.user_id.value,
                    income.amount.amount,
                    income.title,
                )
            )
            sheet.cell(sheet.max_row, 2).number_format = DATE_FORMAT
            sheet.cell(sheet.max_row, 4).number_format = MONEY_FORMAT

    def list_by_user(self, user_id: TelegramUserId) -> list[Income]:
        with self._workbook.reading() as workbook:
            sheet = workbook[INCOMES_SHEET]
            return [
                income
                for index, row in data_rows(sheet)
                if (income := self._to_entity(index, row)).user_id == user_id
            ]

    def remove(self, user_id: TelegramUserId, entry_id: EntryId) -> Income | None:
        with self._workbook.writing() as workbook:
            sheet = workbook[INCOMES_SHEET]
            for index, row in data_rows(sheet):
                income = self._to_entity(index, row)
                if income.id == entry_id and income.user_id == user_id:
                    sheet.delete_rows(index)
                    return income
        return None

    def _to_entity(self, index: int, row: tuple[object, ...]) -> Income:
        try:
            entry_id, occurred_at, user_id, amount, title = row[:5]
            if not isinstance(occurred_at, datetime):
                raise ValueError(f"data inválida: {occurred_at!r}")
            return Income(
                id=EntryId(int(str(entry_id))),
                user_id=TelegramUserId(int(str(user_id))),
                amount=Money(Decimal(str(amount)).quantize(Decimal("0.01"))),
                title=str(title),
                occurred_at=self._workbook.from_excel_datetime(occurred_at),
            )
        except Exception as exc:
            raise CorruptedSpreadsheetError(INCOMES_SHEET, index, str(exc)) from exc

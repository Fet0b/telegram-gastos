"""Implementação Excel da porta `EntryIdGenerator`.

Guarda o último ID emitido na célula B1 da aba oculta "_controle".
Por que não usar só "maior ID existente + 1": depois de remover o último
lançamento, esse cálculo devolveria o mesmo ID de novo — e um `/remover`
repetido apagaria o lançamento errado. O contador persistido nunca volta.

Por robustez, também considera o maior ID presente nas abas: se alguém
colar linhas na planilha à mão com IDs altos, o contador pula para depois
deles em vez de gerar duplicata.
"""

from __future__ import annotations

from App.Domain.value_objects.entry_id import EntryId
from App.Infrastructure.persistence.excel_workbook import (
    CONTROL_SHEET,
    EXPENSES_SHEET,
    INCOMES_SHEET,
    ExcelWorkbook,
    data_rows,
)


class ExcelEntryIdGenerator:
    def __init__(self, workbook: ExcelWorkbook) -> None:
        self._workbook = workbook

    def next_id(self) -> EntryId:
        with self._workbook.writing() as workbook:
            control = workbook[CONTROL_SHEET]
            last_issued = int(str(control["B1"].value or 0))

            highest_in_sheets = max(
                (
                    int(str(row[0]))
                    for name in (EXPENSES_SHEET, INCOMES_SHEET)
                    for _, row in data_rows(workbook[name])
                    if str(row[0]).isdigit()
                ),
                default=0,
            )

            next_value = max(last_issued, highest_in_sheets) + 1
            control["B1"] = next_value
            return EntryId(next_value)

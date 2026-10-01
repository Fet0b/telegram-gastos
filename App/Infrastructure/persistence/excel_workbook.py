"""Acesso de baixo nível à planilha Excel de lançamentos.

Os três adaptadores de persistência (gastos, ganhos e gerador de IDs)
compartilham um único `ExcelWorkbook`, que concentra tudo que é "detalhe
de arquivo": criar a planilha na primeira vez, serializar acesso com um
lock e gravar de forma atômica.

Layout da planilha:

  - aba "Gastos":    ID | Data | ID do usuário | Valor (R$) | Título | Categoria
  - aba "Ganhos":    ID | Data | ID do usuário | Valor (R$) | Título
  - aba "_controle" (oculta): último ID emitido — ver `excel_entry_id_generator.py`

As abas visíveis são pensadas para o dono abrir no Excel e ler direto.
"""

from __future__ import annotations

import os
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font
from openpyxl.worksheet.worksheet import Worksheet

EXPENSES_SHEET = "Gastos"
INCOMES_SHEET = "Ganhos"
CONTROL_SHEET = "_controle"

EXPENSES_HEADER = ("ID", "Data", "ID do usuário", "Valor (R$)", "Título", "Categoria")
INCOMES_HEADER = ("ID", "Data", "ID do usuário", "Valor (R$)", "Título")

DATE_FORMAT = "dd/mm/yyyy hh:mm"
MONEY_FORMAT = "#,##0.00"


class CorruptedSpreadsheetError(Exception):
    """Uma linha da planilha não pôde ser convertida de volta em entidade.

    Acontece, na prática, quando alguém edita a planilha à mão e deixa um
    valor inválido (categoria digitada errada, valor em texto...). A
    mensagem aponta aba e linha para facilitar a correção.
    """

    def __init__(self, sheet: str, row: int, reason: str) -> None:
        super().__init__(f"Planilha inválida na aba {sheet!r}, linha {row}: {reason}")


class ExcelWorkbook:
    def __init__(self, path: Path, timezone: ZoneInfo) -> None:
        self.path = path
        self.timezone = timezone
        # RLock (reentrante): o gerador de IDs e os repositórios podem ser
        # chamados em sequência pela mesma thread sem travar a si mesmos.
        self._lock = threading.RLock()

    @contextmanager
    def reading(self) -> Iterator[Workbook]:
        """Abre a planilha só para leitura (nada é salvo ao final)."""
        with self._lock:
            yield self._load()

    @contextmanager
    def writing(self) -> Iterator[Workbook]:
        """Abre a planilha para escrita e salva atomicamente ao final.

        Se o bloco `with` levantar exceção, nada é salvo — a planilha em
        disco continua exatamente como estava.
        """
        with self._lock:
            workbook = self._load()
            yield workbook
            self._save_atomically(workbook)

    # --- conversão de datas -------------------------------------------------
    # O Excel não guarda fuso horário. Gravamos a hora local do TIMEZONE
    # configurado (é o que o dono quer ver ao abrir a planilha) e, na
    # leitura, reanexamos o mesmo fuso para voltar a um datetime "aware".

    def to_excel_datetime(self, value: datetime) -> datetime:
        return value.astimezone(self.timezone).replace(tzinfo=None)

    def from_excel_datetime(self, value: datetime) -> datetime:
        return value.replace(tzinfo=self.timezone)

    # --- detalhes de arquivo ------------------------------------------------

    def _load(self) -> Workbook:
        if not self.path.exists():
            return self._create()
        workbook = load_workbook(self.path)
        self._ensure_sheets(workbook)
        return workbook

    def _create(self) -> Workbook:
        workbook = Workbook()
        # Workbook() já vem com uma aba vazia; reaproveitamos como "Gastos".
        default = workbook.active
        assert default is not None
        default.title = EXPENSES_SHEET
        self._ensure_sheets(workbook)
        return workbook

    def _ensure_sheets(self, workbook: Workbook) -> None:
        """Cria as abas que faltarem — cobre planilha nova e planilha antiga."""
        for name, header in ((EXPENSES_SHEET, EXPENSES_HEADER), (INCOMES_SHEET, INCOMES_HEADER)):
            if name not in workbook.sheetnames:
                workbook.create_sheet(name)
            sheet = workbook[name]
            if sheet.max_row == 1 and sheet.cell(1, 1).value is None:
                _write_header(sheet, header)

        if CONTROL_SHEET not in workbook.sheetnames:
            control = workbook.create_sheet(CONTROL_SHEET)
            control.append(("ultimo_id", 0))
            control.sheet_state = "hidden"

    def _save_atomically(self, workbook: Workbook) -> None:
        """Salva num arquivo temporário e troca pelo definitivo.

        `os.replace` é atômico no mesmo sistema de arquivos: quem ler a
        planilha vê a versão antiga inteira ou a nova inteira, nunca um
        arquivo pela metade — mesmo se o container morrer durante o save.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(f".{self.path.name}.tmp")
        workbook.save(temporary)
        os.replace(temporary, self.path)


def _write_header(sheet: Worksheet, header: tuple[str, ...]) -> None:
    # Escreve célula a célula na linha 1 em vez de `sheet.append`: só de
    # *ler* `sheet.cell(1, 1)` (em `_ensure_sheets`) o openpyxl cria a
    # célula e avança o cursor interno — um `append` aqui cairia na linha 2.
    for column, title in enumerate(header, start=1):
        sheet.cell(row=1, column=column, value=title).font = Font(bold=True)
    sheet.freeze_panes = "A2"
    widths = {"A": 8, "B": 18, "C": 16, "D": 14, "E": 40, "F": 16}
    for column, width in widths.items():
        sheet.column_dimensions[column].width = width


def data_rows(sheet: Worksheet) -> Iterator[tuple[int, tuple[object, ...]]]:
    """Itera (número da linha, valores) pulando o cabeçalho e linhas vazias."""
    for index, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        if all(value is None for value in row):
            continue
        yield index, row

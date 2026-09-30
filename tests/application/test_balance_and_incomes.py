from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from App.Application.use_cases.get_balance import GetBalanceUseCase
from App.Application.use_cases.list_incomes import ListIncomesUseCase
from App.Domain.value_objects.telegram_user_id import TelegramUserId
from tests.builders import make_expense, make_income
from tests.fakes import InMemoryExpenseRepository, InMemoryIncomeRepository

USER = TelegramUserId(1)


def test_saldo_positivo_e_negativo() -> None:
    expenses = InMemoryExpenseRepository()
    incomes = InMemoryIncomeRepository()
    incomes.add(make_income(id=1, amount="1000"))
    expenses.add(make_expense(id=2, amount="250,50"))
    expenses.add(make_expense(id=3, user=2, amount="9999"))  # outro usuário não entra
    use_case = GetBalanceUseCase(expenses, incomes)

    balance = use_case.execute(USER)
    assert balance.total_incomes == Decimal("1000.00")
    assert balance.total_expenses == Decimal("250.50")
    assert balance.balance == Decimal("749.50")

    expenses.add(make_expense(id=4, amount="800"))
    assert use_case.execute(USER).balance == Decimal("-50.50")


def test_saldo_zerado_sem_lancamentos() -> None:
    balance = GetBalanceUseCase(InMemoryExpenseRepository(), InMemoryIncomeRepository()).execute(
        USER
    )
    assert balance.balance == Decimal("0")


def test_lista_ganhos_em_ordem_cronologica() -> None:
    incomes = InMemoryIncomeRepository()
    late = make_income(id=1, occurred_at=datetime(2026, 2, 1, tzinfo=UTC))
    early = make_income(id=2, occurred_at=datetime(2026, 1, 1, tzinfo=UTC))
    incomes.add(late)
    incomes.add(early)
    assert ListIncomesUseCase(incomes).raw(USER) == [early, late]

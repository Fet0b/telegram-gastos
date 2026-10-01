"""Valor monetário.

Usa `Decimal`, nunca `float`. Ponto flutuante binário não representa
frações decimais exatamente (0.1 + 0.2 != 0.3), o que é inaceitável para
dinheiro — mesmo o comando do bot pedindo um "double" no vocabulário do
usuário, a representação interna correta é decimal.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from App.Domain.exceptions import InvalidMoneyAmountError

TWO_PLACES = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal

    def __post_init__(self) -> None:
        # `is_finite()` vem antes da comparação: Decimal("NaN") <= 0 não
        # retorna False, levanta InvalidOperation.
        if not self.amount.is_finite() or self.amount <= 0:
            raise InvalidMoneyAmountError(str(self.amount))

    @classmethod
    def from_text(cls, raw: str) -> Money:
        """Aceita tanto '45.90' quanto '45,90' (formato brasileiro comum)."""
        normalized = raw.strip().replace(",", ".")
        try:
            amount = Decimal(normalized).quantize(TWO_PLACES)
            return cls(amount)
        except (InvalidOperation, InvalidMoneyAmountError) as exc:
            # Relevanta com o texto original, para a mensagem de erro mostrar
            # o que o usuário digitou ("-5"), e não o valor normalizado ("-5.00").
            raise InvalidMoneyAmountError(raw) from exc

    def __str__(self) -> str:
        return f"R$ {self.amount:.2f}"

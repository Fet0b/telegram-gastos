"""Exceções de domínio.

Representam violações de regras de negócio — nunca erros de infraestrutura
(rede, arquivo, Telegram). Camadas externas traduzem estas exceções para o
que fizer sentido nelas (ex: uma mensagem de resposta no bot).
"""


class DomainError(Exception):
    """Classe base para toda exceção de regra de negócio do domínio."""


class InvalidCategoryError(DomainError):
    """Levantada quando uma categoria informada não está entre as fixas."""

    def __init__(self, category_raw: str, valid_categories: tuple[str, ...]) -> None:
        self.category_raw = category_raw
        self.valid_categories = valid_categories
        super().__init__(
            f"Categoria inválida: {category_raw!r}. "
            f"Categorias válidas: {', '.join(valid_categories)}."
        )


class InvalidMoneyAmountError(DomainError):
    """Levantada quando um valor monetário é inválido (não numérico, <= 0)."""

    def __init__(self, amount_raw: str) -> None:
        self.amount_raw = amount_raw
        super().__init__(f"Valor inválido: {amount_raw!r}. Use um número maior que zero.")


class InvalidExpenseError(DomainError):
    """Levantada quando os dados de um gasto violam uma regra da entidade."""


class UnauthorizedUserError(DomainError):
    """Levantada quando um usuário do Telegram não está na allowlist."""

    def __init__(self, telegram_user_id: int) -> None:
        self.telegram_user_id = telegram_user_id
        super().__init__(f"Usuário não autorizado: {telegram_user_id}.")

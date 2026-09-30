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


class InvalidIncomeError(DomainError):
    """Levantada quando os dados de um ganho violam uma regra da entidade."""


class InvalidEntryIdError(DomainError):
    """Levantada quando o texto informado não é um ID de lançamento válido."""

    def __init__(self, entry_id_raw: str) -> None:
        self.entry_id_raw = entry_id_raw
        super().__init__(f"ID inválido: {entry_id_raw!r}. Use o número mostrado no /gastos.")


class EntryNotFoundError(DomainError):
    """Levantada quando um lançamento não existe para aquele usuário.

    Um ID que existe mas pertence a outro usuário também cai aqui — de
    propósito, para não revelar a existência de lançamentos alheios.
    """

    def __init__(self, entry_id: int) -> None:
        self.entry_id = entry_id
        super().__init__(f"Nenhum lançamento #{entry_id} encontrado.")


class UnauthorizedUserError(DomainError):
    """Levantada quando um usuário do Telegram não está na allowlist."""

    def __init__(self, telegram_user_id: int) -> None:
        self.telegram_user_id = telegram_user_id
        super().__init__(f"Usuário não autorizado: {telegram_user_id}.")

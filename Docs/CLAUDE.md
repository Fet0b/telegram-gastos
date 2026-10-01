# gastos-bot — instruções do projeto

Bot de Telegram pessoal para registrar gastos, arquitetado em **Domain-Driven
Design**, backend em **Python puro**, rodando num **container Docker local**
sem nenhuma porta exposta. Projeto de estudos — priorize clareza e
aderência aos princípios de DDD sobre atalhos.

Este repositório é **público desde o início**. Trate isso como restrição em
todo commit, PR, log e mensagem de erro: nunca token, IP, caminho de
servidor real, nome de usuário do Telegram real ou qualquer dado dos
gastos reais do dono do bot.

## Por que Telegram + long polling (sem porta exposta)

O bot consome a Bot API do Telegram via **long polling** (`getUpdates`),
nunca via webhook. Quem inicia a conexão é sempre o bot, de dentro do
container para fora — o Telegram nunca abre uma conexão de entrada no
servidor. Por isso não é necessário port forwarding no roteador, proxy
reverso nem VPN para o bot funcionar. Não implemente webhook neste
projeto a menos que isso mude explicitamente por decisão do dono.

Consequência prática: o polling deve rodar a cada **30s**
(`POLLING_INTERVAL_SECONDS` no `.env`) — suficiente para uso pessoal e
mantém o consumo de CPU/memória do container mínimo, que é um requisito
do projeto.

## Camadas (DDD)

```
App/
├── Domain/          # regras de negócio puras — zero import externo
│   ├── entities/        # Expense
│   ├── value_objects/   # Money (Decimal!), ExpenseCategory, TelegramUserId
│   ├── ports/           # Protocols: ExpenseRepository, AuthorizedUsersProvider
│   └── exceptions.py    # DomainError e subclasses
├── Application/     # casos de uso — orquestra o Domain, não conhece Telegram/Excel
│   ├── use_cases/       # RegisterExpenseUseCase, ListExpensesUseCase
│   └── dto/             # objetos de transporte entre camadas
└── Infrastructure/  # tudo que fala com o mundo externo
    ├── telegram/        # handlers, bot, allowlist runtime
    ├── persistence/      # implementação Excel do ExpenseRepository
    └── config/           # leitura de env vars
```

Regra de dependência: **Domain não importa nada de Application ou
Infrastructure. Application não importa nada de Infrastructure.** A seta
de dependência sempre aponta para dentro (Infrastructure → Application →
Domain). Infrastructure implementa os `Protocol`s definidos em
`Domain/ports/` e é injetada nos casos de uso via construtor (DI manual,
sem framework — projeto pequeno não justifica um).

Se uma mudança pedir que o Domain importe algo de fora dessas pastas,
pare e pergunte antes de prosseguir — é sinal de que a regra pertence a
outra camada, ou de que a própria fronteira precisa ser repensada.

## Regras de domínio já decididas (não reabrir sem o dono pedir)

- **Dinheiro é sempre `Decimal`, nunca `float`.** Ponto flutuante binário
  não representa frações decimais exatas — inaceitável para valores
  monetários, mesmo que o usuário descreva o campo como "double".
- **Categorias são um enum fechado**: `Transporte`, `Lazer`,
  `Investimentos`, `Casa`, `Alimentação`, `Assinaturas`, `Outros`. Não
  adicione, remova ou torne dinâmica essa lista sem o dono pedir
  explicitamente — é decisão consciente dele, para o bot não virar uma
  bagunça de categorias criadas ad-hoc.
- **`/gasto <valor> <título> <categoria>`** é posicional, não delimitado:
  primeiro token = valor, último token = categoria (validado contra o
  enum), tudo no meio = título (pode ter espaços). Se título e/ou
  categoria vierem faltando ou não reconhecidos, o bot pergunta de volta
  o que falta — nunca assume um valor default para eles.
- **Horário do gasto = horário da mensagem no Telegram** (`message.date`),
  convertido para o timezone configurado (`TIMEZONE`, default
  `America/Sao_Paulo`) — não o horário em que o backend processou o
  update.
- **Permissionamento por allowlist de `user.id`** (não `username`, não
  `chat.id`). Todo handler de comando deve checar a allowlist antes de
  qualquer processamento ou gravação. A checagem é a primeira coisa que
  acontece no handler — mensagens de IDs fora da lista são descartadas
  silenciosamente ou com uma resposta genérica, nunca processadas.
- **Retenção de dados não é problema agora** (ambiente próprio, uso
  pessoal) — não implemente expurgo/retenção de planilha antes de ser
  pedido.

## Segredos e configuração

- Token do bot e a allowlist de IDs vivem em `.env` (nunca commitado —
  ver `.gitignore`), lidos via `python-dotenv`. `.env.example` documenta
  todas as chaves esperadas, sem valores reais.
- Nunca logar o token do bot, mesmo parcialmente, em nenhum nível de log.
- Se precisar adicionar uma nova variável de ambiente, adicione também em
  `.env.example` com um comentário explicando o que é.

## Convenções de código

- Python 3.12+. Use `from __future__ import annotations` e tipagem
  moderna (`list[str]`, `X | None`).
- `dataclass(frozen=True, slots=True)` para entidades e value objects —
  imutabilidade é o padrão no Domain.
- Toda porta (`Domain/ports/`) é um `typing.Protocol`, não uma ABC —
  mantém a Infrastructure livre de herdar de nada do Domain.
- Sem framework de DI. A composição das dependências (qual repositório
  concreto entra em qual caso de uso) acontece num único ponto
  (`Infrastructure/container.py` ou equivalente), chamado a partir de
  `main.py`.
- Lint/format: `ruff` (config em `pyproject.toml`). Rode `ruff check .`
  antes de commitar.

## Testes

- `pytest`, testes em `tests/`, espelhando a estrutura de `App/`.
- Todo caso de uso e toda regra de Domain (parsing de `/gasto`, validação
  de `Money`, resolução de `ExpenseCategory`) precisa de teste unitário —
  são a parte do sistema mais barata de testar isoladamente e mais cara
  de deixar quebrar em produção sem perceber.
- Rode `pytest` antes de qualquer commit que toque `App/`.

## Commits

Commits semânticos ([Conventional Commits](https://www.conventionalcommits.org/pt-br/)),
em português, no imperativo:

```
<tipo>(<escopo opcional>): <resumo curto>

<corpo explicando o "porquê", quando não for óbvio>
```

Tipos usados neste projeto: `feat`, `fix`, `refactor`, `test`, `docs`,
`chore`, `ci`. Escopos comuns: `domain`, `application`, `infrastructure`,
`telegram`, `persistence`, `deploy`.

Como o repositório é público desde o início, revise toda mensagem de
commit e todo diff antes de commitar: nenhum segredo, nenhum dado pessoal
de gasto real, nenhum IP ou hostname real do servidor do dono.

`commitizen` está configurado (`pyproject.toml`) para quem quiser usar
`cz commit` interativamente em vez de escrever a mensagem manualmente.

## Deploy

Ver [`deploy.md`](deploy.md) para o fluxo completo de CI/CD.

## Quando parar e perguntar

Este é um projeto de estudos guiado pelo dono, não um projeto para
Claude decidir sozinho. Pare e pergunte antes de:

- Adicionar uma dependência nova que não esteja em `requirements.txt`.
- Mudar a lista de categorias fixas.
- Trocar polling por webhook, ou qualquer coisa que exija expor porta.
- Mudar o formato do comando `/gasto` ou adicionar um novo comando não
  discutido.
- Introduzir um banco de dados ou qualquer persistência além da planilha
  Excel.

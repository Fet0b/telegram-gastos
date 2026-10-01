# gastos-bot

Bot de Telegram para registrar gastos pessoais, rodando num container local
(sem porta exposta) e salvando tudo numa planilha Excel.

Projeto de estudos: arquitetura em **Domain-Driven Design**, Python puro no
backend, Telegram como interface de entrada (via long polling — o bot nunca
recebe conexão de fora, só consulta o Telegram periodicamente).

## Por que sem porta exposta?

O bot usa **long polling** (`getUpdates`), não webhook: é o container que
pergunta ativamente ao Telegram "tem mensagem nova?", em conexões de saída.
Isso elimina qualquer necessidade de abrir porta no roteador, proxy reverso
ou VPN só para o bot funcionar. Detalhes de arquitetura, decisões e
convenções de código: [`Docs/CLAUDE.md`](Docs/CLAUDE.md).

## Comandos do bot

| Comando | Descrição |
| --- | --- |
| `/ajuda` | Lista todos os comandos disponíveis |
| `/gasto <valor> <título> <categoria>` | Registra um gasto. Se faltar título ou categoria, o bot pergunta o que falta |
| `/gastos` | Mostra os gastos em texto simples (valores brutos e % por categoria) |

Categorias fixas: `Transporte`, `Lazer`, `Investimentos`, `Casa`,
`Alimentação`, `Assinaturas`, `Outros`.

## Rodando localmente

```bash
cp .env.example .env   # preencha TELEGRAM_BOT_TOKEN e AUTHORIZED_USER_IDS
pip install -r requirements-dev.txt --break-system-packages
pytest
python main.py
```

## Rodando em container

```bash
docker compose up -d --build
```

O container não publica nenhuma porta — não precisa e não deve.

## Deploy automático

Ver [`Docs/deploy.md`](Docs/deploy.md) para o fluxo de CI/CD (GitHub Actions
→ GitHub Container Registry → deploy via SSH no servidor local).

## Estrutura do projeto

```
App/
├── Domain/          # regras de negócio puras, sem dependência externa
├── Application/     # casos de uso, orquestra o Domain
└── Infrastructure/  # Telegram, Excel, config — tudo que fala com o mundo externo
```

Ver [`Docs/CLAUDE.md`](Docs/CLAUDE.md) para a explicação completa de cada
camada.

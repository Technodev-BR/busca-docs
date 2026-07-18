# Collector (Python)

Serviço de **coleta**. Pipeline: **download → parse → normalize → enviar para a API de ingestão**
do backend. Não escreve direto no banco (ver [ADR-0001](../arquitetura/decisoes/0001-stack-tecnologica.md)).

## Funções (o que cada peça faz)
Duas responsabilidades: **coleta em lote (CSV)** e **enriquecimento por detalhe (event-driven)**.

### Coleta em lote (CSV, agendada)
| Função | Módulo | Responsabilidade |
|---|---|---|
| `baixar_csv(uf)` | `sources/caixa/downloader.py` | Baixa `Lista_imoveis_{UF}.csv` (httpx + tenacity, backoff em 429/5xx). |
| `parsear_csv(bytes)` | `sources/caixa/parser.py` | `latin1`, pula 2 linhas, separador `;`, `trim`, números BR → tipos. |
| `mapear(linha)` | `sources/caixa/mapper.py` | Linha CSV → `ImovelColetado`; extrai tipo/áreas da descrição. |
| `enviar_lote(imoveis)` | `sinks/api_client.py` | `POST /internal/ingest/imoveis` com `Idempotency-Key` por lote. |
| `executar(uf?)` | `pipeline.py` | Orquestra download→parse→map→envio por UF; guarda `coleta_bruta` (comprimido) e emite métricas. |
| `agendar()` | `scheduler.py` | Dispara a coleta ~1x/dia (APScheduler ou cron do container). |

### Enriquecimento por detalhe (consumidor RabbitMQ)
| Função | Módulo | Responsabilidade |
|---|---|---|
| `consumir_enriquecimento()` | `consumers/enriquecimento.py` | Consome `imoveis.enriquecimento`; **ack manual** após `202`; **rate-limited/paced**. |
| `baixar_detalhe(codigo)` | `sources/caixa/detalhe.py` | `GET detalhe-imovel.asp`; guarda **HTML bruto** em `coleta_bruta`. |
| `parsear_detalhe(html)` | `sources/caixa/detalhe.py` | Extrai campos (2 praças, datas, edital, dívidas...) com seletores **resilientes**. |
| `baixar_midias(...)` | `sources/caixa/detalhe.py` | Baixa **fotos**/**PDFs** (edital, matrícula) → object storage. |
| `detectar_indisponivel(resp)` | `sources/caixa/detalhe.py` | `404`/"imóvel não disponível" → **sinaliza status** (não é erro de parse). Ver [RN-09](../dominio/regras-de-negocio.md#rn-09--ciclo-de-vida-do-imóvel-vendido--removido--reaparecimento). |
| `enviar_detalhe(codigo, detalhe)` | `sinks/api_client.py` | `POST /internal/ingest/imoveis/{codigo}/detalhe`. |

### Transversais
Rate limiter global (token bucket), *user-agent* identificável, **idempotência** por `codigo`,
retry/**DLQ**, `structlog`, métricas Prometheus e **heartbeat** da última execução.

## Estrutura

```
collector/
  pyproject.toml            # deps geridas com uv (ou Poetry)
  src/collector/
    __main__.py             # entrypoint (roda o pipeline)
    config.py               # settings via env (pydantic-settings)
    sources/
      caixa/
        downloader.py       # baixa Lista_imoveis_{UF}.csv (httpx + tenacity)
        parser.py           # trata latin1, pula 2 linhas, separador ';'
        mapper.py           # linha CSV -> modelo de domínio
        detalhe.py          # baixa/parseia detalhe-imovel.asp (enriquecimento — ADR-0010)
    domain/
      models.py             # ImovelColetado, DetalheImovel (pydantic)
    sinks/
      api_client.py         # POST /internal/ingest/imoveis[/{codigo}/detalhe]
    consumers/
      enriquecimento.py     # consome imoveis.enriquecimento (RabbitMQ) — paced/rate-limited
    pipeline.py             # orquestra as etapas por UF
    scheduler.py            # APScheduler (1x/dia) — ou usar cron do container
  tests/
  Dockerfile
```

## Libs
- `httpx` — download HTTP (timeout/retry).
- `tenacity` — retry com backoff.
- `pandas` **ou** `csv` (stdlib) — parsing (pandas facilita limpeza).
- `pydantic` + `pydantic-settings` — modelos e config por env.
- `APScheduler` — agendamento (ou cron externo).
- `structlog` — logs estruturados.
- `selectolax` (ou `beautifulsoup4`/`lxml`) — **parsing do HTML de detalhe**.
- `pika` (ou `aio-pika`) — **consumidor RabbitMQ** do enriquecimento.
- **Dev:** `pytest`, `ruff` (lint+format), `mypy` (tipos).
- Deps: **uv** (rápido) ou **Poetry**.

> O Python **não usa driver do Postgres** no fluxo principal — fala com o backend via HTTP.
> (Na alternativa de staging, entra `SQLAlchemy` + `psycopg`.)

## Criar o projeto (uv)

```bash
pip install uv           # se necessário
uv init collector && cd collector
uv add httpx tenacity pandas pydantic pydantic-settings apscheduler structlog
uv add --dev pytest ruff mypy
```

Rodar o pipeline:
```bash
uv run python -m collector            # coleta padrão
uv run python -m collector --uf SP    # uma UF
```

## Regras de parsing
Seguir a especificação verificada em [Fonte Caixa (CSV)](../dados/fonte-caixa-csv.md)
(encoding `latin1`, pular 2 linhas, `;`, `trim`, converter números BR, guardar `coleta_bruta`).

## Envio ao backend
O `api_client` envia lotes conforme o contrato [API de Ingestão](../contratos/api-ingestao.md)
(header `X-Internal-Token`, `Idempotency-Key` por lote, resposta `202`).

## Coletor de detalhe (enriquecimento)
Segundo pipeline, **event-driven** (ver [ADR-0010](../arquitetura/decisoes/0010-enriquecimento-detalhe.md)):

1. `consumers/enriquecimento.py` consome a fila **`imoveis.enriquecimento`** (evento
   `imovel.enriquecer` com `codigo` + `link`).
2. `sources/caixa/detalhe.py` faz `GET` em `detalhe-imovel.asp?hdnimovel={codigo}`, guarda o
   **HTML bruto** (envia como `coleta_bruta` `fonte='caixa-detalhe'`), parseia com `selectolax` e
   baixa **fotos**/**PDFs** (edital, matrícula).
3. Envia via `POST /internal/ingest/imoveis/{codigo}/detalhe` (schema `DetalheImovel` — ver
   [API de Ingestão](../contratos/api-ingestao.md)). Ao concluir, o backend publica
   `imovel.enriquecido`.

Campos e variações da página em [Fonte Caixa (detalhe)](../dados/fonte-caixa-detalhe.md).

### Ritmo e robustez (escopo = todos os imóveis)
- **Rate limiter global** (token bucket) + `prefetch` baixo + **concorrência baixa** (1–2): a fila
  segura o backlog de dezenas de milhares; o enriquecimento é **lento por design**.
- **Backoff** em `429`/`5xx` (tenacity); *user-agent* identificável; **sem burlar proteção**
  (ver [Legal & LGPD](../legal/lgpd.md)).
- **Ack manual** só após o `202` do backend; falha → retry e, no limite, **DLQ**.
- Parser **tolerante a ausências**; se a página não tiver os campos esperados → falhar o item e
  **alertar** (possível mudança de layout). **Testes com HTML salvo** (fixtures).
- **Idempotência** por `codigo`; refresh por **TTL** e em `imovel.atualizado`.

## Boas práticas de coleta
- *Rate limiting*, *user-agent* identificável, coleta **incremental** (comparar com a última).
- Guardar o **CSV/HTML bruto** antes de normalizar.
- Métricas do job (itens, novos/atualizados, falhas por UF; **fila e taxa de enriquecimento**) — ver
  [Observabilidade](../observabilidade/pilares.md).

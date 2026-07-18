# Contrato — Eventos RabbitMQ

Mensagens trocadas para **processamento assíncrono** dos imóveis. Decisão em
[ADR-0005](../arquitetura/decisoes/0005-mensageria-rabbitmq.md).

## Topologia

- **Exchange principal**: `imoveis` — tipo **topic**.
- **Dead-letter exchange**: `imoveis.dlx` — tipo **topic** (recebe o que falhou).
- **Routing keys** (evento por imóvel):
  - `imovel.recebido` — novo lote ingerido (payload cru normalizável).
  - `imovel.atualizado` — mudança de preço/status detectada.
  - `imovel.removido` — sumiu do CSV → marcar indisponível.
  - `imovel.enriquecer` — pedido para buscar a **página de detalhe** (ver [ADR-0010](../arquitetura/decisoes/0010-enriquecimento-detalhe.md)).
  - `imovel.enriquecido` — detalhe coletado e persistido (dispara recálculo de custos/score).

### Filas (MVP: um worker de processamento)

| Fila | Binding (routing key) | Consumidor |
|---|---|---|
| `imoveis.processamento` | `imovel.recebido`, `imovel.atualizado`, `imovel.enriquecido` | Worker de processamento (Java) |
| `imoveis.enriquecimento` | `imovel.enriquecer` | **Coletor de detalhe (Python)** — paced/rate-limited |
| `imoveis.remocao` | `imovel.removido` | Worker que marca indisponível |
| `imoveis.dlq` | (via `imoveis.dlx`) | Inspeção/reprocessamento manual |

O worker de processamento faz **normalização → geocoding → cálculo de custos → score** e persiste
no PostgreSQL.

> **Enriquecimento (detalhe):** após persistir o imóvel do CSV, o backend publica
> `imovel.enriquecer`. O **coletor Python** consome `imoveis.enriquecimento` de forma **paced**
> (rate limiter + `prefetch` baixo) — a fila absorve o backlog de "todos" os imóveis. Ao concluir,
> o backend publica `imovel.enriquecido`. Detalhes em
> [Fonte Caixa (detalhe)](../dados/fonte-caixa-detalhe.md) e [Collector](../servicos/collector-python.md).

> **Evolução (pipeline por estágios):** dividir em filas por etapa
> (`imoveis.normalizacao` → publica `imovel.normalizado` → `imoveis.geocoding` →
> `imovel.geolocalizado` → `imoveis.custos`), cada uma escalável de forma independente. Começamos
> com uma fila só e evoluímos quando necessário.

## Envelope da mensagem

Todo evento segue um envelope padrão (`header` + `data`):

```json
{
  "header": {
    "eventId": "b1e7...-uuid",
    "type": "imovel.recebido",
    "version": 1,
    "occurredAt": "2026-07-15T09:12:33Z",
    "correlationId": "9c2...-uuid",
    "source": "api-ingestao",
    "loteId": "9c2...-uuid"
  },
  "data": {
    "codigo": "1444408501866",
    "fonte": "caixa",
    "uf": "SP",
    "cidade": "ADAMANTINA",
    "bairro": "VILA JOAQUINA",
    "endereco": "ALAMEDA PADRE ANCHIETA, N. 1159, LT 05 QD 16",
    "preco": 501000.00,
    "valorAvaliacao": 501000.00,
    "descontoPct": 0.0,
    "financiamento": false,
    "descricao": "Casa, 0.00 de área total, 171.43 de área privativa, 384.00 de área do terreno.",
    "modalidade": "Leilão SFI - Edital único",
    "link": "https://venda-imoveis.caixa.gov.br/sistema/detalhe-imovel.asp?hdnimovel=1444408501866"
  }
}
```

### `data` por tipo de evento
- `imovel.recebido` / `imovel.atualizado`: payload completo do imóvel (exemplo acima).
- **`imovel.enriquecer`**: mínimo para buscar o detalhe — `{ "codigo": "...", "fonte": "caixa",
  "link": "https://venda-imoveis.caixa.gov.br/sistema/detalhe-imovel.asp?hdnimovel=..." }`.
- **`imovel.enriquecido`**: `{ "codigo": "...", "status": "ok|parcial|falha" }` (o dado rico já foi
  persistido via [API de Ingestão — detalhe](api-ingestao.md); o evento só dispara o recálculo).
- `imovel.removido`: `{ "codigo": "...", "fonte": "caixa" }`.

### Campos do `header`
| Campo | Descrição |
|---|---|
| `eventId` | UUID único do evento (para dedupe no consumidor). |
| `type` | Tipo do evento (= routing key). |
| `version` | Versão do schema do evento (muda em breaking change). |
| `occurredAt` | Timestamp UTC (ISO-8601). |
| `correlationId` | Correlaciona com logs/traces e com o request de ingestão. |
| `source` | Serviço produtor. |
| `loteId` | Lote de origem (rastreabilidade até o `coleta_bruta`). |

## Regras de consumo

- **Idempotência**: usar `data.codigo` (+ `eventId`) para não processar duas vezes.
- **Retry + DLQ**: em falha transitória, re-tentar com backoff; após N tentativas, enviar para
  `imoveis.dlq` (via `x-dead-letter-exchange: imoveis.dlx`).
- **Ordenação**: não assumir ordem global; a idempotência resolve reprocessos.
- **Propagação de trace**: propagar `correlationId`/trace-id (OpenTelemetry) — ver
  [Observabilidade](../observabilidade/pilares.md).
- **Sem PII** no payload (LGPD) — só dados do imóvel.

## Propriedades da mensagem (AMQP)
- `content_type: application/json`
- `delivery_mode: 2` (persistente)
- `message_id: <eventId>`
- `correlation_id: <correlationId>`
- `type: <type>`
- header `x-schema-version: <version>`

## Convenções
- Publicar com **publisher confirms** habilitado (garantia de entrega ao broker).
- Consumir com **ack manual** após persistir com sucesso.
- Nomes de exchange/fila em **minúsculo com ponto** (`imoveis.processamento`).

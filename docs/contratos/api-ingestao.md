# Contrato — API de Ingestão

API **interna** que o coletor (Python) usa para enviar imóveis ao backend (Java). Não é exposta
publicamente. O contrato formal está em
[`openapi-ingestao.yaml`](openapi-ingestao.yaml) (fonte da verdade — API-first).

## Endpoints

| Método | Rota | Uso |
|---|---|---|
| `POST` | `/internal/ingest/imoveis` | Lote de imóveis do **CSV** (coletor principal) |
| `POST` | `/internal/ingest/imoveis/{codigo}/detalhe` | **Detalhe enriquecido** de um imóvel (coletor de detalhe — ver [ADR-0010](../arquitetura/decisoes/0010-enriquecimento-detalhe.md)) |

Ambos: header `X-Internal-Token`, `Idempotency-Key: <uuid>`, resposta `202 Accepted`
(processamento assíncrono via RabbitMQ).

## Lote de imóveis (CSV)

`POST /internal/ingest/imoveis`

- **Auth**: header `X-Internal-Token` (segredo compartilhado na rede interna).
- **Idempotência**: header `Idempotency-Key: <uuid>` por lote — retry não duplica.
- **Resposta**: `202 Accepted` (processamento assíncrono via RabbitMQ).

## Exemplo de requisição

```http
POST /internal/ingest/imoveis HTTP/1.1
Host: backend:8080
X-Internal-Token: ***
Idempotency-Key: 8f1c...e2
Content-Type: application/json
```

```json
{
  "fonte": "caixa",
  "uf": "SP",
  "geradoEm": "2026-07-15",
  "imoveis": [
    {
      "codigo": "1444408501866",
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
  ]
}
```

## Exemplo de resposta (`202`)

```json
{ "loteId": "9c2...", "recebidos": 1200, "aceitos": 1187, "rejeitados": 13, "publicados": 1187 }
```

## O que o backend faz ao receber (lote CSV)
1. **Valida** o token e o payload (Bean Validation).
2. Verifica a **Idempotency-Key** (se já processada → `409`).
3. Grava o **`coleta_bruta`** (lote bruto, reprocessável).
4. **Publica** um evento por imóvel no RabbitMQ (ver [Eventos RabbitMQ](eventos-rabbitmq.md)),
   incluindo `imovel.enriquecer` para disparar a coleta de detalhe.
5. Responde `202` com o resumo.

## Detalhe enriquecido

`POST /internal/ingest/imoveis/{codigo}/detalhe`

Enviado pelo **coletor de detalhe (Python)** após raspar `detalhe-imovel.asp` (ver
[Fonte Caixa (detalhe)](../dados/fonte-caixa-detalhe.md)). Corpo = schema `DetalheImovel`
(valor 1º/2º leilão, datas das praças, matrícula, CEP, FGTS/financiamento, despesas, fotos, PDFs).

- `404` se o `codigo` ainda não foi ingerido pelo CSV.
- Ao persistir, o backend publica **`imovel.enriquecido`** → recálculo de custos/score.
- Campos são **opcionais** (o parser tolera ausências); `status` pode ser `ok|parcial|falha`.

## Erros
Padrão **Problem Details (RFC 7807)** (`application/problem+json`) — ver schema `Problem` no YAML.

## Notas de implementação
- O coletor **envia em lotes** (ex.: 500–1000 imóveis) para eficiência.
- O parsing do CSV (encoding/linhas/`trim`/números BR) é responsabilidade do coletor — ver
  [Fonte Caixa (CSV)](../dados/fonte-caixa-csv.md) e [Collector](../servicos/collector-python.md).
- O contrato é validado por **testes de contrato** nas duas pontas
  (ver [Testes](../qualidade/testes.md)).

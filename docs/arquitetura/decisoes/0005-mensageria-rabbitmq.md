# ADR-0005 — Mensageria com RabbitMQ (processamento assíncrono)

- **Status:** Aceito
- **Data:** 2026-07-18

## Contexto
A ingestão dos imóveis (vinda do coletor) dispara trabalho que **não precisa ser síncrono**:
normalização, geocoding, cálculo de custos e score. Fazer tudo no request de ingestão deixa a
API lenta e acopla coleta a processamento. Também queremos **resiliência** (retentar sem perder
dados) e capacidade de **escalar workers** de forma independente.

## Decisão
Adotar **RabbitMQ** como broker de mensageria. O fluxo passa a ser:

1. A **API de Ingestão (Java)** valida o lote, grava o `coleta_bruta` e **publica eventos**
   (ex.: `imovel.recebido`) no RabbitMQ.
2. **Workers (Java)** consomem os eventos e executam normalização, geocoding, cálculo de custos e
   score, persistindo no PostgreSQL.
3. A **API REST** apenas lê os dados já processados (com [cache Redis](../../infraestrutura/desenvolvimento-docker.md)).

Padrões: **exchange** por domínio, **filas** por tipo de trabalho, **DLQ** (dead-letter queue)
para mensagens com falha, e **idempotência** por `codigo` do imóvel.

## Consequências
- **+** Ingestão rápida; processamento **desacoplado**, **escalável** e **resiliente** (retry/DLQ).
- **+** Permite reprocessar a partir do `coleta_bruta` sem re-baixar.
- **−** Mais uma peça de infra para operar/observar (métricas de fila, consumidores).
- O RabbitMQ é a **arquitetura-alvo** e o restante da documentação (enriquecimento paced, DLQ,
  eventos `imovel.*`, notificações) **assume filas**. A opção de "começar sem fila" abaixo vale
  **apenas para bootstrap/dev local**, não como alternativa de produção.

> **Nota (alternativa histórica):** era possível começar **sem fila** (processar no próprio serviço)
> e ligar o RabbitMQ depois. Mantido apenas como registro; o alvo do MVP **já inclui RabbitMQ**
> porque o enriquecimento por detalhe é event-driven e *paced* (ADR-0010).

## Alternativas consideradas
- **Kafka**: excelente para altíssimo volume/streaming, porém mais complexo de operar — exagero
  para o estágio atual.
- **Processamento síncrono na ingestão**: simples, mas acopla e não escala — rejeitado como alvo.

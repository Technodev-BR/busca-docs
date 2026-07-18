# ADR-0007 — Cache de leitura com Redis

- **Status:** Aceito
- **Data:** 2026-07-18

## Contexto
A API REST atende **buscas com filtros** (localização, faixa de preço, modalidade) que tendem a se
repetir e podem ser custosas no banco (joins, PostGIS, ordenação/paginação). Queremos **baixa
latência** nas consultas quentes sem sobrecarregar o PostgreSQL, mantendo o banco como fonte da
verdade.

## Decisão
Adotar **Redis** como **cache de leitura** na frente da API REST (cache-aside):

1. A API tenta ler o resultado no Redis (chave derivada dos parâmetros da busca).
2. *Miss* → consulta o PostgreSQL, devolve e **popula** o cache com **TTL**.
3. Escritas/reprocessamentos **invalidam** as chaves afetadas (ou deixam expirar por TTL curto).

O Redis guarda **apenas dados derivados/descartáveis** — nunca estado exclusivo.

## Consequências
- **+** Menor latência nas buscas recorrentes e menos carga no Postgres.
- **+** **Descartável**: em falha/reset, reidrata a partir do banco (ver [Backup & DR](../../infraestrutura/backup-e-dr.md)).
- **−** Risco de **staleness**: exige política de TTL/invalidação clara.
- **−** Mais uma peça de infra para operar e observar (hit ratio, memória).

## Alternativas consideradas
- **Sem cache (só Postgres + índices)**: mais simples; pode bastar no MVP, mas não cobre picos de
  buscas repetidas. Pode-se ligar o Redis quando a latência justificar.
- **Cache em memória no processo (Caffeine)**: rápido, porém não compartilhado entre réplicas e
  perdido a cada deploy — inadequado com múltiplas instâncias.

Relacionado: [ADR-0005 — Mensageria](0005-mensageria-rabbitmq.md) e
[Backend (Java)](../../servicos/backend-java.md).

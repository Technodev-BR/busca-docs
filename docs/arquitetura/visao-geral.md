# Visão geral da arquitetura

O sistema é organizado em **camadas**, com o fluxo de dados de ponta a ponta:

```
Fontes → Coleta (Python) → Ingestão (Java) → RabbitMQ → Workers → Postgres → API (Java) → Front (Angular)
```

Veja os [Diagramas](diagramas.md) para a visão visual.

## Camadas

### 1. Fontes de dados
- **Caixa — lista oficial em CSV** (fonte primária): a Caixa disponibiliza a lista completa de
  imóveis por estado. É a forma oficial e mais estável — **preferir sempre o CSV a raspar HTML**.
  Detalhes em [Fonte Caixa (CSV)](../dados/fonte-caixa-csv.md).
- **Caixa — página de detalhe** (secundária/opcional): só para enriquecer um imóvel (fotos,
  edital), com coleta educada.
- Futuras: outros leiloeiros e dados públicos (IBGE, valores de referência).

### 2. Coleta (Python)
- **Coletor de CSV (primário)**: baixa o arquivo por UF, faz parsing e envia ao backend.
- **Coletor de detalhe (enriquecimento)**: consome `imoveis.enriquecimento` e raspa a página de
  cada imóvel (2 praças, datas, matrícula, CEP, FGTS/dívidas, fotos, edital) — **event-driven** e
  **paced** (rate limiter). Ver [ADR-0010](decisoes/0010-enriquecimento-detalhe.md) e
  [Fonte Caixa (detalhe)](../dados/fonte-caixa-detalhe.md).
- **Scheduler**: roda ~1x/dia (o CSV traz a "Data de geração"). Detalhes em
  [Collector (Python)](../servicos/collector-python.md).

### 3. Ingestão (fronteira Python → Java)
O **backend Java é o dono do banco/schema**. O coletor **não escreve direto** nas tabelas de
negócio; envia via **API de ingestão** (`POST /internal/ingest/...`). A ingestão grava o
`coleta_bruta` e **publica eventos no RabbitMQ** para processamento assíncrono. Ver
[ADR-0001](decisoes/0001-stack-tecnologica.md) e [ADR-0005](decisoes/0005-mensageria-rabbitmq.md).

### 4. Mensageria (RabbitMQ)
Desacopla ingestão de processamento: exchange/filas por tipo de trabalho, **DLQ** para falhas e
**idempotência** por `codigo` do imóvel. Permite escalar workers e reprocessar do `coleta_bruta`.
Contrato dos eventos em [Eventos RabbitMQ](../contratos/eventos-rabbitmq.md).

### 5. Persistência
- **PostgreSQL + PostGIS** (dados, histórico, geo). Schema versionado por **Flyway**.
- **Object storage** (fotos/editais) e **Redis** (**cache** de buscas quentes na API REST).
  Ver [Modelo de dados](../dados/modelo-de-dados.md).

### 6. Processamento & Enriquecimento (workers)
**Workers Java** consomem os eventos do RabbitMQ e executam normalização, geocoding, **motor de
custos** (ITBI/custas/total) e **pré-análise** (score); na evolução, **IA** para resumo de edital.
Ver [Domínio](../dominio/regras-de-negocio.md).

### 7. Backend / API (Java + Spring Boot)
Expõe busca, filtros, detalhe e cálculo. Regras de negócio, auth, paginação/ordenação. É dono do
schema e recebe dados do coletor. Usa **Redis** para cache de buscas. Ver
[Backend (Java)](../servicos/backend-java.md).

### 8. Frontend (Angular)
Lista + filtros, mapa, detalhe + análise, favoritos/alertas. Estilização em **SASS/SCSS**.
Servido via Nginx. Ver [Frontend (Angular)](../servicos/frontend-angular.md).

## Preocupações transversais
- **Observabilidade** (métricas/logs/traces) — ver [Observabilidade](../observabilidade/pilares.md).
- **Segurança/Auth** e **config/segredos** por ambiente.
- **Qualidade** (testes e CI/CD) — ver [Qualidade](../qualidade/testes.md).

## Estilo arquitetural
- Backend em **arquitetura hexagonal** (ports & adapters): domínio puro, infraestrutura nas bordas.
- **API-first** (contrato OpenAPI versionado).
- **12-Factor App** (config por env, logs como stream, processos stateless).

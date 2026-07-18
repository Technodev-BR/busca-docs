# Observabilidade — os três pilares

Enxergar o sistema em produção com **métricas, logs e traces**. Tudo instrumentado desde o início.

## Métricas
- **Java**: **Micrometer** (via Spring Boot Actuator) expondo `/actuator/prometheus`.
- **Python**: `prometheus-client` no coletor (duração do job, nº de imóveis, falhas por UF).
- **Coleta**: **Prometheus** faz *scrape*; **Grafana** para dashboards.
- **Chave (técnicas)**: latência p50/p95/p99 da API, taxa de erro (5xx), **taxa de 429**
  (rate limiting — [ADR-0019](../arquitetura/decisoes/0019-rate-limiting-quotas.md)), throughput,
  saturação (CPU/mem/pool); coletor: itens processados, novos/atualizados, tempo por UF.

### Métricas de negócio
Além da infra, instrumentar sinais de **produto** (dashboards + alertas):

- **Imóveis ativos** por UF/tipo; **% enriquecido** (`status_enriquecimento = ok`).
- **Fila de enriquecimento**: profundidade e **taxa de detalhe/min** (o gargalo *paced*).
- **% geocodado** ([ADR-0016](../arquitetura/decisoes/0016-geocoding.md)) — cobertura do mapa.
- **Alertas disparados** e **notificações enviadas/falhas** ([ADR-0018](../arquitetura/decisoes/0018-notificacoes.md)).
- **Login**: taxa de sucesso do callback OIDC, refresh/reuso detectado.
- **DLQ**: mensagens em dead-letter por fila (canário de parser/layout).

## Logs
- **JSON estruturado** (Java: Logback + `logstash-logback-encoder`; Python: `structlog`).
- **Correlation-id / trace-id** em todo request (propagado ao coletor) para cruzar log ↔ trace.
- Agregação: **Grafana Loki** (leve) ou **ELK/OpenSearch**. Logs em stdout → agente
  (Promtail/Fluent Bit).
- **Sem PII** nos logs (LGPD).

## Traces distribuídos
- **OpenTelemetry** (SDK no Java e no Python) → **OTel Collector** → **Tempo** (ou Jaeger).
- Rastreia: Angular → API Java → banco; e job Python → API de ingestão.

## Health checks & probes
- **Actuator**: `/actuator/health` com *liveness* e *readiness* separados.
- Docker/K8s usam esses endpoints como probes.
- Coletor expõe health simples e *heartbeat* da última execução bem-sucedida.

## Alertas & on-call
- **Alertmanager** (com Prometheus) → e-mail/Slack/Teams.
- Alertas por **sintoma** (SLO burn-rate, 5xx alto, coletor falhou > X h, banco sem conexão),
  não por causa. Evitar ruído.

## Stack sugerida (self-hosted)
`Prometheus + Grafana + Loki + Tempo + OpenTelemetry Collector + Alertmanager`
(atalho: **grafana/otel-lgtm** para subir tudo junto em dev).
Alternativa gerenciada: Grafana Cloud, Datadog, New Relic.

Ver [SLO / SLI](slo-sli.md), [AIOps (MCP)](aiops-mcp.md) e [Runbooks](runbooks.md).

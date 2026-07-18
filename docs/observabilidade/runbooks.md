# Runbooks

Guias curtos de "o que fazer quando X acontecer". Cada alerta relevante deve ter um runbook
linkado na própria notificação.

## Template de runbook

```markdown
# Runbook — <nome do alerta>

## Sintoma
O que o alerta indica (e o que o usuário sente).

## Impacto / severidade
Quem/o que é afetado; severidade (info/warning/critical).

## Diagnóstico rápido
- Dashboards/queries para olhar primeiro.
- Perguntas: mudou algo recente (deploy/PR)? erro em qual serviço?

## Mitigação
Passos para estancar o problema (rollback via Argo CD, escalar réplica, etc.).

## Correção definitiva
Ação de causa raiz + follow-up (issue no GitHub).

## Prevenção
O que evita a recorrência (teste, alerta, limite).
```

## Runbooks iniciais sugeridos
- **API com 5xx alto** → checar deploy recente; rollback no Argo CD; olhar traces (Tempo).
- **Coleta diária falhou** → checar disponibilidade do CSV da Caixa; reprocessar do `coleta_bruta`.
- **Latência p95 acima do SLO** → checar saturação (pool de conexões, CPU); cache/índices.
- **Banco indisponível** → checar CloudNativePG/serviço gerenciado; conexões; disco.
- **DLQ crescendo (enriquecimento)** → possível mudança de layout; inspecionar mensagens; corrigir
  parser; reprocessar do `coleta_bruta`.
- **Parser de detalhe vazio (canário)** → HTML mudou; pausar enriquecimento (kill-switch); ajustar
  seletores; validar com fixtures.
- **Fila RabbitMQ travada / sem consumo** → checar consumidores, `prefetch`, conexões; reiniciar worker.

## Caixa: 429 / bloqueio de coleta
**Sintoma:** alta taxa de `403/429`, CAPTCHA ou timeouts vindos do site da Caixa; enriquecimento
parado ou lento. **Severidade:** warning → critical se persistir.

**Diagnóstico:** métrica de `403/429` por host; taxa de detalhe/min; logs do downloader.

**Mitigação (em ordem):**
1. **Reduzir a taxa** (baixar req/min e concorrência — [política de coleta](../legal/politica-de-coleta.md)).
2. Se persistir, **acionar o kill-switch** `COLETA_HABILITADA=false` (pausa enriquecimento sem deploy).
3. **Registrar incidente** (horário, escopo, evidências) e **não** tentar contornar a proteção.
4. Reavaliar os **termos VOL**; retomar **só após revisão** e com taxa reduzida.

**Prevenção:** limites conservadores, backoff, circuit breaker automático e cache de mídia
([ADR-0017](../arquitetura/decisoes/0017-object-storage.md)).

> O [agente AIOps](aiops-mcp.md) sugere o runbook aplicável junto do diagnóstico.

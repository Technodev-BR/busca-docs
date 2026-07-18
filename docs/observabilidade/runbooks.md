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

> O [agente AIOps](aiops-mcp.md) sugere o runbook aplicável junto do diagnóstico.

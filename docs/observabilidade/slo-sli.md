# SLO / SLI & Error Budget

## Definições
- **SLI** (*indicator*): uma métrica que mede a experiência (ex.: % de requests < 400 ms).
- **SLO** (*objective*): a meta para um SLI num período (ex.: 99,5%/mês).
- **Error budget**: o quanto podemos "falhar" dentro do SLO — orienta priorizar confiabilidade x features.

## SLIs e SLOs propostos

| SLI | SLO | Janela |
|---|---|---|
| Disponibilidade da API (não-5xx) | ≥ 99,5% | 30 dias |
| Latência da busca (p95) | < 400 ms | 30 dias |
| Sucesso do job de coleta diária | ≥ 99% | 30 dias |
| Frescor dos dados (coleta do dia concluída) | até 08:00 | diário |

## Uso do error budget
- Se o budget está **saudável** → priorizar features.
- Se está **queimando rápido** (burn-rate alto) → congelar mudanças arriscadas e focar em confiabilidade.
- Alertas de **burn-rate** (rápido e lento) no Alertmanager.

## Processo
- **Runbooks** por alerta (ver [Runbooks](runbooks.md)).
- **Postmortems sem culpa** para incidentes relevantes, com ações de melhoria rastreadas.

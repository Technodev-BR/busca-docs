# AIOps — resposta a incidentes assistida por IA (via MCP)

Um **agente de IA** que **captura os erros/logs**, **diagnostica o incidente** e envia um
**alerta já analisado** (causa provável, serviço afetado, severidade, próximos passos) — reduzindo
o tempo de detecção→entendimento (MTTA/MTTR).

## Papel do MCP
O agente acessa as fontes de contexto **via servidores MCP** (Model Context Protocol), que
padronizam o acesso a ferramentas/dados. Assim o LLM consulta, sob demanda, as evidências
necessárias, sem integrações pontuais e frágeis.

## Fluxo de um incidente
1. **Gatilho**: **Alertmanager** dispara um *webhook* (ou erro `ERROR/5xx` no stream de logs / **Sentry**).
2. **Coleta de contexto (via MCP)**:
   - **Logs** correlacionados (Loki/OpenSearch) pelo `trace-id`;
   - **Métricas/traces** (Prometheus/Tempo) do período;
   - **Mudanças recentes** (deploys, PRs, commits, sync do Argo CD) via **MCP do GitHub**;
   - **Qualidade/regressões** via **MCP do SonarQube** (quando pertinente).
3. **Diagnóstico (LLM)**: correlaciona sintomas + mudança recente → hipótese de causa raiz,
   serviço/rota afetada, severidade e **runbook sugerido**.
4. **Notificação enriquecida**: envia o resumo para **Slack / Microsoft Teams / e-mail** (e
   escalonamento para on-call se crítico).
5. **Registro**: abre/atualiza um **incidente (issue no GitHub)** ligando dashboard/trace — para o
   *postmortem*.

## Servidores MCP úteis
- **GitHub MCP** — correlacionar incidente com deploy/PR/commit e abrir issues.
- **SonarQube MCP** — apontar regressões de qualidade/segurança.
- **Observabilidade** — MCP de Grafana/Loki/Prometheus/Tempo (ou Sentry/Datadog).

## Canais de acionamento
- **Slack** — *Incoming Webhook*/app; canal `#incidentes` com thread por incidente.
- **Microsoft Teams** — *Incoming Webhook*/Workflows (Adaptive Cards).
- **E-mail** — SMTP para resumo/digest.
- **On-call** (opcional): Opsgenie/PagerDuty ou rotas por severidade no Alertmanager.
- **Roteamento**: `info` → e-mail/digest; `warning` → Slack/Teams; `critical` → Slack/Teams + on-call.
  Notificações **agrupadas** e com *dedup* para evitar ruído.

## Guarda-corpos (importante)
- Agente **read-only por padrão**; ações que mudam estado exigem escopo mínimo e ficam **auditadas**.
- **Sem PII/segredos** no prompt/telemetria enviada ao LLM (LGPD).
- Diagnóstico é **sugestão** — **human-in-the-loop** em incidentes críticos; toda análise cita as
  evidências (links de log/trace).
- Controle de **custo/rate-limit** do LLM e *fallback* para alerta "cru" se a IA indisponível.

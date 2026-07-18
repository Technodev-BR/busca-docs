# Segurança

Segurança "shift-left": verificar cedo, no pipeline, e endurecer em runtime.

## Na esteira (CI)
- **SonarQube** — SAST (código), bugs e vulnerabilidades; Quality Gate obrigatório.
- **Trivy** — vulnerabilidades em **imagens, dependências (SBOM) e IaC**; falha em CVE crítica.
- **Dependabot/Renovate** (opcional) — atualização automática de dependências.

## Aplicação
- **HTTPS** ponta a ponta (cert-manager em prod).
- **JWT** para auth; **rate limiting** na API pública.
- **Validação de entrada** (Bean Validation no Java, pydantic no Python).
- **Problem Details (RFC 7807)** para erros padronizados, sem vazar stack traces.

## Segredos
- **Nunca** no git. Em dev: `.env` (ignorado). Em prod: **Sealed Secrets**/**External Secrets** +
  cofre (Vault) — ver [Kubernetes & GitOps](../infraestrutura/kubernetes-gitops.md).

## Dados & privacidade
- **Sem PII** de terceiros (LGPD) — ver [Legal & LGPD](../legal/lgpd.md).
- Logs e telemetria sem dados sensíveis (inclusive no [agente AIOps](../observabilidade/aiops-mcp.md)).

## Runtime no cluster
- Imagens **não-root**, *read-only filesystem* quando possível.
- **NetworkPolicies** restringindo tráfego interno.
- RBAC mínimo; registry com **assinatura de imagem** (Cosign) e política de admissão.

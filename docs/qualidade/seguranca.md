# Segurança

Segurança "shift-left": verificar cedo, no pipeline, e endurecer em runtime.

## Na esteira (CI)
- **SonarQube** — SAST (código), bugs e vulnerabilidades; Quality Gate obrigatório.
- **Trivy** — vulnerabilidades em **imagens, dependências (SBOM) e IaC**; falha em CVE crítica.
- **DAST (OWASP ZAP baseline)** — varredura dinâmica contra o ambiente de homologação (não bloqueante
  no MVP; alertas viram issues). Alinhado ao que a [Esteira CI/CD](./ci-cd.md) referencia.
- **Dependabot/Renovate** (opcional) — atualização automática de dependências.

## Aplicação
- **HTTPS** ponta a ponta (cert-manager em prod).
- **Autenticação — login social OIDC (padrão BFF)**, **sem senha armazenada** — ver
  [ADR-0013](../arquitetura/decisoes/0013-autenticacao-social-oidc.md):
  - Sessão em **cookies HttpOnly** (`Secure`, `SameSite=Lax`); front nunca lê o token.
  - **Refresh token com rotação** e **detecção de reúso** (revoga a família em caso de replay).
  - **CSRF** (double-submit / `SameSite`) em toda a API pública que muda estado.
- **Rate limiting**: borda no **Traefik** (por IP) + limites por usuário/rota no **Spring** (API pública);
  a **ingestão interna** é protegida por **`X-Internal-Token`** e não é exposta na borda.
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

# Container Registry (Harbor)

Registry **open source** e self-hostável para as imagens Docker.

## Escolha
- **Harbor** (CNCF) — registry self-hosted com:
  - **Scan de vulnerabilidade com Trivy integrado**;
  - **quarantine por política** (bloquear CVE crítica);
  - **RBAC** por projeto;
  - **assinatura de imagem** (Cosign/Notary);
  - **replicação** entre registries.
- *Alternativa zero-ops:* **GitHub Container Registry (ghcr.io)** — nativo do GitHub, ótimo para
  começar; migrar para Harbor quando quiser scan/políticas próprias.

## Convenções de imagem
- Nome: `harbor.exemplo.com/busca-busca/<servico>`.
- Tag: **SemVer + SHA curto** (ex.: `1.4.2-a1b2c3d`); evitar `latest` em produção.
- Toda imagem passa por **Trivy** no CI **e** no push ao Harbor (dupla verificação).

## Integração no pipeline
1. CI builda a imagem (multi-stage).
2. CI escaneia com **Trivy** (falha em CVE crítica).
3. CI faz *push* ao Harbor → Harbor **re-escaneia** por política.
4. CI faz *bump* da tag no repo GitOps → Argo CD sincroniza.

Ver [CI/CD](../qualidade/ci-cd.md) e [Kubernetes & GitOps](kubernetes-gitops.md).

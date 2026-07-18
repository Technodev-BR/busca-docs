# CI/CD (GitHub Actions)

SCM: **GitHub**. Entrega contínua com **GitHub Actions** + **GitOps/Argo CD**
(ver [Kubernetes & GitOps](../infraestrutura/kubernetes-gitops.md)).

## Estágios do pipeline

```
build → test → SonarQube (Quality Gate) → Trivy (scan) → build imagem → push registry → bump GitOps
```

- **build**: por serviço, com *path filters* (só builda o que mudou).
- **test**: unit + integração (Testcontainers) + contrato — ver [Testes](testes.md).
- **SonarQube**: **Quality Gate** bloqueia o merge (bugs, vulnerabilidades, cobertura, code smells).
- **Trivy**: escaneia **imagens, dependências (SBOM) e IaC** — falha em CVE crítica.
- **build imagem**: multi-stage; tag **SemVer + SHA**.
- **push**: para o registry **Harbor** (re-scan por política) — ver [Registry](../infraestrutura/registry-harbor.md).
- **bump GitOps**: commit/PR atualizando a tag no repo `busca-busca-gitops` → Argo CD sincroniza.

## Regras de repositório
- **Pre-commit hooks** (lint/format).
- **Branch protection**: exige pipeline verde + 1 review.
- **Conventional Commits** + versionamento semântico.

## Imagens
- Versionadas (SemVer + SHA), publicadas no Harbor (ou ghcr.io no início).
- Nunca `latest` em produção.

## Segurança na esteira
Ver [Segurança](seguranca.md) para SAST/DAST, gestão de segredos e política de CVEs.

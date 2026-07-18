# Repositórios

Padrão **GitOps de dois repositórios** (separar *código* de *configuração de deploy*). Decisão em
[ADR-0003](../arquitetura/decisoes/0003-dois-repositorios-gitops.md). SCM: **GitHub**.

## 1) `busca-busca` — monorepo de aplicação

```
busca-busca/
  backend/            # Java (Spring Boot)
  collector/          # Python
  frontend/           # Angular
  libs/               # contratos/OpenAPI compartilhados (opcional)
  deploy/helm/        # Helm charts dos serviços (templates)
  .github/workflows/  # pipelines GitHub Actions (CI)
  docker-compose.yml  # ambiente de desenvolvimento
  docs/               # (futuro) esta documentação pode migrar para cá
```

- **Por que monorepo?** projeto pequeno/um time → PRs atômicos cruzando serviços, um histórico e
  CI simples. Cada serviço tem **Dockerfile** e **job de CI** próprios (com *path filters*).
- *Alternativa (polyrepo):* um repo por serviço — só quando times/ciclos divergirem.

## 2) `busca-busca-gitops` — configuração (fonte da verdade)

```
busca-busca-gitops/
  apps/                        # Argo CD Applications (app-of-apps)
  environments/
    dev/    staging/    prod/  # values/overlays por ambiente (Helm ou Kustomize)
  infra/                       # ingress, cert-manager, observabilidade, etc.
```

- O CI **nunca faz `kubectl apply`**; só **atualiza a tag da imagem** aqui (commit/PR). O Argo CD
  detecta e sincroniza. Ver [Kubernetes & GitOps](kubernetes-gitops.md).

## Onde ficam os docs?

- **Agora:** repositório de documentação **dedicado** (este), como fonte única da verdade durante o design.
- **Depois:** quando o monorepo `busca-busca` existir, os **docs cross-cutting** (ADRs, arquitetura,
  domínio, infra) podem migrar para `busca-busca/docs` e serem publicados por CI (GitHub Pages).
  Docs **específicos de um serviço** ficam junto do serviço (README/`docs/` local).

## Criar os repositórios (GitHub CLI)

```bash
# repo de aplicação
gh repo create busca-busca --private --clone
# repo de gitops
gh repo create busca-busca-gitops --private --clone
```

## Convenções de Git
- **Conventional Commits** (`feat:`, `fix:`, `docs:` ...).
- **Trunk-based**/GitFlow leve; **branch protection** exigindo pipeline verde + 1 review.
- **Versionamento semântico** (SemVer) para releases/imagens.

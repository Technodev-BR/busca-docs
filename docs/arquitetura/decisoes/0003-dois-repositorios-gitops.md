# ADR-0003 — Dois repositórios (aplicação + GitOps)

- **Status:** Aceito
- **Data:** 2026-07-16

## Contexto
Vamos versionar código no **GitHub** e fazer deploy em **Kubernetes**. Precisamos definir como
organizar os repositórios e como o deploy chega ao cluster.

## Decisão
Adotar o **padrão GitOps de dois repositórios**:

1. **`busca-busca` (monorepo de aplicação)** — código de `backend/`, `collector/`, `frontend/`,
   `deploy/k8s/` (Kustomize — ver [ADR-0015](0015-kustomize-apps-helm-terceiros.md)) e `.github/workflows/`.
2. **`busca-busca-gitops` (config)** — **fonte da verdade do que roda no cluster**, observado
   pelo **Argo CD** (`apps/`, `environments/{dev,staging,prod}`, `infra/`).

O CI **nunca faz `kubectl apply`**; ele apenas **atualiza a tag da imagem** no repo GitOps
(commit/PR), e o Argo CD sincroniza. Detalhes em
[Repositórios](../../infraestrutura/repositorios.md) e
[Kubernetes & GitOps](../../infraestrutura/kubernetes-gitops.md).

## Consequências
- **+** Deploy **declarativo e auditável**; rollback fácil; separação clara de responsabilidades.
- **+** Monorepo de app dá PRs atômicos e CI simples (com *path filters* por serviço).
- **−** Mais um repositório para gerenciar; exige disciplina no fluxo de bump de imagem.

## Alternativas consideradas
- **Polyrepo** (um repo por serviço): só compensa quando times/ciclos divergem — adiado.
- **CI aplicando direto no cluster (push)**: perde auditabilidade e self-heal do GitOps — rejeitado.
- **Docs junto do código agora**: manteremos os docs separados por enquanto; podem migrar para
  `busca-busca/docs` quando o monorepo existir (ver [Repositórios](../../infraestrutura/repositorios.md)).

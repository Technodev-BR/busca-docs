# Kubernetes & GitOps

Deploy de **produção** em **k3s** (Kubernetes leve, nó único) numa **VPS da Hostinger**, com
entrega contínua **declarativa** via **Argo CD**. Decisão em
[ADR-0006](../arquitetura/decisoes/0006-infra-k3s-vps-cloudflare.md). Visão visual em
[Diagramas → Fluxo de entrega](../arquitetura/diagramas.md).

## Ambiente de produção (k3s na VPS)
- **k3s** já instalado na VPS Hostinger (**single-node**).
- **Traefik** como **ingress**, mas **subido por nós** (Helm, com nossos *values*, versionado no
  GitOps) — o Traefik **embutido do k3s fica desabilitado** (`--disable traefik`). Não usamos Ingress-NGINX.
- **DNS/TLS/exposição**: ver [Rede e exposição](rede-e-exposicao.md) (Cloudflare + `technodev.com.br`).
- **Gerenciamento** (ver pods etc.): ver [Gerenciamento do cluster](gerenciamento-cluster.md).
- **Atenção (nó único):** sem alta disponibilidade — reboot/manutenção derruba os serviços.
  Fazer **backup** do volume do Postgres e dos manifests (GitOps já cobre a config).

## Empacotamento
- **Helm charts** (um por serviço) versionados em `deploy/helm/` no repo de aplicação.
- *Values* por ambiente ficam no repo **GitOps** (`environments/{dev,staging,prod}`).
- Kustomize é alternativa válida.

## Argo CD
- Sincroniza o estado desejado (repo GitOps) → cluster.
- Oferece **diff**, **rollback** com 1 clique, **self-heal** e histórico de sync.
- Padrão **app-of-apps** para orquestrar todas as Applications.

## Estratégia de release
- **Rolling update** por padrão.
- **Canary / blue-green** via **Argo Rollouts** quando precisar de deploy progressivo.

## Plataforma no cluster
- **Traefik** (subido por nós via Helm; o do k3s fica desabilitado) + **cert-manager** com **DNS-01 da Cloudflare** (TLS
  Let's Encrypt, válido também para hosts internos). Detalhes em [Rede e exposição](rede-e-exposicao.md).
- **Segredos**: **Sealed Secrets** ou **External Secrets Operator** (nunca segredo em claro no Git).
- **Storage**: o **`local-path`** padrão do k3s **não suporta VolumeSnapshot**. Para snapshots de
  volume diários usamos **Longhorn** (CSI com snapshot) + **external-snapshotter** +
  `VolumeSnapshotClass`. Ver [Backup & DR](backup-e-dr.md).
- **Banco em produção**: no nó único, **CloudNativePG** (operador) com volume persistente e
  **backup em camadas** (snapshot da VPS + **VolumeSnapshot diário** do PVC + **WAL archiving**
  off-site com PITR); um **Postgres gerenciado** externo é a alternativa mais segura se o orçamento
  permitir. Evitar banco como pod "solto" sem backup. Ver [Backup & DR](backup-e-dr.md).

## Fluxo completo (código → produção)

```
GitHub (push/PR no busca-busca)
  → GitHub Actions: build + testes + SonarQube (Quality Gate) + Trivy (scan)
  → build da imagem Docker (multi-stage) + push no Harbor (re-scan por política)
  → bump da tag de imagem no repo busca-busca-gitops (commit automatizado)
       → Argo CD detecta o diff e sincroniza
            → Kubernetes aplica (rolling/canary via Argo Rollouts)
                 → Observabilidade + Agente IA/MCP monitoram
```

Ver [CI/CD](../qualidade/ci-cd.md), [Registry (Harbor)](registry-harbor.md) e
[Observabilidade](../observabilidade/pilares.md).

# Infraestrutura

Do ambiente de desenvolvimento à produção em k3s.

| Documento | O que traz |
|---|---|
| [Desenvolvimento (Docker)](desenvolvimento-docker.md) | Ambiente local com Docker Compose |
| [Repositórios](repositorios.md) | Padrão de 2 repositórios (app + GitOps) |
| [Kubernetes & GitOps](kubernetes-gitops.md) | Produção em k3s (VPS) + Argo CD |
| [Rede e exposição](rede-e-exposicao.md) | Cloudflare (DNS/TLS), Traefik e VPN |
| [Gerenciamento do cluster](gerenciamento-cluster.md) | Painel público + k9s/Argo (interno) |
| [Configuração & segredos](configuracao-e-segredos.md) | Variáveis por serviço e gestão de segredos |
| [Backup & Disaster Recovery](backup-e-dr.md) | Backup/restore do Postgres e recuperação da VPS |
| [Registry (Harbor)](registry-harbor.md) | Registro de imagens + Trivy/Cosign |

Ver também: [Qualidade](../qualidade/README.md) · [Observabilidade](../observabilidade/README.md).

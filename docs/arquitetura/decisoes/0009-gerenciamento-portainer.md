# ADR-0009 — Portainer como ferramenta de gerenciamento do cluster

- **Status:** Aceito
- **Data:** 2026-07-18

## Contexto
Precisamos de uma UI para **operar o cluster** (ver pods, logs, reiniciar deployments, exec) no
**k3s de nó único** da VPS Hostinger (ver [ADR-0006](0006-infra-k3s-vps-cloudflare.md)). Pelo
[modelo de exposição](../../infraestrutura/rede-e-exposicao.md), **uma** UI pode ficar **pública**
(com autenticação); o resto é interno via VPN. O fator decisivo é o **recurso limitado da VPS**:
queremos gastar CPU/RAM com a aplicação, não com a ferramenta de gestão.

## Decisão
Adotar o **Portainer** como ferramenta padrão de gerenciamento do cluster, complementado pelo
**k9s** no dia a dia via VPN.

- **Portainer** exposto **publicamente** em `portainer.technodev.com.br`, com **autenticação**
  própria e, de preferência, **Cloudflare Access** na frente. Instalado via Helm no GitOps.
- **k9s** (TUI) para operação rápida por SSH/VPN — footprint **zero** no cluster.
- **Argo CD** (estado das apps) e **Grafana** (métricas/logs) já cobrem parte do "observar", então
  o painel de pods pode ser enxuto.

## Consequências
- **+** Leve (~100–300 MB), UI simples para pods/logs/exec/restart, com login e RBAC.
- **+** Sobra recurso na VPS para a aplicação.
- **+** Uma única UI pública, com superfície de ataque controlada (auth + Cloudflare Access).
- **−** É mais uma peça para manter atualizada e proteger (é o único serviço exposto).
- **−** Menos completo que o Rancher para cenários multi-cluster — aceitável no nó único.

## Alternativas consideradas
- **Rancher**: nativo para k3s e muito completo, mas **pesado** (~2 GB+ e vários controllers) —
  overkill para 1 nó pequeno; só compensa com **múltiplos clusters/times**.
- **Headlamp**: também leve e agradável; ótima alternativa se preferirmos um dashboard mais
  "puro". Mantido como plano B.
- **Kubernetes Dashboard**: oficial, porém o login por token atrapalha o dia a dia.
- **Só k9s/Lens (sem UI web pública)**: viável, mas perdemos o acesso rápido por navegador.

Detalhes operacionais em [Gerenciamento do cluster](../../infraestrutura/gerenciamento-cluster.md).

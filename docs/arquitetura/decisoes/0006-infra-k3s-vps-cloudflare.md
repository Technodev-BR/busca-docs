# ADR-0006 — Infra de produção: k3s em VPS Hostinger, Traefik, Cloudflare e VPN

- **Status:** Aceito
- **Data:** 2026-07-18

## Contexto
A produção rodará em uma **VPS da Hostinger** (nó único) com **k3s** já instalado. O domínio
**`technodevbr.com`** está na **Cloudflare**. Queremos: expor **publicamente apenas uma ferramenta
de gerenciamento** do cluster (ver pods etc.), mantendo **todo o resto interno**, acessível via
**VPN**.

## Decisão
- **Orquestrador**: **k3s** (Kubernetes leve) em **nó único** na VPS Hostinger.
- **Ingress**: **Traefik**, **subido por nós** (Helm, *values* próprios, no GitOps) — o Traefik
  embutido do k3s fica **desabilitado** (`--disable traefik`). Substitui o Ingress-NGINX citado antes.
- **DNS**: **Cloudflare** para `technodevbr.com` (subdomínios por serviço).
- **TLS**: **cert-manager** com **desafio DNS-01 da Cloudflare** (funciona também para hosts
  internos, que não são acessíveis pela internet). Alternativa: ACME embutido do Traefik com
  provider Cloudflare.
- **Exposição pública**: **somente** a ferramenta de gerenciamento (ex.: `portainer.technodevbr.com`),
  protegida por autenticação (e, opcionalmente, Cloudflare Access).
- **Acesso interno**: todo o resto (app, Argo CD, Grafana, RabbitMQ mgmt, etc.) só via **VPN**.
- **Gerenciamento**: uma UI de cluster (ver [Gerenciamento do cluster](../../infraestrutura/gerenciamento-cluster.md)).

## Consequências
- **+** Custo baixo e simples de operar (um nó, k3s + Traefik prontos).
- **+** Superfície de ataque mínima: só o painel exposto; o resto atrás de VPN.
- **−** **Nó único = sem alta disponibilidade**; manutenção/reboot derruba tudo. Aceitável no
  estágio atual; escalar para multi-nó depois.
- **−** Recursos limitados da VPS pedem ferramentas leves (evitar stack pesada).
- Detalhes em [Rede e exposição](../../infraestrutura/rede-e-exposicao.md) e
  [Kubernetes & GitOps](../../infraestrutura/kubernetes-gitops.md).

## Alternativas consideradas
- **Kubernetes gerenciado (EKS/GKE/AKS)**: robusto e com HA, porém custo/complexidade altos —
  adiado.
- **Ingress-NGINX**: bom, mas optamos por gerenciar o **Traefik** como serviço próprio (controle
  total dos *values*/versão), desabilitando o embutido do k3s.
- **Cloudflare Tunnel + Access (Zero Trust) no lugar da VPN**: ótima opção sem abrir portas;
  mantida como alternativa à VPN (ver [Rede e exposição](../../infraestrutura/rede-e-exposicao.md)).

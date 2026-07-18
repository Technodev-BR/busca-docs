# ADR-0008 — Traefik gerenciado por nós (k3s sem o Traefik embutido)

- **Status:** Aceito
- **Data:** 2026-07-18

## Contexto
O k3s já entrega um **Traefik embutido**, instalado e atualizado pelo próprio k3s. Queremos
**controle total** sobre a versão, os *values* e a configuração do ingress (middlewares, entrypoints,
integração com cert-manager/Cloudflare) e gerenciá-lo de forma **declarativa no GitOps**, como
qualquer outro componente. Complementa o [ADR-0006](0006-infra-k3s-vps-cloudflare.md).

## Decisão
- **Desabilitar** o Traefik embutido do k3s (`--disable traefik` no install/config do servidor).
- **Subir o Traefik por nós** via **Helm**, com *values* próprios, versionado no **repo GitOps** e
  aplicado pelo Argo CD.
- Manter o Traefik como **ingress único** (portas 80/443 da VPS), com **cert-manager + DNS-01 da
  Cloudflare** para TLS (ver [Rede e exposição](../../infraestrutura/rede-e-exposicao.md)).

## Consequências
- **+** Versão e configuração do ingress **sob nosso controle** e rastreáveis no Git.
- **+** Sem surpresa de upgrade automático do addon do k3s.
- **+** Mesmo fluxo GitOps de todo o resto (Argo CD reaplica em um restore — ver [Backup & DR](../../infraestrutura/backup-e-dr.md)).
- **−** Passamos a ser responsáveis por atualizar o Traefik (deixa de ser "grátis" via k3s).
- **−** Um passo extra no bootstrap do cluster (instalar o Traefik antes das apps).

## Alternativas consideradas
- **Traefik embutido do k3s**: zero configuração inicial, mas pouco controle de versão/values e
  fora do fluxo GitOps — rejeitado.
- **Ingress-NGINX**: alternativa madura, porém preferimos padronizar no Traefik (CRDs
  `IngressRoute`, middlewares) já adotado no [ADR-0006](0006-infra-k3s-vps-cloudflare.md).

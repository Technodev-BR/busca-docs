# Gerenciamento do cluster

Ferramentas para **olhar os pods**, ver logs, reiniciar deployments e operar o **k3s** da VPS.
Aqui vale a regra do [ADR-0006](../arquitetura/decisoes/0006-infra-k3s-vps-cloudflare.md):
**uma** UI pode ficar **pública** (com autenticação); o resto é interno via VPN.

## UI pública: Portainer
A ferramenta padrão é o **Portainer** (decisão em
[ADR-0009](../arquitetura/decisoes/0009-gerenciamento-portainer.md)), exposto em
`portainer.technodevbr.com` com login forte e, de preferência, atrás de **Cloudflare Access**.
É leve (~100–300 MB), tem UI simples para pods/logs/exec/restart e RBAC — ideal para o nó único.

Opções consideradas (contexto: VPS modesta, um nó):

| Ferramenta | Peso | Veredito |
| --- | --- | --- |
| **Portainer** | Leve (~100–300 MB) | **Escolhida** — faz o que precisamos sem pesar. |
| **Headlamp** | Leve (~50–100 MB) | Plano B; dashboard moderno (CNCF), bem enxuto. |
| **Rancher** | Pesado (~2 GB+) | Só se houver **múltiplos clusters**/recurso sobrando. |
| **Kubernetes Dashboard** | Médio | Oficial, mas auth por token atrapalha o dia a dia. |

### Segurança do painel público
- HTTPS obrigatório (cert-manager + Cloudflare, ver [Rede e exposição](rede-e-exposicao.md)).
- Autenticação própria da ferramenta + **Cloudflare Access** (SSO/OTP) na frente, se possível.
- Usuário com o **mínimo de permissão** necessária (evite admin total exposto).

## Ferramentas de linha de comando (via VPN)
- **k9s** — TUI excelente para navegar pods/logs/eventos em tempo real no terminal.
- **kubectl** — base de tudo; use o `kubeconfig` do k3s (`/etc/rancher/k3s/k3s.yaml`) por SSH/VPN.
- **Lens** (desktop) — GUI rica que roda na sua máquina e conecta via VPN (não precisa expor nada).

## Aplicações e observabilidade (internos, via VPN)
- **Argo CD** (`argo.technodevbr.com`) — estado do GitOps, diffs, rollback e sync das apps.
- **Grafana** (`grafana.technodevbr.com`) — métricas/logs/traces (ver [Observabilidade](../observabilidade/pilares.md)).
- **RabbitMQ Management** — filas e mensagens (ver [Eventos RabbitMQ](../contratos/eventos-rabbitmq.md)).

## Resumo do acesso
| Ferramenta | Exposição |
| --- | --- |
| Portainer/Headlamp (painel) | **Público** (autenticado) |
| k9s / kubectl / Lens | Local + **VPN** |
| Argo CD / Grafana / RabbitMQ | **Interno (VPN)** |

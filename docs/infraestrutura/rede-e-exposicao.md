# Rede e exposição (Cloudflare, Traefik e VPN)

Como o tráfego entra no cluster **k3s** da VPS Hostinger, como resolvemos o domínio
**`technodev.com.br`** na **Cloudflare** e o que fica **público** vs. **interno (VPN)**.
Decisão em [ADR-0006](../arquitetura/decisoes/0006-infra-k3s-vps-cloudflare.md).

## Princípio de exposição
- **Público** (via Cloudflare → internet): **apenas a ferramenta de gerenciamento** do cluster,
  ex.: `portainer.technodev.com.br`, sempre com **autenticação** (e, de preferência, Cloudflare Access).
- **Interno** (somente pela **VPN**): **todo o resto** — app/frontend, API, Argo CD, Grafana,
  RabbitMQ management, etc.

```
Internet ──> Cloudflare (DNS + proxy) ──> VPS (IP público) ──> Traefik ──> portainer (público)
Usuário ──> VPN ──────────────────────> VPS (IP interno) ──> Traefik ──> busca-busca/argo/grafana/... (interno)
```

## DNS na Cloudflare
Domínio `technodev.com.br` gerenciado na Cloudflare. Subdomínios:

| Host | Destino | Exposição | Proxy Cloudflare |
| --- | --- | --- | --- |
| `portainer.technodev.com.br` | UI de gerenciamento (Portainer) | Público | Proxied (laranja) |
| `busca-busca.technodev.com.br` | Frontend Angular | Interno (VPN) | DNS only (cinza) |
| `api.technodev.com.br` | API Java | Interno (VPN) | DNS only |
| `argo.technodev.com.br` | Argo CD | Interno (VPN) | DNS only |
| `traefik.technodev.com.br` | Dashboard do Traefik | Interno (VPN) | DNS only |
| `grafana.technodev.com.br` | Grafana | Interno (VPN) | DNS only |
| `rabbit.technodev.com.br` | RabbitMQ mgmt | Interno (VPN) | DNS only |

> Hosts internos podem apontar para o **IP privado da VPN** (ex.: faixa Tailscale/WireGuard) em
> vez do IP público, garantindo que só resolvem/funcionam dentro da VPN.

## Ingress: Traefik (subido por nós)
- O **Traefik é um serviço que nós mesmos subimos** (Helm, com *values* próprios, versionado no
  GitOps). O Traefik **embutido do k3s fica desabilitado** (`--disable traefik` no install/config)
  para não conflitar.
- Expomos serviços com `Ingress` / `IngressRoute` (CRD do Traefik).
- Um único ponto de entrada (portas 80/443 da VPS) roteia por **host/path**.
- Exemplo de `Ingress` para um serviço interno:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-cloudflare
spec:
  rules:
    - host: busca-busca.technodev.com.br
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: busca-busca-frontend
                port:
                  number: 80
  tls:
    - hosts: [busca-busca.technodev.com.br]
      secretName: busca-busca-tls
```

## TLS: cert-manager + DNS-01 da Cloudflare
Como os hosts internos **não** são acessíveis pela internet, o desafio HTTP-01 não funciona para
eles. Usamos **DNS-01 via Cloudflare**, que valida criando um registro TXT — funciona para
qualquer host do domínio.

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-cloudflare
spec:
  acme:
    email: admin@technodev.com.br
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: letsencrypt-cloudflare-key
    solvers:
      - dns01:
          cloudflare:
            apiTokenSecretRef:
              name: cloudflare-api-token
              key: api-token
```

> O **token da Cloudflare** (escopo `Zone.DNS:Edit` na zona `technodev.com.br`) entra como
> `Secret`, gerenciado por Sealed Secrets/External Secrets — **nunca** em claro no Git.
> Alternativa: **ACME embutido do Traefik** com provider Cloudflare (dispensa o cert-manager).

## VPN (acesso interno)
Opção recomendada: **Tailscale** (malha WireGuard, simples de instalar na VPS e nos clientes;
tem inclusive operador para Kubernetes). Alternativa self-hosted: **WireGuard** puro.

- Instalar o cliente na VPS e nos dispositivos; hosts internos resolvem/roteiam pela faixa da VPN.
- Só o painel público fica fora da VPN.

**Alternativa sem VPN tradicional:** como o DNS já está na Cloudflare, dá para usar
**Cloudflare Tunnel + Access (Zero Trust)** — o túnel sai da VPS para a Cloudflare (sem abrir
portas) e o Access aplica login (SSO/OTP) por aplicação. Bom substituto à VPN para acesso interno.

## Firewall da VPS
- Expor **apenas 80/443** publicamente (Traefik) + porta da VPN (ex.: WireGuard `51820/udp`).
- Bloquear acesso direto ao `kube-apiserver` (6443) na internet; administrar via VPN.
- Se usar Cloudflare Tunnel, é possível **não** abrir 80/443 publicamente.

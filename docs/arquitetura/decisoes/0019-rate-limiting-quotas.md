# ADR-0019 — Rate limiting, quotas e WAF

- **Status:** Aceito
- **Data:** 2026-07-18 · **Aceito em:** 2026-07-18

## Contexto
A RNF-06 e a [Segurança](../../qualidade/seguranca.md) citam **rate limiting**, mas sem limites,
camadas ou responsáveis definidos. Precisamos proteger a API pública contra abuso/scraping e o
fluxo de **login OIDC** (ADR-0013), sem afetar a ingestão interna.

## Decisão
Defesa em **camadas**:

1. **Borda (Cloudflare)**: WAF gerenciado + regras contra bots e proteção de DDoS.
2. **Traefik (ingress)**: `rateLimit` middleware **por IP** (burst + média) para toda a API pública.
3. **Spring (aplicação)**: limites **por usuário/rota** com `bucket4j` (respostas `429` +
   `Retry-After`), especialmente em rotas caras/sensíveis.

Quotas de partida (calibráveis):

| Superfície | Limite default |
|---|---|
| API pública anônima | 60 req/min por IP |
| API pública autenticada | 300 req/min por usuário |
| Rotas de auth (`/oauth2/**`, `/auth/refresh`) | 10 req/min por IP |
| Ingestão interna (`/internal/**`) | **sem rate limit de borda** — protegida por `X-Internal-Token`, não exposta no ingress |

- `429` segue **Problem Details** (RFC 7807) com `Retry-After`.
- Métrica de **taxa de 429** e top-talkers na observabilidade (detectar abuso).

## Arquitetura, robustez e escala
- **Contadores distribuídos:** `bucket4j` com **Redis** ([ADR-0007](0007-cache-redis.md)) para os
  limites da aplicação, de modo que o limite valha entre **todas as réplicas** do backend (não por
  instância). Algoritmo **token bucket** (permite rajada controlada).
- **Chaves de limite:** por **IP** (anônimo), por **usuário** (autenticado) e por **rota**; a chave
  correta evita punir usuários legítimos atrás de NAT compartilhado.
- **Headers padrão:** responder `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset` e, no
  `429`, `Retry-After` — clientes bem-comportados se auto-regulam.
- **Proteção de auth:** limite estrito nas rotas OIDC/refresh + **backoff/lockout** progressivo e,
  se necessário, **CAPTCHA** como fallback contra brute-force de callback (ADR-0013).
- **Borda:** Cloudflare (WAF gerenciado, regras de bot, mitigação de DDoS volumétrico) + Traefik
  `rateLimit` por IP como segunda linha; a **ingestão interna** nunca é exposta na borda.
- **Degradação graciosa:** se o Redis dos contadores cair, aplicar **fail-open** com limite local
  conservador por instância (não derrubar a API) e alertar.
- **Configuração como dado:** limites por rota em config versionada, ajustáveis sem redeploy;
  processo de **tuning** guiado por métricas.
- **Observabilidade:** taxa de `429` por rota, top IPs/usuários, latência adicionada pelo middleware,
  hits de regra de WAF (ver [pilares](../../observabilidade/pilares.md)).

## Consequências
- **+** Abuso/scraping contido em várias camadas; login protegido contra brute-force de callback.
- **+** Limites explícitos e observáveis; tuning por rota.
- **−** Risco de bloquear usuários legítimos atrás de NAT/corporativo → limites autenticados por
  usuário mitigam.
- **−** Estado de contadores (Redis) para limites distribuídos entre réplicas do backend.

## Alternativas consideradas
- **Só Cloudflare**: não conhece usuário/rota nem regra de negócio — insuficiente sozinho.
- **Só aplicação**: deixa a borda exposta a floods antes de chegar ao Spring — rejeitado.

## Referências
- [Segurança](../../qualidade/seguranca.md) · [Rede e exposição](../../infraestrutura/rede-e-exposicao.md)
  · [ADR-0008](0008-traefik-self-managed.md) · [ADR-0013](0013-autenticacao-social-oidc.md)

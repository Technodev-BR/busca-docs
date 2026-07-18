# Configuração & segredos

Como cada serviço é configurado por ambiente e como os **segredos** são tratados — do dev
(Docker Compose) à produção (k3s). Princípio base: **config por variável de ambiente**
(12-Factor) e **nenhum segredo em claro no Git**.

## Princípios
- **Config por ambiente** (`.env` no dev; `ConfigMap`/`Secret` no k3s). Nada de valor fixo no código.
- **Segredo nunca no Git**: nem em `.env` versionado, nem em values do Helm. Use
  **Sealed Secrets** ou **External Secrets Operator**.
- **`.env.example`** versionado como referência (só chaves e valores fictícios).
- **Menor privilégio**: cada credencial com o escopo mínimo (ex.: token Cloudflare só `DNS:Edit`).

## Variáveis por serviço
Matriz de referência (nomes ilustrativos; o `.env.example` é a fonte definitiva).

### Backend (Java)
| Variável | Exemplo | Segredo? |
|---|---|---|
| `DB_URL` | `jdbc:postgresql://db:5432/buscabusca` | não |
| `DB_USER` | `buscabusca` | não |
| `DB_PASSWORD` | `***` | **sim** |
| `RABBITMQ_URL` | `amqp://rabbitmq:5672` | não |
| `RABBITMQ_USER` / `RABBITMQ_PASSWORD` | `app` / `***` | **sim** (senha) |
| `REDIS_URL` | `redis://redis:6379` | não |
| `OAUTH_GOOGLE_CLIENT_ID` / `OAUTH_GOOGLE_CLIENT_SECRET` | `***` | **sim** (secret) |
| `OAUTH_GITHUB_CLIENT_ID` / `OAUTH_GITHUB_CLIENT_SECRET` | `***` | **sim** (secret) |
| `ACCESS_TOKEN_SECRET` | `***` (assina o JWT de access, ~15min) | **sim** |
| `ACCESS_TOKEN_TTL` / `REFRESH_TOKEN_TTL` | `15m` / `30d` | não |
| `INGEST_API_TOKEN` | `***` (auth da ingestão) | **sim** |

### Collector (Python)
| Variável | Exemplo | Segredo? |
|---|---|---|
| `INGEST_API_URL` | `http://backend:8080/internal/ingest` | não |
| `INGEST_API_TOKEN` | `***` | **sim** |
| `CAIXA_CSV_BASE_URL` | URL oficial do CSV | não |
| `SCHEDULE_CRON` | `0 5 * * *` | não |
| `LOG_LEVEL` | `INFO` | não |

### Frontend (Angular)
Config em tempo de build/serve (via Nginx). Normalmente só `API_BASE_URL`. **Não** colocar
segredo no frontend (tudo que vai ao browser é público).

### Infra/plataforma
| Variável/segredo | Onde | Segredo? |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` (DNS-01) | cert-manager | **sim** |
| Credenciais do Harbor (pull) | `imagePullSecret` | **sim** |
| Credenciais do Postgres (prod) | CloudNativePG / Secret | **sim** |

## Segredos no desenvolvimento
- Copie `.env.example` → `.env` e preencha localmente. **`.env` está no `.gitignore`.**
- Compose injeta via `env_file`/`environment`. Ver
  [Desenvolvimento (Docker)](desenvolvimento-docker.md).

## Segredos em produção (k3s)
Duas opções (ver [Kubernetes & GitOps](kubernetes-gitops.md)):

- **Sealed Secrets**: você cifra o segredo com a chave pública do controller e **comita o cifrado**
  no repo GitOps; só o cluster consegue decifrar. Simples e GitOps-friendly.
- **External Secrets Operator**: os segredos vivem num cofre externo (ex.: Vault) e o operador os
  sincroniza como `Secret` no cluster. Melhor para rotação centralizada.

> Regra de ouro: o **repo GitOps nunca contém segredo em claro** — só *SealedSecret* (cifrado) ou
> referência do External Secrets.

## Rotação
- Rotacionar `ACCESS_TOKEN_SECRET`, **client secrets OAuth** (Google/GitHub), tokens de ingestão e
  senha do banco periodicamente e após qualquer suspeita de vazamento. Refresh tokens são
  **revogáveis** por usuário (tabela `token_atualizacao`).
- Token da Cloudflare: rotacionar pela dashboard e atualizar o Secret (sem downtime do TLS).

Ver também: [Segurança](../qualidade/seguranca.md) · [Rede e exposição](rede-e-exposicao.md) ·
[Backup & DR](backup-e-dr.md).

# Desenvolvimento (Docker Compose)

O **Docker Compose** é o ambiente de **desenvolvimento**. Em **produção**, o deploy é em
**k3s** via Argo CD (ver [Kubernetes & GitOps](kubernetes-gitops.md)).

## Layout do monorepo de aplicação

```
busca-busca/
  backend/            (Java)      -> Dockerfile multi-stage (Maven build -> JRE)
  collector/          (Python)    -> Dockerfile (slim)
  frontend/           (Angular)   -> Dockerfile multi-stage (node build -> nginx)
  infra/
    db/init/          # scripts SQL de bootstrap (extensão PostGIS)
    nginx/            # config do proxy (se separado)
  docker-compose.yml
  .env.example        # NUNCA versionar .env real
```

## Serviços do `docker-compose.yml`
- `db` — imagem `postgis/postgis:16-3.4`, volume nomeado, `healthcheck` com `pg_isready`.
- `rabbitmq` — imagem `rabbitmq:3-management`, `healthcheck` com `rabbitmq-diagnostics ping`;
  UI de gestão em `:15672` (mensageria — ver [ADR-0005](../arquitetura/decisoes/0005-mensageria-rabbitmq.md)).
- `redis` — imagem `redis:7`, cache de buscas usado pela API.
- `backend` — Java; `depends_on: db, rabbitmq, redis (service_healthy)`; expõe `/api`; Flyway no start.
- `collector` — Python; `depends_on: backend`; roda o pipeline (agendado).
- `frontend` — Nginx servindo o Angular + proxy `/api` → `backend`.
- *(opcional)* `pgadmin`/`adminer`, stack de observabilidade (`grafana/otel-lgtm`).

## Boas práticas de container
- **Multi-stage builds** (imagem final pequena, sem ferramentas de build).
- Rodar como **usuário não-root**; imagens *slim/alpine* quando possível.
- **`.dockerignore`** por serviço (não copiar `node_modules`, `target`, `.venv`).
- **`healthcheck`** em cada serviço e `depends_on: condition: service_healthy`.
- Config **100% por env** (`.env` + `env_file`); segredos fora do git.
- **Volumes nomeados** para Postgres e storage de fotos.
- **Rede interna** dedicada; só o Nginx e a API expostos.
- **Versões fixas** (pinned) das imagens base; logs em stdout.

## Comandos

```bash
cp .env.example .env       # ajuste as variáveis
docker compose up -d       # sobe tudo
docker compose logs -f backend
docker compose down        # derruba (add -v para apagar volumes)
```

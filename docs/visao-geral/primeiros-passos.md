# Primeiros passos

Guia rápido para começar a trabalhar no Busca-Busca — seja lendo a documentação, seja subindo o
ambiente local.

## 1. Entenda o projeto (10 min)
Leia nesta ordem:
1. [Objetivo e escopo](objetivo-e-escopo.md) — o problema e a fronteira do produto.
2. [Visão geral da arquitetura](../arquitetura/visao-geral.md) — as camadas e o fluxo.
3. [Regras de negócio](../dominio/regras-de-negocio.md) — o coração do domínio.

## 2. Fluxo docs-first
Este é um projeto **docs-first**: **primeiro documentamos, depois codamos**.

- Decisão técnica nova? Registre um [ADR](../arquitetura/decisoes/README.md).
- Regra de negócio nova? Documente em [Domínio](../dominio/README.md) antes de implementar.
- Integração nova? Defina o [contrato](../contratos/README.md) primeiro (API-first).
- Convenções de escrita e commits em [CONTRIBUTING](../../CONTRIBUTING.md).

## 3. Suba o ambiente local (quando o código existir)
O ambiente de desenvolvimento é **Docker Compose** (detalhes em
[Desenvolvimento (Docker)](../infraestrutura/desenvolvimento-docker.md)).

```bash
git clone <repo-da-aplicacao> busca-busca
cd busca-busca
cp .env.example .env        # ajuste as variáveis (ver Configuração & segredos)
docker compose up -d        # sobe db, rabbitmq, redis, backend, collector, frontend
docker compose logs -f backend
```

Serviços úteis no dev:

| Serviço | URL padrão |
|---|---|
| Frontend (Angular) | http://localhost:4200 (ou via Nginx) |
| API (Java) | http://localhost:8080/api |
| RabbitMQ management | http://localhost:15672 |
| Postgres | localhost:5432 |

Variáveis e segredos: ver [Configuração & segredos](../infraestrutura/configuracao-e-segredos.md).

## 4. Como isso vai para produção
Push no repo de aplicação → CI (testes, SonarQube, Trivy) → imagem no Harbor → bump no repo GitOps
→ Argo CD sincroniza no **k3s**. Ver [CI/CD](../qualidade/ci-cd.md) e
[Kubernetes & GitOps](../infraestrutura/kubernetes-gitops.md).

## Próximos passos
- Produto: [Requisitos](../produto/requisitos.md) · [Features](../produto/features.md)
- Serviços: [Backend](../servicos/backend-java.md) · [Collector](../servicos/collector-python.md) · [Frontend](../servicos/frontend-angular.md)

Ver também: [Roadmap](roadmap.md) · [Glossário](glossario.md).

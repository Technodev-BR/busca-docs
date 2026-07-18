# Stack tecnológica

<div class="logo-grid">
  <div class="logo-card"><img src="/logos/java.svg" alt="Java" /><span>Java 21</span></div>
  <div class="logo-card"><img src="/logos/spring.svg" alt="Spring Boot" /><span>Spring Boot</span></div>
  <div class="logo-card"><img src="/logos/python.svg" alt="Python" /><span>Python 3.12</span></div>
  <div class="logo-card"><img src="/logos/angular.svg" alt="Angular" /><span>Angular</span></div>
  <div class="logo-card"><img src="/logos/typescript.svg" alt="TypeScript" /><span>TypeScript</span></div>
  <div class="logo-card"><img src="/logos/sass.svg" alt="SASS" /><span>SASS/SCSS</span></div>
  <div class="logo-card"><img src="/logos/postgresql.svg" alt="PostgreSQL" /><span>PostgreSQL + PostGIS</span></div>
  <div class="logo-card"><img src="/logos/redis.svg" alt="Redis" /><span>Redis</span></div>
  <div class="logo-card"><img src="/logos/rabbitmq.svg" alt="RabbitMQ" /><span>RabbitMQ</span></div>
  <div class="logo-card"><img src="/logos/docker.svg" alt="Docker" /><span>Docker</span></div>
  <div class="logo-card"><img src="/logos/kubernetes.svg" alt="Kubernetes" /><span>k3s (Kubernetes)</span></div>
  <div class="logo-card"><img src="/logos/argocd.svg" alt="Argo CD" /><span>Argo CD</span></div>
  <div class="logo-card"><img src="/logos/traefik.svg" alt="Traefik" /><span>Traefik</span></div>
  <div class="logo-card"><img src="/logos/nginx.svg" alt="Nginx" /><span>Nginx</span></div>
  <div class="logo-card"><img src="/logos/cloudflare.svg" alt="Cloudflare" /><span>Cloudflare</span></div>
</div>

| Camada | Tecnologia | Observações |
|---|---|---|
| Backend / API | **Java 21 + Spring Boot 3** | Arquitetura hexagonal (ports & adapters) |
| Coleta / Automação | **Python 3.12** | Pipeline de download + parsing do CSV |
| Frontend | **Angular 17+** (standalone + signals) | UI, mapa e filtros |
| Banco | **PostgreSQL 16 + PostGIS** | Único banco relacional; dono do schema é o backend |
| Migrations | **Flyway** (no backend Java) | Versiona o schema; Python não altera schema |
| Mensageria | **RabbitMQ** | Processamento assíncrono (ver [ADR-0005](decisoes/0005-mensageria-rabbitmq.md)) |
| Cache | **Redis** | Cache de buscas quentes na API REST |
| Estilo (front) | **SASS/SCSS** | Estilização com variáveis/tokens (ver [Frontend](../servicos/frontend-angular.md)) |
| Empacotamento (dev) | **Docker + Docker Compose** | 1 container por serviço |
| Deploy (prod) | **k3s + Argo CD (GitOps)** | VPS Hostinger, Traefik/Cloudflare — ver [Kubernetes & GitOps](../infraestrutura/kubernetes-gitops.md) e [Rede e exposição](../infraestrutura/rede-e-exposicao.md) |
| Reverse proxy | **Nginx** | Serve o Angular e faz proxy `/api` → backend |

A decisão e os trade-offs estão registrados em
[ADR-0001 — Stack tecnológica](decisoes/0001-stack-tecnologica.md).

## Princípio de fronteira (Java ↔ Python)

O **backend Java é o dono do banco/schema**. O coletor Python **não escreve direto nas tabelas de
negócio**; envia os dados por uma **API de ingestão** (`POST /internal/ingest/...`). Isso mantém
regras e validações em um lugar só e evita dois sistemas acoplados ao mesmo schema.

> *Alternativa mais simples (MVP):* o Python grava numa tabela de **staging** (`raw_*`) e o backend
> normaliza. Evite dar ao Python acesso de escrita às tabelas de domínio.

## Detalhes por serviço

- [Backend (Java)](../servicos/backend-java.md) — estrutura hexagonal e libs Maven.
- [Collector (Python)](../servicos/collector-python.md) — pipeline e libs.
- [Frontend (Angular)](../servicos/frontend-angular.md) — organização por feature e libs.

## Catálogo completo de ferramentas

Ver [Ferramentas](ferramentas.md) para o toolchain open source completo (CI/CD,
observabilidade, segurança, etc.).

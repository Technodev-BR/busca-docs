# Ferramentas (toolchain)

Catálogo do toolchain — **open source** sempre que possível.

## Aplicação
| Área | Ferramenta |
|---|---|
| Backend | Java 21, Spring Boot 3, Maven, Hibernate/JPA, Flyway, MapStruct, Lombok, springdoc-openapi |
| Coleta | Python 3.12, httpx, tenacity, pandas, pydantic, APScheduler, structlog, uv, selectolax (HTML), pika (RabbitMQ) |
| Frontend | Angular, **SASS/SCSS**, Angular Material, ngx-leaflet, RxJS/Signals, ESLint/Prettier |
| Banco | PostgreSQL 16 + PostGIS |
| Mensageria | **RabbitMQ** (processamento assíncrono) |
| Cache | **Redis** (buscas quentes) |

## Qualidade & testes
| Área | Ferramenta |
|---|---|
| Testes Java | JUnit 5, Mockito, AssertJ, Testcontainers, Spring Cloud Contract, JaCoCo, PIT |
| Testes Python | pytest, ruff, mypy |
| Testes Front | Jasmine/Karma (ou Jest), Cypress/Playwright |
| Carga | k6 (ou Gatling) |
| Qualidade | **SonarQube** (Quality Gate) |
| Segurança | **Trivy**, Dependabot/Renovate |

## Entrega & infraestrutura
| Área | Ferramenta |
|---|---|
| SCM | **GitHub** |
| CI | **GitHub Actions** |
| Registry | **Harbor** (OSS) / ghcr.io |
| Empacotamento | Docker, Helm |
| Orquestração (prod) | **k3s** (VPS Hostinger, nó único), **Argo CD**, **Argo Rollouts** |
| Ingress/TLS | **Traefik** (subido via Helm; embutido do k3s desabilitado), cert-manager (DNS-01 Cloudflare) |
| DNS | **Cloudflare** (`technodev.com.br`) |
| VPN / acesso interno | **Tailscale** / WireGuard (ou Cloudflare Tunnel + Access) |
| Gerenciamento do cluster | **Portainer** (painel — ADR-0009), **k9s**, Lens (Headlamp: plano B) |
| Segredos | Sealed Secrets / External Secrets (+ Vault) |
| Banco (prod) | CloudNativePG (ou gerenciado) |

## Observabilidade & operação
| Área | Ferramenta |
|---|---|
| Métricas | Micrometer, Prometheus |
| Logs | structlog/Logback (JSON), Loki (ou ELK/OpenSearch) |
| Traces | OpenTelemetry, Tempo (ou Jaeger) |
| Dashboards | Grafana |
| Alertas | Alertmanager |
| AIOps | Agente IA via **MCP** (GitHub, SonarQube, observabilidade) |
| Notificação | Slack, Microsoft Teams, e-mail, (Opsgenie/PagerDuty) |

## Evolução (quando necessário)
| Área | Ferramenta |
|---|---|
| Busca textual/facetada | OpenSearch/Elasticsearch |
| Feature flags | Unleash |
| IaC | Terraform / Ansible |
| Resiliência | Resilience4j |
| Qualidade de dados | dbt / testes de dados |
| DX | Dev Containers, Makefile, perfis do docker compose |

Ver também: [Stack tecnológica](stack.md) · [Visão geral](README.md).

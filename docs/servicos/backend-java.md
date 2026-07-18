# Backend (Java + Spring Boot)

Arquitetura **hexagonal / Clean (Ports & Adapters)**: domínio puro no centro, infraestrutura nas
bordas. O backend é o **dono do banco/schema**.

## Estrutura

```
backend/
  pom.xml
  src/main/java/br/com/buscabusca/
    BuscaBuscaApplication.java
    domain/                 # regras de negócio puras (sem Spring/JPA)
      model/                #   Imovel, AnaliseCusto, Money, Endereco (VOs)
      port/
        in/                 #   casos de uso (interfaces): BuscarImoveisUseCase...
        out/                #   ImovelRepositoryPort, GeocodingPort...
      service/              #   implementação dos casos de uso (regras)
    application/            # orquestração/DTOs de caso de uso (opcional)
    infrastructure/
      persistence/          # adapters JPA: entities, repos, mappers (MapStruct)
      web/                  # controllers REST, DTOs de API, exception handler
      ingest/               # endpoints internos de ingestão (recebe do Python)
      config/               # beans, security, openapi
  src/main/resources/
    application.yml
    db/migration/           # Flyway: V1__init.sql, V2__...
  src/test/java/...         # JUnit 5 + Testcontainers
```

**Regra de dependência:** `web/persistence/ingest` dependem de `domain`, **nunca o contrário**.
O domínio não conhece Spring nem JPA.

## Funções (casos de uso)
O backend é o **dono do domínio e do banco**. Casos de uso agrupados por responsabilidade — cada um
é uma **porta de entrada** (`port/in`) implementada em `domain/service`.

### Ingestão (interno — recebe do coletor)
| Caso de uso | Responsabilidade | Regras |
|---|---|---|
| `IngerirLoteCsvUseCase` | Recebe o lote do coletor, grava `coleta_bruta`, faz **upsert idempotente** por `codigo`, detecta mudança de preço/desconto/status e grava `historico_preco`; publica `imovel.recebido` e `imovel.enriquecer`. | RN-01, RN-02 |
| `IngerirDetalheUseCase` | Persiste `imovel_detalhe` (1:1) e `imovel_foto`; recalcula custo/score; publica `imovel.enriquecido`. | RN-05, RN-07 |
| `ConciliarAusenciasUseCase` | Compara os `codigo` do snapshot atual com os `disponivel` no banco e aplica ciclo de vida (carência → `vendido`/`removido`). | **RN-09** |
| `MarcarStatusImovelUseCase` | Aplica transição de status (inclui sinal de `404`/indisponível vindo do detalhe) e registra em `historico_preco`. | RN-02, RN-09 |

### Processamento (workers — consomem eventos do RabbitMQ)
| Caso de uso | Responsabilidade | Regras |
|---|---|---|
| `NormalizarImovelUseCase` | Normaliza endereço/bairro/tipo e extrai áreas da descrição. | RN-03 |
| `GeocodificarImovelUseCase` | Resolve `localizacao` `geography(Point)` via `GeocodingPort` (usa CEP do detalhe quando houver). | RN-03 |
| `CalcularCustoUseCase` | Calcula **custo total** e **desconto real** (base = 2ª praça) e grava `analise_custo`. | RN-05 |
| `CalcularScoreUseCase` | Score de viabilidade + nível de confiança; sinaliza riscos (ocupação/dívidas). | RN-06, RN-07 |
| `AnalisarJuridicoUseCase` (evolução) | Via `AnaliseJuridicaPort` (LLM plugável), extrai flags jurídicas do edital/matrícula (nua-propriedade, fração, ônus) com grounding; alimenta o score. Ver [ADR-0014](../arquitetura/decisoes/0014-analise-juridica-ia.md). | RN-07, RN-08 |

### Consulta (API pública)
| Caso de uso | Responsabilidade |
|---|---|
| `BuscarImoveisUseCase` | Busca com filtros (UF, cidade, tipo, modalidade, faixa de preço/desconto real, ocupação), **busca espacial** (raio/bbox via PostGIS), ordenação e paginação. Cache Redis; por padrão só `disponivel` (filtro "incluir encerrados"). |
| `ObterImovelUseCase` | Detalhe completo: imóvel + `imovel_detalhe` + fotos + `analise_custo` + histórico. |
| `ListarHistoricoPrecoUseCase` | Timeline de preço/status para o gráfico de tendência. |

### Engajamento (fase com autenticação)
| Caso de uso | Responsabilidade |
|---|---|
| `ProcessarLoginSocialUseCase` | Após o callback OIDC (Google/GitHub), faz **upsert** do `usuario` por `provedor`+`provedor_id` e emite access+refresh (cookies HttpOnly). Ver [ADR-0013](../arquitetura/decisoes/0013-autenticacao-social-oidc.md). |
| `RenovarTokenUseCase` | Valida o refresh, **rotaciona** (detecção de reúso) e emite novo par (`/api/v1/auth/refresh`). |
| `EncerrarSessaoUseCase` | Revoga o refresh atual (ou todos os dispositivos) no `logout`. |
| `ObterUsuarioAtualUseCase` | Retorna o usuário autenticado (`/api/v1/auth/me`). |
| `FavoritarImovelUseCase` / `ListarFavoritosUseCase` | Gerência de favoritos. |
| `CriarAlertaUseCase` / `AvaliarAlertasUseCase` | Alertas por filtro salvo; dispara notificação (imóvel favoritado **vendido**, **queda de preço**). | 

**Transversais:** publicação/consumo de eventos (`port/out` + adapters AMQP), **idempotência** por
`codigo`, **DLQ** para falhas. **Segurança:** **login social OIDC** (Google/GitHub) com sessão em
**cookie HttpOnly** (padrão BFF) + **CSRF** na API pública; **`X-Internal-Token`** na ingestão.
**Sem senha armazenada** — ver [ADR-0013](../arquitetura/decisoes/0013-autenticacao-social-oidc.md).

## Libs (Maven)
- `spring-boot-starter-web` — REST.
- `spring-boot-starter-data-jpa` + `hibernate-spatial` — persistência (+ tipos PostGIS).
- `org.postgresql:postgresql` — driver.
- `flyway-core` + `flyway-database-postgresql` — migrations.
- `spring-boot-starter-validation` — Bean Validation (jakarta).
- `org.mapstruct:mapstruct` — mapeamento entity ↔ domínio ↔ DTO.
- `org.projectlombok:lombok` — reduz boilerplate.
- `springdoc-openapi-starter-webmvc-ui` — Swagger/OpenAPI.
- `spring-boot-starter-actuator` + `micrometer` — health, métricas.
- `spring-boot-starter-security` + `spring-boot-starter-oauth2-client` — **login social OIDC**
  (Google/GitHub), sessão em cookie HttpOnly + CSRF (padrão BFF; ver [ADR-0013](../arquitetura/decisoes/0013-autenticacao-social-oidc.md)).
- `spring-boot-starter-amqp` — **RabbitMQ** (publicar/consumir eventos; ver [ADR-0005](../arquitetura/decisoes/0005-mensageria-rabbitmq.md)).
- `spring-boot-starter-cache` + `spring-boot-starter-data-redis` — **cache** de buscas (Redis).
- **Testes:** `spring-boot-starter-test` (JUnit 5, Mockito, AssertJ) + `testcontainers`
  (Postgres **e** RabbitMQ reais).
- Build: **Maven**; Java **21 LTS**.

## Mensageria e cache

- **RabbitMQ**: a ingestão publica eventos (`imovel.recebido`); **workers** consomem e processam
  (normalização, geocoding, custos, score). Usar **DLQ** para falhas e **idempotência** por
  `codigo`. Ver [Visão geral](../arquitetura/visao-geral.md) e
  [ADR-0005](../arquitetura/decisoes/0005-mensageria-rabbitmq.md).
- **Redis (cache)**: `@Cacheable` nas buscas mais frequentes; invalidar ao atualizar o imóvel.

## Criar o projeto

Via [Spring Initializr](https://start.spring.io) (CLI):

```bash
curl https://start.spring.io/starter.zip -d type=maven-project -d language=java \
  -d bootVersion=3.3.2 -d javaVersion=21 -d groupId=br.com.buscabusca \
  -d artifactId=backend -d name=backend -d packageName=br.com.buscabusca \
  -d dependencies=web,data-jpa,postgresql,flyway,validation,actuator,security,oauth2-client \
  -o backend.zip
unzip backend.zip -d backend && rm backend.zip
```

Rodar:
```bash
cd backend
./mvnw spring-boot:run
```

## Endpoints
**API Pública** (consumida pelo frontend) — contrato em [API Pública](../contratos/api-publica.md) /
[openapi-api.yaml](../contratos/openapi-api.yaml):
- `GET /api/v1/imoveis` — busca/filtros/mapa (paginado).
- `GET /api/v1/imoveis/{id}` — detalhe + análise de custo.
- `GET /api/v1/imoveis/{id}/historico` — histórico de preço/status.
- `GET|POST|DELETE /api/v1/favoritos` · `GET|POST|PUT|DELETE /api/v1/alertas` — engajamento (JWT).
- `POST /api/v1/auth/registrar|login` — autenticação.

**API interna de ingestão** — contrato em [API de Ingestão](../contratos/api-ingestao.md) /
[openapi-ingestao.yaml](../contratos/openapi-ingestao.yaml):
- `POST /internal/ingest/imoveis` e `/internal/ingest/imoveis/{codigo}/detalhe` (recebe do coletor).

**Operação:** `GET /actuator/health`, `/actuator/prometheus`.

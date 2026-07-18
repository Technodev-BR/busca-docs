# Estratégia de testes

Seguimos a **pirâmide de testes**: muitos unitários, alguns de integração, poucos E2E.

## Backend (Java)
- **Unitários**: JUnit 5 + AssertJ + Mockito — foco no **domínio** (regras de custo/score).
- **Integração**: **Testcontainers** subindo **PostgreSQL/PostGIS real** para testar repositórios
  e migrations Flyway; `@SpringBootTest` para fluxos de API (MockMvc/WebTestClient).
- **Contrato**: **Spring Cloud Contract** (ou Pact) — contrato coletor Python ↔ API de ingestão e
  API ↔ frontend.
- **Cobertura**: JaCoCo com *gate* mínimo (ex.: 80% no domínio).
- **Mutation testing** (opcional, alto valor no domínio): **PIT**.

## Coleta (Python)
- **pytest** para downloader/parser/mapper — fixtures com CSV de exemplo, **inclusive casos ruins**
  (encoding, linhas extras, campos vazios). Base: [Fonte Caixa (CSV)](../dados/fonte-caixa-csv.md).
- **Parser de detalhe (HTML)**: testes com **fixtures de HTML salvo** cobrindo as variações reais
  (com/sem 2ª praça, descrição vazia, imóvel ocupado, campos ausentes). Como o HTML é **frágil**,
  um teste-canário deve **falhar quando o parse vier vazio** (sinal de mudança de layout) — ver
  [Fonte Caixa (detalhe)](../dados/fonte-caixa-detalhe.md) e [ADR-0010](../arquitetura/decisoes/0010-enriquecimento-detalhe.md).
- **Testes de contrato** contra a API de ingestão (schema pydantic ↔ DTO Java), **CSV e `/detalhe`**.
- `ruff` (lint+format) e `mypy` (tipos) no CI.

## Frontend (Angular)
- **Unitários**: Jasmine + Karma (ou Jest) para componentes/serviços/pipes.
- **E2E**: **Cypress** ou **Playwright** — fluxos dos [estudos de caso](../produto/estudos-de-caso.md)
  (buscar, filtrar, abrir detalhe, favoritar).
- ESLint + Prettier.

## Não-funcionais
- **Carga/performance**: **k6** (ou Gatling) nos endpoints de busca com dados realistas
  (validar SLO de p95 — ver [SLO/SLI](../observabilidade/slo-sli.md)).
- **Segurança**: ver [Segurança](seguranca.md).

Tudo roda no pipeline — ver [CI/CD](ci-cd.md).

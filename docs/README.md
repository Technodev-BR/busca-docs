# Busca-Busca

Plataforma para **centralizar a busca, o filtro e a pré-análise de imóveis em leilão** —
começando pela Caixa Econômica Federal — de forma visual, com **cálculo de custos** (ITBI,
custas, registro, reforma) e uma **pré-análise de viabilidade**, podendo evoluir para análise
assistida por **IA**.

> **Documentação docs-first** — esta é a **fonte única da verdade** do projeto. Primeiro
> documentamos objetivo, regras de negócio, arquitetura e decisões; o código nasce a partir daqui.
> É **markdown puro** (sem site a gerar) — ver [ADR-0004](arquitetura/decisoes/0004-documentacao-markdown-puro.md).


> Novo por aqui? Comece pelos [Primeiros passos](visao-geral/primeiros-passos.md).

## Por onde começar

- **Entenda o produto**: [Objetivo e escopo](visao-geral/objetivo-e-escopo.md) ·
  [Requisitos](produto/requisitos.md) · [Features](produto/features.md)
- **Regras de negócio**: [Regras](dominio/regras-de-negocio.md) ·
  [Cálculo de custos](dominio/calculo-de-custos.md) ·
  [Pré-análise](dominio/pre-analise-viabilidade.md)
- **Arquitetura**: [Visão geral](arquitetura/visao-geral.md) · [Stack](arquitetura/stack.md) ·
  [Diagramas](arquitetura/diagramas.md) · [ADRs](arquitetura/decisoes/README.md)
- **Operação**: [Kubernetes & GitOps](infraestrutura/kubernetes-gitops.md) ·
  [Rede e exposição](infraestrutura/rede-e-exposicao.md) ·
  [Backup & DR](infraestrutura/backup-e-dr.md) ·
  [Observabilidade](observabilidade/pilares.md) · [Qualidade](qualidade/testes.md)

## Documentação por tema

Este é o **índice canônico** — cada tema tem uma página de entrada (`README.md` da pasta):

| Tema | Entrada |
|---|---|
| **Visão geral** | [visao-geral/](visao-geral/README.md) — objetivo, primeiros passos, glossário, roadmap |
| **Produto** | [produto/](produto/README.md) — requisitos, features, estudos de caso, rastreabilidade |
| **Arquitetura** | [arquitetura/](arquitetura/README.md) — visão, stack, diagramas, ADRs |
| **Domínio** | [dominio/](dominio/README.md) — regras, cálculo de custos, pré-análise |
| **Contratos** | [contratos/](contratos/README.md) — API de ingestão (OpenAPI), eventos RabbitMQ |
| **Dados** | [dados/](dados/README.md) — modelo de dados, fonte Caixa (CSV/detalhe) |
| **Serviços** | [servicos/](servicos/README.md) — backend (Java), collector (Python), frontend (Angular) |
| **Infraestrutura** | [infraestrutura/](infraestrutura/README.md) — Docker, k3s/GitOps, rede, config/segredos, backup |
| **Observabilidade** | [observabilidade/](observabilidade/README.md) — pilares, SLO/SLI, AIOps, runbooks |
| **Qualidade** | [qualidade/](qualidade/README.md) — testes, CI/CD, segurança |
| **Legal & conformidade** | [legal/](legal/README.md) — LGPD, termos de uso, scraping educado |

## Em uma frase

> Coletar imóveis de leilão de fontes públicas → armazenar e enriquecer → calcular custo real e
> viabilidade → apresentar com busca, filtros e mapa → alertar e, no futuro, opinar com IA.

## Stack (resumo)

**Java 21 + Spring Boot** (backend) · **Python 3.12** (coleta) · **Angular** (frontend) ·
**PostgreSQL + PostGIS** · **Redis** (cache) · **RabbitMQ** (mensageria) · **Docker** (dev) ·
**k3s + Argo CD** (prod, VPS) · toolchain **100% open source**. Detalhes em
[Stack tecnológica](arquitetura/stack.md).

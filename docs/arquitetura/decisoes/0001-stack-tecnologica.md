# ADR-0001 — Stack tecnológica e fronteira Java/Python

- **Status:** Aceito
- **Data:** 2026-07-16

## Contexto
Precisamos definir linguagens/frameworks para backend, coleta e frontend, e como esses serviços
se relacionam com o banco de dados, mantendo regras de negócio coesas.

## Decisão
- **Backend/API:** Java 21 + Spring Boot 3, em **arquitetura hexagonal**.
- **Coleta:** Python 3.12 (melhor ergonomia para scraping/parsing de dados).
- **Frontend:** Angular 17+ (standalone + signals).
- **Banco:** PostgreSQL 16 + PostGIS; **migrations via Flyway** no backend.
- **Fronteira:** o **backend Java é o dono do schema**. O coletor Python **não escreve direto**
  nas tabelas de negócio; envia dados por uma **API de ingestão** (`POST /internal/ingest/...`).

## Consequências
- **+** Regras/validações centralizadas no backend; serviços desacoplados do schema.
- **+** Cada linguagem no que faz melhor (Java para domínio/API; Python para coleta).
- **−** Overhead de manter dois runtimes e um contrato entre eles (mitigado por testes de contrato).
- Alternativa de MVP: Python grava em tabela **staging** e o backend normaliza.

## Alternativas consideradas
- **Tudo em Python (FastAPI)** ou **tudo em Node**: menor custo cognitivo, mas o time quer Java no
  backend e Python na coleta.
- **Python escrevendo direto no banco**: mais simples, porém acopla dois sistemas ao schema e
  espalha regras de negócio — rejeitado.

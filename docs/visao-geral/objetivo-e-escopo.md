# Objetivo e escopo

## Objetivo

Criar uma plataforma que:

1. **Coleta** automaticamente imóveis em leilão de fontes públicas (Caixa e, no futuro, outros leiloeiros).
2. **Armazena** e mantém histórico dos imóveis (preços, status, datas de leilão).
3. **Enriquece** os dados cruzando com outras informações (valor de mercado, localização, região).
4. **Calcula** custos de aquisição (lance + ITBI + custas + reforma estimada) e uma **pré-análise de viabilidade**.
5. **Apresenta** tudo em uma interface web com busca, filtros, mapa e comparações.
6. (Evolução) Usa **IA** para resumir editais e apoiar a decisão ("vale a pena?").

## Problema

Imóveis de leilão estão espalhados, com dados semiestruturados e difíceis de comparar. Avaliar
se um imóvel "vale a pena" exige somar custos que não aparecem no anúncio (ITBI, custas,
registro, reforma, dívidas) e comparar com o valor de mercado. Falta uma visão **centralizada,
filtrável e com análise de custo real**.

## Escopo (o que é)

- Centralização e **normalização** de imóveis de leilão.
- **Busca/filtros** avançados + **mapa**.
- **Motor de custos** e **pré-análise de viabilidade**.
- **Favoritos e alertas**.

## Fora de escopo (o que NÃO é)

- **Não** intermedeia a compra nem participa do leilão pelo usuário.
- **Não** coleta nem armazena **dados pessoais** de terceiros (arrematantes, propostas) — ver
  [Legal & LGPD](../legal/lgpd.md).
- **Não** substitui a leitura do edital nem assessoria jurídica; a análise é **apoio à decisão**.

## Público-alvo

Investidores e compradores de imóveis de leilão (do iniciante ao recorrente) que precisam
**filtrar rápido** e **estimar o custo total** antes de aprofundar em um imóvel.

## Princípios do projeto

- **Docs-first** e **fonte única da verdade**.
- **Fonte de dados oficial e legal** sempre que possível (CSV da Caixa).
- **Open source** no toolchain.
- **Observabilidade desde o início** (métricas, logs, traces).

# ADR-0002 — Fonte oficial: CSV da Caixa (em vez de scraping de HTML)

- **Status:** Aceito — **emendado em 2026-07-18** (escopo do detalhe, ver nota abaixo)
- **Data:** 2026-07-16

> **Emenda (2026-07-18):** o [ADR-0010](0010-enriquecimento-detalhe.md) redefine o scraping da
> **página de detalhe** como **secundário mas obrigatório em volume** (enriquecer **todos** os
> imóveis, de forma *paced*/event-driven), e **não** como "opcional/pontual". O CSV permanece a
> **fonte primária** (verdade de existência/preço); o detalhe é a segunda camada obrigatória.
> As referências a "enriquecimento pontual" abaixo estão **superadas** por essa emenda.

## Contexto
Precisamos coletar imóveis de leilão da Caixa. Havia duas opções: **raspar o HTML** do site ou
usar algum canal oficial. A Caixa **publica a lista completa de imóveis por estado em CSV**.

## Decisão
Usar a **lista oficial em CSV** como **fonte primária**:
`https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_{UF}.csv` (verificada, responde `200`).
O scraping da **página de detalhe** é fonte **secundária obrigatória em volume** (fotos, edital,
praças, dívidas, ocupação), coletada de forma **educada e *paced*** para todos os imóveis — ver a
emenda acima e o [ADR-0010](0010-enriquecimento-detalhe.md). Limites e salvaguardas na
[política de coleta](../../legal/politica-de-coleta.md). Detalhes técnicos em
[Fonte Caixa (CSV)](../../dados/fonte-caixa-csv.md).

## Consequências
- **+** Muito mais **estável** (não quebra com mudança de layout) e **legalmente mais seguro**
  (canal sancionado pela própria Caixa).
- **+** Menos carga no site da Caixa; parsing determinístico.
- **−** O CSV tem menos campos que a página de detalhe → **enriquecimento em volume obrigatório**
  (secundário, *paced*), não pontual — ver emenda e ADR-0010.
- Guardamos o **CSV bruto** antes de normalizar (reprocessável).

## Alternativas consideradas
- **Scraping do HTML como fonte primária**: frágil e com maior risco jurídico/de bloqueio —
  rejeitado como primário.

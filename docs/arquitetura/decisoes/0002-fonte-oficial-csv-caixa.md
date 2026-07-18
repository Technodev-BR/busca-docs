# ADR-0002 — Fonte oficial: CSV da Caixa (em vez de scraping de HTML)

- **Status:** Aceito
- **Data:** 2026-07-16

## Contexto
Precisamos coletar imóveis de leilão da Caixa. Havia duas opções: **raspar o HTML** do site ou
usar algum canal oficial. A Caixa **publica a lista completa de imóveis por estado em CSV**.

## Decisão
Usar a **lista oficial em CSV** como **fonte primária**:
`https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_{UF}.csv` (verificada, responde `200`).
O scraping da **página de detalhe** fica como fonte **secundária/opcional** (fotos, edital), com
coleta educada. Detalhes técnicos em [Fonte Caixa (CSV)](../../dados/fonte-caixa-csv.md).

## Consequências
- **+** Muito mais **estável** (não quebra com mudança de layout) e **legalmente mais seguro**
  (canal sancionado pela própria Caixa).
- **+** Menos carga no site da Caixa; parsing determinístico.
- **−** O CSV tem menos campos que a página de detalhe → enriquecimento pontual quando necessário.
- Guardamos o **CSV bruto** antes de normalizar (reprocessável).

## Alternativas consideradas
- **Scraping do HTML como fonte primária**: frágil e com maior risco jurídico/de bloqueio —
  rejeitado como primário.

# ADR-0010 — Enriquecimento por página de detalhe (Caixa)

- **Status:** Aceito
- **Data:** 2026-07-18

## Contexto
O CSV oficial por UF (ver [ADR-0002](0002-fonte-oficial-csv-caixa.md)) traz só o básico do imóvel.
A **página de detalhe** (`detalhe-imovel.asp?hdnimovel={codigo}`) contém dados que **mudam o produto**
e não existem no CSV — verificados em amostra real (ver
[Fonte Caixa (detalhe)](../../dados/fonte-caixa-detalhe.md)):

- **Valor do 1º e do 2º leilão** separados (o CSV traz um preço só) → impacta o desconto real.
- **Datas das praças** (1º/2º leilão), leiloeiro, nº do edital/item.
- **Matrícula, comarca, ofício, inscrição imobiliária** e **CEP completo** (geocoding preciso).
- **Formas de pagamento** (FGTS/recursos próprios) e **responsabilidade de despesas**
  (condomínio/tributos = possíveis dívidas).
- **PDFs** (matrícula, edital) e **galeria de fotos**.

Precisamos enriquecer cada imóvel com esses dados de forma **robusta, respeitosa e escalável**.

## Decisão
Adotar um **enriquecimento assíncrono em 2 fases**, **event-driven**, com o **coletor Python** como
responsável pelo fetch/scraping (mantém a fronteira do [ADR-0001](0001-stack-tecnologica.md):
Python = coleta, Java = domínio/banco).

1. Após ingerir o CSV e persistir o imóvel, o backend publica **`imovel.enriquecer`**
   (`codigo` + `link`) na fila **`imoveis.enriquecimento`**.
2. Um **coletor Python de detalhe** consome a fila, baixa a página, **parseia o HTML**, baixa
   fotos/PDFs, guarda o **HTML bruto** em `coleta_bruta` (`fonte='caixa-detalhe'`) e envia o
   resultado ao backend via **`POST /internal/ingest/imoveis/{codigo}/detalhe`**.
3. O backend persiste os campos extras/fotos, publica **`imovel.enriquecido`** e dispara o
   **recálculo de custos/score**.

**Escopo:** enriquecer **todos** os imóveis do CSV. Como isso é **alto volume** (dezenas de milhares),
o consumo é **paced**: rate limiter global, `prefetch` baixo e a fila absorve o backlog (pode levar
horas/dias). Refresh por **TTL** e ao detectar `imovel.atualizado` (mudança de preço/status).

**Respeito ao site (obrigatório):** *User-agent* identificável, **poucos req/min**, **backoff** em
429/5xx, **concorrência baixa**, **cache** (não re-baixar o que não mudou) e **sem burlar proteção**
(ver [Legal & LGPD](../../legal/lgpd.md)).

## Consequências
- **+** Dados muito mais ricos (2 praças, datas, FGTS, dívidas, fotos, edital) → melhor cálculo,
  filtros e pré-análise.
- **+** Desacoplado: falha/lentidão no detalhe **não** trava a ingestão do CSV; retry/DLQ por item.
- **+** Fronteira limpa (Python raspa, Java é dono do dado).
- **−** Scraping de HTML é **frágil** (layout muda) → exige parser resiliente e **testes com fixtures**
  de HTML salvo, além de alertas de anomalia (parse vazio).
- **−** Volume "todos" pressiona o rate limit → o enriquecimento é **lento por design** (paced) e
  precisa de monitoração (fila, taxa, falhas).
- **−** Mais uma peça operacional (consumer Python) e storage de fotos/PDFs.

## Alternativas consideradas
- **Java faz o fetch**: quebraria a fronteira do ADR-0001 e duplicaria scraping/HTTP no backend —
  rejeitado.
- **Batch/pull** (backend lista pendentes, Python puxa agendado): mais simples, mas perde retry/DLQ
  por item e o casamento natural com a mensageria — mantido como fallback.
- **Lazy/on-demand** (só ao abrir o imóvel): menos requests, porém cobertura parcial e latência no
  detalhe — pode complementar o event-driven no futuro.
- **Enriquecer só priorizados** (alto desconto/alertas): menor volume, mas perde cobertura — optamos
  por **todos** com ritmo controlado.

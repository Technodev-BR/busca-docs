# Política de coleta (scraping educado)

Regras **operacionais e legais** da coleta de dados da Caixa. Torna concreto o "scraping educado"
citado na [LGPD](lgpd.md) e no [ADR-0002](../arquitetura/decisoes/0002-fonte-oficial-csv-caixa.md) /
[ADR-0010](../arquitetura/decisoes/0010-enriquecimento-detalhe.md). Cumpri-la é **pré-requisito para
produção**.

## 1. Revisão de termos (registro obrigatório)
Antes de cada exposição pública, registrar a revisão das **"Regras da venda online" (VOL)** e dos
termos do site:

| Item | Valor | Última revisão |
|---|---|---|
| URL das regras VOL | `.../editais/regras-VOL/comocomprar.pdf` | `[DATA]` |
| `robots.txt` do domínio | `[verificado? conteúdo]` | `[DATA]` |
| Responsável pela revisão | `[NOME]` | `[DATA]` |
| Conclusão | `[permitido / restrições / pendências]` | `[DATA]` |

> Sem `robots.txt` convencional aplicável → adotamos postura **conservadora** por padrão.

## 2. Limites de coleta (defaults calibráveis)
| Parâmetro | Valor default | Onde |
|---|---|---|
| Requisições/min por host (detalhe) | **≤ 30/min** (≈ 1 a cada 2 s) | rate limiter global do collector |
| Concorrência | **1–2** conexões | consumidor de enriquecimento |
| `prefetch` da fila | baixo (ex.: 5) | RabbitMQ |
| Backoff em `429`/`5xx` | exponencial (tenacity), com teto | downloader |
| Re-download de mídia | **proibido** (cache/object storage) | [ADR-0017](../arquitetura/decisoes/0017-object-storage.md) |
| Janela de coleta CSV | 1x/dia | scheduler |

- **User-Agent identificável** (nome do projeto + contato), nunca disfarçado.
- **Nunca** burlar CAPTCHA, WAF ou proteção. **Sem** paralelismo agressivo.

## 3. Kill-switch e degradação
- **Flag global** `COLETA_HABILITADA` (config) para **parar** coleta/enriquecimento sem deploy.
- Ao detectar bloqueio sistemático (muitos `403/429`, CAPTCHA, ou queda de layout), **pausar
  automaticamente** o enriquecimento (circuit breaker) e alertar.
- Coleta do **CSV** e **enriquecimento** têm switches independentes.

## 4. Plano se a Caixa bloquear (resumo)
Ver o [runbook Caixa 429/bloqueio](../observabilidade/runbooks.md#caixa-429--bloqueio-de-coleta).
Em síntese: reduzir taxa → pausar via kill-switch → registrar incidente → reavaliar termos → só
retomar após revisão. **Nunca** contornar a proteção.

## 5. Atribuição e transparência
- Exibir que os dados são de **fonte pública da Caixa** e **linkar de volta** ao imóvel oficial.
- Não replicar o site; agregamos e organizamos para triagem.

## 6. Checklist legal pré-produção
- [ ] Revisão dos termos VOL registrada (§1) e vigente.
- [ ] Limites (§2) aplicados e testados em homologação.
- [ ] Kill-switch (§3) validado.
- [ ] Runbook de bloqueio publicado e conhecido pelo on-call.
- [ ] Atribuição/links de volta no frontend.
- [ ] [Política de Privacidade](politica-de-privacidade.md) e [Termos](termos-de-uso.md) publicados.

Ver também: [LGPD](lgpd.md) · [Collector](../servicos/collector-python.md) · [ADR-0010](../arquitetura/decisoes/0010-enriquecimento-detalhe.md).

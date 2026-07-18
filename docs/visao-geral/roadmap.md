# Roadmap

Fases incrementais, do **MVP** à evolução, alinhadas à arquitetura atual (enriquecimento por
detalhe *event-driven* — [ADR-0010](../arquitetura/decisoes/0010-enriquecimento-detalhe.md); auth
OIDC — [ADR-0013](../arquitetura/decisoes/0013-autenticacao-social-oidc.md); análise jurídica com
IA — [ADR-0014](../arquitetura/decisoes/0014-analise-juridica-ia.md)).

> A coluna **RF cobertos** liga ao [mapa de requisitos](../produto/requisitos.md) e à
> [rastreabilidade](../produto/rastreabilidade.md). **MVP** = escopo mínimo para valor ao usuário;
> **Evolução** = incrementos posteriores.

## Fases

| Fase | Escopo | RF cobertos | Faixa |
|---|---|---|---|
| **1 — Coleta CSV** | Coletor Python (CSV da Caixa) → **API de ingestão** (Java) → **PostgreSQL** + `coleta_bruta` + RabbitMQ. Sem frontend; foco em **dados confiáveis**. | RF-01, RF-02 | **MVP** |
| **2 — Enriquecimento por detalhe** | Pipeline *event-driven* e **paced** que raspa a página de detalhe (1ª/2ª praça, datas, edital, dívidas, ocupação, fotos) para **todos** os imóveis. | RF-12 | **MVP** |
| **3 — Busca, filtros e detalhe** | Angular listando/filtrando; **página de detalhe** com fotos, praças, edital e histórico de preço. | RF-03, RF-05 | **MVP** |
| **4 — Custos e score** | Motor de **custo total** (ITBI + custas + registro + reforma) e **desconto real**; **pré-análise (score)** com confiança e riscos. | RF-06, RF-07 | **MVP** |
| **5 — Geo + mapa + UX de detalhe** | **Geocoding** e **mapa** (PostGIS + ngx-leaflet); **cronômetro** dos leilões, **aviso de ocupação** e **mini-mapa** no detalhe. | RF-04, RF-15 | **MVP** |
| **6 — Ciclo de vida + painel de coletas** | Conciliar ausências (marcar **vendido/removido**), painel de **status das coletas** por UF. | RF-11, RF-13 | Evolução |
| **7 — Contas + engajamento** | **Login social OIDC** (Google/GitHub, cookies HttpOnly), **favoritos**, **alertas** e **notificações** (e-mail no MVP de notificação). | RF-08, RF-13 (notificar) | Evolução (auth) |
| **8 — Comparador** | Comparar 2–3 imóveis lado a lado (custo/desconto/score). | RF-09 | Evolução |
| **9 — IA jurídica** | **Resumo do edital** (parecer textual, RF-10) e **análise jurídica estruturada** (flags + grounding, RF-14), com disclaimer e explicabilidade. | RF-10, RF-14 | Evolução |

---

## Transversais (contínuos)

- **Observabilidade** desde a Fase 1 (métricas/logs/traces + métricas de negócio).
- **Testes automatizados** e **CI/CD** a cada fase.
- **Segurança/LGPD** revisadas **antes** de qualquer exposição pública — inclui a
  [política de coleta](../legal/politica-de-coleta.md) e a
  [política de privacidade](../legal/politica-de-privacidade.md).

## Marcos de infraestrutura

- Dev em **Docker Compose** desde a Fase 1.
- **k3s + Argo CD (GitOps)** (VPS Hostinger, Traefik/Cloudflare) a partir de quando houver
  ambiente de staging/prod. Ver [Rede e exposição](../infraestrutura/rede-e-exposicao.md).

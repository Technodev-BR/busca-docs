# Roadmap

Fases sugeridas, do MVP à evolução. Cada fase entrega valor de forma incremental.

## Fase 1 — MVP de coleta
Coletor Python (CSV da Caixa) → **API de ingestão** (Java) → **PostgreSQL**.
Sem frontend ainda; objetivo é ter **dados confiáveis** no banco.

## Fase 2 — API + Front básico
Angular listando e filtrando imóveis; página de detalhe consumindo a API Java.

## Fase 3 — Cálculo de custos
Motor de custos: **ITBI + custas + registro + reforma** → **custo total** e **% desconto real**.

## Fase 4 — Geo + Mapa
**Geocoding** dos endereços e visualização no **mapa** (PostGIS + ngx-leaflet).

## Fase 5 — Enriquecimento
Valor de mercado por região, **histórico de preço** e sinais de liquidez.

## Fase 6 — IA
Resumo de **edital** e **parecer de viabilidade** ("vale a pena?").

## Fase 7 — Contas de usuário
**Favoritos, alertas** e **comparação** entre imóveis.

---

## Transversais (contínuos)

- **Observabilidade** desde a Fase 1 (métricas/logs/traces).
- **Testes automatizados** e **CI/CD** a cada fase.
- **Segurança/LGPD** revisadas antes de qualquer exposição pública.

## Marcos de infraestrutura

- Dev em **Docker Compose** desde a Fase 1.
- **k3s + Argo CD (GitOps)** (VPS Hostinger, Traefik/Cloudflare) a partir de quando houver
  ambiente de staging/prod. Ver [Rede e exposição](../infraestrutura/rede-e-exposicao.md).

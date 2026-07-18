# Score de viabilidade — especificação v0 (heurística)

Especificação **fechada e implementável** do score do MVP (`versaoScore = v0-heuristico`). É
**apoio à decisão/triagem**, não recomendação de investimento. Complementa a visão conceitual em
[Pré-análise de viabilidade](pre-analise-viabilidade.md).

> **Valores default** — pesos e faixas abaixo são um ponto de partida calibrável. Devem ficar em
> configuração versionada (ver [parâmetros de custo](../dados/parametros-custo.md) para o padrão de
> versionamento) e ajustados com dados reais.

> **Origem dos pesos (importante).** Diferente dos [parâmetros de custo](../dados/parametros-custo.md)
> (que têm fonte oficial — ITBI, comissão de 5%, emolumentos, SINAPI), os **pesos do score não são
> "dado externo"**: dependem de **resultado histórico** (arremate → revenda/tempo de venda) que só
> teremos após operar. Portanto o v0 usa **julgamento de especialista**, calibrável (§8). Não
> apresentar o score como fruto de dados que ainda não existem.

## 1. Modelo

Soma ponderada de **subscores** normalizados em `[0,1]`:

```
score_bruto = Σ (peso_i × subscore_i)          # ∈ [0,1]
score       = round(100 × score_bruto)          # ∈ [0,100]
```

Cada `subscore_i ∈ [0,1]` (1 = melhor, 0 = pior). Os pesos do **MVP** somam **1.0**.

## 2. Pesos (MVP)

| Sinal (`nome`) | Peso | Fonte |
|---|---|---|
| `desconto_real` | **0.40** | motor de custos ([Cálculo de custos](calculo-de-custos.md)) |
| `ocupacao` | **0.20** | detalhe (`situacao_ocupacao`) |
| `onus_dividas` | **0.15** | detalhe (`despesas_*_comprador`) + edital |
| `liquidez_regiao` | **0.15** | dados de mercado (indisponível no MVP → neutro) |
| `acesso_credito` | **0.10** | detalhe (`aceita_fgts`, `aceita_financiamento`) |

> **Evolução (IA jurídica, RF-14):** ao entrar o sinal `juridico` (peso sugerido **0.20**),
> renormalizar os demais proporcionalmente para o total continuar `1.0`. Ver
> [ADR-0014](../arquitetura/decisoes/0014-analise-juridica-ia.md).

## 3. Subscores (funções de normalização)

| Sinal | Fórmula do subscore | Notas |
|---|---|---|
| `desconto_real` | `clip(descontoRealPct, 0, 40) / 40` | **teto calibrado com dados reais** (p90 ≈ 40% — ver §8); 0% → 0; ≥40% → 1 |
| `ocupacao` | `desocupado=1.0`, `desconhecido=0.5`, `ocupado=0.0` | penaliza ocupado |
| `onus_dividas` | `sem dívida do comprador e sem ônus=1.0`; `dívida do comprador OU ônus=0.3`; `ambos=0.0` | no MVP sem IA, só `despesas_*_comprador` (nenhuma=1.0, alguma=0.3) |
| `liquidez_regiao` | MVP: **0.5 (neutro)** | sem dados de mercado; reduz **confiança**, não o valor |
| `acesso_credito` | `fgts && financiamento=1.0`; `um deles=0.6`; `nenhum=0.2`; `desconhecido=0.5` | mais compradores → mais líquido |

**Regra de ouro:** sinal ausente **nunca** vira valor inventado — usa o **neutro** e **reduz a
confiança** (§5). Não zera o score.

## 4. Explicabilidade (`fatores[]`)

Para cada sinal, retornar um `FatorScore` (ver [openapi-api.yaml](../contratos/openapi-api.yaml)):

```
contribuicao_i = round(100 × peso_i × subscore_i, 1)          # pontos que o sinal somou
share_neutro_i = 100 × peso_i × 0.5
direcao_i      = positivo se contribuicao_i > share_neutro_i
                 negativo se contribuicao_i < share_neutro_i
                 neutro   caso contrário
```

A UI mostra os 2–3 de maior módulo (ex.: `+ Desconto real 34%`, `− Imóvel ocupado`).

## 5. Confiança (`confianca ∈ [0,1]`)

Fração do peso total sustentada por **dados reais** (não-neutros/fallback):

```
confianca = Σ (peso_i × disponivel_i)     # disponivel_i ∈ {0,1}
```

- `disponivel_i = 0` quando o subscore usou **neutro/fallback** (dado ausente).
- No MVP, `liquidez_regiao` é sempre neutro ⇒ **confiança máxima ≈ 0.85**.
- `status_enriquecimento != ok` ⇒ sinais do detalhe indisponíveis ⇒ confiança cai; a UI exibe
  "aguardando detalhe". Recalcula ao receber `imovel.enriquecido`.

## 6. Exemplos golden (base de teste)

Casos determinísticos para os testes unitários (ver [Testes](../qualidade/testes.md)).

### G1 — "negócio limpo" (detalhe completo)
`descontoRealPct=33` (≈ mediana real de SP), `desocupado`, sem dívidas do comprador,
`fgts && financiamento`, liquidez neutra.

| Sinal | subscore | peso | contribuição |
|---|---|---|---|
| desconto_real | 0.825 | 0.40 | 33.0 |
| ocupacao | 1.00 | 0.20 | 20.0 |
| onus_dividas | 1.00 | 0.15 | 15.0 |
| liquidez_regiao | 0.50 | 0.15 | 7.5 |
| acesso_credito | 1.00 | 0.10 | 10.0 |

**score = 86**, **confianca = 0.85** (só liquidez ausente).

### G2 — "ocupado com dívidas"
`descontoRealPct=40` (≈ p90 real), `ocupado`, despesas do comprador, sem crédito, liquidez neutra.

| Sinal | subscore | peso | contribuição |
|---|---|---|---|
| desconto_real | 1.00 | 0.40 | 40.0 |
| ocupacao | 0.00 | 0.20 | 0.0 |
| onus_dividas | 0.30 | 0.15 | 4.5 |
| liquidez_regiao | 0.50 | 0.15 | 7.5 |
| acesso_credito | 0.20 | 0.10 | 2.0 |

**score = 54**, **confianca = 0.85**. `fatores`: `+ desconto real`, `− ocupado`, `− dívidas`.

### G3 — "só CSV" (enriquecimento pendente)
`descontoRealPct=20` (base CSV), demais sinais **ausentes** (neutros).

| Sinal | subscore | peso | contribuição |
|---|---|---|---|
| desconto_real | 0.50 | 0.40 | 20.0 |
| ocupacao | 0.50 (neutro) | 0.20 | 10.0 |
| onus_dividas | 0.50 (neutro) | 0.15 | 7.5 |
| liquidez_regiao | 0.50 (neutro) | 0.15 | 7.5 |
| acesso_credito | 0.50 (neutro) | 0.10 | 5.0 |

**score = 50 (provisório)**, **confianca = 0.40** (só desconto real é dado real). UI: "aguardando detalhe".

## 7. Guarda-corpos
- Estimativa/triagem, **não** recomendação; ocupação e dívidas sempre viram **alerta explícito**
  mesmo com score alto.
- Toda mudança de pesos/fórmula **incrementa `versaoScore`** e é registrada (auditoria/reprocesso).

## 8. Calibração com dados reais (plano)
Os pesos v0 são **provisórios**. À medida que dados forem sendo coletados, calibrar por etapas:

1. **Ancoragem por distribuição (curto prazo, sem outcome):** ajustar o teto de `desconto_real`
   e as faixas usando a **distribuição real** dos imóveis coletados (percentil 90 como teto), para o
   subscore não saturar nem achatar.
   - ✅ **Executado (2026-07) com dados reais** via `tools/validacao/validar_parametros.py` sobre o
     CSV oficial de **SP** (3.607 imóveis, 2.540 em leilão): desconto **anunciado** mediana 38,8% /
     p90 41,5%; desconto **real** (com ITBI + comissão 5% + registro) mediana **32,7%** / **p90 ≈ 40%**.
     → **teto do subscore ajustado de 50% para 40%**. Reexecutar por UF e periodicamente.
2. **Validação de face:** revisar com especialista uma amostra rotulada ("bom/ruim negócio") e
   conferir se o ranking do score bate com o julgamento humano (Spearman).
3. **Calibração supervisionada (médio prazo, requer outcome):** quando houver histórico de
   **resultado** (imóvel saiu como `vendido`, tempo até sair do CSV, reaparecimento), ajustar os
   pesos por **regressão/otimização** contra esse alvo; migrar `versaoScore` (v1).
4. **Monitoramento:** acompanhar drift do score e das faixas via métricas de negócio
   ([observabilidade](../observabilidade/pilares.md)); recalibrar periodicamente.

Até a etapa 3, comunicar o score como **triagem heurística** (não modelo treinado).

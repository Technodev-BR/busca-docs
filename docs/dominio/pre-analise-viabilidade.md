# Pré-análise de viabilidade

Um **score** que resume, em um número, quão promissor é um imóvel — para **ordenar** e **triar**.
É **apoio à decisão**, não recomendação de investimento.

## Sinais que entram no score

Pesos e fórmulas **fechados** na [especificação v0 do score](score-v0-spec.md) (fonte da verdade
para implementação e testes). Resumo dos sinais do MVP:

| Sinal | Peso (v0) | Direção |
|---|---|---|
| **Desconto real** (após custo total, base 2ª praça) | 0.40 | quanto maior, melhor |
| **Ocupação** (`situacao_ocupacao`) | 0.20 | ocupado penaliza |
| **Ônus/dívidas do comprador** | 0.15 | dívida/ônus penaliza |
| **Liquidez da região** (demanda/venda) | 0.15 | quanto maior, melhor (neutro no MVP) |
| **Acesso a crédito** (FGTS/financiamento) | 0.10 | mais opções, melhor |

## Sinais vindos do enriquecimento (detalhe)
Vários sinais só existem após o [enriquecimento por detalhe](../dados/fonte-caixa-detalhe.md)
(ver [ADR-0010](../arquitetura/decisoes/0010-enriquecimento-detalhe.md)):

| Campo do detalhe | Efeito no score |
|---|---|
| `valor_segundo_leilao` | Melhora o **desconto real** (base mais barata) — ver [Cálculo de custos](calculo-de-custos.md) |
| `situacao_ocupacao = ocupado` | **Penaliza** (custo/tempo de desocupação, risco jurídico) |
| `despesas_condominio/tributos_comprador` | **Penaliza** (dívidas por conta do comprador entram no custo) |
| `aceita_fgts` / `aceita_financiamento` | **Bônus de liquidez/acesso** (mais compradores possíveis) |
| `data_1o/2o_leilao` | Urgência/janela — informativo (pode virar alerta, não peso forte) |

## Sinais jurídicos (via IA — evolução)
A [análise jurídica com IA](analise-juridica-ia.md) ([ADR-0014](../arquitetura/decisoes/0014-analise-juridica-ia.md))
adiciona flags que **pesam bastante** no score:

| Fato jurídico | Efeito no score |
|---|---|
| **Nua-propriedade** (usufruto de terceiro) | **Penaliza forte** (uso/renda limitados) |
| **Fração ideal / co-propriedade** | **Penaliza** (condomínio, direito de preferência) |
| **Ônus/gravames** (penhora, hipoteca, alienação fiduciária) | **Penaliza** (regularização) |
| **Propriedade plena + desocupado + sem ônus** | **Favorece** (negócio "limpo") |

## Modelo (evolução em fases)

1. **Heurístico (MVP):** soma ponderada normalizada (0–100), com fórmula, subscores e exemplos
   golden em [score-v0-spec.md](score-v0-spec.md). Transparente e explicável.
2. **Com dados de mercado:** incorporar valor de mercado e histórico de preço.
3. **Com IA:** LLM resume o **edital**/matrícula, extrai riscos jurídicos (nua-propriedade, fração,
   ônus) que alimentam o score e gera um parecer ("vale a pena?"). Ver
   [Análise jurídica com IA](analise-juridica-ia.md) (uso de **produto**) e
   [AIOps/IA](../observabilidade/aiops-mcp.md) (padrão de uso de IA em operação).

## Explicabilidade
O score sempre vem acompanhado dos **fatores** que mais pesaram (ex.: "+ desconto real 22%,
− imóvel ocupado"). Nunca é uma "caixa-preta". Esses fatores são expostos no contrato como
`AnaliseCusto.fatores[]` (schema `FatorScore` — ver [openapi-api.yaml](../contratos/openapi-api.yaml)),
com `confianca` e `versaoScore`.

## Confiança do score (dados faltantes)
O score carrega um **nível de confiança** conforme o `status_enriquecimento` do imóvel:

- **`ok`**: score completo (usa 2ª praça, ocupação, dívidas).
- **`pendente`/`falha`/`parcial`**: score **provisório** só com dados do CSV — **confiança
  reduzida** e sinalizada na UI ("aguardando detalhe"). É **recalculado** quando chega
  `imovel.enriquecido`.
- Sinais ausentes **não** viram valores inventados: reduzem a confiança, não o valor.

## Guarda-corpos
- Deixar claro que é **estimativa/triagem**.
- Não prometer retorno; sinalizar incertezas (dados faltantes reduzem a confiança do score).
- **Imóvel ocupado** e **dívidas do comprador** sempre aparecem como **alertas explícitos**, mesmo
  com score alto.

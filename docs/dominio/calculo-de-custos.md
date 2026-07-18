# Cálculo de custos

O **motor de custos** transforma o preço anunciado no **custo total** de aquisição e no
**desconto real**. É uma regra de domínio pura (testável isoladamente).

## Fórmula

```
custo_total = valor_arremate
            + itbi
            + custas_leiloeiro
            + registro_cartorio
            + dividas
            + reforma_estimada

desconto_real_% = (valor_referencia - custo_total) / valor_referencia * 100
```

Onde `valor_referencia` é a **avaliação** (ou o **valor de mercado** estimado, quando disponível).

### `valor_arremate` — usar o dado enriquecido (2ª praça)
O CSV traz **um** preço só; a [página de detalhe](../dados/fonte-caixa-detalhe.md) traz o **valor
mínimo do 1º e do 2º leilão** separados (ver [ADR-0010](../arquitetura/decisoes/0010-enriquecimento-detalhe.md)).
Como o **2º leilão costuma ser o menor** (melhor entrada), ele deve ser a **base do desconto real**:

- **Base do cálculo** = `valor_segundo_leilao` (quando existir), senão `valor_primeiro_leilao`, senão
  `valor_minimo` do CSV (**fallback** — ver "Variações" abaixo).
- Idealmente calcular **os dois cenários** (1ª e 2ª praça) e expor ambos, destacando o desconto
  real da praça mais barata.
- **Nunca** basear o desconto real no preço genérico do CSV quando o detalhe já estiver disponível.

## Componentes

| Item | Como é obtido | Observações |
|---|---|---|
| **Valor de arremate** | `valor_segundo_leilao` (detalhe) → fallback `valor_primeiro_leilao`/`valor_minimo` | Base do cálculo (ver acima) |
| **ITBI** | `aliquota_municipio × base` | Base = **maior entre arremate e valor venal de referência** (STJ Tema 1.113). Alíquota real por município ([parâmetros](../dados/parametros-custo.md#1-itbi-aliquota_itbi)): capitais ~3% (Curitiba 2,7%), demais ~2% |
| **Comissão de leiloeiro** | **5% da proposta** em **leilão/licitação**; **0% em Venda Online/Compra Direta** | Paga pelo arrematante, **fora do lance** (confirmado nos editais Caixa); na venda direta a corretagem é paga pela Caixa. Ver RN-04 e [parâmetros](../dados/parametros-custo.md#2-custas--comissao-de-leiloeiro-parametro_custo-chavecustas_pct) |
| **Registro em cartório** | Tabela/estimativa por faixa de valor | Varia por estado |
| **Dívidas** | Flags do detalhe (`despesas_condominio/tributos_comprador`) + edital | Se por conta do **comprador**, somar estimativa; senão, zero |
| **Reforma estimada** | Estimativa do usuário ou heurística | Configurável (R$/m² por tipo) |

## Variações por imóvel (tratar no motor)
O detalhe **nem sempre** vem completo — o cálculo precisa ser **defensivo**:

- **Sem 2º leilão** (venda direta/licitação): usar `valor_primeiro_leilao` ou `valor_minimo`; marcar que
  há **só uma praça**.
- **Descrição/áreas vazias**: reforma por heurística fica **indisponível** → sinalizar estimativa
  parcial (não inventar).
- **Ocupação**: se `situacao_ocupacao = ocupado`, sinalizar **risco** (custo/tempo de desocupação)
  na pré-análise — ver [Pré-análise](pre-analise-viabilidade.md).
- **Enriquecimento pendente/falho** (`status_enriquecimento`): calcular com o que houver do CSV e
  **marcar como estimativa provisória**, recalculando quando `imovel.enriquecido` chegar.

## Parâmetros configuráveis
Defaults, fontes e versionamento em [Parâmetros de custo](../dados/parametros-custo.md)
(tabelas `aliquota_itbi` e `parametro_custo`). O cálculo grava a `parametro_custo_versao` usada.

- **Alíquota de ITBI por município** (com valor default por UF e nacional).
- **% de custas** por modalidade.
- **Custo de registro** por faixa de valor.
- **R$/m² de reforma** por tipo de imóvel.

> **Atenção à precisão:** valores de ITBI, custas e registro **variam por município/estado**. O
> cálculo é uma **estimativa** para triagem; o valor final exige conferência no edital e nos
> órgãos locais.

## Casos de teste
Os [estudos de caso](../produto/estudos-de-caso.md) (ex.: "o desconto anunciado engana") são a base
dos testes do motor de custos. Ver [Testes](../qualidade/testes.md).

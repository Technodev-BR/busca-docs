# Estudos de caso

Cenários reais que guiam o produto e servem de base para testes de aceitação. São exemplos
ilustrativos; os números finais dependem do município e do edital.

## Caso 1 — "O desconto anunciado engana"

**Situação:** um imóvel aparece com avaliação de R$ 300.000 e preço de R$ 210.000
(**30% de desconto** anunciado).

**Análise da plataforma (custo total):**

| Item | Valor (exemplo) |
|---|---|
| Lance / preço | R$ 210.000 |
| ITBI (ex.: 3%) | R$ 6.300 |
| Custas/comissão leiloeiro (ex.: 5%) | R$ 10.500 |
| Registro em cartório (estimado) | R$ 4.000 |
| Dívidas (IPTU/condomínio) | R$ 8.000 |
| Reforma estimada | R$ 25.000 |
| **Custo total** | **R$ 263.800** |

**Desconto real** vs. avaliação: ~**12%** (não 30%).
**Valor para o usuário:** a plataforma mostra o **desconto real** e evita uma decisão baseada só
no número do anúncio.

## Caso 2 — "Filtrar rápido o que importa"

**Situação:** o usuário quer apartamentos em Curitiba, até R$ 250 mil, com desconto real ≥ 20%.

**Fluxo:** aplica filtros (cidade + tipo + preço + desconto real) → vê no **mapa** → ordena por
desconto real → **favorita** 3 imóveis → cria **alerta** para novos que entrem no filtro.

**Valor:** de centenas de imóveis para um punhado relevante, em segundos.

## Caso 3 — "Risco escondido no edital" (evolução com IA)

**Situação:** imóvel atrativo, mas o edital indica **ocupação** e dívidas.

**Fluxo:** a IA resume o edital, destaca "imóvel ocupado — desocupação por conta do comprador" e
sinaliza risco alto; o score de viabilidade cai.

**Valor:** o usuário entende o risco **antes** de investir tempo/dinheiro.

---

> Estes casos alimentam os **testes E2E** (ver [Testes](../qualidade/testes.md)) e a validação do
> [motor de custos](../dominio/calculo-de-custos.md).

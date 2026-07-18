# Spike de validação de parâmetros (dados reais)

Script **descartável** (não é código de produção) para validar as premissas de custo e score com
**dados reais da fonte da verdade** (CSV oficial da Caixa), **antes** de construir o MVP.

## O que faz
1. Baixa o CSV oficial de uma UF (`Lista_imoveis_{UF}.csv`) e parseia conforme a
   [spec verificada](../../docs/dados/fonte-caixa-csv.md) (latin1, pula 2 linhas, `;`, números BR).
2. Mede a **distribuição real do desconto anunciado** (percentis).
3. Aplica o **motor de custos** com os [parâmetros reais](../../docs/dados/parametros-custo.md)
   (ITBI por UF, comissão 5% em leilão/licitação, registro por faixa) e calcula o **desconto real**.
4. Sugere o **teto do subscore `desconto_real`** (p90 do real positivo) para calibrar o
   [score v0](../../docs/dominio/score-v0-spec.md).

## Uso
```bash
python tools/validacao/validar_parametros.py --uf SP
python tools/validacao/validar_parametros.py --uf RJ
python tools/validacao/validar_parametros.py --insecure          # se proxy corporativo quebrar TLS
python tools/validacao/validar_parametros.py --arquivo Lista_imoveis_SP.csv  # CSV já baixado
```
Sem dependências externas (só stdlib). Requer Python 3.11+.

## Resultado de referência (SP, 2026-07)
- 3.607 imóveis válidos, 2.540 em leilão/licitação.
- Desconto **anunciado**: mediana 38,8% · p90 41,5% · máx 75,6%.
- Desconto **real**: mediana 32,7% · p90 ≈ 40%.
- Erosão média ≈ 6 p.p.; só ~5% mantêm desconto real ≥ 40% → **teto do score ajustado p/ 40%**.

## Limitações (honestas)
- O CSV traz **um** preço; a **2ª praça** só vem do detalhe (enriquecimento) → resultado provisório.
- Base do **ITBI** real = maior entre arremate e **valor venal de referência** do município
  (STJ Tema 1.113), que **não** está no CSV → aqui usamos o arremate (lower bound).
- **Dívidas/responsabilidade** vêm do **edital** (fonte per-imóvel), não do CSV.

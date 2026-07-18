# ADR-0014 — Análise jurídica de investimento assistida por IA

- **Status:** Proposto
- **Data:** 2026-07-18

## Contexto
Muitos imóveis de leilão escondem detalhes jurídicos que **mudam o valor real do negócio**:
nua-propriedade (com usufruto de terceiro), venda de **fração ideal**, **ônus/gravames** (penhora,
hipoteca, alienação fiduciária), ocupação e responsabilidade de desocupação, direito de preferência.
Isso está no **edital** e na **matrícula** (PDFs), que hoje o usuário teria de ler manualmente.
Queremos **extrair esses fatos** e indicar os **melhores negócios** — sem cruzar a linha da LGPD nem
virar "aconselhamento jurídico".

## Decisão
Adicionar uma etapa de **análise jurídica assistida por IA** (fase de evolução, pós-MVP) que lê
edital/matrícula/detalhe e produz uma **saída estruturada** (flags + parecer) que alimenta a
[pré-análise](../../dominio/pre-analise-viabilidade.md) e a tela de detalhe. Detalhe funcional em
[Análise jurídica com IA](../../dominio/analise-juridica-ia.md).

**Princípios:**
- **Grounding obrigatório**: cada flag cita o trecho de origem; sem fonte → "não identificado".
- **Estruturado primeiro**: LLM devolve JSON validável (schema) + texto; nada de só texto solto.
- **Confiança explícita** e **human-in-the-loop** em alto valor/risco.
- **LGPD by design**: só **fatos do imóvel**; **redigir/omitir PII** (nomes de proprietários,
  devedores, antigo comprador) antes de persistir; **sem perfil de pessoas**; sem PII em prompts
  registrados. Ver [Legal & LGPD](../../legal/lgpd.md).
- **Provedor plugável**: abstrair via porta (`AnaliseJuridicaPort`) para trocar LLM (API gerenciada
  ou modelo self-hosted) sem acoplar o domínio.
- **Custo/limite**: rodar **sob demanda/priorizado** (não em todos os imóveis de uma vez) para
  controlar custo de inferência.

## Consequências
- **+** Diferencial forte: transforma leitura jurídica manual em **triagem automática** e ajuda a
  achar os **melhores negócios** (alto desconto real **e** baixo risco).
- **+** Alimenta score/alertas com sinais que hoje são invisíveis no CSV.
- **−** Risco de **alucinação** → mitigado por grounding, confiança e revisão humana.
- **−** **Custo** de inferência e latência → execução priorizada/assíncrona.
- **−** Responsabilidade: **disclaimer** claro (não é parecer jurídico) e cuidado LGPD.

## Alternativas consideradas
- **Regras/regex apenas**: barato e determinístico, mas frágil com a linguagem livre dos editais —
  usar como **pré-filtro** combinado à IA, não sozinho.
- **Sem análise jurídica**: perde o principal fator de risco/valor — rejeitado.
- **Analisar situação do antigo comprador/proprietário**: **rejeitado** — é dado pessoal de
  terceiro (LGPD) e fora do escopo (só o imóvel).

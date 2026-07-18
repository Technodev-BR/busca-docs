# ADR-0014 — Análise jurídica de investimento assistida por IA

- **Status:** Aceito (implementação na **Fase 9** do [roadmap](../../visao-geral/roadmap.md); MVP não depende dela)
- **Data:** 2026-07-18 · **Aceito em:** 2026-07-18

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

## Arquitetura, robustez e escala
- **Event-driven** (ADR-0005): consumidor da fila `imovel.analisar_juridico`, disparado **após** o
  enriquecimento (ADR-0010) e **priorizado** por `desconto_real` (analisar primeiro o que interessa).
- **Pipeline determinístico → IA:**
  1. **Extração de texto** do PDF (edital/matrícula) com camada determinística (parser + OCR quando
     necessário).
  2. **Redação de PII** (nomes, CPF/CNPJ, etc.) **antes** de qualquer prompt — LGPD by design.
  3. **Pré-filtro por regras/regex** (penhora, usufruto, fração…) para baratear e ancorar a IA.
  4. **LLM com saída estruturada** validada por **JSON Schema** (`AnaliseJuridica`/`FlagJuridica` —
     [openapi-api.yaml](../../contratos/openapi-api.yaml)); **retry com reparo** se o JSON não validar.
  5. **Grounding**: cada flag guarda o **trecho citado**; sem trecho → `presente=false`/"não identificado".
- **Roteamento de modelo (custo):** modelo **barato** primeiro; **escalar** para modelo maior só em
  baixa confiança ou alto valor. **Orçamento diário de tokens** com corte suave (adia o restante).
- **Idempotência e cache:** chave por `hash(texto_redigido) + versao_prompt + modelo`. Reprocessa só
  quando muda o documento, o prompt ou o modelo — evita custo repetido.
- **Human-in-the-loop:** confiança abaixo do limiar **ou** alto valor → fila de **revisão humana**
  antes de exibir como "confirmado".
- **Resiliência:** timeout + retry com backoff; falha persistente → **DLQ** e imóvel fica com IA
  `status=falha` (score usa só sinais determinísticos, confiança reduzida).
- **Observabilidade:** custo/tokens por análise, latência, `% flags com grounding`, taxa de reparo de
  JSON, amostragem periódica para medir **alucinação** (ver [pilares](../../observabilidade/pilares.md)).

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

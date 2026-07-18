# Regras de negócio

Regras que valem independentemente de tecnologia. Vivem no **domínio** do backend (arquitetura
hexagonal) e são cobertas por testes unitários.

## RN-01 — Identidade e deduplicação
- O **N° do imóvel** (da Caixa) é a **chave natural**. Imóveis são deduplicados por ele.
- A coleta é **idempotente**: sempre faz **upsert** por `codigo` — **nunca** insere duplicado nem
  cria um registro novo para um imóvel já conhecido.
- O ciclo de vida (disponível → vendido/removido → eventual reaparecimento) é tratado pela **RN-09**.

## RN-02 — Histórico de preço/status
- Toda mudança de **preço**, **desconto** ou **status** gera um registro em `historico_preco`.
- Isso permite mostrar tendência, detectar reduções e **auditar quando o imóvel foi vendido**.

## RN-03 — Normalização
- Endereço, cidade, bairro e tipo são **normalizados** (trim, capitalização, remoção de ruído).
- A **descrição** semiestruturada da Caixa é parseada para extrair **tipo** e **áreas**
  (total/privativa/terreno). Ver [Fonte Caixa (CSV)](../dados/fonte-caixa-csv.md).

## RN-04 — Modalidade de venda
- A **modalidade** (ex.: *Leilão SFI*, *Venda Direta*, *Licitação*) é preservada e vira **filtro**.
- Regras de custo podem variar por modalidade (ex.: comissão do leiloeiro só em leilão).

## RN-05 — Custo total e desconto real
- O sistema sempre calcula o **custo total** (ver [Cálculo de custos](calculo-de-custos.md)) e o
  **desconto real** — nunca exibe só o desconto anunciado como se fosse o ganho.

## RN-06 — Pré-análise de viabilidade
- Cada imóvel recebe um **score** de viabilidade. Ver [Pré-análise](pre-analise-viabilidade.md).
- O score é **apoio à decisão**, não recomendação de investimento.

## RN-07 — Riscos do edital
- Riscos como **ocupação**, **dívidas** (IPTU/condomínio) e **desocupação por conta do comprador**
  devem ser sinalizados e impactar o score.

## RN-08 — Privacidade (LGPD)
- Só tratamos **dados do imóvel** (públicos). **Nunca** dados pessoais de terceiros.
  Ver [Legal & LGPD](../legal/lgpd.md).
- **Proibido perfilar pessoas.** Não coletamos, armazenamos nem analisamos a **situação do antigo
  comprador/proprietário/devedor** (nomes citados em edital/matrícula). Isso é dado pessoal de
  terceiro e está **fora do escopo**.
- **Só fatos do imóvel.** Da leitura de edital/matrícula extraímos apenas atributos do **bem**
  (ex.: existe **penhora**, **usufruto**, **fração ideal**, **ônus**), **redigindo/omitindo** nomes
  e identificadores pessoais **antes de persistir**. Qualquer dado que sobrar deve ser **público e
  vinculado ao imóvel**, nunca um perfil de indivíduo.
- **Sem PII** em logs, telemetria e **prompts de IA** que sejam registrados. Ver
  [Análise jurídica com IA](analise-juridica-ia.md) e [ADR-0014](../arquitetura/decisoes/0014-analise-juridica-ia.md).

## RN-09 — Ciclo de vida do imóvel (vendido / removido / reaparecimento)
A Caixa **não marca** "vendido" no CSV: o imóvel simplesmente **desaparece** da lista quando é
arrematado/retirado. O sistema infere o estado e **nunca apaga** o registro.

**Estados** (`status` = `status_imovel`): `disponivel` · `vendido` · `suspenso` · `removido`.

- **Presente no CSV/detalhe** → `disponivel` (faz upsert dos campos).
- **Sumiu do CSV** → não marcar na hora (pode ser falha transitória de download). Só transiciona
  após **período de carência** (ausente por *N* coletas consecutivas, ex.: 2–3) **ou** confirmação
  pelo detalhe:
  - detalhe indica **venda concluída / arrematado** → `vendido`;
  - detalhe retorna **404 / "imóvel não disponível"** ou ausência sem causa clara → `removido`;
  - retirada temporária / sub judice conhecida → `suspenso`.
- **Reaparecimento** (re-leilão): se um imóvel `vendido`/`removido` **volta** a aparecer no CSV,
  **reativa** para `disponivel`, iniciando um novo ciclo — o histórico anterior é **preservado**
  em `historico_preco`.
- Toda transição de status registra linha em `historico_preco` (**RN-02**) com `capturado_em`.
- **Exclusão lógica ≠ venda:** `vendido`/`removido` são **estados de negócio** (coluna `status`),
  **não** usam `excluido_em`. O soft delete é reservado a **dado inválido/duplicado**, não a
  imóvel que saiu do catálogo. Ver [Modelo de dados](../dados/modelo-de-dados.md).

## RN-10 — Efeitos de "vendido" (enriquecimento, busca, alertas)
- **Enriquecimento:** imóveis `vendido`/`removido` **não** são re-enfileirados para scraping do
  detalhe (economia e respeito ao site); se já estavam na fila, o worker **descarta** o evento.
  Ver [Enriquecimento (ADR-0010)](../arquitetura/decisoes/0010-enriquecimento-detalhe.md).
- **Cálculo/score:** ao virar `vendido`, o cálculo é **congelado** e a oferta é marcada como
  **encerrada** — não é reapresentada como oportunidade.
- **Busca:** por padrão lista só `disponivel`; `vendido`/`removido` ficam acessíveis via filtro
  "incluir encerrados" e nas páginas de histórico.
- **Favoritos/alertas:** se um imóvel **favoritado** muda para `vendido`, o usuário é
  **notificado** ("este imóvel foi vendido"); ele continua visível no favorito com selo **Vendido**.

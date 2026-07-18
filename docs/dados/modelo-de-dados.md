# Modelo de dados

Modelo relacional (PostgreSQL 16 + PostGIS), **normalizado (3FN)** e com **nomes em português**.
O schema é versionado por **Flyway** no backend Java.

> **Diagrama:** veja o esquema visual em
> [Diagramas → Esquema do banco de dados](../arquitetura/diagramas.md#esquema-do-banco-de-dados).

## Convenções e padrões
- **Nomenclatura:** `snake_case`, tabelas e colunas em **português**, nomes **no singular**, sem
  **palavras reservadas** (ex.: `usuario`, nunca `user`).
- **Chave primária:** `id` `bigint GENERATED ALWAYS AS IDENTITY` (padrão SQL). **Sempre `bigint`**,
  mesmo em tabelas pequenas — o `int` estoura em ~2,1 bi e trocar depois é migração cara ([ADR-0012](../arquitetura/decisoes/0012-retencao-dados-historico.md)).
- **Chave estrangeira:** `<tabela_referenciada>_id` (ex.: `imovel_id`).
- **Constraints nomeadas:** `pk_<tabela>`, `fk_<tabela>_<ref>`, `uq_<tabela>_<col>`,
  `ck_<tabela>_<regra>`, `ix_<tabela>_<col>`.
- **Tempo:** `timestamptz` em **UTC**; `criado_em`/`atualizado_em` com default `now()`.
- **Dinheiro:** `numeric(14,2)`. **Percentual:** `numeric(6,2)`.
- **Geo:** `geography(Point,4326)` (PostGIS) com índice **GiST**.
- **Vocabulário controlado:** tabelas de **referência** (`tipo_imovel`, `modalidade_venda`) ou
  **tipos enumerados** (`status_imovel`, `status_enriquecimento`), evitando texto livre repetido.
- **Migrations imutáveis e incrementais** (`V1__init.sql`, `V2__...`).

## Auditoria e exclusão lógica (padrão em todas as tabelas)
Toda tabela (exceto as de **referência**, que são imutáveis) carrega estas colunas — por isso elas
**não são repetidas** em cada tabela abaixo:

| Coluna | Tipo | Regra |
|---|---|---|
| `criado_em` | `timestamptz NOT NULL DEFAULT now()` | Data/hora de criação do registro. |
| `atualizado_em` | `timestamptz NOT NULL DEFAULT now()` | Atualizada em todo `UPDATE` via **trigger** `set_atualizado_em`. |
| `excluido_em` | `timestamptz NULL` | **Exclusão lógica** (soft delete). `NULL` = ativo; preenchido = excluído. |

- **Nunca fazer `DELETE` físico** no fluxo da aplicação — sempre marcar `excluido_em = now()`.
- Toda **leitura** filtra `WHERE excluido_em IS NULL` (encapsular numa **view** `vw_<tabela>_ativo`
  ou repositório base). **UNIQUE** de negócio vira **índice parcial** (`... WHERE excluido_em IS NULL`)
  para permitir recriar um registro após exclusão lógica.
- **Trigger padrão** (uma função reutilizada por todas as tabelas):

```sql
CREATE OR REPLACE FUNCTION set_atualizado_em() RETURNS trigger AS $$
BEGIN NEW.atualizado_em = now(); RETURN NEW; END;
$$ LANGUAGE plpgsql;
-- por tabela:
CREATE TRIGGER tg_<tabela>_atualizado_em BEFORE UPDATE ON <tabela>
  FOR EACH ROW EXECUTE FUNCTION set_atualizado_em();
```

## Tipos enumerados
- `status_imovel`: `disponivel | vendido | suspenso | removido`.
- `status_enriquecimento`: `pendente | ok | parcial | falha`.
- `canal_alerta`: `email | push | webhook`.

## Tabelas de referência
### `municipio`
`id` (PK), `codigo_ibge` (**uq**), `nome`, `uf` `char(2)`.

### `tipo_imovel`
`id` (PK), `nome` (**uq**) — Casa, Apartamento, Terreno, Comercial...

### `modalidade_venda`
`id` (PK), `nome` (**uq**) — "Leilão SFI", "Venda Direta Online", "Licitação Aberta"...

## Tabelas principais
### `imovel`
Núcleo (dados do CSV). Colunas: `id` (PK), `codigo` (N° do imóvel, **uq por fonte**), `fonte`,
`url`, `titulo`, `tipo_imovel_id` (FK), `modalidade_venda_id` (FK), `municipio_id` (FK), `bairro`,
`endereco`, `localizacao` `geography(Point,4326)`, `area_total`, `area_privativa`, `area_terreno`,
`quartos`, `valor_avaliacao`, `valor_minimo`, `desconto_pct`, `status` (`status_imovel`)
+ [colunas de auditoria](#auditoria-e-exclusão-lógica-padrão-em-todas-as-tabelas).

### `imovel_detalhe` (enriquecimento — ADR-0010)
**1:1** com `imovel` (`imovel_id` FK **uq**). Dados raspados da
[página de detalhe](fonte-caixa-detalhe.md): `valor_primeiro_leilao`, `valor_segundo_leilao`,
`data_primeiro_leilao`, `data_segundo_leilao`, `leiloeiro`, `edital`, `numero_item`, `matricula`,
`comarca`, `oficio`, `inscricao_imobiliaria`, `cep`, `endereco_completo`, `aceita_fgts`,
`aceita_financiamento`, `despesas_condominio_comprador`, `despesas_tributos_comprador`,
`situacao_ocupacao`, `descricao_completa`, `edital_url`, `matricula_url`, `enriquecido_em`,
`status_enriquecimento` (`status_enriquecimento`).

### `imovel_foto`
`id` (PK), `imovel_id` (FK), `url`, `ordem`. **uq**(`imovel_id`, `ordem`).

### `historico_preco`
`id` (PK), `imovel_id` (FK), `valor`, `desconto_pct`, `status` (`status_imovel`), `capturado_em`
(histórico de preço/status — ver RN-02).

### `analise_custo`
**1:1** com `imovel` (`imovel_id` FK **uq**), recalculada quando o imóvel muda/é enriquecido:
`itbi`, `custas`, `registro`, `dividas`, `reforma_estimada`, `custo_total`, `desconto_real_pct`,
`score` `smallint` (0–100), `confianca` `numeric(4,3)` (0–1), `versao_score` (ex.: `v0-heuristico`),
`fatores` `jsonb` (array de `{nome, rotulo, contribuicao, direcao}` — explicabilidade, ver
[score-v0-spec](../dominio/score-v0-spec.md)), `parametro_custo_versao` (versão dos parâmetros usados),
`status_confianca` (`status_enriquecimento`), `calculado_em`.

### `analise_juridica` (IA — ADR-0014, evolução)
**1:1** com `imovel` (`imovel_id` FK **uq**). Resultado da [análise jurídica com IA](../dominio/analise-juridica-ia.md):
`resumo` `text` (parecer em linguagem simples — RF-10), `flags` `jsonb` (array de
`{tipo, presente, confianca, trecho_citado, origem}` — grounding), `nivel_risco`
(`baixo|medio|alto`), `modelo` (ex.: `gpt-4o-mini`), `versao_prompt`, `fonte` (`edital|matricula`),
`analisado_em`, `status` (`ok|parcial|falha`). **Não** substitui parecer jurídico humano
(disclaimer obrigatório). Guarda os **trechos citados** que embasam cada flag (nunca "caixa-preta").

### `coleta_bruta`
`id` (PK), `fonte` (`caixa` = CSV, `caixa-detalhe` = HTML), `uf`, `codigo`, `payload_bruto`
`bytea` (**comprimido**), `compressao` (`zstd|gzip|none`), `payload_hash` `char(64)` (SHA-256),
`tamanho_bytes`, `coletado_em`. Permite **reprocessar** sem re-baixar (inclusive re-parsear o
detalhe se o parser mudar).

- **Compressão, não base64:** o payload (HTML/CSV cru) é comprimido com **zstd** e guardado como
  `bytea`. **Base64 é proibido** aqui — codifica sem comprimir e **infla ~33%**. Ver
  [ADR-0012](../arquitetura/decisoes/0012-retencao-dados-historico.md).
- **`payload_hash`** dá **integridade** e **dedup** (não regravar coleta idêntica).
- **Retenção:** ~**90 dias** em banco; depois descartar ou arquivar frio (object storage). É o dado
  que mais **pesa** — ver [Backup & DR](../infraestrutura/backup-e-dr.md). Já `historico_preco` tem
  retenção **longa** (é pequeno e é parte do produto).

## Parâmetros de custo (versionados)
Alimentam o [motor de custos](../dominio/calculo-de-custos.md). São **versionados por vigência**:
o `analise_custo` grava a `parametro_custo_versao` usada, para o cálculo ser **auditável e
reprodutível**. Defaults e fontes em [Parâmetros de custo](parametros-custo.md).

### `aliquota_itbi`
Alíquota de ITBI (varia por município). `id` (PK), `municipio_id` (FK, **null** = default por UF),
`uf` `char(2)` (usado no default por UF), `aliquota_pct` `numeric(6,2)`, `vigencia_inicio` `date`,
`vigencia_fim` `date NULL`, `fonte` (URL/lei), `versao`. **uq** parcial por (`municipio_id`,
`vigencia_inicio`) `WHERE excluido_em IS NULL`.

### `parametro_custo`
Demais parâmetros configuráveis (custas, registro, R$/m² de reforma). `id` (PK), `chave`
(`custas_pct | registro_faixa | reforma_m2`), `escopo` (`nacional | uf | municipio`), `uf`
`char(2) NULL`, `municipio_id` (FK **NULL**), `tipo_imovel_id` (FK **NULL**, p/ reforma por tipo),
`valor` `numeric(14,2) NULL`, `percentual` `numeric(6,2) NULL`, `faixa_min`/`faixa_max`
`numeric(14,2) NULL` (p/ registro por faixa), `vigencia_inicio` `date`, `vigencia_fim` `date NULL`,
`fonte`, `versao`. Resolução: **município → UF → nacional** (mais específico vence).

## Usuários e engajamento
### `usuario`
`id` (PK), `email` (**uq**), `nome`, `avatar_url`, `provedor` (`google|github`), `provedor_id`
(`sub`/id no provedor). **uq**(`provedor`, `provedor_id`). **Sem `senha_hash`** — login social via
OIDC ([ADR-0013](../arquitetura/decisoes/0013-autenticacao-social-oidc.md)); só e-mail verificado.

### `token_atualizacao` (refresh token)
`id` (PK), `usuario_id` (FK), `token_hash` `char(64)` (SHA-256 do refresh, **uq**),
`familia_id` `uuid` (agrupa a cadeia de rotação), `expira_em`, `revogado_em`, `substituido_por` (FK
self, rastreia a rotação), `user_agent`, `ip`. Guardado **hasheado**; habilita **revogação** e
**detecção de reúso** ([ADR-0013](../arquitetura/decisoes/0013-autenticacao-social-oidc.md)).
Retenção: podar expirados/revogados.

### `favorito`
`id` (PK), `usuario_id` (FK), `imovel_id` (FK). **uq**(`usuario_id`, `imovel_id`).

### `alerta`
`id` (PK), `usuario_id` (FK), `filtro` `jsonb`, `canal` (`canal_alerta`), `ativo` `boolean`.

## Tabelas de suporte (infra)
Sustentam decisões arquiteturais aceitas; não são entidades de negócio.

### `geocode_cache` (ADR-0016)
`id` (PK), `chave_hash` `char(64)` (**uq**, SHA-256 de `endereco_normalizado`+`cep`), `lat`, `lng`,
`qualidade` (`exato|aproximado|centroide_bairro|centroide_cidade`), `provedor`, `resolvido_em`.
Evita reconsultar o geocoder; TTL longo.

### `outbox` (ADR-0018 / padrão Transactional Outbox)
`id` (PK), `agregado` (ex.: `imovel`, `alerta`), `agregado_id`, `tipo_evento`, `payload` `jsonb`,
`disponivel_em`, `publicado_em` `NULL`, `tentativas`. Gravada **na mesma transação** da mudança de
estado; um relay publica no RabbitMQ (**at-least-once**, sem perder evento).

### `notificacao_enviada` (ADR-0018 / idempotência)
`id` (PK), `usuario_id` (FK), `tipo_evento`, `imovel_id` (FK **NULL**), `janela` (ex.: dia),
`canal` (`canal_alerta`), `enviado_em`, `status` (`enviado|falha|bounce|complaint`).
**uq**(`usuario_id`, `tipo_evento`, `imovel_id`, `janela`) → dedup de envio.

## Índices e busca
- Filtros: `ix_imovel_municipio`, `ix_imovel_tipo`, `ix_imovel_modalidade`, `ix_imovel_status` e
  índice em `desconto_pct`/`desconto_real_pct` (via `analise_custo`).
- **Espacial (GiST)** em `imovel.localizacao` para busca por raio/região (PostGIS).
- `uq_imovel_codigo_fonte` (`codigo` único por `fonte`) — deduplicação (RN-01); como
  **índice parcial** `WHERE excluido_em IS NULL` (permite recriar após exclusão lógica).

Ver [Backend (Java)](../servicos/backend-java.md) e [Cálculo de custos](../dominio/calculo-de-custos.md).

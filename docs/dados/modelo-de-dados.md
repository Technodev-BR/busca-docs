# Modelo de dados

Modelo relacional (PostgreSQL 16 + PostGIS), **normalizado (3FN)** e com **nomes em português**.
O schema é versionado por **Flyway** no backend Java.

> **Diagrama:** o esquema visual está em
> [`assets/diagramas/banco-dados.drawio`](../assets/diagramas/banco-dados.drawio) — ver
> [Diagramas](../arquitetura/diagramas.md) para como abrir.

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
`score`, `status_confianca` (`status_enriquecimento`), `calculado_em`.

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

## Índices e busca
- Filtros: `ix_imovel_municipio`, `ix_imovel_tipo`, `ix_imovel_modalidade`, `ix_imovel_status` e
  índice em `desconto_pct`/`desconto_real_pct` (via `analise_custo`).
- **Espacial (GiST)** em `imovel.localizacao` para busca por raio/região (PostGIS).
- `uq_imovel_codigo_fonte` (`codigo` único por `fonte`) — deduplicação (RN-01); como
  **índice parcial** `WHERE excluido_em IS NULL` (permite recriar após exclusão lógica).

Ver [Backend (Java)](../servicos/backend-java.md) e [Cálculo de custos](../dominio/calculo-de-custos.md).

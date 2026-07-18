# ADR-0012 — Retenção de dados: histórico curado + coleta bruta comprimida

- **Status:** Aceito
- **Data:** 2026-07-18

## Contexto
A fonte (Caixa) é **volátil**: preços mudam entre 1ª/2ª praça, imóveis são re-listados e
**desaparecem quando vendidos** (ver [RN-09](../../dominio/regras-de-negocio.md)). Precisamos decidir
**o que guardar, por quanto tempo e em que formato**, sem inflar o banco à toa.

Dois artefatos são frequentemente confundidos, mas têm custo e propósito **muito diferentes**:

- **`historico_preco`** — timeline **curada e pequena**: só `valor`, `desconto_pct`, `status` e
  `capturado_em`, gravada **apenas quando muda** (RN-02). É a base de "baixou X%", alertas,
  tendência e auditoria de venda. **Valor alto, custo baixo.**
- **`coleta_bruta`** — payload **cru** (linha CSV ou HTML da página) para **reprocessar/auditar**.
  É o que realmente **pesa** (HTML de detalhe é grande e há um por imóvel).

## Decisão
1. **Manter `historico_preco`** como histórico curado (write-on-change, só preço/desconto/status).
   Retenção **longa/indefinida** — é barato e é parte do produto.
2. **Não versionar todos os campos.** Endereço, áreas, leiloeiro etc. **não** têm histórico próprio;
   se necessário, reconstrói-se a partir do `coleta_bruta`.
3. **`coleta_bruta` comprimido:** o payload é armazenado como **`bytea` comprimido com zstd** (nível
   ~3–6) pelo coletor — **não** base64 (base64 é codificação e **aumenta ~33%**, não comprime).
   Metadados: `payload_hash` (SHA-256, integridade/dedup), `compressao` (`zstd|gzip|none`),
   `tamanho_bytes`. O Postgres ainda aplica TOAST por cima, mas comprimir na origem dá **ratio muito
   melhor** para HTML e evita reprocessar texto gigante.
4. **Retenção do `coleta_bruta`:** manter **90 dias** em banco (janela de reprocesso/depuração).
   Depois: **descartar** ou **arquivar frio** em object storage (MinIO/S3) — configurável. Purga por
   `CronJob` (`DELETE ... WHERE coletado_em < now() - interval '90 days'`).
5. **Chaves `bigint`:** todas as PKs são `bigint GENERATED ALWAYS AS IDENTITY` (o `int` estoura em
   ~2,1 bi; o custo de `bigint` é irrisório e evita migração dolorosa no futuro).

## Consequências
- **+** Banco enxuto: o que pesa (`coleta_bruta`) tem retenção; o que é valioso e leve
  (`historico_preco`) fica.
- **+** Reprocessamento continua possível dentro da janela de retenção; `payload_hash` permite
  **dedup** (não regravar coleta idêntica) e verificação de integridade.
- **+** Compressão zstd reduz muito o storage do HTML bruto vs. texto puro ou base64.
- **−** `coleta_bruta.payload_bruto` deixa de ser **legível/consultável** direto no SQL (é `bytea`
  comprimido) — precisa descomprimir no app/ferramenta. Aceitável: é dado de auditoria, não de query.
- **−** Retenção de 90 dias significa que reprocessar algo **muito antigo** exige recoleta (ou o
  arquivo frio). Trade-off consciente.

## Alternativas consideradas
- **Base64 no payload:** rejeitado — **infla** o tamanho e não comprime; só faz sentido em transporte
  textual, não em storage.
- **`jsonb` para o bruto:** bom para consulta, mas o HTML não é JSON e `jsonb` não comprime bem o
  texto cru — perde o propósito de "snapshot fiel". Rejeitado para o bruto.
- **TOAST/compressão nativa apenas** (`text` + LZ4 do Postgres): simples, mas ratio pior que zstd na
  origem e ainda ocupa mais I/O. Mantido como camada complementar, não como única estratégia.
- **Guardar tudo para sempre:** custo de storage cresce sem retorno proporcional — rejeitado.
- **Versionar todos os campos (temporal table):** complexidade alta e ruído; só rastreamos o que gera
  valor (preço/desconto/status) — rejeitado.

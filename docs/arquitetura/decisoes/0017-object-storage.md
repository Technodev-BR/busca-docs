# ADR-0017 — Object storage para mídias (fotos, editais, matrículas)

- **Status:** Aceito
- **Data:** 2026-07-18 · **Aceito em:** 2026-07-18

## Contexto
O enriquecimento (ADR-0010) baixa **fotos** e **PDFs** (edital, matrícula) e o
[backup](../../infraestrutura/backup-e-dr.md) prevê arquivar frio a `coleta_bruta`. Falta desenhar
**onde** e **como** esses binários são guardados, servidos e expirados. `imovel_foto.url` precisa de
um significado concreto.

## Decisão
- **MinIO (S3-compatível), self-hosted** no cluster (chart Helm — ADR-0015), como storage de
  objetos do MVP; migração para S3 real fica trivial (mesma API).
- **Layout de buckets:**
  - `imoveis` (público via CDN): `imoveis/{codigo}/fotos/{ordem}.jpg`.
  - `documentos` (privado): `documentos/{codigo}/edital.pdf`, `.../matricula.pdf` — acesso por
    **URL assinada** (expira), nunca link público direto.
  - `coleta-fria`: arquivamento da `coleta_bruta` após a retenção quente (ADR-0012).
- **`imovel_foto.url`** guarda a **chave do objeto** (ou URL pública via CDN), não o binário no banco.
- **CDN**: fotos servidas atrás do **Cloudflare** (cache), reduzindo carga no MinIO.
- **Lifecycle**: expiração/arquivo por prefixo; imagens reprocessáveis a partir da `coleta_bruta`.

## Arquitetura, robustez e escala
- **Abstração S3 (porta):** o código fala **S3 API** (SDK); endpoint/credenciais por env. Trocar
  MinIO ↔ S3/Backblaze é só configuração — **sem lock-in**.
- **Content-addressing + dedup:** nome do objeto inclui `sha256` do binário → mesma foto não é
  regravada; casa com o `payload_hash` da `coleta_bruta`.
- **Pipeline de imagem:** gerar **derivados** (thumbnail/card, médio, original) no worker de mídia;
  servir WebP quando possível; `Cache-Control` longo + CDN (Cloudflare) na frente das fotos públicas.
- **Documentos privados (edital/matrícula):** **URLs assinadas** com TTL curto (ex.: 5–15 min);
  nunca públicas. Opcional: **varredura antivírus** de PDFs antes de liberar.
- **Segurança:** buckets **privados por padrão**, política mínima por prefixo, credenciais em Secret,
  criptografia em repouso (SSE) e TLS em trânsito.
- **Lifecycle concreto:** `imoveis/**` mantém enquanto o imóvel existir; `coleta-fria/**` expira/move
  conforme retenção (ADR-0012); versão anterior de foto expira em N dias.
- **HA & capacidade:** MVP em **MinIO single-node** (backup do volume); plano de crescimento para
  **MinIO distribuído** (erasure coding) ou S3 gerenciado quando o volume exigir. Cotas/limite de
  tamanho por imóvel para evitar abuso.
- **Backup/DR:** replicação do bucket (ou snapshot do volume) alinhada ao [Backup & DR](../../infraestrutura/backup-e-dr.md);
  tudo é **reprocessável** a partir da `coleta_bruta` como último recurso.
- **Observabilidade:** uso por bucket/prefixo, taxa de erro de upload, latência, hit de CDN,
  objetos órfãos (sem `imovel_foto` correspondente).

## Consequências
- **+** Banco leve (sem BLOBs); servir mídia barato e cacheável.
- **+** Documentos sensíveis protegidos por URL assinada; troca para S3 sem mudar código.
- **−** Mais um serviço stateful para operar/backupar (bucket + credenciais).
- **−** Precisa de política de dedup/limite de tamanho por imóvel.

## Alternativas consideradas
- **Binários no PostgreSQL (bytea)**: infla o banco e os backups — rejeitado (só `coleta_bruta`
  comprimida fica no banco por prazo curto).
- **Servir direto do site da Caixa (hotlink)**: frágil, sem controle de disponibilidade/ToS —
  rejeitado.

## Referências
- [ADR-0010](0010-enriquecimento-detalhe.md) · [ADR-0012](0012-retencao-dados-historico.md)
  · [Backup & DR](../../infraestrutura/backup-e-dr.md) · [Modelo de dados](../../dados/modelo-de-dados.md)

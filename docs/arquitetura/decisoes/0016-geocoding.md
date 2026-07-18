# ADR-0016 — Geocoding (endereço → coordenadas)

- **Status:** Aceito
- **Data:** 2026-07-18 · **Aceito em:** 2026-07-18

## Contexto
O **mapa** (RF-04), a busca por **raio/bbox** (PostGIS) e o **mini-mapa** do detalhe (RF-15) exigem
`localizacao geography(Point)` para cada imóvel. O CSV/detalhe traz endereço/bairro/CEP, não
coordenadas. É preciso um `GeocodingPort` com uma implementação concreta, respeitando os **Termos
de Uso** do serviço e a escala de **dezenas de milhares** de imóveis.

## Decisão
- **Primário: Nominatim self-hosted** (container/Helm no cluster) sobre dados do OpenStreetMap.
  Evita o limite de **1 req/s** do Nominatim público (cujos ToS **proíbem** uso em massa) e mantém
  o dado interno.
- **Cache persistente**: toda resolução é gravada (coordenadas + `qualidade`/`confianca` + fonte) e
  reusada; re-geocoding só quando o endereço muda. Nunca geocodar em request de usuário (é batch,
  no worker `GeocodificarImovelUseCase`).
- **Preferência de entrada**: `CEP` do detalhe > endereço completo > bairro/cidade (fallback com
  menor confiança).
- **Fallback opcional** para provedor pago (ex.: LocationIQ/Google) apenas para endereços que o
  Nominatim não resolve, com **flag de custo** e limite mensal.
- **Rate limit e backoff** no worker; **paced** junto do enriquecimento (ADR-0010).

## Arquitetura, robustez e escala
- **Porta + cadeia de fallback:** `GeocodingPort` com adapters ordenados
  (`nominatim → provedor_pago → indisponível`). Cada adapter tem **circuit breaker**; falha do
  primário abre o breaker e passa ao próximo sem derrubar o worker.
- **Cache persistente** (`geocode_cache`): chave = `hash(endereco_normalizado + cep)`; guarda
  `lat/lng`, `qualidade` (`exato|aproximado|centroide_bairro|centroide_cidade`), `provedor`,
  `resolvido_em`. **Hit** evita nova chamada; TTL longo (endereço muda pouco).
- **Normalização** antes de consultar (abreviações, acentos, tipo de logradouro) para maximizar hit
  e qualidade; preferir **CEP** quando houver.
- **Nominatim self-hosted:** container com base OSM do Brasil; **réplicas stateless** de leitura atrás
  de um Service; atualização do **dump mensal** via job agendado (blue/green para não derrubar).
  Dimensionar disco (dezenas de GB) e memória do índice.
- **Escala do batch:** geocoding roda no worker `GeocodificarImovelUseCase`, **paced** junto do
  enriquecimento; nunca no request do usuário. Throughput alvo acompanha o backlog da fila.
- **Qualidade & mapa:** armazenar `qualidade`/`confianca`; a UI sinaliza pontos de baixa precisão
  (ex.: só centroide de bairro) e evita "falsa exatidão".
- **Observabilidade:** `% imóveis geocodados`, distribuição de `qualidade`, latência p95, taxa de
  fallback e de erro por provedor, custo do provedor pago (ver [pilares](../../observabilidade/pilares.md)).

## Consequências
- **+** Sem custo por chamada nem violação de ToS; escala controlada por nós.
- **+** Cobertura medida por métrica de negócio (`% imóveis geocodados`).
- **−** Operar mais um serviço (Nominatim + base OSM ~dezenas de GB); atualização periódica do dump.
- **−** Qualidade variável em endereços ruins → armazenar `confianca` e sinalizar no mapa.

## Alternativas consideradas
- **Nominatim público**: viola ToS para volume; rate limit inviável — rejeitado como primário.
- **Só provedor pago**: custo por chamada em escala e dependência externa — fica como fallback.
- **Geocoding via PostGIS Tiger**: dados de qualidade fraca no Brasil — rejeitado.

## Referências
- [Modelo de dados](../../dados/modelo-de-dados.md) · [Collector](../../servicos/collector-python.md)
  · [SLO/SLI](../../observabilidade/slo-sli.md) · [Política de coleta](../../legal/politica-de-coleta.md)

# Fonte Caixa (detalhe) — enriquecimento por imóvel

Fonte **secundária** de dados: a **página de detalhe** de cada imóvel, usada para **enriquecer** o
que o [CSV](fonte-caixa-csv.md) não traz. Estratégia e fronteira em
[ADR-0010](../arquitetura/decisoes/0010-enriquecimento-detalhe.md).

## Onde buscar
- **URL** (a mesma do campo `link` do CSV):
  `https://venda-imoveis.caixa.gov.br/sistema/detalhe-imovel.asp?hdnimovel={codigo}`
- `{codigo}` = **N° do imóvel** do CSV (ex.: `1444408501866`; na página aparece formatado como
  `144440850186-6`).
- **Coleta respeitosa** (obrigatória): *user-agent* identificável, poucos req/min, backoff em
  429/5xx, concorrência baixa, cache e **sem burlar proteção** (ver [Legal & LGPD](../legal/lgpd.md)).

## Campos disponíveis (verificado em amostra real)
Exemplo: imóvel `1444408501866` (ADAMANTINA/SP).

| Campo | Exemplo | Observação / novo vs. CSV |
|---|---|---|
| Título (cidade - bairro) | `ADAMANTINA - VILA JOAQUINA` | |
| Tipo de imóvel | `Casa` | também no CSV (via Descrição) |
| Número do imóvel | `144440850186-6` | = `codigo` (sem o traço) |
| **Valor de avaliação** | `R$ 501.000,00` | |
| **Valor mín. 1º Leilão** | `R$ 501.000,00` | **novo** (CSV tinha 1 preço só) |
| **Valor mín. 2º Leilão** | `R$ 300.600,00` | **novo** — base do desconto real |
| **Data do 1º Leilão** | `04/08/2026 - 10h00` | **novo** |
| **Data do 2º Leilão** | `10/08/2026 - 10h00` | **novo** |
| Modalidade | `Leilão SFI` | |
| **Edital / item** | `0035/0226 - CPA/RE` · item `465` | **novo** |
| **Leiloeiro(a)** | `AYRTON DE SOUZA PORTO FILHO` | **novo** |
| **Matrícula(s)** | `14601` | **novo** |
| **Comarca / Ofício** | `ADAMANTINA-SP` / `01` | **novo** |
| **Inscrição imobiliária** | `770900` | **novo** |
| Área privativa / terreno | `171,43 m²` / `384,00 m²` | confirma o CSV |
| **Endereço + CEP** | `... CEP: 17800-000, ADAMANTINA - SAO PAULO` | **CEP novo** → geocoding preciso |
| **Formas de pagamento** | `Recursos próprios. Permite FGTS.` | **novo** (FGTS/financiamento) |
| **Despesas** | `Condomínio e Tributos: por conta do comprador` | **novo** — sinaliza dívidas |
| **Matrícula (PDF)** | link "Baixar matrícula do imóvel" | **novo** |
| **Edital (PDF)** | link "Baixar edital e anexos" (+ data de publicação) | **novo** |
| **Galeria de fotos** | seção "Galeria de fotos" | **novo** |

> **A verificar / variações por imóvel:** nem todo imóvel tem 2 praças (venda direta/licitação
> podem ter só "valor mínimo"); a **Descrição** às vezes vem vazia (`.`); imóveis ocupados têm
> aviso de **situação de ocupação**; o padrão exato de URL das **fotos** e dos **PDFs** deve ser
> confirmado ao implementar (salvar amostras de HTML como fixtures de teste).

## Regras de parsing (para o coletor de detalhe)
1. `GET` na URL com *user-agent* identificável (a página é ASP — tratar cookie/sessão se necessário).
2. Guardar o **HTML bruto** em `coleta_bruta` (`fonte='caixa-detalhe'`) antes de parsear.
3. Extrair os campos da tabela acima com seletores **resilientes** (tolerar ausência de campos).
4. Converter valores BR (`.` milhar, `,` decimal) e datas (`dd/mm/aaaa - HHhMM` → UTC).
5. Baixar **fotos** e **PDFs** (matrícula/edital) → object storage; guardar URLs/caminhos.
6. Detectar **anomalia de parse** (página sem campos esperados) → falhar o item (retry/DLQ) e
   **alertar** (pode ser mudança de layout).
7. **Detectar imóvel indisponível/vendido**: `404` ou página de "imóvel não disponível" **não** é
   erro de parse — sinaliza ao backend para transição de status (`vendido`/`removido`), sem retry.
   Ver [RN-09](../dominio/regras-de-negocio.md#rn-09--ciclo-de-vida-do-imóvel-vendido--removido--reaparecimento).
8. Enviar ao backend via [API de Ingestão — detalhe](../contratos/api-ingestao.md).

Ver [Collector (Python)](../servicos/collector-python.md) e
[Eventos RabbitMQ](../contratos/eventos-rabbitmq.md).

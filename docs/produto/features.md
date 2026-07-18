# Features

Features funcionais por módulo. Cada uma se conecta a regras de negócio e a requisitos.

## Busca & Filtros
Busca por UF, cidade, bairro, tipo, faixa de preço, % de desconto e modalidade (leilão/venda
direta), com ordenação e paginação.

## Mapa
Pins por imóvel, busca por raio/região (PostGIS) e cluster de marcadores.

## Detalhe do imóvel
Dados, **galeria de fotos**, link do edital/matrícula (PDF), histórico de preço e a análise de custo.
Extras que ajudam a decidir:

- **Cronômetro (contagem regressiva)** para o 1º e o 2º leilão (urgência clara).
- **Aviso de ocupação**: banner destacado quando o imóvel está **ocupado** (risco de desocupação).
- **Mini-mapa** com a localização do imóvel (Leaflet + PostGIS) e entorno.
- **Painel de análise jurídica/IA** (nua-propriedade, fração ideal, usufruto, ônus/gravames) —
  ver [Análise jurídica com IA](../dominio/analise-juridica-ia.md).
- (Se houver) **avaliações/indicadores** da região para contexto de liquidez.

## Motor de custos
Cálculo de **ITBI** (alíquota por município configurável) + custas + registro + reforma estimada
→ **custo total** e **desconto real** vs. avaliação/mercado.
Detalhe em [Cálculo de custos](../dominio/calculo-de-custos.md).

## Pré-análise de viabilidade
Score a partir de desconto, liquidez da região e riscos do edital.
Detalhe em [Pré-análise](../dominio/pre-analise-viabilidade.md).

## Favoritos & Alertas
Salvar buscas e ser notificado quando surgir imóvel dentro do filtro.

## Comparação
Colocar 2+ imóveis lado a lado.

## IA (evolução)
Resumo do edital e parecer "vale a pena?", **análise jurídica de investimento** (detecta
nua-propriedade, fração ideal, usufruto, direitos reais e ônus/gravames) e indicação dos **melhores
negócios**. Detalhe e guarda-corpos em [Análise jurídica com IA](../dominio/analise-juridica-ia.md)
e [ADR-0014](../arquitetura/decisoes/0014-analise-juridica-ia.md).

## Admin / Observação
Status das coletas e última "Data de geração" por UF.

# Requisitos

## Requisitos funcionais (RF)

| ID | Requisito |
|---|---|
| RF-01 | Coletar imóveis da lista oficial da Caixa (CSV por UF) periodicamente. |
| RF-02 | Normalizar e deduplicar imóveis pelo **N° do imóvel**. |
| RF-03 | Buscar e filtrar por UF, cidade, bairro, tipo, faixa de preço, % de desconto e modalidade. |
| RF-04 | Exibir imóveis em **mapa** com busca por região/raio. |
| RF-05 | Exibir **página de detalhe** com fotos, link do edital e histórico de preço. |
| RF-06 | Calcular **custo total** (lance + ITBI + custas + registro + reforma) e **desconto real**. |
| RF-07 | Gerar **pré-análise de viabilidade** (score). |
| RF-08 | Permitir **favoritar** imóveis e criar **alertas** por filtro (requer **login social** Google/GitHub). |
| RF-09 | Comparar 2+ imóveis lado a lado. |
| RF-10 | (Evolução) Resumir edital e emitir parecer com **IA**. |
| RF-14 | (Evolução) **Análise jurídica com IA**: detectar nua-propriedade, fração ideal, usufruto, direitos reais e **ônus/gravames** para indicar os **melhores negócios**. |
| RF-15 | Na tela de detalhe: **cronômetro** dos leilões, **aviso de ocupação** e **mini-mapa** da localização. |
| RF-11 | Painel de **status das coletas** (última "Data de geração" por UF). |
| RF-12 | **Enriquecer** o imóvel pela página de detalhe (1º/2º leilão, edital, dívidas, ocupação, fotos). |
| RF-13 | Tratar **ciclo de vida**: marcar **vendido/removido** quando sai do CSV e **notificar** favoritos. |

## Requisitos não-funcionais (RNF)

| ID | Requisito | Meta |
|---|---|---|
| RNF-01 | Desempenho da busca | p95 < 400 ms |
| RNF-02 | Tempo de carga inicial | < 2 s |
| RNF-03 | Disponibilidade (API) | SLO 99,5%/mês |
| RNF-04 | Escala inicial | dezenas de milhares de imóveis |
| RNF-05 | Atualização de dados | coleta diária; marcar "removido" quando sai do CSV |
| RNF-06 | Segurança | HTTPS, **login social OIDC** (sem senha, cookie HttpOnly + CSRF), rate limiting, segredos fora do git, imagens sem CVE crítica |
| RNF-07 | Privacidade | sem dados pessoais (LGPD) — só dados do imóvel |
| RNF-08 | Portabilidade | dev com `docker compose up`; prod em k3s (Kubernetes) |
| RNF-09 | Acessibilidade/i18n | pt-BR, contraste e navegação por teclado |
| RNF-10 | Observabilidade | métricas, logs e traces instrumentados desde o início |

Ver metas de confiabilidade detalhadas em [SLO / SLI](../observabilidade/slo-sli.md).

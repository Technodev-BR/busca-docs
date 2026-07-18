# Rastreabilidade (requisito → onde é atendido)

Mapa que liga cada [requisito](requisitos.md) ao **onde ele é implementado** (serviço), ao
**contrato/regra** que o sustenta e a **como é verificado** (teste/observabilidade). Serve para
garantir que nada fica "órfão" e para avaliar impacto de mudanças.

## Requisitos funcionais (RF)

| RF | Onde é atendido (serviço) | Caso(s) de uso | Regra/contrato | Como é verificado |
|---|---|---|---|---|
| RF-01 Coletar CSV da Caixa | [Collector](../servicos/collector-python.md) + [Backend](../servicos/backend-java.md) | `executar`/`baixar_csv` · `IngerirLoteCsvUseCase` | [Fonte Caixa (CSV)](../dados/fonte-caixa-csv.md), [API de Ingestão](../contratos/api-ingestao.md) | Testes do collector; painel de coletas (RF-11) |
| RF-02 Normalizar/deduplicar | [Backend](../servicos/backend-java.md) (workers) | `NormalizarImovelUseCase` · `GeocodificarImovelUseCase` · idempotência do `IngerirLoteCsvUseCase` | [Eventos RabbitMQ](../contratos/eventos-rabbitmq.md), idempotência por `codigo` | Testes de contrato + unidade |
| RF-03 Busca e filtros | [Backend](../servicos/backend-java.md) + [Frontend](../servicos/frontend-angular.md) | `BuscarImoveisUseCase` | [API Pública](../contratos/api-publica.md), [Modelo de dados](../dados/modelo-de-dados.md) | Testes de API; métrica p95 (RNF-01) |
| RF-04 Mapa por região/raio | [Frontend](../servicos/frontend-angular.md) + [Backend](../servicos/backend-java.md) | `BuscarImoveisUseCase` (`bbox`/`raioKm`) | PostGIS ([Modelo de dados](../dados/modelo-de-dados.md)) | Testes de UI/e2e |
| RF-05 Página de detalhe | [Frontend](../servicos/frontend-angular.md) + [Backend](../servicos/backend-java.md) | `ObterImovelUseCase` · `ListarHistoricoPrecoUseCase` | histórico de preço ([Modelo de dados](../dados/modelo-de-dados.md)) | e2e |
| RF-06 Cálculo de custo/desconto | [Backend](../servicos/backend-java.md) (workers) | `CalcularCustoUseCase` | [Cálculo de custos](../dominio/calculo-de-custos.md) | Testes unitários do motor de custos |
| RF-07 Pré-análise (score) | [Backend](../servicos/backend-java.md) (workers) | `CalcularScoreUseCase` | [Pré-análise de viabilidade](../dominio/pre-analise-viabilidade.md) | Testes unitários do score |
| RF-08 Favoritos e alertas | [Backend](../servicos/backend-java.md) + [Frontend](../servicos/frontend-angular.md) | `ProcessarLoginSocialUseCase` · `Favoritar`/`ListarFavoritos` · `CriarAlerta`/`AvaliarAlertas` | [ADR-0013](../arquitetura/decisoes/0013-autenticacao-social-oidc.md), [Regras de negócio](../dominio/regras-de-negocio.md) | Testes de API/e2e |
| RF-09 Comparar imóveis | [Frontend](../servicos/frontend-angular.md) | (composição no front sobre `ObterImovelUseCase`) | — | e2e |
| RF-10 Resumo do edital (IA, textual) | [Backend](../servicos/backend-java.md) (`AnaliseJuridicaPort`) | `AnalisarJuridicoUseCase` (saída textual/parecer; subconjunto de RF-14) | [ADR-0014](../arquitetura/decisoes/0014-analise-juridica-ia.md), [Análise jurídica com IA](../dominio/analise-juridica-ia.md) | Testes com editais de amostra; disclaimer obrigatório |
| RF-11 Painel de coletas | [Backend](../servicos/backend-java.md) + [Frontend](../servicos/frontend-angular.md) | métricas do collector + status por UF | "Data de geração" ([Fonte Caixa](../dados/fonte-caixa-csv.md)) | Testes de API |
| RF-12 Enriquecer (detalhe) | [Collector](../servicos/collector-python.md) + [Backend](../servicos/backend-java.md) | `consumir_enriquecimento`/`parsear_detalhe` · `IngerirDetalheUseCase` | [ADR-0010](../arquitetura/decisoes/0010-enriquecimento-detalhe.md), [Fonte Caixa (detalhe)](../dados/fonte-caixa-detalhe.md) | Testes com fixtures de HTML |
| RF-13 Ciclo de vida (vendido) | [Backend](../servicos/backend-java.md) + [Collector](../servicos/collector-python.md) | `ConciliarAusenciasUseCase` · `MarcarStatusImovelUseCase` · `AvaliarAlertasUseCase` | [RN-09](../dominio/regras-de-negocio.md#rn-09--ciclo-de-vida-do-imóvel-vendido--removido--reaparecimento) | Testes unitários (carência/transições) |
| RF-14 Análise jurídica (IA) | [Backend](../servicos/backend-java.md) (`AnaliseJuridicaPort`) | `AnalisarJuridicoUseCase` (extrai flags do edital/matrícula) | [ADR-0014](../arquitetura/decisoes/0014-analise-juridica-ia.md), [Análise jurídica com IA](../dominio/analise-juridica-ia.md) | Testes com editais de amostra; grounding/confiança |
| RF-15 Detalhe: cronômetro/aviso/mapa | [Frontend](../servicos/frontend-angular.md) | consome `ObterImovelUseCase` (datas, `situacao_ocupacao`, `localizacao`) | [API Pública](../contratos/api-publica.md) | e2e/UI |

## Requisitos não-funcionais (RNF)

| RNF | Onde é atendido | Como é verificado |
|---|---|---|
| RNF-01 Desempenho busca (p95<400ms) | [Cache Redis](../arquitetura/decisoes/0007-cache-redis.md) + índices | Métricas ([SLO/SLI](../observabilidade/slo-sli.md)) |
| RNF-02 Carga inicial (<2s) | [Frontend](../servicos/frontend-angular.md) (build/otimização) | Lighthouse/e2e |
| RNF-03 Disponibilidade (99,5%) | [k3s + GitOps](../infraestrutura/kubernetes-gitops.md) | [SLO/SLI](../observabilidade/slo-sli.md), alertas |
| RNF-04 Escala inicial | [Modelo de dados](../dados/modelo-de-dados.md), [RabbitMQ](../arquitetura/decisoes/0005-mensageria-rabbitmq.md) | Testes de carga |
| RNF-05 Atualização diária | [Collector](../servicos/collector-python.md) (scheduler) | Painel de coletas (RF-11) |
| RNF-06 Segurança | [ADR-0013](../arquitetura/decisoes/0013-autenticacao-social-oidc.md) (OIDC/BFF), [Segurança](../qualidade/seguranca.md), [Config & segredos](../infraestrutura/configuracao-e-segredos.md) | [CI/CD](../qualidade/ci-cd.md): Trivy/SonarQube |
| RNF-07 Privacidade (LGPD) | [Legal & LGPD](../legal/lgpd.md) | Revisão de dados coletados |
| RNF-08 Portabilidade | [Docker](../infraestrutura/desenvolvimento-docker.md) / [k3s](../infraestrutura/kubernetes-gitops.md) | Build de imagem + deploy |
| RNF-09 Acessibilidade/i18n | [Frontend](../servicos/frontend-angular.md) | e2e / auditoria a11y |
| RNF-10 Observabilidade | [Pilares](../observabilidade/pilares.md) | Dashboards Grafana |

> Manutenção: ao criar/alterar um requisito, atualize esta matriz no **mesmo PR**. Um requisito
> sem coluna "onde é atendido" é sinal de lacuna de implementação ou de doc.

Ver também: [Requisitos](requisitos.md) · [Testes](../qualidade/testes.md) · [SLO/SLI](../observabilidade/slo-sli.md).

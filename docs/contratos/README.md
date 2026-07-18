# Contratos (API-first)

Os **contratos são a fonte da verdade** das integrações entre os componentes. Definimos o
contrato **antes** de implementar (API-first), e ele é versionado aqui.

## Contratos deste projeto

| Contrato | O que define | Arquivo |
|---|---|---|
| **API Pública (consulta)** | Como o frontend (Angular) lê imóveis, detalhe, histórico, favoritos/alertas | [api-publica.md](api-publica.md) · [openapi-api.yaml](openapi-api.yaml) |
| **API de Ingestão** | Como o coletor (Python) envia imóveis para o backend (Java) | [api-ingestao.md](api-ingestao.md) · [openapi-ingestao.yaml](openapi-ingestao.yaml) |
| **Eventos RabbitMQ** | Mensagens trocadas para processamento assíncrono | [eventos-rabbitmq.md](eventos-rabbitmq.md) |

## Princípios

- **Versionamento**: contrato tem versão explícita (`/v1`, `version` no evento). Mudança
  incompatível → nova versão.
- **Compatibilidade**: preferir mudanças **retrocompatíveis** (adicionar campo opcional, nunca
  remover/renomear em uma mesma versão).
- **Validação nas duas pontas**: quem envia e quem recebe validam contra o schema.
- **Testes de contrato**: garantem que produtor e consumidor não quebrem
  (ver [Testes](../qualidade/testes.md)) — Spring Cloud Contract (Java) e schema pydantic (Python).
- **Idempotência**: o `codigo` do imóvel (N° do imóvel da Caixa) é a chave natural para
  deduplicar e reprocessar sem efeitos colaterais.

## Fluxo

```
Coletor (Python)
   → [API de Ingestão /v1]  grava coleta_bruta e publica evento
        → [Exchange imoveis]  → filas de processamento (workers)
             → persiste em PostgreSQL
                  ← [API Pública /api/v1]  ← Frontend (Angular)
```

Ver [Visão geral da arquitetura](../arquitetura/visao-geral.md),
[ADR-0001](../arquitetura/decisoes/0001-stack-tecnologica.md) e
[ADR-0005](../arquitetura/decisoes/0005-mensageria-rabbitmq.md).

# Decisões de arquitetura (ADRs)

Um **ADR** (*Architecture Decision Record*) registra, de forma curta e imutável, uma decisão
técnica relevante: o **contexto**, a **decisão** e as **consequências**.

- ADRs são **imutáveis** após aceitos. Para mudar, crie um novo ADR que **supersede** o anterior.
- Numeração sequencial: `NNNN-titulo.md`.

## Índice

| ADR | Título | Status |
|---|---|---|
| [0001](0001-stack-tecnologica.md) | Stack tecnológica e fronteira Java/Python | Aceito |
| [0002](0002-fonte-oficial-csv-caixa.md) | Fonte oficial: CSV da Caixa (não scraping) | Aceito |
| [0003](0003-dois-repositorios-gitops.md) | Dois repositórios (app + GitOps) | Aceito |
| [0004](0004-documentacao-markdown-puro.md) | Documentação em Markdown puro (sem framework) | Aceito |
| [0005](0005-mensageria-rabbitmq.md) | Mensageria com RabbitMQ (processamento assíncrono) | Aceito |
| [0006](0006-infra-k3s-vps-cloudflare.md) | Infra de produção: k3s/VPS Hostinger, Traefik, Cloudflare, VPN | Aceito |
| [0007](0007-cache-redis.md) | Cache de leitura com Redis (cache-aside) | Aceito |
| [0008](0008-traefik-self-managed.md) | Traefik gerenciado por nós (k3s sem Traefik embutido) | Aceito |
| [0009](0009-gerenciamento-portainer.md) | Portainer como ferramenta de gerenciamento do cluster | Aceito |
| [0010](0010-enriquecimento-detalhe.md) | Enriquecimento por página de detalhe (Caixa) | Aceito |
| [0011](0011-portal-docs-vitepress.md) | Portal de documentação gerado (VitePress) | Proposto |
| [0012](0012-retencao-dados-historico.md) | Retenção: histórico curado + coleta bruta comprimida | Aceito |
| [0013](0013-autenticacao-social-oidc.md) | Autenticação social (Google/GitHub) com OIDC e BFF | Aceito |
| [0014](0014-analise-juridica-ia.md) | Análise jurídica de investimento assistida por IA | Proposto |

## Template

```markdown
# ADR-NNNN — Título

- **Status:** Proposto | Aceito | Substituído por ADR-XXXX
- **Data:** AAAA-MM-DD

## Contexto
Qual é o problema/força que motiva a decisão?

## Decisão
O que foi decidido (de forma clara e afirmativa).

## Consequências
Positivas, negativas e trade-offs. O que passa a ser verdade depois desta decisão.

## Alternativas consideradas
Opções avaliadas e por que não foram escolhidas.
```

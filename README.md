# Busca-Busca — Documentação (docs-first)

Repositório de **documentação** do **Busca-Busca**, uma plataforma para **centralizar a busca,
o filtro e a pré-análise de imóveis em leilão** (começando pela Caixa), com cálculo de custos
(ITBI, custas, etc.) e evolução para análise assistida por IA.

> **Abordagem docs-first:** primeiro documentamos objetivo, regras de negócio, arquitetura e
> decisões; o código nasce a partir daqui. Esta é a **fonte única da verdade** do projeto.

> **Só markdown, sem ferramenta de build.** A documentação é **markdown puro**, para ler direto no
> GitHub/editor e ser facilmente compreendida por pessoas e por agentes de IA. Não há site a
> gerar. (Decisão registrada em [ADR-0004](docs/arquitetura/decisoes/0004-documentacao-markdown-puro.md).)

## Índice

O **índice canônico** da documentação fica em **[`docs/`](docs/README.md)** — comece por
lá. Novo no projeto? Veja os **[Primeiros passos](docs/visao-geral/primeiros-passos.md)**.

Entradas por tema (cada pasta abre seu `README.md` automaticamente no GitHub):

| Tema | Entrada |
|---|---|
| Visão geral | [docs/visao-geral/](docs/visao-geral/README.md) |
| Produto | [docs/produto/](docs/produto/README.md) |
| Arquitetura | [docs/arquitetura/](docs/arquitetura/README.md) |
| Domínio | [docs/dominio/](docs/dominio/README.md) |
| Contratos | [docs/contratos/](docs/contratos/README.md) |
| Dados | [docs/dados/](docs/dados/README.md) |
| Serviços | [docs/servicos/](docs/servicos/README.md) |
| Infraestrutura | [docs/infraestrutura/](docs/infraestrutura/README.md) |
| Observabilidade | [docs/observabilidade/](docs/observabilidade/README.md) |
| Qualidade | [docs/qualidade/](docs/qualidade/README.md) |
| Legal & conformidade | [docs/legal/](docs/legal/README.md) |

## Estrutura de pastas

Cada pasta temática tem um `README.md` como página de entrada (renderiza sozinho ao abrir a pasta).

```
docs/
  README.md                    # índice canônico (porta de entrada)
  visao-geral/                 # objetivo, primeiros passos, glossário, roadmap
  produto/                     # requisitos, features, estudos de caso, rastreabilidade
  arquitetura/                 # visão, stack, ferramentas, diagramas e ADRs (decisões)
  dominio/                     # regras de negócio, cálculo de custos, pré-análise
  contratos/                   # API de ingestão (OpenAPI) e eventos RabbitMQ
  dados/                       # modelo de dados e a fonte Caixa (CSV/detalhe)
  servicos/                    # backend (Java), collector (Python), frontend (Angular)
  infraestrutura/              # Docker (dev), repos, k3s/GitOps, rede, config/segredos, backup, registry
  observabilidade/             # métricas/logs/traces, SLO, AIOps (MCP), runbooks
  qualidade/                   # testes, CI/CD, segurança
  legal/                       # LGPD, termos de uso, conformidade
  assets/diagramas/            # arquivos .drawio (diagrams.net)
tools/                         # geradores dos diagramas (Python)
```

## Diagramas

Os diagramas estão em [`docs/assets/diagramas/`](docs/assets/diagramas/) no formato
[draw.io](https://draw.io) (`.drawio`). Abra em [app.diagrams.net](https://app.diagrams.net)
(File → Open) ou pela extensão *Draw.io Integration* no VS Code/Cursor. São gerados por script:

```bash
python tools/gerar_drawio.py     # arquitetura, fluxo GitOps e esquema do banco
```

## Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md) — convenções de escrita, ADRs e commits.

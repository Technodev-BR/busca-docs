# Busca-Busca — Documentação (docs-first)

Repositório de **documentação** do **Busca-Busca**, uma plataforma para **centralizar a busca,
o filtro e a pré-análise de imóveis em leilão** (começando pela Caixa), com cálculo de custos
(ITBI, custas, etc.) e evolução para análise assistida por IA.

> **Abordagem docs-first:** primeiro documentamos objetivo, regras de negócio, arquitetura e
> decisões; o código nasce a partir daqui. Esta é a **fonte única da verdade** do projeto.

> **Markdown como fonte única.** A documentação é **markdown puro**, para ler direto no
> GitHub/editor e ser facilmente compreendida por pessoas e por agentes de IA
> (ver [ADR-0004](docs/arquitetura/decisoes/0004-documentacao-markdown-puro.md)). Opcionalmente,
> há um **portal navegável** gerado a partir desses mesmos `.md` — veja
> [Portal de documentação](#portal-de-documentação-vitepress) abaixo.

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
  public/diagramas/            # .drawio (fonte, diagrams.net) + SVG servidos pelo portal
tools/                         # geradores dos diagramas (Python)
```

## Diagramas

Os diagramas estão em [`docs/public/diagramas/`](docs/public/diagramas/) no formato
[draw.io](https://draw.io) (`.drawio`). Abra em [app.diagrams.net](https://app.diagrams.net)
(File → Open) ou pela extensão *Draw.io Integration* no VS Code/Cursor. São gerados por script:

```bash
node tools/gerar_drawio.mjs      # arquitetura, fluxo GitOps e esquema do banco
# ou: npm run diagrams
```

## Portal de documentação (VitePress)

Além de ler os `.md` direto no GitHub/editor, há um **portal navegável** (menu lateral, busca
full-text) gerado com [VitePress](https://vitepress.dev) a partir dos mesmos arquivos de `docs/`.
É opcional — hospedado no **GitHub Pages** como paliativo até o deploy definitivo via k3s/GitOps
(ver [ADR-0011](docs/arquitetura/decisoes/0011-portal-docs-vitepress.md)).

Pré-requisito: **Node.js 20+**.

```bash
npm install          # instala as dependências (uma vez)
npm run docs:dev     # sobe o portal em modo dev -> http://localhost:5173
npm run docs:build   # gera o site estático em docs/.vitepress/dist
npm run docs:preview # pré-visualiza o build de produção
```

> Os diagramas aparecem como **placeholders** em ambiente local; no build de publicação (CI) os
> arquivos `.drawio` são renderizados em SVG automaticamente.

## Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md) — convenções de escrita, ADRs e commits.

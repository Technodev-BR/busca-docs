# Como contribuir com a documentação

Esta base segue **docs-as-code**: a documentação é versionada como código, revisada por PR e
publicada por CI.

## Princípios

- **Docs-first**: decisões e regras são documentadas **antes** de codar.
- **Fonte única da verdade**: evite duplicar conteúdo; prefira **linkar** entre páginas.
- **Português (pt-BR)**, objetivo e direto. Uma ideia por parágrafo.

## Estrutura e onde escrever

| Tipo de conteúdo | Onde |
|---|---|
| Objetivo, escopo, glossário, roadmap | `docs/visao-geral/` |
| Requisitos, features, casos de uso | `docs/produto/` |
| Visão de arquitetura, stack, diagramas | `docs/arquitetura/` |
| **Decisões técnicas** | `docs/arquitetura/decisoes/` (ADR) |
| Regras de negócio, cálculos | `docs/dominio/` |
| Modelo/dicionário de dados, fontes | `docs/dados/` |
| Detalhes por serviço | `docs/servicos/` |
| Docker, K8s, GitOps, registry | `docs/infraestrutura/` |
| Métricas/logs/traces, SLO, runbooks | `docs/observabilidade/` |
| Testes, CI/CD, segurança | `docs/qualidade/` |
| Legal, privacidade, LGPD, conformidade | `docs/legal/` |

## ADRs (Architecture Decision Records)

Toda decisão relevante (escolha de tecnologia, padrão, trade-off) vira um ADR curto em
`docs/arquitetura/decisoes/NNNN-titulo.md` usando o [template](docs/arquitetura/decisoes/README.md).

- ADRs são **imutáveis** após aceitos; para mudar, crie um novo ADR que **supersede** o anterior.

## Diagramas

- Fonte em `docs/assets/diagramas/*.drawio` (formato [draw.io](https://draw.io)), gerados por
  scripts em `tools/`.
- Ao alterar a arquitetura, **atualize o diagrama** (rode `python tools/gerar_drawio.py`) no mesmo PR.

## Convenções de página

Padrão para manter as páginas navegáveis e consistentes:

- **Título `# H1`** no topo, seguido de **1 parágrafo** dizendo o que a página cobre.
- **Rodapé "Ver também"**: última linha com links para 2–4 páginas relacionadas
  (ex.: `Ver também: [Segurança](...) · [Rede e exposição](...).`).
- **Pasta = tema**: cada pasta tem um `README.md` de entrada (renderiza sozinho ao abrir a pasta no
  GitHub) com uma tabela dos documentos dela. Ao adicionar um doc novo, **linke-o no `README.md` da pasta**.
- **Índice canônico** em [`docs/README.md`](docs/README.md): ao criar um tema novo, adicione-o lá
  (o README apenas aponta para esse índice — não duplique a lista).

## Convenções

- **Documentação em markdown puro** — sem ferramenta de build (ver
  [ADR-0004](docs/arquitetura/decisoes/0004-documentacao-markdown-puro.md)). Escreva de forma que
  renderize bem no GitHub/editor.
- **Commits**: [Conventional Commits](https://www.conventionalcommits.org/) — ex.: `docs: adiciona ADR-0005`.
- **Markdown**: títulos em sentence case, listas curtas, tabelas quando comparar opções.
- **Revisão**: todo PR precisa de 1 review antes do merge.

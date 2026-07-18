# Diagramas

Os diagramas estão em formato [draw.io](https://draw.io) (`.drawio`) e são **gerados por script**
(fonte versionada), garantindo consistência.

## Como abrir
- **Web:** [app.diagrams.net](https://app.diagrams.net) → *File → Open* → selecione o `.drawio`.
- **VS Code / Cursor:** instale a extensão *Draw.io Integration* e abra o arquivo direto no editor.

## Como regenerar
```bash
python tools/gerar_drawio.py       # gera todos os diagramas de uma vez
```

> No **portal de docs** (VitePress), os diagramas abaixo aparecem renderizados em **SVG**
> (exportados no build a partir do `.drawio`). No GitHub/editor, use o link do `.drawio`.

## Arquitetura geral
Camadas do sistema, laterais de **Observabilidade & SRE** e **Qualidade & Testes/CI**, e a faixa
de **Entrega (GitOps)**.

![Arquitetura geral do sistema](/diagramas/arquitetura.svg)

- Arquivo: [`assets/diagramas/arquitetura.drawio`](../assets/diagramas/arquitetura.drawio)

## Fluxo de entrega (CI + GitOps + Kubernetes)
Padrão de **dois repositórios** (app + config), **Argo CD** sincronizando ambientes e o loop de
observabilidade/IA.

![Fluxo de entrega: CI, GitOps e Kubernetes](/diagramas/fluxo-gitops.svg)

- Arquivo: [`assets/diagramas/fluxo-gitops.drawio`](../assets/diagramas/fluxo-gitops.drawio)

## Esquema do banco de dados
Modelo relacional (entidades e relacionamentos). Ver também
[Modelo de dados](../dados/modelo-de-dados.md).

![Esquema do banco de dados](/diagramas/banco-dados.svg)

- Arquivo: [`assets/diagramas/banco-dados.drawio`](../assets/diagramas/banco-dados.drawio)

## Sequência do fluxo ponta a ponta
Da coleta do CSV à consulta no front, passando por ingestão, mensageria, enriquecimento (detalhe) e
recálculo de custo/score. Ver [Visão geral](visao-geral.md) e [Regras de negócio](../dominio/regras-de-negocio.md).

![Sequência do fluxo ponta a ponta](/diagramas/sequencia-fluxo.svg)

- Arquivo: [`assets/diagramas/sequencia-fluxo.drawio`](../assets/diagramas/sequencia-fluxo.drawio)

## Sequência do login (OIDC + refresh)
Login social (Google/GitHub) com Authorization Code + PKCE, **rotação de refresh token** e logout.
Ver [ADR-0013](decisoes/0013-autenticacao-social-oidc.md) e [API Pública](../contratos/api-publica.md).

![Sequência do login social (OIDC + refresh)](/diagramas/sequencia-login.svg)

- Arquivo: [`assets/diagramas/sequencia-login.drawio`](../assets/diagramas/sequencia-login.drawio)

> **Exportar imagem:** no draw.io, *File → Export as → PNG/SVG* para `docs/assets/diagramas/` e
> referencie com `![](...)` se quiser embutir a imagem no markdown.

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

## Arquitetura geral
Camadas do sistema, laterais de **Observabilidade & SRE** e **Qualidade & Testes/CI**, e a faixa
de **Entrega (GitOps)**.

- Arquivo: [`assets/diagramas/arquitetura.drawio`](../assets/diagramas/arquitetura.drawio)

## Fluxo de entrega (CI + GitOps + Kubernetes)
Padrão de **dois repositórios** (app + config), **Argo CD** sincronizando ambientes e o loop de
observabilidade/IA.

- Arquivo: [`assets/diagramas/fluxo-gitops.drawio`](../assets/diagramas/fluxo-gitops.drawio)

## Esquema do banco de dados
Modelo relacional (entidades e relacionamentos). Ver também
[Modelo de dados](../dados/modelo-de-dados.md).

- Arquivo: [`assets/diagramas/banco-dados.drawio`](../assets/diagramas/banco-dados.drawio)

## Sequência do fluxo ponta a ponta
Da coleta do CSV à consulta no front, passando por ingestão, mensageria, enriquecimento (detalhe) e
recálculo de custo/score. Ver [Visão geral](visao-geral.md) e [Regras de negócio](../dominio/regras-de-negocio.md).

- Arquivo: [`assets/diagramas/sequencia-fluxo.drawio`](../assets/diagramas/sequencia-fluxo.drawio)

## Sequência do login (OIDC + refresh)
Login social (Google/GitHub) com Authorization Code + PKCE, **rotação de refresh token** e logout.
Ver [ADR-0013](decisoes/0013-autenticacao-social-oidc.md) e [API Pública](../contratos/api-publica.md).

- Arquivo: [`assets/diagramas/sequencia-login.drawio`](../assets/diagramas/sequencia-login.drawio)

> **Exportar imagem:** no draw.io, *File → Export as → PNG/SVG* para `docs/assets/diagramas/` e
> referencie com `![](...)` se quiser embutir a imagem no markdown.

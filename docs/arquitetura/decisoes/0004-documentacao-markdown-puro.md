# ADR-0004 — Documentação em Markdown puro (sem framework de site)

- **Status:** Aceito
- **Data:** 2026-07-18

## Contexto
Avaliamos usar **MkDocs + Material** para gerar um site de documentação. Porém:

- O objetivo principal é que **pessoas e agentes de IA** entendam o projeto lendo os arquivos —
  algo que **markdown puro** já atende muito bem (renderiza no GitHub/editor, é trivial de parsear).
- O **MkDocs 2.0** é uma reescrita incompatível com o Material for MkDocs; o Material passou a
  exibir aviso e o MkDocs 1.x entra em modo sem manutenção. Isso adiciona ruído e risco de
  ferramenta a um projeto que ainda está em fase de definição.

## Decisão
Manter a documentação em **Markdown puro**, organizada por pastas em `docs/`, **sem ferramenta de
build**. A navegação se dá pelo [README](../../../README.md) (índice) e por **links entre páginas**.

## Consequências
- **+** Zero dependência/tooling; sem o problema do MkDocs 2.0; fácil leitura por humanos e IA.
- **+** Portável: renderiza igual no GitHub, no editor e em qualquer visualizador de markdown.
- **−** Sem busca full-text nem tema navegável de site (aceitável no estágio atual).
- Se no futuro quisermos publicar um site, reavaliar o **[Zensical](https://zensical.org)**
  (sucessor do Material) — nova ADR.

## Alternativas consideradas
- **MkDocs + Material 9.x (pinado)**: funciona, mas agrega tooling e o ruído do MkDocs 2.0.
- **Zensical**: sucessor do Material, porém novo (2026) e ainda amadurecendo — adiado.

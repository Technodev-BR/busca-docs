# Portal de documentação (VitePress) — manutenção

Guia operacional do **portal de docs** gerado com [VitePress](https://vitepress.dev) a partir dos
`.md` de `docs/`. Hoje é publicado no **GitHub Pages** como **paliativo**, até o deploy definitivo
via **k3s/GitOps** (ver [ADR-0011](../arquitetura/decisoes/0011-portal-docs-vitepress.md)).

## Pré-requisitos
- **Node.js 20+** (versão fixada em `.nvmrc`; com `nvm`: `nvm use`).
- Dependências: `npm install` (uma vez).

## Comandos
```bash
npm run docs:dev      # dev com hot-reload  -> http://localhost:5173
npm run docs:build    # gera o site em docs/.vitepress/dist
npm run docs:preview  # pré-visualiza o build de produção
```

## Como as páginas viram o site
- **Fonte única:** os próprios `.md` em `docs/`. O site **renderiza**, não duplica.
- **Página inicial e seções:** todo `README.md` é mapeado para `index` automaticamente
  (via `rewrites` gerado na config), então `/`, `/produto/`, etc. funcionam.
- **Menu lateral:** gerado dinamicamente varrendo as pastas de `docs/`
  (ver `docs/.vitepress/config.mts`). **Criar um `.md` novo já o inclui no menu** — o título vem
  do primeiro `# Título` do arquivo.

## Diagramas (draw.io)
- **Fonte:** `docs/public/diagramas/*.drawio`, gerados por `node tools/gerar_drawio.mjs` (`npm run diagrams`).
- **Imagens:** no deploy (CI), cada `.drawio` é renderizado em **SVG** na mesma pasta.
  Localmente, `npm run docs:*` cria **placeholders** automaticamente
  (`tools/ensure-diagram-svgs.mjs`) — o build nunca quebra por falta de imagem.
- **Links de download:** use âncora com `target="_blank"` para o navegador baixar o `.drawio`
  (evita o roteador SPA capturar o clique). Ex.:
  `<a href="/diagramas/arquivo.drawio" target="_blank" download>arquivo.drawio</a>`.

## Imagens e logos
- Arquivos estáticos ficam em `docs/public/` e são servidos na raiz
  (ex.: `docs/public/logos/x.svg` → `/logos/x.svg`).
- Os logos de ferramentas usam a classe `.logo-grid` / `.logo-card`
  (definida em `docs/.vitepress/theme/custom.css`).

## Publicação (GitHub Pages)
- Workflow: `.github/workflows/docs.yml` (build no push da `main` → **GitHub Pages**).
- No repositório: **Settings → Pages → Source = GitHub Actions**.
- **Domínio:** `docs/public/CNAME` (hoje `docs.technodevbr.com`) e `base: '/'` na config.
  Se voltar a usar a URL `*.github.io/busca-docs/`, troque `base` para `'/busca-docs/'`.

## Checklist ao adicionar/editar conteúdo
1. Criar/editar o `.md` na pasta temática correta.
2. Começar o arquivo com um `# Título` (vira o rótulo no menu).
3. Links **entre páginas** em markdown relativo (`../pasta/arquivo.md`).
4. Rodar `npm run docs:build` localmente — ele **valida os links** e falha se houver link quebrado.

## Futuro (definitivo)
Migrar o deploy do Pages para **k3s + Argo CD** atrás do **Traefik** em `docs.technodevbr.com`
(interno via VPN), conforme [ADR-0011](../arquitetura/decisoes/0011-portal-docs-vitepress.md) e
[Rede e exposição](rede-e-exposicao.md).

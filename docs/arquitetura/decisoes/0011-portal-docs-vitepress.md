# ADR-0011 — Portal de documentação gerado (VitePress)

- **Status:** Parcialmente implementado (paliativo em GitHub Pages)
- **Data:** 2026-07-18

## Contexto
A documentação é **markdown puro**, lida no editor/GitHub ([ADR-0004](0004-documentacao-markdown-puro.md)).
Isso atende bem hoje. No futuro, pode surgir a necessidade de um **portal navegável** (menu lateral,
**busca full-text**, visual próprio) — possivelmente publicado junto com o site do produto. Este ADR
registra **como** faremos isso quando o gatilho chegar, sem implementar agora.

## Decisão (proposta)
Quando houver necessidade, publicar um **portal de docs dedicado** gerado a partir dos **mesmos
`.md`**, seguindo docs-as-code:

- **Gerador: VitePress** (markdown-first, busca local embutida, config mínima, roda em Node — já
  presente no build do frontend). *Docusaurus* só se precisarmos de **versionamento/i18n**.
- **Fonte única**: os arquivos em `docs/` continuam sendo a verdade — o site **renderiza**, não
  duplica (mantém o [ADR-0004](0004-documentacao-markdown-puro.md); este ADR o **complementa**).
- **Mesmo repositório**: a config do site fica ao lado de `docs/`, para o PR atualizar código e
  docs juntos.
- **Portal dedicado, não embutido no app Angular**: evita acoplar o ciclo de vida das docs ao
  produto e permite **controle de acesso próprio**.
- **Publicação**: build no GitHub Actions → imagem Nginx → **GitOps/Argo CD** no **k3s atrás do
  Traefik** em `docs.technodevbr.com`, **interno via VPN** por padrão (coerente com
  [ADR-0006](0006-infra-k3s-vps-cloudflare.md)).
- **Diagramas**: o gerador (`tools/gerar_drawio.mjs`, Node) passa a **exportar `.drawio` → SVG** no build,
  mantendo o `.drawio` como fonte.

## Situação atual (implementado — paliativo)
O portal **já foi implementado com VitePress** e é publicado no **GitHub Pages** como solução
**paliativa**, enquanto o cluster k3s não está pronto:

- **Build/deploy:** GitHub Actions (`.github/workflows/docs.yml`) no push da `main`.
- **Domínio:** `docs.technodevbr.com` (arquivo `docs/public/CNAME`), com `base: '/'`.
- **Diagramas:** `.drawio` renderizados em SVG no CI; placeholders locais automáticos.
- **Operação e how-to:** ver [Portal de documentação](../../infraestrutura/portal-docs.md).

Quando o k3s/GitOps entrar, o **deploy migra** para Nginx + Argo CD atrás do Traefik (mesmo
domínio, interno via VPN), sem mudar a fonte (`docs/`) nem o gerador (VitePress).

## Gatilho (quando implementar)
Só adotar quando houver **necessidade real** — evitar over-engineering:
- leitores externos/stakeholders precisando navegar as docs;
- dor de **busca** no volume atual;
- onboarding em escala.
Até lá: **markdown + preview do editor + GitHub** basta.

## Consequências
- **+** Navegação e busca; visual próprio; mesma fonte `.md` (sem retrabalho).
- **+** Deploy declarativo e acesso controlado (VPN) como o resto da plataforma.
- **−** Mais um artefato de build/deploy para manter.
- **−** Exige exportar diagramas para SVG e cuidar de links relativos no build.

## Alternativas consideradas
- **Docs embutidas no app Angular** (`ngx-markdown`, rota `/docs`): mais "junto com o site", mas
  **acopla** docs ao produto e infla o bundle — reservado para "ajuda in-app" (feature de produto).
- **Docusaurus / Starlight (Astro)**: ótimos; escolher se precisarmos de versionamento/i18n ou de
  mais recursos.
- **MkDocs Material**: bom, mas já migramos para fora dele (atrito com a versão 2.0) — evitar
  reverter sem motivo forte.
- **Não ter site (status quo)**: continua válido enquanto não houver gatilho.

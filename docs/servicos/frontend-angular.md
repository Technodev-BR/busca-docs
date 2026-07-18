# Frontend (Angular)

Angular **standalone components + signals**, organizado por *feature*. Servido em produção via
Nginx (proxy `/api` → backend).

## Estrutura

```
frontend/
  angular.json, package.json
  src/app/
    core/                   # singletons: services HTTP, interceptors, guards
      services/ imovel.service.ts, analise.service.ts
      interceptors/ error.interceptor.ts, credentials.interceptor.ts (withCredentials + CSRF)
    shared/                 # componentes/pipes reutilizáveis (card, moeda-pipe)
    features/
      home/                 # destaques (descontos reais, quedas de preço)
      imoveis-lista/        # busca + filtros
      imovel-detalhe/       # detalhe + fotos + análise + histórico
      mapa/                 # mapa (Leaflet)
      favoritos/            # favoritos
      alertas/              # alertas (filtro salvo + canal)
      auth/                 # login social (Google/GitHub) + /me
    models/                 # interfaces TS (Imovel, AnaliseCusto)
    app.routes.ts, app.config.ts
  src/environments/         # environment.ts / environment.prod.ts (URL da API)
  Dockerfile                # build multi-stage -> nginx
  nginx.conf
```

## Telas (features)
Cada tela é uma *feature* standalone com sua rota. **MVP** marcado; o resto é evolução.

| Tela | Rota | O que mostra / faz | Fase |
|---|---|---|---|
| **Home / destaques** | `/` | Maiores **descontos reais**, novidades e **quedas de preço** recentes; atalhos de busca. | Pós-MVP |
| **Busca / Lista** | `/imoveis` | Filtros (UF, cidade, tipo, modalidade, faixa de preço, **desconto real**, ocupação), ordenação, paginação, toggle **"incluir encerrados"**. Card com foto, preço, desconto real e selo de status. | **MVP** |
| **Mapa** | `/mapa` | Leaflet com busca por **região/raio** (PostGIS), *clusters* e popup-resumo; alterna com a lista. | **MVP** |
| **Detalhe do imóvel** | `/imoveis/:id` | Galeria de fotos; **1ª/2ª praça** com **cronômetro (contagem regressiva)** para cada leilão; **banner de aviso se ocupado**; **mini-mapa** com a localização (Leaflet/PostGIS); **análise de custo** (custo total + desconto real); **riscos** (ocupação/dívidas) e **score**; **painel de análise jurídica/IA** (nua-propriedade, fração, ônus — ver abaixo); links de **edital/matrícula (PDF)**; **gráfico de histórico de preço**; selo **Vendido/Encerrado**; botão **favoritar**. | **MVP** (cronômetro/mapa/aviso) · IA pós-MVP |
| **Favoritos** | `/favoritos` | Imóveis favoritados com selo **Vendido** quando aplicável; remover. | Pós-MVP (auth) |
| **Alertas** | `/alertas` | Criar/gerir alertas (filtro salvo + canal), ativar/desativar. | Pós-MVP (auth) |
| **Login (social)** | `/login` | Botões **Entrar com Google** / **Entrar com GitHub** (redireciona para `/oauth2/authorization/{provedor}`); sessão via cookie HttpOnly. Ver [ADR-0013](../arquitetura/decisoes/0013-autenticacao-social-oidc.md). | Pós-MVP (auth) |
| **Comparador** | `/comparar` | Comparar 2–3 imóveis lado a lado (custo/desconto/score). | Roadmap |

**Padrões de UX (todas as telas):** estados de **loading / vazio / erro** explícitos, layout
**responsivo** (mobile-first), acessibilidade (ARIA/contraste) e **skeletons** no carregamento.
Consome os casos de uso do [Backend](backend-java.md); tipos gerados do
[OpenAPI](../contratos/openapi-ingestao.yaml).

## Libs
- **Angular CLI** + `@angular/router`, `HttpClient`, RxJS + **Signals**.
- UI: **Angular Material** (ou PrimeNG).
- Mapa: **`@bluehalo/ngx-leaflet`** (Leaflet) — combina com o PostGIS.
- Forms reativos para os filtros; `environments` para a URL da API.
- Lint/format: ESLint + Prettier.

## Estilização (SASS/SCSS)
O projeto usa **SASS/SCSS** (`ng new --style=scss`). Organização sugerida:

```
src/styles/
  _tokens.scss      # design tokens: cores, espaçamentos, tipografia (variáveis SASS/CSS)
  _mixins.scss      # mixins/functions reutilizáveis (media queries, etc.)
  _theme.scss       # tema do Angular Material (paleta) baseado nos tokens
  styles.scss       # entrypoint global (importa tokens/mixins/theme)
```

Boas práticas:
- **Design tokens** centralizados em `_tokens.scss` (fonte única de cores/espaços).
- Estilos de componente **encapsulados** (arquivo `.scss` por componente); global só o essencial.
- Reaproveitar **mixins** para responsividade; evitar valores mágicos (usar variáveis).

## Criar o projeto

```bash
npm install -g @angular/cli
ng new frontend --standalone --routing --style=scss
cd frontend
ng add @angular/material
npm i leaflet @bluehalo/ngx-leaflet
```

Rodar:
```bash
ng serve         # http://localhost:4200
ng build         # build de produção em dist/
```

## Convenções
- Uma **feature** por pasta, com seus componentes/rotas.
- Serviços HTTP em `core/services`; tratamento de erro via **interceptor**.
- Tipos compartilhados em `models/` (idealmente gerados a partir do OpenAPI do backend).
- **Auth por cookie (BFF)**: requests com `withCredentials: true` e **token CSRF** nas escritas.
  **Não** guardar token em `localStorage` (proteção contra XSS) — ver [ADR-0013](../arquitetura/decisoes/0013-autenticacao-social-oidc.md).

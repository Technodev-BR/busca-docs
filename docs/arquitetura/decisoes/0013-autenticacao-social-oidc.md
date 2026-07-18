# ADR-0013 — Autenticação social (Google/GitHub) com OIDC e padrão BFF

- **Status:** Aceito
- **Data:** 2026-07-18

## Contexto
Os recursos de engajamento (favoritos, alertas) exigem conta de usuário. Não queremos **gerenciar
senhas** (custo e risco: hashing, reset, vazamento, brute-force). O login deve ser **simples** para
o usuário e **robusto** para o sistema. O front é um SPA Angular e o back é Spring Boot.

## Decisão
Usar **login social via OpenID Connect (OIDC)** com **Google** e **GitHub** como *Identity
Providers* — **sem senha própria**. O backend é o **cliente OAuth2/OIDC** (Spring Security OAuth2
Client) e adota o padrão **BFF (Backend-for-Frontend)**.

**Fluxo (Authorization Code + PKCE):**
1. Front chama `GET /oauth2/authorization/{provedor}` (`google`|`github`) → backend redireciona ao IdP.
2. IdP autentica e retorna ao callback `GET /login/oauth2/code/{provedor}` (com `state` + PKCE).
3. Backend valida, faz **upsert** do `usuario` (por `provedor` + `provedor_id`/`sub`) e emite o
   **par de tokens** (ver abaixo) em **cookies `HttpOnly`**.
4. Front chama `GET /api/v1/auth/me`; renova via `POST /api/v1/auth/refresh`; `POST /api/v1/auth/logout` encerra.

**Estratégia de tokens (access + refresh):**
- **Access token** — **JWT curto** (~15 min), em cookie **`HttpOnly` + `Secure` + `SameSite=Lax`**.
  Não fica em `localStorage`.
- **Refresh token** — **opaco** (aleatório, alta entropia), TTL longo (~7–30 dias), em cookie
  `HttpOnly` **com path restrito** (`/api/v1/auth/refresh`). Guardado **hasheado** (SHA-256) na
  tabela `token_atualizacao` para permitir **revogação**.
- **Rotação com detecção de reúso:** todo `refresh` **invalida** o token usado e emite um novo
  (rotação). Se um refresh **já usado/revogado** for reapresentado → **reúso detectado** → revoga
  **toda a família** de tokens daquele login (possível roubo) e força novo login.
- **`logout`** revoga o refresh atual; **"sair de todos os dispositivos"** revoga todos do usuário.

**Boas práticas adotadas (sistemas robustos):**
- **Sem senha armazenada** — zero `senha_hash`. Elimina toda uma classe de vulnerabilidades.
- **Cookies `HttpOnly`**: tokens **não** ficam acessíveis a JS (evita roubo por **XSS**).
  `Secure`, `SameSite=Lax`, com **CSRF token** (double-submit) para operações de escrita.
- **Authorization Code + PKCE**, `state` (anti-CSRF no fluxo) e `nonce` (anti-replay OIDC).
- **Escopos mínimos**: `openid email profile` (Google) / `read:user user:email` (GitHub).
- **Só e-mail verificado**; **account linking** por e-mail (Google e GitHub → mesma conta).
- **Segredos** (`client_secret`, chave de assinatura do JWT) via Secret, nunca no Git.
- **Rate limiting** no callback e no `refresh`; refresh tokens **expiram** e são **podados**.

## Consequências
- **+** Onboarding em 1 clique; **não** guardamos nem tratamos senhas.
- **+** Superfície de ataque menor (sem reset de senha, sem brute-force de login).
- **+** Cookie `HttpOnly` protege o token contra XSS (melhor que JWT em `localStorage`).
- **−** Dependência de IdPs externos (indisponibilidade do Google/GitHub afeta login).
- **−** Fluxo com cookie exige **CSRF** e cuidado com **CORS**/domínios (front e API no mesmo site
  ajuda: `technodevbr.com` / `api.technodevbr.com`).
- **−** Precisamos cadastrar apps OAuth em Google e GitHub (redirect URIs por ambiente).

## Alternativas consideradas
- **E-mail/senha próprio (JWT):** mais controle, porém assume o **risco de senhas** e mais código
  (hash, reset, verificação) — rejeitado para o MVP.
- **JWT no `localStorage`:** simples no SPA, mas **vulnerável a XSS** — rejeitado em favor de cookie
  `HttpOnly` (BFF).
- **Keycloak / Auth0 (IdP dedicado):** muito robusto e centraliza identidade, mas **pesado** para um
  k3s de nó único no início. Mantido como **evolução** se surgir mais provedores/SSO corporativo.
- **Firebase Auth / Supabase Auth:** rápido, mas acopla a um SaaS e tira a identidade do nosso
  domínio — rejeitado por ora.

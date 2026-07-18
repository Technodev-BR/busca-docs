# Contrato — API Pública (consulta)

API **pública** consumida pelo **frontend (Angular)**. Expõe busca/filtro, detalhe com análise de
custo, histórico e engajamento (favoritos/alertas). Exposta via Traefik/Cloudflare em
`api.technodev.com.br`. Contrato formal (fonte da verdade — API-first):
[`openapi-api.yaml`](openapi-api.yaml).

> Complementa a [API de Ingestão](api-ingestao.md) (interna, coletor→backend). Esta é a de leitura
> para o usuário final.

## Endpoints

| Método | Rota | Caso de uso | Auth |
|---|---|---|---|
| `GET` | `/api/v1/imoveis` | `BuscarImoveisUseCase` (filtros + espacial + paginação) | público |
| `GET` | `/api/v1/imoveis/{id}` | `ObterImovelUseCase` (detalhe + análise + fotos) | público |
| `GET` | `/api/v1/imoveis/{id}/historico` | `ListarHistoricoPrecoUseCase` (tendência) | público |
| `GET`/`POST` | `/api/v1/favoritos` | `ListarFavoritosUseCase` / `FavoritarImovelUseCase` | sessão |
| `DELETE` | `/api/v1/favoritos/{imovelId}` | desfavoritar | sessão |
| `GET`/`POST` | `/api/v1/alertas` | listar / `CriarAlertaUseCase` | sessão |
| `PUT`/`DELETE` | `/api/v1/alertas/{id}` | atualizar / remover | sessão |
| `GET` | `/oauth2/authorization/{provedor}` | inicia **login social** (Google/GitHub) | público |
| `GET` | `/api/v1/auth/me` · `POST /api/v1/auth/logout` | usuário atual / logout | sessão |

## Filtros da busca (`GET /api/v1/imoveis`)
Ligam a **tela de busca** ↔ ao `BuscarImoveisUseCase`:

| Parâmetro | Descrição |
|---|---|
| `uf`, `cidade`, `tipo`, `modalidade` | Filtros categóricos. |
| `precoMin`, `precoMax` | Faixa de preço. |
| `descontoRealMin` | Desconto **real** mínimo (%) — considera o custo total, não o anunciado (RN-05). |
| `ocupacao` | `ocupado | desocupado | desconhecido` (RN-07). |
| `incluirEncerrados` | Inclui `vendido`/`removido` (padrão **false**) — ver [RN-09](../dominio/regras-de-negocio.md#rn-09--ciclo-de-vida-do-imóvel-vendido--removido--reaparecimento). |
| `q` | Busca textual (endereço/bairro/cidade). |
| `lat` + `lng` + `raioKm` | Busca por **raio** (PostGIS). |
| `bbox` | *Bounding box* para o **mapa** (`minLng,minLat,maxLng,maxLat`). |
| `ordenarPor`, `ordem` | `descontoReal|preco|score|dataSegundoLeilao|atualizadoEm` · `asc|desc`. |
| `page`, `size` | Paginação (base 0; `size` ≤ 100). |

## Convenções
- **Versão** no path (`/api/v1`); mudança incompatível → `/api/v2`.
- **Auth**: **login social OIDC** (Google/GitHub); sessão em **cookie HttpOnly** (padrão BFF) +
  **CSRF** nas escritas. Sem senha, sem token no `localStorage`. Ver [ADR-0013](../arquitetura/decisoes/0013-autenticacao-social-oidc.md).
- **Erros**: Problem Details (RFC 7807), `application/problem+json` — igual à API de ingestão.
- **Paginação** no padrão `content/page/size/totalElements/totalPages` (compatível com Spring Data).
- **Tipos do frontend** são **gerados** a partir deste YAML (ver [Frontend](../servicos/frontend-angular.md)).

Ver [Backend (casos de uso)](../servicos/backend-java.md) e [Modelo de dados](../dados/modelo-de-dados.md).

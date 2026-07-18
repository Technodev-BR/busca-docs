# Política de Privacidade

Como o Busca-Busca trata dados pessoais **de seus usuários**, conforme a **LGPD (Lei 13.709/18)**.
Complementa a [visão de LGPD](lgpd.md) (que foca em dados de **terceiros do edital**).

> **Placeholders a preencher antes de publicar:** `[RAZÃO SOCIAL / CONTROLADOR]`, `[CNPJ]`,
> `[ENDEREÇO]`, `[E-MAIL DO DPO/ENCARREGADO]`. Este documento é um **modelo técnico**; revisar com
> apoio jurídico antes de ir a produção.

## 1. Controlador e Encarregado (DPO)
- **Controlador:** `[RAZÃO SOCIAL / CONTROLADOR]`, `[CNPJ]`, `[ENDEREÇO]`.
- **Encarregado (DPO):** `[E-MAIL DO DPO/ENCARREGADO]` — canal para dúvidas e exercício de direitos.

## 2. Dados que tratamos (de usuários)
Só coletamos o necessário para **login social** e **engajamento** (ver
[modelo de dados](../dados/modelo-de-dados.md)):

| Dado | Origem | Tabela | Finalidade |
|---|---|---|---|
| Nome, e-mail, avatar, `provedor`+`provedor_id` | Login social OIDC (Google/GitHub) | `usuario` | Autenticar e identificar a conta |
| Refresh token (hasheado), `user_agent`, `ip` | Sessão | `token_atualizacao` | Segurança da sessão e revogação |
| Imóveis favoritados | Ação do usuário | `favorito` | Salvar favoritos |
| Filtros salvos + canal | Ação do usuário | `alerta` | Enviar alertas/notificações |

- **Sem senha** (login social — [ADR-0013](../arquitetura/decisoes/0013-autenticacao-social-oidc.md)).
- Não coletamos dados sensíveis. Não vendemos dados pessoais.

## 3. Bases legais (art. 7º LGPD)
- **Execução de contrato/serviço** (art. 7º, V): manter conta, favoritos e alertas que o usuário pediu.
- **Legítimo interesse** (art. 7º, IX): segurança, prevenção a fraude e métricas agregadas de uso.
- **Consentimento** (art. 7º, I): envio de notificações/alertas — com **opt-out** a qualquer momento.

## 4. Compartilhamento e operadores
- **Provedores OIDC** (Google/GitHub): autenticação (o usuário se autentica lá).
- **Provedor de e-mail** transacional: envio de notificações ([ADR-0018](../arquitetura/decisoes/0018-notificacoes.md)).
- **Infra (hospedagem/CDN)**: Hostinger/Cloudflare como operadores. Não há transferência para fins
  de marketing de terceiros.

## 5. Retenção e exclusão
| Dado | Retenção |
|---|---|
| Conta (`usuario`) e favoritos/alertas | Enquanto a conta existir |
| `token_atualizacao` | Podados quando expiram/são revogados |
| Logs com `ip`/`user_agent` | Prazo curto (segurança), depois anonimizados/descartados |

- **Exclusão de conta:** o usuário pode solicitar exclusão (ver §6). Fazemos **hard-delete** dos
  dados pessoais (`usuario`, `favorito`, `alerta`, `token_atualizacao`) — **exceção** documentada à
  regra geral de soft-delete ([modelo de dados](../dados/modelo-de-dados.md)), pois é apagamento
  legal. Dados de imóvel **não** são pessoais e permanecem.

## 6. Direitos do titular (art. 18)
Acesso, correção, portabilidade, **exclusão**, revogação de consentimento e informação sobre
compartilhamento. Canais:
- **Autoatendimento:** botão **"Excluir minha conta"** e **"Baixar meus dados"** na área logada
  (fluxo `EncerrarSessaoUseCase` + rotina de purga).
- **DPO:** `[E-MAIL DO DPO/ENCARREGADO]` — resposta em até 15 dias.

## 7. Segurança
Cookies HttpOnly, refresh com rotação, HTTPS ponta a ponta, segredos fora do git — ver
[Segurança](../qualidade/seguranca.md).

## 8. Cookies
Usamos cookies **estritamente necessários** de sessão (`ACCESS_TOKEN`/`REFRESH_TOKEN`, HttpOnly) e
CSRF. Não usamos cookies de rastreamento de terceiros no MVP.

## 9. Alterações
Mudanças materiais serão comunicadas no portal e, quando aplicável, por e-mail.

Ver também: [LGPD (dados de terceiros)](lgpd.md) · [Termos de Uso](termos-de-uso.md).

# ADR-0018 — Notificações (alertas de imóveis)

- **Status:** Aceito
- **Data:** 2026-07-18 · **Aceito em:** 2026-07-18

## Contexto
Os **alertas** (RF-08) e o **ciclo de vida** (RF-13: favorito vendido, queda de preço) precisam
**notificar** o usuário. O modelo prevê `canal_alerta = email | push | webhook`, mas não há provedor,
templates, fila nem autenticação de webhook definidos.

## Decisão
- **Event-driven** via RabbitMQ (ADR-0005): os casos de uso publicam eventos `notificacao.*`
  (ex.: `notificacao.favorito_vendido`, `notificacao.queda_preco`, `notificacao.alerta_match`);
  um **worker de notificação** consome, renderiza o template e envia. **DLQ** para falhas.
- **Escopo do MVP = somente e-mail**, via provedor SMTP transacional (ex.: Amazon SES / Resend /
  Postmark) — configurável por env/secret. `push` e `webhook` ficam como evolução.
- **Idempotência**: chave por (`usuario_id`, `evento`, `imovel_id`, janela) evita duplicar envio.
- **Templates** versionados (assunto + corpo) com dados mínimos; link de **descadastro**.
- **Webhook (evolução)**: assinatura **HMAC** no header + retries com backoff; segredo por alerta.
- **Preferências/retenção**: registrar consentimento e permitir opt-out (LGPD — ver
  [política de privacidade](../../legal/politica-de-privacidade.md)).

## Arquitetura, robustez e escala
- **Transactional Outbox:** o caso de uso grava o evento numa tabela `outbox` **na mesma transação**
  da mudança de estado; um relay publica no RabbitMQ. Garante **at-least-once** sem perder evento
  em caso de crash (evita "publiquei mas não commitei", e vice-versa).
- **Idempotência de envio:** chave `(usuario_id, tipo_evento, imovel_id, janela)` numa tabela
  `notificacao_enviada`; consumidor **at-least-once** + dedup ⇒ efeito **exactly-once** percebido.
- **Provedor plugável:** `NotificacaoPort` com adapter SMTP/transacional (SES/Resend/Postmark) por
  env; trocar provedor sem tocar no domínio.
- **Deliverability:** configurar **SPF, DKIM e DMARC**; tratar **bounces/complaints** (webhook do
  provedor) para suprimir endereços inválidos e proteger a reputação do domínio.
- **Cadência anti-spam:** agrupar em **digest** quando houver muitos matches; limite por usuário/dia;
  respeitar preferências e **opt-out** (token de descadastro **assinado**).
- **Retry/DLQ:** backoff exponencial; após N tentativas → **DLQ** + alerta; falha de provedor não
  bloqueia a fila (circuit breaker por provedor).
- **Escala:** workers de notificação **horizontalmente escaláveis** (consumo concorrente idempotente);
  templates versionados e renderizados fora do publisher.
- **Webhook (evolução):** entrega assinada por **HMAC** (header + timestamp anti-replay), timeout
  curto, retries com backoff e desativação automática de endpoints que falham cronicamente.
- **Observabilidade:** enviados/entregues/bounce/complaint, latência de entrega, tamanho da DLQ,
  taxa de opt-out (ver [pilares](../../observabilidade/pilares.md)).

## Consequências
- **+** Desacoplado e resiliente (fila + DLQ + idempotência); MVP simples (só e-mail).
- **+** Fácil adicionar canais depois sem mexer nos publishers.
- **−** Dependência de provedor de e-mail (deliverability, SPF/DKIM/DMARC a configurar).
- **−** Mais um worker e um contrato de eventos a manter (ver contrato de eventos de notificação).

## Alternativas consideradas
- **Envio síncrono no request**: acopla e trava a API; sem retry — rejeitado.
- **Só push/web**: exige base logada e service worker; menor alcance no MVP — adiado.

## Referências
- [ADR-0005](0005-mensageria-rabbitmq.md) · [Eventos RabbitMQ](../../contratos/eventos-rabbitmq.md)
  · [Regras de negócio (RN-09)](../../dominio/regras-de-negocio.md)

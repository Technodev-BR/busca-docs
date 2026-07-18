# Backup & Disaster Recovery

Como recuperar o sistema após falhas. **Contexto importante:** produção roda em **k3s de nó único**
numa VPS (ver [ADR-0006](../arquitetura/decisoes/0006-infra-k3s-vps-cloudflare.md)) — **não há alta
disponibilidade**, então backup e um plano de restore são essenciais.

## O que é crítico (e o que não é)
| Ativo | Criticidade | Estratégia |
|---|---|---|
| **PostgreSQL** (dados dos imóveis, histórico, análises) | **Alta** | **Backup em camadas**: snapshot da VPS + VolumeSnapshot diário (k3s) + WAL/base backup off-site (ver abaixo) |
| **Object storage** (fotos/editais) | Média | Reconstituível pela coleta; backup se caro de recoletar |
| **Configuração do cluster** (manifests/Helm) | Alta | Já no **repo GitOps** (Argo CD re-aplica) |
| **Segredos** | Alta | Sealed Secrets no Git (cifrado) / cofre External Secrets |
| **Redis (cache)** | Baixa | **Descartável** — reidrata a partir do Postgres |
| **RabbitMQ** | Baixa/Média | Filas transitórias; reprocessar do `coleta_bruta` |

> **Regra:** só o **Postgres** guarda estado insubstituível. O resto é reconstruível (GitOps +
> recoleta + reprocessamento do `coleta_bruta`).

## Retenção de dados (o que fazer crescer e o que podar)
Nem todo dado do Postgres deve viver para sempre — ver [ADR-0012](../arquitetura/decisoes/0012-retencao-dados-historico.md).

| Dado | Retenção | Racional |
|---|---|---|
| `historico_preco` | **Longa/indefinida** | Pequeno (só preço/desconto/status na mudança) e é parte do produto (tendência, alertas, auditoria de venda). |
| `imovel` / `imovel_detalhe` / `analise_custo` | Longa | Estado atual + soft delete; não cresce sem limite. |
| **`coleta_bruta`** | **~90 dias** em banco → descartar ou **arquivar frio** (object storage) | É o que mais **pesa** (HTML cru comprimido). Reprocesso raramente precisa de algo tão antigo. |
| **Object storage** (fotos/PDFs) | Longa; poda de órfãos | Reconstituível pela coleta; remover ativos de imóveis excluídos há muito tempo. |

- **Purga do `coleta_bruta`** por `CronJob` (exemplo):

```sql
DELETE FROM coleta_bruta WHERE coletado_em < now() - interval '90 days';
```

- O payload já é **comprimido (zstd) em `bytea`** na origem (não base64) — reduz drasticamente o
  storage do HTML bruto (ver [Modelo de dados](../dados/modelo-de-dados.md)).

## Objetivos (metas)
- **RPO** (perda máxima aceitável): ~24h no início (a coleta roda ~1x/dia); ideal chegar a ≤1h.
- **RTO** (tempo para voltar): algumas horas (recriar VPS + k3s + Argo sync + restore do banco).

## Backup do PostgreSQL — camadas
Usamos **defesa em profundidade**: cada camada cobre a falha da outra.

| Camada | O quê | Frequência | Cobre | Limite |
|---|---|---|---|---|
| **1. Snapshot da VPS** (Hostinger) | Imagem da **máquina inteira** | Conforme plano | Perda total da VPS; restore rápido | Granularidade grossa; não é *consistente com o banco* |
| **2. VolumeSnapshot no k3s** (via CloudNativePG) | Snapshot do **PVC do Postgres** | **Diário** | Corrupção/perda do **volume**; restore rápido no cluster | Fica **na mesma VPS** — não substitui off-site |
| **3. Base backup + WAL** (CloudNativePG → S3) | Backup lógico/físico **off-site** + WAL archiving | Contínuo (WAL) + diário | Perda da VPS **e** *point-in-time recovery* | Restore um pouco mais lento |

> **Por que CloudNativePG:** ele orquestra tanto o **VolumeSnapshot** (camada 2, nativo via CSI)
> quanto **base backup + WAL archiving** (camada 3, PITR) de forma **consistente com o Postgres**
> (fsync/checkpoint corretos) — um snapshot "cru" da VPS sozinho não garante isso.

### Pré-requisito de storage (importante)
O **`local-path`** padrão do k3s **não suporta VolumeSnapshot**. Para a camada 2 é preciso um
**CSI com suporte a snapshot** — recomendado **Longhorn** no nó único — mais o
**external-snapshotter** (CRDs `VolumeSnapshot*`) e uma **`VolumeSnapshotClass`**. Só então o
CloudNativePG consegue tirar o snapshot diário do volume. Ver [Kubernetes & GitOps](kubernetes-gitops.md).

### Off-site (camada 3)
- **Base backups** agendados + **WAL archiving** (permite *point-in-time recovery*).
- Guardar **off-site** (não na mesma VPS): bucket S3/R2/Backblaze.
- Reter, por ex., 7 backups diários + 4 semanais.
- Longhorn também pode enviar seus **backups** (não só snapshots locais) a um bucket S3 — reforça a
  camada 2 tornando-a off-site.

Alternativa simples (sem operador): `pg_dump` agendado por CronJob enviando o dump cifrado ao bucket.

```bash
# dump lógico (exemplo de CronJob)
pg_dump --format=custom "$DB_URL" | gzip | \
  aws s3 cp - "s3://backups/buscabusca/$(date +%F).dump.gz"
```

## Notificações de backup (Slack)
Backup **não pode ficar no escuro**. Duas notificações complementares (ver
[Observabilidade](../observabilidade/pilares.md)):

**1. Falha → alerta imediato (Alertmanager → Slack).** É o que realmente importa. O CloudNativePG
expõe métricas de backup ao Prometheus; alertamos por **sintoma**, ex.: sem backup íntegro há > 24h
ou último backup em estado `failed`.

```yaml
# regra Prometheus (exemplo)
- alert: BackupPostgresAtrasado
  expr: time() - cnpg_collector_last_available_backup_timestamp > 24*3600
  for: 30m
  labels: { severity: critical }
  annotations:
    summary: "Backup do Postgres sem sucesso há mais de 24h"
```

O **receiver Slack** do Alertmanager entrega no canal (ex.: `#buscabusca-ops`).

**2. Resumo positivo em horários fixos (digest → Slack).** Dá confiança de que rodou. Um `CronJob`
posta o status no Slack via **Incoming Webhook** nos "momentos do dia" desejados (ex.: **08:00 e
20:00** — `schedule: "0 8,20 * * *"`, `timeZone: America/Sao_Paulo`).

```bash
# CronJob: confere o último backup e avisa no Slack
STATUS=$(kubectl get backup -n db -o jsonpath='{.items[-1:].status.phase}')
QUANDO=$(kubectl get backup -n db -o jsonpath='{.items[-1:].metadata.creationTimestamp}')
curl -sf -X POST "$SLACK_WEBHOOK_URL" -H 'Content-type: application/json' \
  --data "{\"text\":\":floppy_disk: Backup Busca-Busca — status *$STATUS* ($QUANDO)\"}"
```

> **Segredo:** a `SLACK_WEBHOOK_URL` é sensível → guardar como **Secret** (Sealed/External Secrets),
> nunca em claro no Git. Ver [Configuração & segredos](configuracao-e-segredos.md).
> O **Longhorn** também dispara notificação/registro ao concluir seus *recurring backups*, reforçando
> a camada 2.

## Restore do PostgreSQL
Escolha a camada conforme o cenário (mais rápido → mais preciso):

1. **VolumeSnapshot (camada 2):** recriar o cluster CloudNativePG a partir do **snapshot diário** do
   PVC — restore rápido para corrupção/perda de volume no mesmo cluster.
2. **Base backup + WAL (camada 3):** restaurar o último base backup e aplicar WAL até o ponto
   desejado (**PITR**), **ou** `pg_restore` do dump lógico — usado quando a VPS foi perdida.
3. Rodar migrations pendentes (Flyway valida no start do backend).
4. **Reaquecer** o cache Redis naturalmente (primeiras buscas repovoam).

```bash
gunzip -c latest.dump.gz | pg_restore --clean --if-exists -d "$DB_URL"
```

## Recuperação total da VPS (a VPS caiu)
1. **Provisionar nova VPS** na Hostinger.
2. Instalar **k3s** (`--disable traefik`, ver [Kubernetes & GitOps](kubernetes-gitops.md)).
3. Instalar **Argo CD** e apontar para o **repo GitOps** → ele reaplica todo o estado (Traefik,
   cert-manager, apps).
4. Restaurar o **Postgres** (seção acima).
5. Ajustar **DNS na Cloudflare** para o novo IP (ver [Rede e exposição](rede-e-exposicao.md)).
6. Validar TLS (cert-manager reemite via DNS-01) e *smoke test* das rotas.

> Como config e segredos (cifrados) estão no GitOps, a recuperação é majoritariamente
> **declarativa** — o ponto manual crítico é o **restore do banco** e o **DNS**.

## Testar o plano
- **Restore de teste** periódico (mensal): restaurar o backup num ambiente isolado e validar.
- Um backup **nunca testado** não é um backup confiável.

## Evolução (reduzir o risco de nó único)
- Segundo nó / cluster multi-nó para HA quando o projeto justificar.
- Postgres **gerenciado** externo (tira o estado crítico da VPS).

Ver também: [Configuração & segredos](configuracao-e-segredos.md) ·
[Kubernetes & GitOps](kubernetes-gitops.md) · [Runbooks](../observabilidade/runbooks.md).

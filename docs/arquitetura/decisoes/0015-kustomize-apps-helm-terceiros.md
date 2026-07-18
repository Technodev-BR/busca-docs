# ADR-0015 — Kustomize para serviços próprios, Helm para terceiros

- **Status:** Aceito
- **Data:** 2026-07-18

## Contexto
Precisamos empacotar/parametrizar os manifests Kubernetes para o deploy via GitOps (Argo CD) no
k3s ([ADR-0006](0006-infra-k3s-vps-cloudflare.md), [ADR-0003](0003-dois-repositorios-gitops.md)).
Há duas famílias de workloads:

- **Serviços próprios**: `backend` (Java), `collector` (Python), `frontend` (Angular) — manifests
  simples (Deployment, Service, ConfigMap, HPA, Ingress/IngressRoute) que **nós** controlamos.
- **Componentes de terceiros**: Traefik, cert-manager, RabbitMQ, operadores de Postgres/Redis,
  stack de observabilidade (Prometheus/Grafana/Loki), Sealed/External Secrets, etc. — softwares de
  fornecedores, com muitas opções de configuração.

A versão anterior da doc previa "um **Helm chart por serviço**". Para manifests próprios e simples,
Helm adiciona **indireção** (templates, `values.yaml`, `_helpers.tpl`) sem ganho real.

## Decisão
Usar a ferramenta certa para cada caso:

- **Kustomize** para os **serviços próprios**: `deploy/k8s/base/` (manifests planos e legíveis) +
  `overlays/{dev,staging,prod}` (patches por ambiente: réplicas, recursos, host, imagem). A **tag da
  imagem** é atualizada pelo CI no overlay (via `images:` do Kustomize) — sem `kubectl apply`.
- **Helm** para **componentes de terceiros**: consumir os **charts oficiais** da comunidade,
  fixando versão e mantendo nossos `values` versionados no repo GitOps (`infra/`).
- **Argo CD** suporta ambos nativamente (uma `Application` aponta para um chart Helm **ou** para um
  diretório Kustomize), então o padrão **app-of-apps** convive com as duas abordagens.

## Consequências
- **+** Manifests próprios simples, explícitos e fáceis de revisar (diff limpo no PR).
- **+** Sem manter templates Helm caseiros; menos boilerplate e menos armadilhas de renderização.
- **+** Reaproveita o ecossistema maduro de charts para software de terceiros (upgrades e valores
  bem documentados).
- **+** Bump de imagem trivial e seguro via `kustomize edit set image` no CI.
- **−** Dois mecanismos no repositório (Kustomize + Helm) — mitigado por serem de domínios distintos
  (nossas apps vs. terceiros) e ambos suportados pelo Argo CD.
- **−** Kustomize tem parametrização mais limitada que Helm; aceitável para manifests próprios.

## Alternativas consideradas
- **Helm para tudo (inclusive apps próprias):** overhead de templates para manifests simples; padrão
  anterior, agora revisado.
- **Kustomize para tudo (inclusive terceiros):** exigiria manter/gerar bases de software de
  terceiros à mão, perdendo o valor dos charts oficiais.
- **Jsonnet/cdk8s:** poder maior, porém curva de aprendizado e complexidade desnecessárias para o
  tamanho atual do projeto.

## Referências
- [Kubernetes & GitOps](../../infraestrutura/kubernetes-gitops.md) · [Repositórios](../../infraestrutura/repositorios.md)

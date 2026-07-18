# Glossário

Linguagem ubíqua do projeto — usada igual no código, na documentação e nas conversas.

| Termo | Definição |
|---|---|
| **Imóvel** | Unidade à venda em leilão/venda direta, identificada pelo **N° do imóvel** (Caixa). |
| **Modalidade de venda** | Como o imóvel é vendido (ex.: *Leilão SFI*, *Venda Direta*, *Licitação Aberta*). |
| **Valor de avaliação** | Valor de referência do imóvel informado pela Caixa. |
| **Preço / Valor mínimo** | Valor mínimo de lance / preço de venda anunciado. |
| **Desconto (anunciado)** | Diferença percentual entre avaliação e preço, conforme a fonte. |
| **Desconto real** | Desconto recalculado considerando o **custo total** de aquisição. |
| **ITBI** | Imposto de Transmissão de Bens Imóveis; alíquota varia por **município**. |
| **Custas** | Comissão do leiloeiro e taxas do processo de venda. |
| **Custo total** | Lance + ITBI + custas + registro + dívidas + reforma estimada. |
| **Pré-análise** | Score de viabilidade (desconto, liquidez, riscos) — apoio à decisão. |
| **Edital** | Documento oficial com regras e riscos do imóvel (ocupação, dívidas). |
| **Coletor (collector)** | Serviço Python que baixa e processa os dados da fonte. |
| **API de ingestão** | Endpoint interno do backend que recebe os dados do coletor. |
| **Enriquecimento (detalhe)** | Raspar a **página de detalhe** do imóvel (1ª/2ª praça, datas, edital, dívidas, ocupação, fotos, PDFs) e persistir em `imovel_detalhe`/`imovel_foto`. É o sentido principal no projeto — ver [ADR-0010](../arquitetura/decisoes/0010-enriquecimento-detalhe.md). |
| **Geocoding** | Resolver a `localizacao` (Point) do imóvel a partir de endereço/CEP (não confundir com enriquecimento de detalhe). |
| **Valor de mercado** | Estimativa de referência de preço (feature futura); não faz parte do enriquecimento de detalhe. |
| **ADR** | *Architecture Decision Record* — registro de uma decisão técnica. |
| **GitOps** | Operar o cluster a partir de um repositório Git como fonte da verdade. |
| **SLO / SLI** | Meta de confiabilidade / indicador que a mede. |
| **AIOps** | Uso de IA para apoiar operação/diagnóstico de incidentes. |
| **MCP** | *Model Context Protocol* — padrão de acesso a ferramentas/dados por um agente de IA. |

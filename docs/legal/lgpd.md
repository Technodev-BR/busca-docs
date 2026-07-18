# Legal & LGPD

Aspectos legais e de privacidade da coleta e do uso dos dados.

## Fonte oficial (preferência)
- Usar a **lista oficial em CSV** publicada pela Caixa é o canal **legítimo e mais estável**.
  Reduz risco jurídico e de bloqueio e diminui a carga no site. Ver
  [ADR-0002](../arquitetura/decisoes/0002-fonte-oficial-csv-caixa.md) e
  [Fonte Caixa (CSV)](../dados/fonte-caixa-csv.md).

## LGPD (Lei 13.709/18)
- A Caixa cita a LGPD nas regras da venda online. Os **dados dos imóveis** são públicos
  (transparência do processo).
- **Não coletar nem armazenar dados pessoais** de terceiros (nomes de arrematantes, propostas
  etc.). Nosso escopo é **só o imóvel**.
- **Situação do antigo comprador/proprietário: NÃO tratamos.** Editais e matrículas citam nomes de
  pessoas (proprietários, devedores, ex-arrematantes). **Não** fazemos perfil nem análise da
  situação pessoal deles — extraímos apenas **fatos jurídicos do imóvel** (penhora, usufruto,
  fração, ônus), **redigindo/omitindo** nomes e identificadores antes de persistir. Ver
  [Análise jurídica com IA](../dominio/analise-juridica-ia.md) e
  [ADR-0014](../arquitetura/decisoes/0014-analise-juridica-ia.md).
- **Sem PII** em logs, telemetria e prompts de IA (ver [AIOps](../observabilidade/aiops-mcp.md)).

## Termos de uso
- Revisar os **termos** no rodapé do portal e as **"Regras da venda online"**
  (`.../editais/regras-VOL/comocomprar.pdf`) antes de publicar o serviço.

## Scraping educado (página de detalhe)
Usamos a página de detalhe para **enriquecer todos os imóveis** (ver
[ADR-0010](../arquitetura/decisoes/0010-enriquecimento-detalhe.md)) — como o volume é alto, o
cuidado com o ritmo é **essencial**:

- *User-agent* identificável, **poucos acessos por minuto** (rate limiter global), **cache** local
  para não repetir requisições, **backoff** em erros, e **nada de burlar proteções**.
- Enriquecimento é **lento por design** (fila paced) — nunca "martelar" o site em rajada.
- **Sem robots.txt convencional** no domínio → na dúvida, ser **conservador** no ritmo de acesso.
- Baixar **fotos/PDFs** uma vez e guardar (object storage), evitando re-download.

## Atribuição
- Deixar claro que os dados são de **fonte pública da Caixa** e **linkar de volta** para a página
  oficial de cada imóvel.

## Disclaimer de produto
- A **pré-análise** e o **cálculo de custos** são **estimativas de triagem**, não recomendação de
  investimento nem assessoria jurídica. O usuário deve conferir o **edital** e os órgãos locais.

Ver também: [Regras de negócio](../dominio/regras-de-negocio.md) · [Segurança](../qualidade/seguranca.md).

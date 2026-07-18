# Análise jurídica de investimento com IA

Uma camada de **produto** que lê o **edital** e a **matrícula** (mais o detalhe já coletado) e
extrai, de forma estruturada, os **fatos jurídicos do imóvel** que mais impactam a decisão de
investir — indicando os **melhores negócios** e os **riscos**.

> **Não é assessoria jurídica.** É triagem/estimativa. O usuário deve conferir o edital e um
> advogado. Ver [Disclaimer](../legal/lgpd.md) e [Pré-análise](pre-analise-viabilidade.md).

## O que a IA tenta identificar
Sinais **do imóvel** (nunca perfil de pessoas — ver LGPD abaixo):

| Fato jurídico | Por que importa |
|---|---|
| **Nua-propriedade vs. propriedade plena** | Se só a **nua-propriedade** está à venda, há **usufruto** de terceiro → uso/renda limitados; preço deve refletir. |
| **Usufruto / uso / habitação** | Direito real de terceiro sobre o bem; afeta posse e liquidez. |
| **Fração ideal / co-propriedade** | Venda de **percentual** (ex.: 50%) e não do imóvel inteiro → condomínio, direito de preferência. |
| **Direito de superfície / servidão** | Ônus que limita o uso do solo. |
| **Ônus e gravames** | **Penhora**, **hipoteca**, **alienação fiduciária**, **indisponibilidade**, arresto — podem exigir baixa/regularização. |
| **Ocupação** e responsabilidade de **desocupação** | Custo/tempo/risco (por conta do comprador?). |
| **Dívidas** (IPTU, condomínio) e de quem é a responsabilidade | Entram no **custo total**. |
| **Direito de preferência** (locatário, condômino) | Pode preterir o arrematante. |
| **Modalidade/estágio** (1ª/2ª praça, venda direta, licitação) | Muda regras e base de cálculo. |
| **Ação/processo e foro** | Complexidade e prazo. |

Saída **estruturada** (JSON) + **parecer** em linguagem natural com **nível de confiança** e
**citação dos trechos** que embasaram cada flag (grounding — nada de "achismo").

## Como alimenta o produto
- Vira **flags/riscos** na [pré-análise](pre-analise-viabilidade.md) e ajusta o **score** (ex.:
  nua-propriedade e ônus penalizam; propriedade plena e desocupado favorecem).
- Aparece no **painel de análise jurídica** da tela de detalhe (com os trechos citados).
- Ajuda a **rankear os melhores negócios** (alto desconto real **e** baixo risco jurídico).

## Guarda-corpos (obrigatórios)
- **Grounding + citação**: toda afirmação aponta o trecho do edital/matrícula. Sem fonte → marcar
  como "não identificado", não inventar.
- **Confiança explícita**: PDFs variam; quando o parser/IA não tem certeza, **baixa confiança** e
  sinaliza "conferir manualmente".
- **Human-in-the-loop** para casos de alto valor/alto risco.
- **Disclaimer** de que não é parecer jurídico.

## LGPD — dados de terceiros (importante)
Editais e matrículas contêm **nomes de pessoas** (proprietários, devedores, ex-arrematantes). Por
[política de LGPD (RN-08)](regras-de-negocio.md), **não** fazemos perfil nem análise da
**situação pessoal do antigo comprador/proprietário**:

- Extraímos apenas **fatos jurídicos do imóvel** (existência de penhora, usufruto, fração etc.),
  **não** dados pessoais de indivíduos.
- **Redigir/omitir** nomes e identificadores pessoais antes de persistir; **não** enviar PII em
  prompts que sejam registrados; **não** armazenar perfis de pessoas.
- Ver [Legal & LGPD](../legal/lgpd.md) e [ADR-0014](../arquitetura/decisoes/0014-analise-juridica-ia.md).

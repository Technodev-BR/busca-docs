# Parâmetros de custo (dados reais, fontes e versionamento)

Valores que o [motor de custos](../dominio/calculo-de-custos.md) usa para estimar ITBI, custas,
registro e reforma. Ficam nas tabelas `aliquota_itbi` e `parametro_custo`
([modelo de dados](modelo-de-dados.md#parâmetros-de-custo-versionados)), **versionados por
vigência**. O `analise_custo` guarda a `parametro_custo_versao` usada — cálculo **auditável e
reprodutível**.

> **Base real, não valores inventados.** Os números abaixo vêm de fontes oficiais/de mercado (§6),
> verificadas em 2026. Ainda assim, ITBI e emolumentos **mudam por lei local**: o valor final exige
> conferência no edital e nos órgãos do município/estado. O cálculo é **estimativa de triagem**.

> **Validação com dados reais (2026-07).** O spike `tools/validacao/validar_parametros.py` rodou
> sobre o **CSV oficial de SP** (3.607 imóveis) aplicando estes parâmetros: o desconto **anunciado**
> (mediana 38,8%) cai para um desconto **real** (mediana **32,7%**, p90 ≈ 40%) depois de ITBI +
> comissão de 5% + registro — **erosão de ~6 p.p.** na mediana, e só ~5% dos imóveis mantêm desconto
> real ≥ 40%. Confirma a tese do produto e calibrou o teto do score (ver
> [score-v0-spec §8](../dominio/score-v0-spec.md)).

## 1. ITBI (`aliquota_itbi`)

Resolução: **município específico → default da UF → default nacional**. Base de cálculo = **maior
valor entre o arremate e o valor venal de referência** do município (STJ, Tema 1.113).

| Município | Alíquota | Observação |
|---|---|---|
| São Paulo/SP | **3,0%** | SFH: 0,5% sobre a parcela financiada até R$ 120.968 (imóveis até R$ 725.808); 3% no excedente |
| Rio de Janeiro/RJ | **3,0%** | SFH: 0,5% sobre a parte financiada (1º imóvel residencial) |
| Belo Horizonte/MG | **3,0%** | isenção residencial até ~R$ 74,6 mil; redução 50% em faixa intermediária |
| Porto Alegre/RS | **3,0%** | — |
| Salvador/BA | **3,0%** | — |
| Recife/PE | **3,0%** | — |
| Curitiba/PR | **2,7%** | progressiva por faixa; ~2,7% residencial médio |
| Campinas/SP | **2,5%** | — |
| Vitória/ES | **2,0%** | — |
| **Default nacional (fallback)** | **2,0%** | maioria dos municípios menores usa 2% |

- **Fortaleza/CE, Brasília/DF, Manaus/AM, Florianópolis/SC**: fontes divergem (2% a 3%) → **não
  semear com valor fixo**; buscar na prefeitura antes de usar; enquanto isso, cai no default da UF.
- **MCMV**: isenção total em muitos municípios (tratar quando houver a flag).
- Seed inicial: capitais confirmadas acima + maiores municípios por volume no CSV; o resto herda o
  default nacional até ser conferido.

## 2. Custas / comissão de leiloeiro (`parametro_custo`, `chave=custas_pct`)

**Fonte primária: editais oficiais da Caixa** (item "COMISSÃO" e cláusula de pagamentos no ato).

| Modalidade | % sobre a proposta/lance | Observação |
|---|---|---|
| **Leilão (1º/2º) e Licitação Aberta** | **5,0%** | Paga **pelo arrematante ao leiloeiro**, no ato; **NÃO compõe o lance** (é custo adicional). |
| **Venda Online / Compra Direta** | **0%** | Sem comissão de leiloeiro — a corretagem é **paga pela Caixa** (não pelo comprador). |

> Regra de negócio: a comissão entra no **custo total** do comprador nas modalidades de leilão, mas
> **não** deve ser somada nas vendas diretas/online. Ver [RN-04](../dominio/regras-de-negocio.md).

## 3. Registro em cartório (`parametro_custo`, `chave=registro_faixa`)

**Não existe tabela nacional.** Emolumentos são fixados por **lei estadual** (Lei 10.169/2000) e
reajustados anualmente por cada **Tribunal de Justiça**, cobrados por **faixa de valor do imóvel**
(valor fixo + adicional). Diferença entre estados pode chegar a ~30% para o mesmo ato.

- **Seed por UF a partir da tabela oficial do TJ** (ex.: GO — Provimento CGJ nº 179/2025; MG — Lei
  15.424/2004; SP — tabela via UFESP). Fontes agregadas na ANOREG/BR (§6).
- **Referência de ordem de grandeza** para triagem (não substitui a tabela do TJ): registro de um
  imóvel na faixa de **R$ 200–400 mil** custa aproximadamente **R$ 1.500 a R$ 3.500** (varia por UF).
- Sobre os emolumentos pode incidir **ISSQN municipal** (3%–5%) e taxas estaduais (ex.: FUNREJUS/RS,
  fundos do TJ) — incluir quando a tabela do estado previr.

## 4. Reforma (`parametro_custo`, `chave=reforma_m2`)

R$/m² sobre `area_privativa`/`area_construida`. Só aplica quando há área no detalhe; senão a
estimativa fica **indisponível** (não inventar — ver [cálculo de custos](../dominio/calculo-de-custos.md)).
Base: **SINAPI (Caixa/IBGE)** + pesquisa de mercado 2026. O **CUB não** serve para reforma (é obra
nova); reforma custa 30%–40% a mais por m² por causa de demolição/logística.

| Padrão (default por tipo) | R$/m² | Escopo |
|---|---|---|
| Simples (default **Apartamento/Comercial**) | **R$ 800/m²** | pintura, reparos, troca pontual de acabamentos |
| Médio (default **Casa**) | **R$ 1.300/m²** | pisos, revestimentos, parte elétrica/hidráulica |
| Completo (opcional pelo usuário) | **R$ 2.500/m²** | demolição, infraestrutura nova, acabamentos |
| Terreno | R$ 0 (n/a) | — |

- **Ajuste regional**: Sul/Sudeste tendem a **+15% a +20%** sobre a média nacional (aplicar por UF).
- **Contingência recomendada**: +15% a 20% sobre a estimativa (imprevistos de reforma).
- Default do motor = **padrão simples/médio** (conservador para triagem); o usuário pode escolher o
  padrão.

## 5. Versionamento e administração

- Toda alteração cria um **novo registro** com `vigencia_inicio` (não sobrescreve) → histórico.
- O cálculo usa a versão **vigente na data do cálculo** e grava `parametro_custo_versao`.
- Cada parâmetro guarda a **`fonte`** (URL/lei) usada.
- Manutenção via **seed/migration** (Flyway) no MVP; endpoint admin
  (`/api/v1/admin/parametros-custo`) com RBAC fica como evolução.

## 6. Fonte da verdade (onde consultar por estado/município)

**Não existe um cadastro único nacional** que devolva todos esses custos por estado. A autoridade é
**fragmentada por competência** — cada custo tem sua fonte oficial. Para o projeto, gravar sempre a
`fonte` (URL/lei) usada em cada registro dos parâmetros.

| Custo | Competência / fonte da verdade | Onde consultar (oficial) |
|---|---|---|
| **Comissão de leiloeiro (5%)** | **O edital do imóvel** (Caixa) — é a fonte **per-imóvel** | Cada edital PDF em `venda-imoveis.caixa.gov.br/editais/` (cláusula "COMISSÃO" / "DOS PAGAMENTOS NO ATO"); o coletor já baixa o edital. Regras gerais: `caixa.gov.br/voce/habitacao/imoveis-venda` |
| **Registro (emolumentos)** | **Estadual** — lei estadual + **TJ/Corregedoria** (Lei federal 10.169/2000) | Agregador dos 27 estados: **ANOREG/BR** (`anoreg.org.br/site/tabela-de-emolumentos`); calculadora nacional dos cartórios: `registrodeimoveis.org.br`; **ONR** (`onr.org.br`, Lei 13.465/2017); simulador do TJ (ex.: RJ — `portaltj.tjrj.jus.br/web/cgj/servicos/custas/custas-extrajudiciais`) |
| **ITBI** | **Municipal** — lei municipal | Portal/simulador de **cada prefeitura** (não há cadastro nacional); base de cálculo: STJ **Tema 1.113** (REsp 1.937.821) |
| **Reforma (R$/m²)** | Referência técnica de mercado | **SINAPI** (Caixa/IBGE) para insumos/mão de obra; **CUB** (SindusCon) só para obra nova, não reforma |

> **Estratégia recomendada para o projeto:**
> - **Comissão**: idealmente **extrair do próprio edital** de cada imóvel (fonte per-imóvel), com o
>   default de 5%/0% como fallback quando o parser não achar.
> - **Registro e ITBI**: **semear por UF/município** a partir das fontes oficiais acima (ANOREG/TJ e
>   prefeituras), tratando o valor como **estimativa de triagem** e versionando por vigência (§5).
> - **Nenhuma** dessas fontes tem API pública padronizada; a atualização é **manual/curada** (seed +
>   migration), com `fonte` e data registradas.

### Referências verificadas (2026)
- **ITBI**: imobisoft (`imobisoft.com.br/blog/itbi-como-calcular`), CustoCartório — cruzados com os
  portais das prefeituras; STJ Tema 1.113.
- **Comissão (5%)**: editais oficiais Caixa (`venda-imoveis.caixa.gov.br/editais/`).
- **Emolumentos**: Lei 10.169/2000; ANOREG/BR; ONR; portarias de TJ (ex.: RJ — Portaria CGJ
  516/2026; GO — Provimento CGJ 179/2025; MG — Lei 15.424/2004).
- **Reforma**: SINAPI (Caixa/IBGE) + pesquisa de mercado 2026.

Ver [Cálculo de custos](../dominio/calculo-de-custos.md) e
[Modelo de dados](modelo-de-dados.md#parâmetros-de-custo-versionados).

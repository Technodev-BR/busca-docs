# Fonte Caixa (CSV) — especificação verificada

Fonte **primária** de dados. Decisão em
[ADR-0002](../arquitetura/decisoes/0002-fonte-oficial-csv-caixa.md).

## Onde baixar
- **Página**: `https://venda-imoveis.caixa.gov.br/sistema/download-lista.asp` (seleciona a UF).
- **URL direta do arquivo** (verificada, responde `200`):
  `https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_{UF}.csv`
  (ex.: `..._SP.csv`, `..._RJ.csv`; existe também `..._Geral.csv` para o Brasil todo).

## Formato do arquivo (verificado)
- **Encoding:** `latin1` / ISO-8859-1 (atenção ao converter para UTF-8).
- **Separador:** `;` (ponto e vírgula).
- **As 2 primeiras linhas não são dados**: uma linha de título ("Lista de Imóveis da Caixa;
  Data de geração; dd/mm/aaaa") e uma linha em branco. **Pule-as** e use a 3ª como cabeçalho.
- **Valores em formato brasileiro:** preço `501.000,00`, desconto `0.00`; campos com **espaços
  sobrando** (fazer `trim`).

## Colunas
```
N° do imóvel | UF | Cidade | Bairro | Endereço | Preço | Valor de avaliação |
Desconto | Financiamento | Descrição | Modalidade de venda | Link de acesso
```

- **N° do imóvel**: chave natural; aparece no link `detalhe-imovel.asp?hdnimovel={n}` → usada para
  deduplicação (RN-01) e para o coletor de detalhe.
- **Descrição**: texto semiestruturado (tipo + áreas total/privativa/terreno) → parsear para os
  filtros.

## Exemplo (linha real, resumida)
```
1444408501866 ;SP ;ADAMANTINA ;VILA JOAQUINA ;ALAMEDA PADRE ANCHIETA, N. 1159, LT 05 QD 16 ;
501.000,00;501.000,00;0.00;Não;Casa, 0.00 de área total, 171.43 de área privativa, 384.00 de área
do terreno.;Leilão SFI - Edital único;https://venda-imoveis.caixa.gov.br/sistema/detalhe-imovel.asp?hdnimovel=1444408501866
```

## Regras de parsing (para o coletor)
1. Baixar como bytes; decodificar com `latin1`.
2. Descartar as 2 primeiras linhas; ler a 3ª como cabeçalho.
3. `split(';')`, `trim` em cada campo.
4. Converter preço/avaliação (`.` milhar, `,` decimal) para `numeric`.
5. Extrair tipo/áreas da **Descrição**.
6. Guardar a linha bruta em `coleta_bruta` antes de normalizar.
7. **Conciliar ausências**: comparar o conjunto de `codigo` do snapshot atual com os imóveis
   `disponivel` no banco. Os que **sumiram** não são apagados — entram no fluxo de ciclo de vida
   (venda/remoção com período de carência). Ver [RN-09](../dominio/regras-de-negocio.md#rn-09--ciclo-de-vida-do-imóvel-vendido--removido--reaparecimento).

Ver implementação sugerida em [Collector (Python)](../servicos/collector-python.md).

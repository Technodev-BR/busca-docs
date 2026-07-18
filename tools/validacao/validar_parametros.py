#!/usr/bin/env python3
"""
Spike de validação de parâmetros de custo e score — Busca-Busca.

NÃO é código de produção. É um "spike" descartável para VALIDAR premissas com
DADOS REAIS da fonte da verdade (CSV oficial da Caixa) antes de construir o MVP:

  1. Baixa o CSV oficial de uma UF (fonte da verdade) e parseia conforme a spec
     verificada (docs/dados/fonte-caixa-csv.md).
  2. Mede a DISTRIBUIÇÃO REAL do desconto anunciado (para calibrar o teto do
     score — score-v0-spec.md §8).
  3. Aplica o MOTOR DE CUSTOS com os PARÂMETROS REAIS (docs/dados/parametros-custo.md):
     ITBI por UF, comissão de leiloeiro 5% (leilão/licitação), registro por faixa.
  4. Compara "desconto anunciado" x "desconto real" (o ponto central do produto).

Uso:
    python tools/validacao/validar_parametros.py --uf SP
    python tools/validacao/validar_parametros.py --uf RJ --insecure   # se proxy corporativo quebrar TLS
    python tools/validacao/validar_parametros.py --arquivo Lista_imoveis_SP.csv  # usar CSV já baixado

Limitações conhecidas (honestas):
  - O CSV traz UM preço; o valor da 2ª praça só vem do DETALHE (enriquecimento).
    Aqui o arremate é aproximado pelo preço do CSV → resultado PROVISÓRIO.
  - A base do ITBI real é o MAIOR entre arremate e o valor venal de referência
    do município (STJ Tema 1.113), que não está no CSV. Aqui usamos o arremate
    como base (LOWER BOUND) e sinalizamos isso.
  - Dívidas e responsabilidade vêm do EDITAL (fonte per-imóvel), não do CSV.
"""
from __future__ import annotations

import argparse
import csv
import io
import ssl
import sys
import urllib.request
from statistics import mean, median
from urllib.error import HTTPError, URLError

URL_CSV = "https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_{uf}.csv"
USER_AGENT = "busca-busca-validacao/0.1 (spike; contato: dev@technodevbr.com)"

# --- Parâmetros REAIS (fonte: docs/dados/parametros-custo.md) ---------------
# ITBI por município é o ideal; aqui usamos um default por UF (capital) como
# aproximação para o spike. Fonte: portais das prefeituras / STJ Tema 1.113.
ITBI_POR_UF = {
    "SP": 0.03, "RJ": 0.03, "MG": 0.03, "RS": 0.03, "BA": 0.03,
    "PE": 0.03, "PR": 0.027, "ES": 0.02,
}
ITBI_DEFAULT_NACIONAL = 0.02  # maioria dos municípios menores
COMISSAO_LEILAO = 0.05        # 5% — confirmado nos editais oficiais da Caixa


def aliquota_itbi(uf: str) -> float:
    return ITBI_POR_UF.get(uf.upper(), ITBI_DEFAULT_NACIONAL)


def custo_registro(valor: float) -> float:
    """Estimativa por faixa (ordem de grandeza — conferir tabela do TJ estadual)."""
    if valor <= 100_000:
        return 1_500.0
    if valor <= 300_000:
        return 3_000.0
    if valor <= 600_000:
        return 5_000.0
    return round(valor * 0.009, 2)


def eh_leilao(modalidade: str) -> bool:
    m = (modalidade or "").lower()
    return "leilão" in m or "leilao" in m or "licitação" in m or "licitacao" in m


def brl_para_float(txt: str) -> float | None:
    """Converte número BR ('501.000,00' ou '0.00') para float."""
    if txt is None:
        return None
    s = txt.strip().replace(" ", "")
    if not s:
        return None
    # remove separador de milhar '.' e troca decimal ',' por '.'
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def baixar_csv(uf: str, insecure: bool) -> bytes:
    url = URL_CSV.format(uf=uf.upper())
    ctx = ssl.create_default_context()
    if insecure:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    print(f"[download] {url}")
    with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
        return resp.read()


def parsear(dados: bytes) -> list[dict]:
    texto = dados.decode("latin1")
    linhas = texto.splitlines()
    # As 2 primeiras linhas não são dados; a 3ª é o cabeçalho (spec verificada).
    if len(linhas) < 4:
        raise ValueError("CSV com menos linhas que o esperado (layout mudou?).")
    corpo = "\n".join(linhas[2:])
    leitor = csv.reader(io.StringIO(corpo), delimiter=";")
    cabecalho = [c.strip() for c in next(leitor)]
    registros = []
    for campos in leitor:
        if len(campos) < len(cabecalho):
            continue
        registros.append({cabecalho[i]: campos[i].strip() for i in range(len(cabecalho))})
    return registros


def percentis(valores: list[float]) -> dict:
    if not valores:
        return {}
    v = sorted(valores)

    def p(q: float) -> float:
        idx = min(len(v) - 1, int(q * (len(v) - 1)))
        return v[idx]

    return {
        "n": len(v), "min": v[0], "p25": p(0.25), "p50": p(0.50),
        "p75": p(0.75), "p90": p(0.90), "p95": p(0.95), "max": v[-1],
    }


def fmt(x: float) -> str:
    return f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")


def achar_coluna(cabecalho: list[str], *chaves: str) -> str | None:
    for col in cabecalho:
        low = col.lower()
        if all(k in low for k in chaves):
            return col
    return None


def main() -> int:
    # Console do Windows costuma ser cp1252; força UTF-8 para acentos/símbolos.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(description="Spike de validação de parâmetros (dados reais Caixa).")
    ap.add_argument("--uf", default="SP", help="UF (default SP)")
    ap.add_argument("--insecure", action="store_true", help="Ignora verificação TLS (proxy corporativo)")
    ap.add_argument("--arquivo", help="Caminho de um CSV já baixado (pula o download)")
    ap.add_argument("--limite", type=int, default=0, help="Analisar só os N primeiros (0 = todos)")
    args = ap.parse_args()

    try:
        if args.arquivo:
            with open(args.arquivo, "rb") as f:
                dados = f.read()
            print(f"[arquivo] {args.arquivo}")
        else:
            dados = baixar_csv(args.uf, args.insecure)
    except (HTTPError, URLError, TimeoutError) as e:
        print(f"\n[ERRO] Falha ao baixar o CSV: {e}")
        print("Possível bloqueio de rede/proxy (Zscaler). Tente:")
        print("  1) baixar manualmente e usar --arquivo Lista_imoveis_SP.csv")
        print("  2) --insecure se for erro de certificado TLS")
        return 2

    registros = parsear(dados)
    if args.limite:
        registros = registros[: args.limite]
    if not registros:
        print("[ERRO] Nenhum registro parseado.")
        return 3

    cab = list(registros[0].keys())
    col_preco = achar_coluna(cab, "preço") or achar_coluna(cab, "preco")
    col_aval = achar_coluna(cab, "avalia")
    col_desc = achar_coluna(cab, "desconto")
    col_mod = achar_coluna(cab, "modalidade")
    print(f"[colunas] preço={col_preco!r} avaliação={col_aval!r} desconto={col_desc!r} modalidade={col_mod!r}")

    desc_anunciado: list[float] = []
    desc_real: list[float] = []
    n_leilao = 0
    n_validos = 0

    for r in registros:
        preco = brl_para_float(r.get(col_preco, ""))
        aval = brl_para_float(r.get(col_aval, ""))
        if not preco or not aval or aval <= 0:
            continue
        n_validos += 1
        uf = (r.get("UF") or args.uf).strip()

        # desconto anunciado (referência = avaliação)
        d_anunciado = (aval - preco) / aval * 100
        desc_anunciado.append(d_anunciado)

        # motor de custos com parâmetros REAIS
        leilao = eh_leilao(r.get(col_mod, ""))
        n_leilao += 1 if leilao else 0
        itbi = aliquota_itbi(uf) * preco            # base = arremate (lower bound; ver limitações)
        comissao = COMISSAO_LEILAO * preco if leilao else 0.0
        registro = custo_registro(preco)
        custo_total = preco + itbi + comissao + registro  # dívidas/reforma = 0 (não no CSV)
        d_real = (aval - custo_total) / aval * 100
        desc_real.append(d_real)

    print("\n" + "=" * 64)
    print(f"AMOSTRA REAL — UF {args.uf.upper()} | registros válidos: {n_validos} | leilão/licitação: {n_leilao}")
    print("=" * 64)

    pa = percentis(desc_anunciado)
    pr = percentis(desc_real)
    print("\n[Desconto ANUNCIADO %] (avaliação - preço)/avaliação")
    print(f"  p25={fmt(pa['p25'])}  p50={fmt(pa['p50'])}  p75={fmt(pa['p75'])}  p90={fmt(pa['p90'])}  p95={fmt(pa['p95'])}  max={fmt(pa['max'])}")
    print("\n[Desconto REAL %] já com ITBI + comissão(5% leilão) + registro")
    print(f"  p25={fmt(pr['p25'])}  p50={fmt(pr['p50'])}  p75={fmt(pr['p75'])}  p90={fmt(pr['p90'])}  p95={fmt(pr['p95'])}  max={fmt(pr['max'])}")

    if desc_anunciado and desc_real:
        gap = mean(desc_anunciado) - mean(desc_real)
        print(f"\n[Erosão média do desconto] anunciado - real = {fmt(gap)} p.p. (média)")
        print(f"  média anunciado={fmt(mean(desc_anunciado))}  média real={fmt(mean(desc_real))}  mediana real={fmt(median(desc_real))}")

    # Calibração do teto do score (score-v0-spec §8): usar o p90 do desconto REAL positivo
    reais_pos = [d for d in desc_real if d > 0]
    if reais_pos:
        teto = percentis(reais_pos)["p90"]
        print(f"\n[Calibração score] teto sugerido p/ subscore desconto_real (p90 do real positivo) ~= {fmt(teto)}%")
        print(f"  (hoje a spec usa teto fixo de 50%; ajustar conforme a distribuição real)")

    # Quantos continuam "bons negócios" após o custo real
    for corte in (20, 30, 40):
        q = sum(1 for d in desc_real if d >= corte)
        print(f"  imóveis com desconto REAL >= {corte}%: {q} ({q*100//max(1,len(desc_real))}%)")

    print("\n[Limitações] arremate ≈ preço do CSV (2ª praça só no detalhe); base ITBI = arremate")
    print("             (real pode ser o valor venal de referência, maior); dívidas vêm do edital.")
    print("[OK] validação concluída — dados reais da fonte oficial.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

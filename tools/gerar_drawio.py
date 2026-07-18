"""Gera os diagramas em formato draw.io (.drawio) na pasta docs/assets/diagramas/.

Diagramas:
  - arquitetura.drawio    : visão geral do sistema (camadas + laterais + entrega)
  - fluxo-gitops.drawio   : fluxo de entrega (CI + GitOps + Kubernetes)
  - banco-dados.drawio    : esquema do banco (entidades e relacionamentos)
  - sequencia-fluxo.drawio: sequência coleta → ingestão → enriquecimento → consulta
  - sequencia-login.drawio: sequência login social (OIDC + PKCE) · refresh · logout

Rode: python tools/gerar_drawio.py
Abra em https://app.diagrams.net (File > Open) ou pela extensão Draw.io no VS Code/Cursor.
"""
import os
import xml.etree.ElementTree as ET

OUTDIR = os.path.join(os.path.dirname(__file__), "..", "docs", "assets", "diagramas")


def esc(raw: str) -> str:
    return (raw.replace("&", "&amp;").replace("<", "&lt;")
               .replace(">", "&gt;").replace('"', "&quot;"))


class Diagram:
    def __init__(self, name):
        self.name = name
        self.cells = []
        self._id = 1

    def nid(self):
        self._id += 1
        return f"n{self._id}"

    def node(self, x, y, w, h, label, fill="#ffffff", stroke="#333333",
             rounded=True, dashed=False, fontsize=12, bold_title=True, align="center"):
        cid = self.nid()
        # label pode conter <br> e <b>; escapamos o HTML inteiro
        style = (
            f"rounded={'1' if rounded else '0'};whiteSpace=wrap;html=1;"
            f"fillColor={fill};strokeColor={stroke};fontSize={fontsize};"
            f"align={align};verticalAlign=middle;"
            f"{'dashed=1;' if dashed else ''}"
        )
        self.cells.append(
            f'<mxCell id="{cid}" value="{esc(label)}" style="{esc(style)}" '
            f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" '
            f'height="{h}" as="geometry"/></mxCell>'
        )
        return cid

    def band(self, x, y, w, h, fill="#f5f5f5", stroke="#e0e0e0"):
        cid = self.nid()
        style = (f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};"
                 f"strokeColor={stroke};dashed=0;opacity=60;")
        self.cells.append(
            f'<mxCell id="{cid}" value="" style="{esc(style)}" vertex="1" '
            f'parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" '
            f'as="geometry"/></mxCell>'
        )
        return cid

    def label(self, x, y, w, text, fontsize=13, color="#555555", align="left", bold=True):
        cid = self.nid()
        style = (f"text;html=1;strokeColor=none;fillColor=none;align={align};"
                 f"verticalAlign=middle;fontSize={fontsize};fontColor={color};"
                 f"{'fontStyle=1;' if bold else ''}")
        self.cells.append(
            f'<mxCell id="{cid}" value="{esc(text)}" style="{esc(style)}" '
            f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" '
            f'height="24" as="geometry"/></mxCell>'
        )
        return cid

    def edge(self, src, tgt, label="", dashed=False, stroke="#555555", start="none",
             end="block"):
        cid = self.nid()
        style = (
            f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={stroke};"
            f"startArrow={start};endArrow={end};{'dashed=1;' if dashed else ''}"
        )
        self.cells.append(
            f'<mxCell id="{cid}" value="{esc(label)}" style="{esc(style)}" '
            f'edge="1" parent="1" source="{src}" target="{tgt}">'
            f'<mxGeometry relative="1" as="geometry"/></mxCell>'
        )
        return cid

    def msg(self, x1, y, x2, label="", dashed=False, stroke="#555555", end="block"):
        """Seta horizontal livre (mensagem de sequência) entre dois pontos."""
        cid = self.nid()
        style = (f"html=1;rounded=0;endArrow={end};startArrow=none;"
                 f"strokeColor={stroke};{'dashed=1;' if dashed else ''}"
                 f"fontSize=10;verticalAlign=bottom;")
        self.cells.append(
            f'<mxCell id="{cid}" value="{esc(label)}" style="{esc(style)}" '
            f'edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
            f'<mxPoint x="{x1}" y="{y}" as="sourcePoint"/>'
            f'<mxPoint x="{x2}" y="{y}" as="targetPoint"/>'
            f'</mxGeometry></mxCell>'
        )
        return cid

    def xml(self):
        body = "\n        ".join(self.cells)
        return (
            f'<mxfile host="app.diagrams.net" type="device">\n'
            f'  <diagram name="{esc(self.name)}" id="{esc(self.name)}">\n'
            f'    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" '
            f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
            f'pageWidth="1600" pageHeight="1200" math="0" shadow="0">\n'
            f'      <root>\n'
            f'        <mxCell id="0"/>\n'
            f'        <mxCell id="1" parent="0"/>\n'
            f'        {body}\n'
            f'      </root>\n'
            f'    </mxGraphModel>\n'
            f'  </diagram>\n'
            f'</mxfile>\n'
        )

    def save(self):
        path = os.path.join(OUTDIR, f"{self.name}.drawio")
        ET.fromstring(self.xml())  # valida o XML
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.xml())
        print(f"OK - {self.name}.drawio ({len(self.cells)} células)")


# paleta
SRC = ("#fff2cc", "#d6b656"); COLL = ("#ffe6cc", "#d79b00")
ING = ("#e1d5e7", "#9673a6"); MQ = ("#f8cecc", "#b85450")
PROC = ("#e1d5e7", "#9673a6"); DB = ("#d5e8d4", "#82b366")
API = ("#dae8fc", "#6c8ebf"); FRONT = ("#d5f5f0", "#3aa89a")
OBS = ("#f8cecc", "#b85450"); TEST = ("#fce4ec", "#c2185b")
DEP = ("#eeeeee", "#666666"); SAT = ("#f5f5f5", "#999999")


# ------------------------------------------------------------------ 1) ARQUITETURA
def build_arquitetura():
    d = Diagram("arquitetura")
    d.label(360, 20, 900, "Busca-Busca — Arquitetura (visão geral)", fontsize=20, color="#222222")
    d.label(360, 46, 1100,
            "Java (Spring Boot) + Python (coleta) + Angular · PostgreSQL/PostGIS · RabbitMQ · Redis · Docker/K8s",
            fontsize=12, color="#888888", bold=False)

    cx, w, h = 560, 260, 60
    ys = [90, 194, 298, 402, 506, 610, 714, 818]
    n_src = d.node(cx, ys[0], w, h, "<b>Caixa — CSV oficial</b><br/>(por UF · fonte primária)", *SRC)
    n_coll = d.node(cx, ys[1], w, h, "<b>Coletor — Python</b><br/>download + parse + envio", *COLL)
    n_ing = d.node(cx, ys[2], w, h, "<b>API de Ingestão — Java</b><br/>POST /internal/ingest", *ING)
    n_mq = d.node(cx, ys[3], w, h, "<b>RabbitMQ</b><br/>eventos p/ processamento assíncrono", *MQ)
    n_proc = d.node(cx, ys[4], w, h, "<b>Workers — Java</b><br/>normalização · geocoding · custos · score", *PROC)
    n_db = d.node(cx, ys[5], w, h, "<b>PostgreSQL 16 + PostGIS</b><br/>schema via Flyway", *DB)
    n_api = d.node(cx, ys[6], w, h, "<b>API REST — Java</b><br/>busca · filtros · detalhe · OpenAPI", *API)
    n_front = d.node(cx, ys[7], w, h, "<b>Frontend — Angular</b><br/>lista · mapa · detalhe (Nginx)", *FRONT)

    for a, b in [(n_src, n_coll), (n_coll, n_ing), (n_ing, n_mq), (n_mq, n_proc),
                 (n_proc, n_db), (n_db, n_api), (n_api, n_front)]:
        d.edge(a, b)

    # satélites — enriquecimento por detalhe (ADR-0010)
    n_det_src = d.node(250, ys[0], 220, h, "Caixa — página de detalhe<br/>fotos · edital · matrícula", *SRC)
    n_det = d.node(250, ys[2], 220, 74,
                   "<b>Coletor de detalhe — Python</b><br/>consome fila · raspa HTML · POST /detalhe", *COLL)
    d.edge(n_det_src, n_det, dashed=True, label="GET detalhe")
    d.edge(n_mq, n_det, dashed=True, label="imovel.enriquecer")
    d.edge(n_det, n_ing, label="POST /detalhe")
    n_obj = d.node(880, ys[4], 190, h, "Object Storage<br/>fotos · editais", *SAT)
    d.edge(n_proc, n_obj, dashed=True, end="none")
    n_redis = d.node(880, ys[6], 190, h, "Redis (cache)<br/>buscas quentes", *SAT)
    d.edge(n_api, n_redis, dashed=True, end="none", label="cache")

    # painel esquerdo: qualidade & CI
    d.band(40, 80, 190, 470, fill=TEST[0], stroke=TEST[1])
    d.label(56, 92, 170, "Qualidade & CI", fontsize=13, color=TEST[1])
    for i, t in enumerate(["GitHub Actions", "SonarQube<br/>(Quality Gate)", "Trivy<br/>(scan CVE)",
                            "Testes<br/>(unit · integração · E2E)"]):
        d.node(56, 128 + i * 100, 160, 74, t, "#ffffff", TEST[1], fontsize=11)

    # painel direito: observabilidade & SRE
    d.band(1110, 80, 210, 760, fill=OBS[0], stroke=OBS[1])
    d.label(1126, 92, 190, "Observabilidade & SRE", fontsize=13, color=OBS[1])
    for i, t in enumerate(["Métricas<br/>Micrometer→Prometheus", "Logs JSON<br/>Loki + correlation-id",
                           "Traces<br/>OpenTelemetry→Tempo", "Dashboards · Alertas<br/>Grafana + Alertmanager",
                           "Agente IA · AIOps<br/>(via MCP)", "Notificações<br/>Slack · Teams · E-mail"]):
        d.node(1126, 128 + i * 116, 180, 88, t, "#ffffff", OBS[1], fontsize=11)

    # faixa de entrega (bottom)
    d.band(300, 930, 1000, 120, fill=DEP[0], stroke=DEP[1])
    d.label(316, 942, 400, "Entrega · GitOps (open source)", fontsize=13, color=DEP[1])
    dep = []
    for i, t in enumerate(["GitHub Actions", "Harbor<br/>(registry + Trivy)",
                           "Argo CD<br/>(GitOps)", "k3s (VPS)<br/>Traefik · Helm · Rollouts"]):
        dep.append(d.node(330 + i * 240, 976, 200, 60, t, "#ffffff", DEP[1], fontsize=11))
    for a, b in zip(dep, dep[1:]):
        d.edge(a, b)
    d.save()


# ------------------------------------------------------------------ 2) FLUXO GITOPS
def build_gitops():
    d = Diagram("fluxo-gitops")
    d.label(40, 20, 1000, "Busca-Busca — Fluxo de Entrega (CI + GitOps + k3s)",
            fontsize=18, color="#222222")
    d.label(40, 46, 1100, "Padrão de 2 repositórios (app + config) · deploy declarativo com Argo CD",
            fontsize=12, color="#888888", bold=False)

    dev = d.node(40, 120, 150, 70, "<b>Dev</b><br/>commit / PR", *FRONT)
    app = d.node(240, 110, 240, 90,
                 "<b>GitHub · busca-busca</b><br/>backend · collector · frontend<br/>deploy/helm · .github/workflows",
                 *DEP)
    ci = d.node(540, 110, 250, 90,
                "<b>GitHub Actions (CI)</b><br/>build · testes · SonarQube<br/>Trivy · build+push imagem", *COLL)
    harbor = d.node(850, 120, 200, 70, "<b>Harbor</b><br/>registry + Trivy + Cosign", *FRONT)
    gitops = d.node(540, 300, 250, 100,
                    "<b>GitHub · busca-busca-gitops</b><br/>apps/ (app-of-apps)<br/>environments/{dev,staging,prod}",
                    *ING)
    argo = d.node(850, 305, 200, 90, "<b>Argo CD</b><br/>watch · sync · rollback · self-heal", *TEST)

    k8s = d.node(1120, 110, 300, 470, "<b>k3s (VPS Hostinger)</b>", *DB, align="left")
    d.label(1140, 150, 260, "Traefik + cert-manager (Cloudflare DNS-01)", fontsize=11, color="#555555", bold=False)
    ns = []
    for i, name in enumerate(["namespace: dev", "namespace: staging", "namespace: prod"]):
        ns.append(d.node(1140, 190 + i * 100, 260, 80,
                         f"<b>{name}</b><br/>backend · collector · frontend", "#ffffff", DB[1], fontsize=11))
    d.node(1140, 490, 260, 60, "PostgreSQL (CloudNativePG)", "#ffffff", DB[1], fontsize=11)

    obs = d.node(240, 470, 550, 90,
                 "<b>Observabilidade & Agente IA (via MCP)</b><br/>"
                 "Métricas·Logs·Traces · diagnostica incidente · Slack/Teams/E-mail", *OBS)

    # exposição & acesso (Cloudflare / Traefik / Portainer / VPN)
    d.band(1110, 600, 320, 200, fill=SRC[0], stroke=SRC[1])
    d.label(1126, 612, 290, "Exposição & acesso · technodev.com.br", fontsize=13, color=SRC[1])
    cf = d.node(1126, 648, 140, 64, "Cloudflare<br/>DNS + TLS (proxy)", "#ffffff", SRC[1], fontsize=11)
    vpn = d.node(1280, 648, 135, 64, "VPN (Tailscale)<br/>acesso interno", "#ffffff", SRC[1], fontsize=11)
    portainer = d.node(1126, 726, 140, 60, "Portainer<br/>painel (público)", "#ffffff", SRC[1], fontsize=11)
    internal = d.node(1280, 726, 135, 60, "app · argo · grafana<br/>(interno)", "#ffffff", SRC[1], fontsize=11)

    d.edge(dev, app, "push")
    d.edge(app, ci, "trigger")
    d.edge(ci, harbor, "push imagem")
    d.edge(ci, gitops, "bump da tag")
    d.edge(gitops, argo, "watch")
    d.edge(harbor, argo, "pull imagem", dashed=True)
    d.edge(argo, k8s, "sync / apply")
    d.edge(k8s, obs, "telemetria", dashed=True)
    d.edge(obs, dev, "issue / alerta diagnosticado", dashed=True)
    d.edge(cf, k8s, "→ Traefik", dashed=True)
    d.edge(vpn, k8s, "→ Traefik", dashed=True)
    d.edge(cf, portainer, "público")
    d.edge(vpn, internal, "VPN")
    d.save()


# ------------------------------------------------------------------ 3) BANCO DE DADOS
def build_banco():
    d = Diagram("banco-dados")
    d.label(40, 20, 900, "Busca-Busca — Esquema do banco (PostgreSQL + PostGIS)",
            fontsize=18, color="#222222")
    d.label(40, 46, 1000, "PK = chave primária · FK = chave estrangeira · 1..* = um para muitos",
            fontsize=12, color="#888888", bold=False)
    d.node(40, 780, 240, 96,
           "<b>Padrão de auditoria</b> (todas as tabelas,<br/>exceto referência)<br/>"
           "<hr size='1'/>criado_em · atualizado_em<br/>excluido_em (exclusão lógica / soft delete)",
           "#fff2cc", "#d6b656", fontsize=11, align="left")

    def entity(x, y, title, fields, fill, stroke, w=290):
        rows = "<br/>".join(fields)
        h = 34 + len(fields) * 18
        label = f"<b>{title}</b><br/><hr size='1'/>{rows}"
        return d.node(x, y, w, h, label, fill, stroke, fontsize=11, align="left")

    # tabelas de referência (vocabulário controlado)
    municipio = entity(40, 100, "municipio", [
        "PK id", "codigo_ibge · UNIQUE", "nome · uf"], *COLL, w=210)
    tipo = entity(40, 240, "tipo_imovel", [
        "PK id", "nome · UNIQUE"], *COLL, w=210)
    modalidade = entity(40, 350, "modalidade_venda", [
        "PK id", "nome · UNIQUE"], *COLL, w=210)

    # tabelas filhas de imovel
    foto = entity(310, 100, "imovel_foto", [
        "PK id", "FK imovel_id", "url · ordem", "UNIQUE(imovel_id, ordem)"], *API, w=230)
    historico = entity(310, 260, "historico_preco", [
        "PK id", "FK imovel_id", "valor · desconto_pct", "status (status_imovel)",
        "capturado_em"], *API, w=230)
    analise = entity(310, 430, "analise_custo", [
        "PK id", "FK imovel_id (1..1)", "itbi · custas · registro", "dividas · reforma_estimada",
        "custo_total · desconto_real_pct", "score · status_confianca", "calculado_em"], *API, w=230)
    coleta = entity(310, 640, "coleta_bruta", [
        "PK id", "fonte (csv/detalhe) · uf · codigo", "payload_bruto (bytea · zstd)",
        "compressao · payload_hash · tamanho_bytes", "coletado_em · retenção ~90d"], *SAT, w=250)

    # núcleo
    imovel = entity(620, 100, "imovel", [
        "PK id", "codigo · UNIQUE por fonte", "FK tipo_imovel_id · FK modalidade_venda_id",
        "FK municipio_id · bairro · endereco", "localizacao (geography Point 4326)",
        "area_total · area_privativa · area_terreno", "quartos",
        "valor_avaliacao · valor_minimo · desconto_pct", "status (status_imovel)",
        "criado_em · atualizado_em"], *DB, w=330)
    detalhe = entity(620, 470, "imovel_detalhe (1..1)", [
        "PK id · FK imovel_id · UNIQUE", "valor_primeiro/segundo_leilao",
        "data_primeiro/segundo_leilao", "leiloeiro · edital · numero_item",
        "matricula · comarca · oficio", "inscricao_imobiliaria · cep", "endereco_completo",
        "aceita_fgts · aceita_financiamento", "despesas_condominio/tributos_comprador",
        "situacao_ocupacao · descricao_completa", "edital_url · matricula_url",
        "enriquecido_em · status_enriquecimento"], *SAT, w=340)

    usuario = entity(1010, 100, "usuario", [
        "PK id", "email · UNIQUE", "nome · avatar_url",
        "provedor · provedor_id (OIDC)", "UNIQUE(provedor, provedor_id)"], *ING, w=220)
    favorito = entity(1010, 280, "favorito", [
        "PK id", "FK usuario_id", "FK imovel_id", "criado_em", "UNIQUE(usuario_id, imovel_id)"],
        *ING, w=220)
    alerta = entity(1010, 470, "alerta", [
        "PK id", "FK usuario_id", "filtro (jsonb)", "canal (canal_alerta) · ativo",
        "criado_em"], *ING, w=220)
    token = entity(1010, 630, "token_atualizacao", [
        "PK id", "FK usuario_id", "token_hash · UNIQUE", "familia_id (uuid)",
        "expira_em · revogado_em", "substituido_por (FK self)", "user_agent · ip"], *SAT, w=220)

    d.edge(municipio, imovel, "FK")
    d.edge(tipo, imovel, "FK")
    d.edge(modalidade, imovel, "FK")
    d.edge(imovel, foto, "1..*", end="none")
    d.edge(imovel, historico, "1..*", end="none")
    d.edge(imovel, analise, "1..1", end="none")
    d.edge(imovel, detalhe, "1..1", end="none")
    d.edge(coleta, imovel, "por codigo", dashed=True, end="none")
    d.edge(usuario, favorito, "1..*", end="none")
    d.edge(imovel, favorito, "1..*", end="none")
    d.edge(usuario, alerta, "1..*", end="none")
    d.edge(usuario, token, "1..*", end="none")
    d.save()


def build_sequencia():
    d = Diagram("sequencia-fluxo")
    d.label(40, 20, 1200, "Busca-Busca — Sequência: coleta → ingestão → enriquecimento → recálculo → consulta",
            fontsize=17, color="#222222")

    # lifelines (centro x, título, cor)
    lanes = [
        (110, "Coletor (Python)", COLL),
        (330, "API Ingestão (Java)", ING),
        (540, "RabbitMQ", MQ),
        (740, "Worker (Java)", PROC),
        (950, "PostgreSQL", DB),
        (1170, "API Pública (Java)", API),
        (1390, "Frontend (Angular)", FRONT),
    ]
    top, bottom = 60, 900
    cx = {}
    for x, titulo, (fill, stroke) in lanes:
        d.node(x - 85, top, 170, 40, f"<b>{titulo}</b>", fill, stroke, fontsize=11)
        # linha de vida (aresta livre vertical)
        cid = d.nid()
        style = "html=1;endArrow=none;dashed=1;strokeColor=#aaaaaa;"
        d.cells.append(
            f'<mxCell id="{cid}" value="" style="{esc(style)}" edge="1" parent="1">'
            f'<mxGeometry relative="1" as="geometry">'
            f'<mxPoint x="{x}" y="{top + 40}" as="sourcePoint"/>'
            f'<mxPoint x="{x}" y="{bottom}" as="targetPoint"/>'
            f'</mxGeometry></mxCell>'
        )
        cx[titulo] = x

    C, I, M, W, DBx, P, F = (cx["Coletor (Python)"], cx["API Ingestão (Java)"],
                             cx["RabbitMQ"], cx["Worker (Java)"], cx["PostgreSQL"],
                             cx["API Pública (Java)"], cx["Frontend (Angular)"])

    y = 130
    step = 44
    def m(a, b, label, dashed=False):
        nonlocal y
        d.msg(a, y, b, label, dashed=dashed)
        y += step

    m(C, I, "POST /internal/ingest/imoveis (lote CSV)")
    m(I, DBx, "upsert imovel · coleta_bruta · historico_preco (na mudança)")
    m(I, M, "publica imovel.recebido / imovel.enriquecer")
    m(I, C, "202 Accepted", dashed=True)
    m(M, W, "imovel.recebido")
    m(W, DBx, "normaliza · geocoding · calcula custo/score")
    m(M, C, "imovel.enriquecer (consumer detalhe)")
    # ação externa do coletor (GET no site) — caixinha na lifeline do coletor
    d.node(C - 90, y - 14, 180, 30, "GET detalhe-imovel.asp (site Caixa)", *SAT, fontsize=10)
    y += step
    m(C, I, "POST /internal/ingest/imoveis/{codigo}/detalhe")
    m(I, DBx, "upsert imovel_detalhe · fotos")
    m(I, M, "publica imovel.enriquecido")
    m(M, W, "imovel.enriquecido")
    m(W, DBx, "recalcula analise_custo (RF-06/07)")
    m(F, P, "GET /api/v1/imoveis (busca/filtros)")
    m(P, DBx, "query + cache Redis")
    m(P, F, "200 · resultados", dashed=True)
    d.save()


def build_sequencia_login():
    d = Diagram("sequencia-login")
    d.label(40, 20, 1200, "Busca-Busca — Sequência: login social (OIDC + PKCE) · refresh · logout",
            fontsize=17, color="#222222")

    lanes = [
        (170, "Frontend (Angular)", FRONT),
        (500, "Backend (Spring Security)", API),
        (830, "IdP (Google/GitHub)", COLL),
        (1120, "PostgreSQL", DB),
    ]
    top, bottom = 60, 930
    cx = {}
    for x, titulo, (fill, stroke) in lanes:
        d.node(x - 95, top, 190, 40, f"<b>{titulo}</b>", fill, stroke, fontsize=11)
        cid = d.nid()
        style = "html=1;endArrow=none;dashed=1;strokeColor=#aaaaaa;"
        d.cells.append(
            f'<mxCell id="{cid}" value="" style="{esc(style)}" edge="1" parent="1">'
            f'<mxGeometry relative="1" as="geometry">'
            f'<mxPoint x="{x}" y="{top + 40}" as="sourcePoint"/>'
            f'<mxPoint x="{x}" y="{bottom}" as="targetPoint"/>'
            f'</mxGeometry></mxCell>'
        )
        cx[titulo] = x

    F = cx["Frontend (Angular)"]
    B = cx["Backend (Spring Security)"]
    P = cx["IdP (Google/GitHub)"]
    DBx = cx["PostgreSQL"]

    y = [128]
    step = 38
    def m(a, b, label, dashed=False):
        d.msg(a, y[0], b, label, dashed=dashed)
        y[0] += step
    def fase(txt):
        d.label(36, y[0] - 6, 130, txt, fontsize=11, color="#8a56ac")
        y[0] += 26

    fase("1 · Login")
    m(F, B, "GET /oauth2/authorization/{provedor}")
    m(B, F, "302 → provedor (authorize + PKCE + state)", dashed=True)
    m(F, P, "login + consentimento")
    m(P, F, "302 code → /login/oauth2/code/{provedor}", dashed=True)
    m(F, B, "GET /login/oauth2/code (code)")
    m(B, P, "troca code → tokens (valida id_token/nonce)")
    m(P, B, "id_token + userinfo", dashed=True)
    m(B, DBx, "upsert usuario (provedor+provedor_id) · cria refresh (familia)")
    m(B, F, "302 app + Set-Cookie ACCESS+REFRESH (HttpOnly)", dashed=True)
    m(F, B, "GET /api/v1/auth/me")
    m(B, F, "200 · Usuario", dashed=True)

    fase("2 · Renovação")
    m(F, B, "request protegido (ACCESS expirado)")
    m(B, F, "401", dashed=True)
    m(F, B, "POST /api/v1/auth/refresh (cookie REFRESH)")
    m(B, DBx, "valida hash · rotaciona (revoga antigo, detecta reúso)")
    m(B, F, "204 + Set-Cookie novos ACCESS+REFRESH", dashed=True)

    fase("3 · Logout")
    m(F, B, "POST /api/v1/auth/logout")
    m(B, DBx, "revoga refresh (familia / todos dispositivos)")
    m(B, F, "204", dashed=True)
    d.save()


if __name__ == "__main__":
    build_arquitetura()
    build_gitops()
    build_banco()
    build_sequencia()
    build_sequencia_login()
    print("Diagramas gerados em docs/assets/diagramas/")

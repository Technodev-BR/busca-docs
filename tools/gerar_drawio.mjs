/**
 * Gera os diagramas em formato draw.io (.drawio) na pasta docs/public/diagramas/.
 *
 * Diagramas:
 *   - arquitetura.drawio    : visão geral do sistema (camadas + laterais + entrega)
 *   - fluxo-gitops.drawio   : fluxo de entrega (CI + GitOps + Kubernetes)
 *   - banco-dados.drawio    : esquema do banco (entidades e relacionamentos)
 *   - sequencia-fluxo.drawio: sequência coleta → ingestão → enriquecimento → consulta
 *   - sequencia-login.drawio: sequência login social (OIDC + PKCE) · refresh · logout
 *
 * Rode: node tools/gerar_drawio.mjs   (ou: npm run diagrams)
 * Abra em https://app.diagrams.net (File > Open) ou pela extensão Draw.io no VS Code/Cursor.
 *
 * Sem dependências externas (só Node stdlib) — unifica a stack de tooling das docs em JS/Node.
 */
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUTDIR = join(__dirname, "..", "docs", "public", "diagramas");

function esc(raw) {
  return String(raw)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

class Diagram {
  constructor(name) {
    this.name = name;
    this.cells = [];
    this._id = 1;
  }

  nid() {
    this._id += 1;
    return `n${this._id}`;
  }

  node(x, y, w, h, label, fill = "#ffffff", stroke = "#333333", opts = {}) {
    const { rounded = true, dashed = false, fontsize = 12, align = "center" } = opts;
    const cid = this.nid();
    const style =
      `rounded=${rounded ? "1" : "0"};whiteSpace=wrap;html=1;` +
      `fillColor=${fill};strokeColor=${stroke};fontSize=${fontsize};` +
      `align=${align};verticalAlign=middle;` +
      `${dashed ? "dashed=1;" : ""}`;
    this.cells.push(
      `<mxCell id="${cid}" value="${esc(label)}" style="${esc(style)}" ` +
        `vertex="1" parent="1"><mxGeometry x="${x}" y="${y}" width="${w}" ` +
        `height="${h}" as="geometry"/></mxCell>`
    );
    return cid;
  }

  band(x, y, w, h, opts = {}) {
    const { fill = "#f5f5f5", stroke = "#e0e0e0" } = opts;
    const cid = this.nid();
    const style =
      `rounded=1;whiteSpace=wrap;html=1;fillColor=${fill};` +
      `strokeColor=${stroke};dashed=0;opacity=60;`;
    this.cells.push(
      `<mxCell id="${cid}" value="" style="${esc(style)}" vertex="1" ` +
        `parent="1"><mxGeometry x="${x}" y="${y}" width="${w}" height="${h}" ` +
        `as="geometry"/></mxCell>`
    );
    return cid;
  }

  label(x, y, w, text, opts = {}) {
    const { fontsize = 13, color = "#555555", align = "left", bold = true } = opts;
    const cid = this.nid();
    const style =
      `text;html=1;strokeColor=none;fillColor=none;align=${align};` +
      `verticalAlign=middle;fontSize=${fontsize};fontColor=${color};` +
      `${bold ? "fontStyle=1;" : ""}`;
    this.cells.push(
      `<mxCell id="${cid}" value="${esc(text)}" style="${esc(style)}" ` +
        `vertex="1" parent="1"><mxGeometry x="${x}" y="${y}" width="${w}" ` +
        `height="24" as="geometry"/></mxCell>`
    );
    return cid;
  }

  edge(src, tgt, label = "", opts = {}) {
    const { dashed = false, stroke = "#555555", start = "none", end = "block" } = opts;
    const cid = this.nid();
    const style =
      `edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=${stroke};` +
      `startArrow=${start};endArrow=${end};${dashed ? "dashed=1;" : ""}`;
    this.cells.push(
      `<mxCell id="${cid}" value="${esc(label)}" style="${esc(style)}" ` +
        `edge="1" parent="1" source="${src}" target="${tgt}">` +
        `<mxGeometry relative="1" as="geometry"/></mxCell>`
    );
    return cid;
  }

  msg(x1, y, x2, label = "", opts = {}) {
    // Seta horizontal livre (mensagem de sequência) entre dois pontos.
    const { dashed = false, stroke = "#555555", end = "block" } = opts;
    const cid = this.nid();
    const style =
      `html=1;rounded=0;endArrow=${end};startArrow=none;` +
      `strokeColor=${stroke};${dashed ? "dashed=1;" : ""}` +
      `fontSize=10;verticalAlign=bottom;`;
    this.cells.push(
      `<mxCell id="${cid}" value="${esc(label)}" style="${esc(style)}" ` +
        `edge="1" parent="1"><mxGeometry relative="1" as="geometry">` +
        `<mxPoint x="${x1}" y="${y}" as="sourcePoint"/>` +
        `<mxPoint x="${x2}" y="${y}" as="targetPoint"/>` +
        `</mxGeometry></mxCell>`
    );
    return cid;
  }

  // linha de vida (aresta livre vertical) para diagramas de sequência
  lifeline(x, top, bottom) {
    const cid = this.nid();
    const style = "html=1;endArrow=none;dashed=1;strokeColor=#aaaaaa;";
    this.cells.push(
      `<mxCell id="${cid}" value="" style="${esc(style)}" edge="1" parent="1">` +
        `<mxGeometry relative="1" as="geometry">` +
        `<mxPoint x="${x}" y="${top + 40}" as="sourcePoint"/>` +
        `<mxPoint x="${x}" y="${bottom}" as="targetPoint"/>` +
        `</mxGeometry></mxCell>`
    );
    return cid;
  }

  xml() {
    const body = this.cells.join("\n        ");
    return (
      `<mxfile host="app.diagrams.net" type="device">\n` +
      `  <diagram name="${esc(this.name)}" id="${esc(this.name)}">\n` +
      `    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" ` +
      `tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" ` +
      `pageWidth="1600" pageHeight="1200" math="0" shadow="0">\n` +
      `      <root>\n` +
      `        <mxCell id="0"/>\n` +
      `        <mxCell id="1" parent="0"/>\n` +
      `        ${body}\n` +
      `      </root>\n` +
      `    </mxGraphModel>\n` +
      `  </diagram>\n` +
      `</mxfile>\n`
    );
  }

  save() {
    const path = join(OUTDIR, `${this.name}.drawio`);
    writeFileSync(path, this.xml(), { encoding: "utf-8" });
    console.log(`OK - ${this.name}.drawio (${this.cells.length} células)`);
  }
}

// paleta [fill, stroke]
const SRC = ["#fff2cc", "#d6b656"];
const COLL = ["#ffe6cc", "#d79b00"];
const ING = ["#e1d5e7", "#9673a6"];
const MQ = ["#f8cecc", "#b85450"];
const PROC = ["#e1d5e7", "#9673a6"];
const DB = ["#d5e8d4", "#82b366"];
const API = ["#dae8fc", "#6c8ebf"];
const FRONT = ["#d5f5f0", "#3aa89a"];
const OBS = ["#f8cecc", "#b85450"];
const TEST = ["#fce4ec", "#c2185b"];
const DEP = ["#eeeeee", "#666666"];
const SAT = ["#f5f5f5", "#999999"];

// ------------------------------------------------------------------ 1) ARQUITETURA
function buildArquitetura() {
  const d = new Diagram("arquitetura");
  d.label(360, 20, 900, "Busca-Busca — Arquitetura (visão geral)", { fontsize: 20, color: "#222222" });
  d.label(360, 46, 1100,
    "Java (Spring Boot) + Python (coleta) + Angular · PostgreSQL/PostGIS · RabbitMQ · Redis · Docker/K8s",
    { fontsize: 12, color: "#888888", bold: false });

  const cx = 560, w = 260, h = 60;
  const ys = [90, 194, 298, 402, 506, 610, 714, 818];
  const n_src = d.node(cx, ys[0], w, h, "<b>Caixa — CSV oficial</b><br/>(por UF · fonte primária)", SRC[0], SRC[1]);
  const n_coll = d.node(cx, ys[1], w, h, "<b>Coletor — Python</b><br/>download + parse + envio", COLL[0], COLL[1]);
  const n_ing = d.node(cx, ys[2], w, h, "<b>API de Ingestão — Java</b><br/>POST /internal/ingest", ING[0], ING[1]);
  const n_mq = d.node(cx, ys[3], w, h, "<b>RabbitMQ</b><br/>eventos p/ processamento assíncrono", MQ[0], MQ[1]);
  const n_proc = d.node(cx, ys[4], w, h, "<b>Workers — Java</b><br/>normalização · geocoding · custos · score", PROC[0], PROC[1]);
  const n_db = d.node(cx, ys[5], w, h, "<b>PostgreSQL 16 + PostGIS</b><br/>schema via Flyway", DB[0], DB[1]);
  const n_api = d.node(cx, ys[6], w, h, "<b>API REST — Java</b><br/>busca · filtros · detalhe · OpenAPI", API[0], API[1]);
  const n_front = d.node(cx, ys[7], w, h, "<b>Frontend — Angular</b><br/>lista · mapa · detalhe (Nginx)", FRONT[0], FRONT[1]);

  for (const [a, b] of [[n_src, n_coll], [n_coll, n_ing], [n_ing, n_mq], [n_mq, n_proc],
    [n_proc, n_db], [n_db, n_api], [n_api, n_front]]) {
    d.edge(a, b);
  }

  // satélites — enriquecimento por detalhe (ADR-0010)
  const n_det_src = d.node(250, ys[0], 220, h, "Caixa — página de detalhe<br/>fotos · edital · matrícula", SRC[0], SRC[1]);
  const n_det = d.node(250, ys[2], 220, 74,
    "<b>Coletor de detalhe — Python</b><br/>consome fila · raspa HTML · POST /detalhe", COLL[0], COLL[1]);
  d.edge(n_det_src, n_det, "GET detalhe", { dashed: true });
  d.edge(n_mq, n_det, "imovel.enriquecer", { dashed: true });
  d.edge(n_det, n_ing, "POST /detalhe");
  const n_obj = d.node(880, ys[4], 190, h, "Object Storage<br/>fotos · editais", SAT[0], SAT[1]);
  d.edge(n_proc, n_obj, "", { dashed: true, end: "none" });
  const n_redis = d.node(880, ys[6], 190, h, "Redis (cache)<br/>buscas quentes", SAT[0], SAT[1]);
  d.edge(n_api, n_redis, "cache", { dashed: true, end: "none" });

  // painel esquerdo: qualidade & CI
  d.band(40, 80, 190, 470, { fill: TEST[0], stroke: TEST[1] });
  d.label(56, 92, 170, "Qualidade & CI", { fontsize: 13, color: TEST[1] });
  ["GitHub Actions", "SonarQube<br/>(Quality Gate)", "Trivy<br/>(scan CVE)",
    "Testes<br/>(unit · integração · E2E)"].forEach((t, i) => {
    d.node(56, 128 + i * 100, 160, 74, t, "#ffffff", TEST[1], { fontsize: 11 });
  });

  // painel direito: observabilidade & SRE
  d.band(1110, 80, 210, 760, { fill: OBS[0], stroke: OBS[1] });
  d.label(1126, 92, 190, "Observabilidade & SRE", { fontsize: 13, color: OBS[1] });
  ["Métricas<br/>Micrometer→Prometheus", "Logs JSON<br/>Loki + correlation-id",
    "Traces<br/>OpenTelemetry→Tempo", "Dashboards · Alertas<br/>Grafana + Alertmanager",
    "Agente IA · AIOps<br/>(via MCP)", "Notificações<br/>Slack · Teams · E-mail"].forEach((t, i) => {
    d.node(1126, 128 + i * 116, 180, 88, t, "#ffffff", OBS[1], { fontsize: 11 });
  });

  // faixa de entrega (bottom)
  d.band(300, 930, 1000, 120, { fill: DEP[0], stroke: DEP[1] });
  d.label(316, 942, 400, "Entrega · GitOps (open source)", { fontsize: 13, color: DEP[1] });
  const dep = [];
  ["GitHub Actions", "Harbor<br/>(registry + Trivy)",
    "Argo CD<br/>(GitOps)", "k3s (VPS)<br/>Traefik · Helm · Rollouts"].forEach((t, i) => {
    dep.push(d.node(330 + i * 240, 976, 200, 60, t, "#ffffff", DEP[1], { fontsize: 11 }));
  });
  for (let i = 0; i < dep.length - 1; i++) d.edge(dep[i], dep[i + 1]);
  d.save();
}

// ------------------------------------------------------------------ 2) FLUXO GITOPS
function buildGitops() {
  const d = new Diagram("fluxo-gitops");
  d.label(40, 20, 1000, "Busca-Busca — Fluxo de Entrega (CI + GitOps + k3s)", { fontsize: 18, color: "#222222" });
  d.label(40, 46, 1100, "Padrão de 2 repositórios (app + config) · deploy declarativo com Argo CD",
    { fontsize: 12, color: "#888888", bold: false });

  const dev = d.node(40, 120, 150, 70, "<b>Dev</b><br/>commit / PR", FRONT[0], FRONT[1]);
  const app = d.node(240, 110, 240, 90,
    "<b>GitHub · busca-busca</b><br/>backend · collector · frontend<br/>deploy/k8s · .github/workflows", DEP[0], DEP[1]);
  const ci = d.node(540, 110, 250, 90,
    "<b>GitHub Actions (CI)</b><br/>build · testes · SonarQube<br/>Trivy · build+push imagem", COLL[0], COLL[1]);
  const harbor = d.node(850, 120, 200, 70, "<b>Harbor</b><br/>registry + Trivy + Cosign", FRONT[0], FRONT[1]);
  const gitops = d.node(540, 300, 250, 100,
    "<b>GitHub · busca-busca-gitops</b><br/>apps/ (app-of-apps)<br/>environments/{dev,staging,prod}", ING[0], ING[1]);
  const argo = d.node(850, 305, 200, 90, "<b>Argo CD</b><br/>watch · sync · rollback · self-heal", TEST[0], TEST[1]);

  const k8s = d.node(1120, 110, 300, 470, "<b>k3s (VPS Hostinger)</b>", DB[0], DB[1], { align: "left" });
  d.label(1140, 150, 260, "Traefik + cert-manager (Cloudflare DNS-01)", { fontsize: 11, color: "#555555", bold: false });
  ["namespace: dev", "namespace: staging", "namespace: prod"].forEach((name, i) => {
    d.node(1140, 190 + i * 100, 260, 80, `<b>${name}</b><br/>backend · collector · frontend`, "#ffffff", DB[1], { fontsize: 11 });
  });
  d.node(1140, 490, 260, 60, "PostgreSQL (CloudNativePG)", "#ffffff", DB[1], { fontsize: 11 });

  const obs = d.node(240, 470, 550, 90,
    "<b>Observabilidade & Agente IA (via MCP)</b><br/>" +
    "Métricas·Logs·Traces · diagnostica incidente · Slack/Teams/E-mail", OBS[0], OBS[1]);

  // exposição & acesso (Cloudflare / Traefik / Portainer / VPN)
  d.band(1110, 600, 320, 200, { fill: SRC[0], stroke: SRC[1] });
  d.label(1126, 612, 290, "Exposição & acesso · technodevbr.com", { fontsize: 13, color: SRC[1] });
  const cf = d.node(1126, 648, 140, 64, "Cloudflare<br/>DNS + TLS (proxy)", "#ffffff", SRC[1], { fontsize: 11 });
  const vpn = d.node(1280, 648, 135, 64, "VPN (Tailscale)<br/>acesso interno", "#ffffff", SRC[1], { fontsize: 11 });
  const portainer = d.node(1126, 726, 140, 60, "Portainer<br/>painel (público)", "#ffffff", SRC[1], { fontsize: 11 });
  const internal = d.node(1280, 726, 135, 60, "app · argo · grafana<br/>(interno)", "#ffffff", SRC[1], { fontsize: 11 });

  d.edge(dev, app, "push");
  d.edge(app, ci, "trigger");
  d.edge(ci, harbor, "push imagem");
  d.edge(ci, gitops, "bump da tag");
  d.edge(gitops, argo, "watch");
  d.edge(harbor, argo, "pull imagem", { dashed: true });
  d.edge(argo, k8s, "sync / apply");
  d.edge(k8s, obs, "telemetria", { dashed: true });
  d.edge(obs, dev, "issue / alerta diagnosticado", { dashed: true });
  d.edge(cf, k8s, "→ Traefik", { dashed: true });
  d.edge(vpn, k8s, "→ Traefik", { dashed: true });
  d.edge(cf, portainer, "público");
  d.edge(vpn, internal, "VPN");
  d.save();
}

// ------------------------------------------------------------------ 3) BANCO DE DADOS
function buildBanco() {
  const d = new Diagram("banco-dados");
  d.label(40, 20, 900, "Busca-Busca — Esquema do banco (PostgreSQL + PostGIS)", { fontsize: 18, color: "#222222" });
  d.label(40, 46, 1000, "PK = chave primária · FK = chave estrangeira · 1..* = um para muitos",
    { fontsize: 12, color: "#888888", bold: false });
  d.node(40, 780, 240, 96,
    "<b>Padrão de auditoria</b> (todas as tabelas,<br/>exceto referência)<br/>" +
    "<hr size='1'/>criado_em · atualizado_em<br/>excluido_em (exclusão lógica / soft delete)",
    "#fff2cc", "#d6b656", { fontsize: 11, align: "left" });

  const entity = (x, y, title, fields, fill, stroke, w = 290) => {
    const rows = fields.join("<br/>");
    const h = 34 + fields.length * 18;
    const label = `<b>${title}</b><br/><hr size='1'/>${rows}`;
    return d.node(x, y, w, h, label, fill, stroke, { fontsize: 11, align: "left" });
  };

  // tabelas de referência (vocabulário controlado)
  const municipio = entity(40, 100, "municipio", ["PK id", "codigo_ibge · UNIQUE", "nome · uf"], COLL[0], COLL[1], 210);
  const tipo = entity(40, 240, "tipo_imovel", ["PK id", "nome · UNIQUE"], COLL[0], COLL[1], 210);
  const modalidade = entity(40, 350, "modalidade_venda", ["PK id", "nome · UNIQUE"], COLL[0], COLL[1], 210);

  // tabelas filhas de imovel
  const foto = entity(310, 100, "imovel_foto", ["PK id", "FK imovel_id", "url · ordem", "UNIQUE(imovel_id, ordem)"], API[0], API[1], 230);
  const historico = entity(310, 260, "historico_preco", ["PK id", "FK imovel_id", "valor · desconto_pct", "status (status_imovel)", "capturado_em"], API[0], API[1], 230);
  const analise = entity(310, 430, "analise_custo", ["PK id", "FK imovel_id (1..1)", "itbi · custas · registro", "dividas · reforma_estimada", "custo_total · desconto_real_pct", "score · status_confianca", "calculado_em"], API[0], API[1], 230);
  const coleta = entity(310, 640, "coleta_bruta", ["PK id", "fonte (csv/detalhe) · uf · codigo", "payload_bruto (bytea · zstd)", "compressao · payload_hash · tamanho_bytes", "coletado_em · retenção ~90d"], SAT[0], SAT[1], 250);

  // núcleo
  const imovel = entity(620, 100, "imovel", ["PK id", "codigo · UNIQUE por fonte", "FK tipo_imovel_id · FK modalidade_venda_id", "FK municipio_id · bairro · endereco", "localizacao (geography Point 4326)", "area_total · area_privativa · area_terreno", "quartos", "valor_avaliacao · valor_minimo · desconto_pct", "status (status_imovel)", "criado_em · atualizado_em"], DB[0], DB[1], 330);
  const detalhe = entity(620, 470, "imovel_detalhe (1..1)", ["PK id · FK imovel_id · UNIQUE", "valor_primeiro/segundo_leilao", "data_primeiro/segundo_leilao", "leiloeiro · edital · numero_item", "matricula · comarca · oficio", "inscricao_imobiliaria · cep", "endereco_completo", "aceita_fgts · aceita_financiamento", "despesas_condominio/tributos_comprador", "situacao_ocupacao · descricao_completa", "edital_url · matricula_url", "enriquecido_em · status_enriquecimento"], SAT[0], SAT[1], 340);

  const usuario = entity(1010, 100, "usuario", ["PK id", "email · UNIQUE", "nome · avatar_url", "provedor · provedor_id (OIDC)", "UNIQUE(provedor, provedor_id)"], ING[0], ING[1], 220);
  const favorito = entity(1010, 280, "favorito", ["PK id", "FK usuario_id", "FK imovel_id", "criado_em", "UNIQUE(usuario_id, imovel_id)"], ING[0], ING[1], 220);
  const alerta = entity(1010, 470, "alerta", ["PK id", "FK usuario_id", "filtro (jsonb)", "canal (canal_alerta) · ativo", "criado_em"], ING[0], ING[1], 220);
  const token = entity(1010, 630, "token_atualizacao", ["PK id", "FK usuario_id", "token_hash · UNIQUE", "familia_id (uuid)", "expira_em · revogado_em", "substituido_por (FK self)", "user_agent · ip"], SAT[0], SAT[1], 220);

  d.edge(municipio, imovel, "FK");
  d.edge(tipo, imovel, "FK");
  d.edge(modalidade, imovel, "FK");
  d.edge(imovel, foto, "1..*", { end: "none" });
  d.edge(imovel, historico, "1..*", { end: "none" });
  d.edge(imovel, analise, "1..1", { end: "none" });
  d.edge(imovel, detalhe, "1..1", { end: "none" });
  d.edge(coleta, imovel, "por codigo", { dashed: true, end: "none" });
  d.edge(usuario, favorito, "1..*", { end: "none" });
  d.edge(imovel, favorito, "1..*", { end: "none" });
  d.edge(usuario, alerta, "1..*", { end: "none" });
  d.edge(usuario, token, "1..*", { end: "none" });
  d.save();
}

function buildSequencia() {
  const d = new Diagram("sequencia-fluxo");
  d.label(40, 20, 1200, "Busca-Busca — Sequência: coleta → ingestão → enriquecimento → recálculo → consulta",
    { fontsize: 17, color: "#222222" });

  // lifelines (centro x, título, cor)
  const lanes = [
    [110, "Coletor (Python)", COLL],
    [330, "API Ingestão (Java)", ING],
    [540, "RabbitMQ", MQ],
    [740, "Worker (Java)", PROC],
    [950, "PostgreSQL", DB],
    [1170, "API Pública (Java)", API],
    [1390, "Frontend (Angular)", FRONT],
  ];
  const top = 60, bottom = 900;
  const cx = {};
  for (const [x, titulo, [fill, stroke]] of lanes) {
    d.node(x - 85, top, 170, 40, `<b>${titulo}</b>`, fill, stroke, { fontsize: 11 });
    d.lifeline(x, top, bottom);
    cx[titulo] = x;
  }

  const C = cx["Coletor (Python)"], I = cx["API Ingestão (Java)"], M = cx["RabbitMQ"],
    W = cx["Worker (Java)"], DBx = cx["PostgreSQL"], P = cx["API Pública (Java)"], F = cx["Frontend (Angular)"];

  let y = 130;
  const step = 44;
  const m = (a, b, label, dashed = false) => {
    d.msg(a, y, b, label, { dashed });
    y += step;
  };

  m(C, I, "POST /internal/ingest/imoveis (lote CSV)");
  m(I, DBx, "upsert imovel · coleta_bruta · historico_preco (na mudança)");
  m(I, M, "publica imovel.recebido / imovel.enriquecer");
  m(I, C, "202 Accepted", true);
  m(M, W, "imovel.recebido");
  m(W, DBx, "normaliza · geocoding · calcula custo/score");
  m(M, C, "imovel.enriquecer (consumer detalhe)");
  // ação externa do coletor (GET no site) — caixinha na lifeline do coletor
  d.node(C - 90, y - 14, 180, 30, "GET detalhe-imovel.asp (site Caixa)", SAT[0], SAT[1], { fontsize: 10 });
  y += step;
  m(C, I, "POST /internal/ingest/imoveis/{codigo}/detalhe");
  m(I, DBx, "upsert imovel_detalhe · fotos");
  m(I, M, "publica imovel.enriquecido");
  m(M, W, "imovel.enriquecido");
  m(W, DBx, "recalcula analise_custo (RF-06/07)");
  m(F, P, "GET /api/v1/imoveis (busca/filtros)");
  m(P, DBx, "query + cache Redis");
  m(P, F, "200 · resultados", true);
  d.save();
}

function buildSequenciaLogin() {
  const d = new Diagram("sequencia-login");
  d.label(40, 20, 1200, "Busca-Busca — Sequência: login social (OIDC + PKCE) · refresh · logout",
    { fontsize: 17, color: "#222222" });

  const lanes = [
    [170, "Frontend (Angular)", FRONT],
    [500, "Backend (Spring Security)", API],
    [830, "IdP (Google/GitHub)", COLL],
    [1120, "PostgreSQL", DB],
  ];
  const top = 60, bottom = 930;
  const cx = {};
  for (const [x, titulo, [fill, stroke]] of lanes) {
    d.node(x - 95, top, 190, 40, `<b>${titulo}</b>`, fill, stroke, { fontsize: 11 });
    d.lifeline(x, top, bottom);
    cx[titulo] = x;
  }

  const F = cx["Frontend (Angular)"], B = cx["Backend (Spring Security)"],
    P = cx["IdP (Google/GitHub)"], DBx = cx["PostgreSQL"];

  let y = 128;
  const step = 38;
  const m = (a, b, label, dashed = false) => {
    d.msg(a, y, b, label, { dashed });
    y += step;
  };
  const fase = (txt) => {
    d.label(36, y - 6, 130, txt, { fontsize: 11, color: "#8a56ac" });
    y += 26;
  };

  fase("1 · Login");
  m(F, B, "GET /oauth2/authorization/{provedor}");
  m(B, F, "302 → provedor (authorize + PKCE + state)", true);
  m(F, P, "login + consentimento");
  m(P, F, "302 code → /login/oauth2/code/{provedor}", true);
  m(F, B, "GET /login/oauth2/code (code)");
  m(B, P, "troca code → tokens (valida id_token/nonce)");
  m(P, B, "id_token + userinfo", true);
  m(B, DBx, "upsert usuario (provedor+provedor_id) · cria refresh (familia)");
  m(B, F, "302 app + Set-Cookie ACCESS+REFRESH (HttpOnly)", true);
  m(F, B, "GET /api/v1/auth/me");
  m(B, F, "200 · Usuario", true);

  fase("2 · Renovação");
  m(F, B, "request protegido (ACCESS expirado)");
  m(B, F, "401", true);
  m(F, B, "POST /api/v1/auth/refresh (cookie REFRESH)");
  m(B, DBx, "valida hash · rotaciona (revoga antigo, detecta reúso)");
  m(B, F, "204 + Set-Cookie novos ACCESS+REFRESH", true);

  fase("3 · Logout");
  m(F, B, "POST /api/v1/auth/logout");
  m(B, DBx, "revoga refresh (familia / todos dispositivos)");
  m(B, F, "204", true);
  d.save();
}

function main() {
  mkdirSync(OUTDIR, { recursive: true });
  buildArquitetura();
  buildGitops();
  buildBanco();
  buildSequencia();
  buildSequenciaLogin();
  console.log("Diagramas gerados em docs/public/diagramas/");
}

main();

import { defineConfig } from 'vitepress'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const CONFIG_DIR = path.dirname(fileURLToPath(import.meta.url)) // docs/.vitepress
const DOCS_ROOT = path.resolve(CONFIG_DIR, '..') // docs/

// Ordem e rotulos das secoes de topo (pastas dentro de docs/).
const SECTIONS: { dir: string; text: string }[] = [
  { dir: 'visao-geral', text: 'Visao geral' },
  { dir: 'produto', text: 'Produto' },
  { dir: 'arquitetura', text: 'Arquitetura' },
  { dir: 'dominio', text: 'Dominio' },
  { dir: 'contratos', text: 'Contratos' },
  { dir: 'dados', text: 'Dados' },
  { dir: 'servicos', text: 'Servicos' },
  { dir: 'infraestrutura', text: 'Infraestrutura' },
  { dir: 'observabilidade', text: 'Observabilidade' },
  { dir: 'qualidade', text: 'Qualidade' },
  { dir: 'legal', text: 'Legal & conformidade' },
]

function firstHeading(absFile: string, fallback: string): string {
  try {
    const content = fs.readFileSync(absFile, 'utf-8')
    const m = content.match(/^#\s+(.+?)\s*$/m)
    if (m) return m[1].replace(/[`*_]/g, '').trim()
  } catch {
    /* ignore */
  }
  return fallback
}

function toLink(absFile: string): string {
  let rel = path.relative(DOCS_ROOT, absFile).split(path.sep).join('/')
  rel = rel.replace(/README\.md$/i, '').replace(/\.md$/i, '')
  return '/' + rel
}

// VitePress nao trata README.md como index automaticamente. Varremos todos os
// README.md e mapeamos README.md -> index.md para que '/', '/produto/', etc. existam.
function buildReadmeRewrites(dir: string, acc: Record<string, string> = {}): Record<string, string> {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const abs = path.join(dir, e.name)
    if (e.isDirectory()) {
      buildReadmeRewrites(abs, acc)
    } else if (e.isFile() && e.name.toLowerCase() === 'readme.md') {
      const rel = path.relative(DOCS_ROOT, abs).split(path.sep).join('/')
      acc[rel] = rel.replace(/README\.md$/i, 'index.md')
    }
  }
  return acc
}

// Constroi os itens de uma pasta (arquivos .md + subpastas recursivamente).
function buildItems(dir: string): any[] {
  const entries = fs.readdirSync(dir, { withFileTypes: true })
  const files = entries
    .filter((e) => e.isFile() && e.name.endsWith('.md') && e.name.toLowerCase() !== 'readme.md')
    .sort((a, b) => a.name.localeCompare(b.name))
  const dirs = entries
    .filter((e) => e.isDirectory())
    .sort((a, b) => a.name.localeCompare(b.name))

  const items: any[] = []
  for (const f of files) {
    const abs = path.join(dir, f.name)
    items.push({ text: firstHeading(abs, f.name.replace(/\.md$/i, '')), link: toLink(abs) })
  }
  for (const d of dirs) {
    const sub = path.join(dir, d.name)
    const readme = path.join(sub, 'README.md')
    const group: any = {
      text: fs.existsSync(readme) ? firstHeading(readme, d.name) : d.name,
      collapsed: true,
      items: buildItems(sub),
    }
    if (fs.existsSync(readme)) group.link = toLink(readme)
    items.push(group)
  }
  return items
}

function buildSidebar(): any[] {
  const groups: any[] = []
  for (const s of SECTIONS) {
    const dir = path.join(DOCS_ROOT, s.dir)
    if (!fs.existsSync(dir)) continue
    const readme = path.join(dir, 'README.md')
    const group: any = {
      text: s.text,
      collapsed: true,
      items: buildItems(dir),
    }
    if (fs.existsSync(readme)) group.link = toLink(readme)
    groups.push(group)
  }
  return groups
}

export default defineConfig({
  lang: 'pt-BR',
  title: 'Busca-Busca',
  description:
    'Documentacao docs-first da plataforma de busca e pre-analise de imoveis em leilao.',
  // Dominio proprio (GitHub Pages) serve na raiz -> base '/'.
  // Se voltar a usar a URL technodev-br.github.io/busca-docs/, troque para '/busca-docs/'.
  base: '/',
  cleanUrls: true,
  rewrites: buildReadmeRewrites(DOCS_ROOT),
  lastUpdated: true,
  // Checagem real de links quebrados (.md). Ignora apenas links para arquivos-fonte
  // (.yaml/.drawio) e localhost, que nao sao paginas do site.
  ignoreDeadLinks: [/\.ya?ml(#.*)?$/, /\.drawio(#.*)?$/, 'localhostLinks'],
  themeConfig: {
    logo: undefined,
    outline: { level: [2, 3], label: 'Nesta pagina' },
    search: { provider: 'local' },
    nav: [
      { text: 'Inicio', link: '/' },
      { text: 'Visao geral', link: '/visao-geral/' },
      { text: 'Produto', link: '/produto/' },
      { text: 'Arquitetura', link: '/arquitetura/' },
      { text: 'Servicos', link: '/servicos/' },
      { text: 'Infraestrutura', link: '/infraestrutura/' },
    ],
    sidebar: buildSidebar(),
    socialLinks: [
      { icon: 'github', link: 'https://github.com/Technodev-BR/busca-docs' },
    ],
    docFooter: { prev: 'Anterior', next: 'Proxima' },
    darkModeSwitchLabel: 'Tema',
    returnToTopLabel: 'Voltar ao topo',
    sidebarMenuLabel: 'Menu',
    lastUpdated: { text: 'Atualizado em' },
  },
})

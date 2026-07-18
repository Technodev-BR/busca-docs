// Garante que cada diagrama .drawio tenha um .svg correspondente em
// docs/public/diagramas/. Se faltar (ambiente local, sem render do draw.io),
// cria um placeholder para o build do VitePress nunca quebrar por imagem ausente.
// No deploy (CI), os SVGs reais ja foram renderizados dos .drawio, entao este
// script nao sobrescreve nada (so cria o que estiver faltando).
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const DIR = path.resolve(HERE, '..', 'docs', 'public', 'diagramas')

function placeholder(name) {
  const title = name.replace(/[-_]/g, ' ')
  return `<svg xmlns="http://www.w3.org/2000/svg" width="760" height="200" viewBox="0 0 760 200">
  <rect width="760" height="200" rx="10" fill="#f3f6fb" stroke="#cbd5e1"/>
  <text x="380" y="92" font-family="Segoe UI, Arial, sans-serif" font-size="20" font-weight="600" fill="#334155" text-anchor="middle">${title}</text>
  <text x="380" y="124" font-family="Segoe UI, Arial, sans-serif" font-size="13" fill="#64748b" text-anchor="middle">Diagrama renderizado no build (CI) a partir do .drawio</text>
</svg>
`
}

if (!fs.existsSync(DIR)) {
  console.log('[diagramas] pasta docs/public/diagramas nao encontrada; nada a fazer.')
  process.exit(0)
}

const drawios = fs.readdirSync(DIR).filter((f) => f.toLowerCase().endsWith('.drawio'))
let created = 0
for (const f of drawios) {
  const svgPath = path.join(DIR, f.replace(/\.drawio$/i, '.svg'))
  if (!fs.existsSync(svgPath)) {
    fs.writeFileSync(svgPath, placeholder(f.replace(/\.drawio$/i, '')))
    created++
  }
}
console.log(`[diagramas] ${drawios.length} .drawio encontrado(s); ${created} placeholder(s) SVG criado(s).`)

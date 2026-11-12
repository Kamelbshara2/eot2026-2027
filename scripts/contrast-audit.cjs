// Contrast audit (WCAG AA) of the student pages in every theme. Usage: node scripts/contrast-audit.cjs [baseURL] [--json out.json]
// For every visible element that owns text, the effective background is found by walking up to the first opaque
// background colour; gradient/image backgrounds are sampled by their first colour stop. Large text (>=24px, or
// >=18.66px bold) needs 3:1, other text 4.5:1.
const {chromium} = require('playwright');
const U = process.argv[2] && !process.argv[2].startsWith('--') ? process.argv[2] : 'http://localhost:5199/';
const PAGES = [
  ['home', '#/'],
  ['class', '#/classrooms/9G3/banks/term1'],
  ['mcq+solution', '#/classrooms/9G3/banks/term1/outcomes/LO01', 'solution'],
  ['calculator', '#/classrooms/10A1/banks/term1/outcomes/LO19', 'calc'],
  ['frq-numberline', '#/classrooms/9A/banks/term1/outcomes/LO21', 'nl'],
  ['card-12G', '#/classrooms/12G/banks/term1/outcomes/LO06'],
  ['mock', '#/classrooms/9G3/banks/term1/mock'],
  ['quiz', '#/classrooms/10G3/banks/term1/quiz'],
];
const scan = () => {
  const parse = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1}; };
  const lum = ({r, g, b}) => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
  const blend = (top, bot) => ({r: top.r * top.a + bot.r * (1 - top.a), g: top.g * top.a + bot.g * (1 - top.a), b: top.b * top.a + bot.b * (1 - top.a), a: 1});
  const bgOf = el => {
    const layers = [];
    for (let e = el; e; e = e.parentElement) {
      const cs = getComputedStyle(e);
      const img = cs.backgroundImage.match(/rgba?\([^)]+\)/);
      const col = parse(cs.backgroundColor);
      if (col && col.a > 0) { layers.push(col); if (col.a >= 0.99) break; }
      else if (img && cs.backgroundImage !== 'none') { const c = parse(img[0]); if (c) { layers.push({...c, a: Math.max(c.a, 0.99)}); break; } }
    }
    let base = {r: 255, g: 255, b: 255, a: 1};
    const root = parse(getComputedStyle(document.documentElement).backgroundColor); if (root && root.a > 0.99) base = root;
    return layers.reverse().reduce((acc, l) => blend(l, acc), base);
  };
  const out = [];
  for (const el of document.querySelectorAll('body *')) {
    if (!el.childNodes.length || el.closest('.katex-mathml,[aria-hidden=true],svg,script,style,.question-watermark,.shield-cover')) continue;
    const text = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join(' ').trim();
    if (!text) continue;
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    if (!r.width || !r.height || cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue;
    let hidden = false; for (let e = el; e; e = e.parentElement) { if (e.hidden || getComputedStyle(e).display === 'none') { hidden = true; break; } if (e.tagName === 'DETAILS' && !e.open && !el.closest('summary')) { hidden = true; break; } } if (hidden) continue;
    const fg = parse(cs.color); if (!fg) continue;
    const bg = bgOf(el), col = blend(fg, bg);
    const L1 = lum(col), L2 = lum(bg), ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const size = parseFloat(cs.fontSize), bold = +cs.fontWeight >= 700, large = size >= 24 || (bold && size >= 18.66);
    const need = large ? 3 : 4.5;
    if (ratio < need) out.push({sel: el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : ''), text: text.slice(0, 40), fg: cs.color, bg: `rgb(${bg.r | 0}, ${bg.g | 0}, ${bg.b | 0})`, ratio: +ratio.toFixed(2), need});
  }
  return out;
};
(async () => {
  const b = await chromium.launch(); const all = [];
  for (const theme of ['current', 'studio', 'masar']) {
    const p = await b.newPage({viewport: {width: 1280, height: 900}});
    await p.addInitScript(t => { try { localStorage.setItem('math100-student-theme-v1', t); } catch {} }, theme);
    for (const [name, hash, action] of PAGES) {
      await p.goto(U + hash); await p.waitForTimeout(1100);
      const ii = await p.$$('dialog[open] input'); if (ii.length) { await ii[0].fill('طالب'); await ii[1].fill('مدرسة'); await p.click('dialog[open] button[type=submit]'); await p.waitForTimeout(900); await p.goto(U + hash); await p.waitForTimeout(1100); }
      if (action === 'solution') await p.click('[data-help=solution]').catch(() => {});
      if (action === 'calc') await p.click('[data-help=calc]').catch(() => {});
      if (action === 'nl') { const n = await p.locator('#study-practice-select option').count(); for (let i = 0; i < n; i++) { await p.selectOption('#study-practice-select', String(i)); await p.waitForTimeout(80); if (await p.locator('#study-practice .nl-box').count()) break; } }
      await p.waitForTimeout(400);
      const res = await p.evaluate(scan);
      const seen = new Map(); for (const r of res) { const k = r.sel + r.fg + r.bg; if (!seen.has(k)) seen.set(k, {...r, count: 0}); seen.get(k).count++; }
      for (const v of seen.values()) all.push({theme, page: name, ...v});
    }
    await p.close();
  }
  await b.close();
  const byTheme = {}; for (const r of all) byTheme[r.theme] = (byTheme[r.theme] || 0) + r.count;
  console.log('low-contrast text elements by theme:', byTheme);
  for (const r of all.sort((a, b) => a.ratio - b.ratio).slice(0, 80)) console.log(`${r.theme.padEnd(7)} ${r.page.padEnd(15)} ${String(r.ratio).padEnd(5)}/${r.need} x${r.count} ${r.sel} "${r.text}" ${r.fg} on ${r.bg}`);
  const j = process.argv.indexOf('--json'); if (j > 0) require('fs').writeFileSync(process.argv[j + 1], JSON.stringify(all, null, 1));
})();

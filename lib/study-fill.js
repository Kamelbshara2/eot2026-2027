// Fill-in-the-blank engine for written (FRQ) study questions.
// Template syntax inside a LaTeX line:
//   [[answer|alt]]      equivalent-expression blank (2r+12 == 12+2r, 1/2 == 0.5)
//   [[!answer|alt]]     exact blank (normalised text must match, no algebra)
//   [[answer#g]]        unordered group g: answers of a group may be entered in any order
//   [[?A;B;C|B]]        drop-down choice, correct label after the bar
import katex from 'katex';

export const BLANK = /\[\[(.+?)\]\]/g;
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

export function parseLine(line, state = {n: 0}) {
  const out = []; let last = 0, m;
  const re = new RegExp(BLANK.source, 'g');
  while ((m = re.exec(line))) {
    if (m.index > last) out.push({kind: 'tex', value: line.slice(last, m.index)});
    let body = m[1], group = null, select = null, exact = false, tol = 0;
    const g = body.match(/#([A-Za-z0-9_]+)$/); if (g) { group = g[1]; body = body.slice(0, -g[0].length); }
    if (body.startsWith('?')) {
      const [opts, ans] = body.slice(1).split(/\|(?=[^|]*$)/);
      select = opts.split(';').map(s => s.trim()); body = ans;
    } else if (body.startsWith('!')) { exact = true; body = body.slice(1); }
    else { const t = body.match(/^~([0-9.]+):/); if (t) { tol = Number(t[1]); body = body.slice(t[0].length); } }
    out.push({kind: 'blank', index: state.n++, answers: body.split('|').map(s => s.trim()), group, select, exact, tol});
    last = m.index + m[0].length;
  }
  if (last < line.length) out.push({kind: 'tex', value: line.slice(last)});
  return out;
}

export function parseBlanks(spec) {
  const state = {n: 0};
  const lines = (spec.lines || []).map(l => ({label: null, segments: parseLine(l, state)}));
  // tables: [{caption, xlabel, ylabel, xs, ys, end}]  (end = index of the endpoint column, marked in the header)
  const tables = [...(spec.table ? [spec.table] : []), ...(spec.tables || [])].map(t => ({
    ...t,
    xs: t.xs.map(String),
    cells: t.ys.map(a => ({kind: 'blank', index: state.n++, answers: String(a).split('|'), group: null, select: null, exact: false, tol: 0}))
  }));
  return {lines, tables, table: tables[0] || null, count: state.n};
}

// ---------- normalisation & equivalence ----------
export function norm(s) {
  let t = String(s ?? '').trim().toLowerCase();
  t = t.replace(/[−–—]/g, '-').replace(/[×·]/g, '*').replace(/÷/g, '/').replace(/\\(?:cdot|times)/g, '*').replace(/\\div/g, '/')
    .replace(/\\(?:left|right|,|;|!|quad|qquad)/g, '').replace(/\\[dt]frac/g, '\\frac').replace(/\\text\{([^}]*)\}/g, '$1')
    .replace(/\\ell|ℓ/g, 'l').replace(/\\pi|π/g, 'pi').replace(/\\infty|∞/g, 'inf').replace(/\\varnothing|∅/g, 'empty').replace(/\\mathbb\{?r\}?|ℝ/g, 'R'.toLowerCase())
    .replace(/√\s*([a-z0-9.]+)/g, 'sqrt($1)').replace(/\\sqrt/g, 'sqrt').replace(/\\circ|°/g, '').replace(/sqrt\{([^{}]*)\}/g, 'sqrt($1)')
    .replace(/²/g, '^2').replace(/³/g, '^3').replace(/\s+/g, '');
  for (let i = 0; i < 6; i++) t = t.replace(/\\frac\{([^{}]*)\}\{([^{}]*)\}/g, '(($1)/($2))').replace(/\\frac(\d)(\d)/g, '(($1)/($2))');
  t = t.replace(/sqrt\{([^{}]*)\}/g, 'sqrt($1)').replace(/\^\{([^{}]*)\}/g, '^($1)').replace(/_\{([^{}]*)\}/g, '_$1').replace(/[{}]/g, m => m === '{' ? '(' : ')');
  return t.replace(/sqrt(\d+(?:\.\d+)?)/g, 'sqrt($1)');
}

function toJs(t) {
  const tokens = t.match(/sqrt|pi|inf|\d+(?:\.\d+)?|\.\d+|[a-z]|\*\*|[()+\-*/^_,]/g);
  if (!tokens || tokens.join('') !== t.replace(/_/g, '_')) return null;
  const vars = new Set(); let js = '', prev = null;
  const isVal = x => x && (/^[\d.]/.test(x) || /^[a-z]$/.test(x) || x === 'pi' || x === 'inf' || x === ')');
  for (let i = 0; i < tokens.length; i++) {
    const x = tokens[i];
    if (x === '_') return null;
    const startsVal = /^[\d.]/.test(x) || /^[a-z]$/.test(x) || x === 'pi' || x === 'inf' || x === '(' || x === 'sqrt';
    if (isVal(prev) && startsVal && !(prev === ')' && x === ')')) js += '*';
    if (x === '^') js += '**';
    else if (x === 'sqrt') js += 'Math.sqrt';
    else if (x === 'pi') js += 'Math.PI';
    else if (x === 'inf') js += 'Infinity';
    else if (/^[a-z]$/.test(x)) { vars.add(x); js += `V.${x}`; }
    else js += x;
    prev = x;
  }
  return {js, vars: [...vars]};
}
const SAMPLES = [1.7, -2.3, 0.9, 3.1, -0.6, 2.4];
function evaluate(t) {
  const c = toJs(t); if (!c) return null;
  const vs = c.vars, pts = vs.length ? [0, 1, 2, 3].map(k => Object.fromEntries(vs.map((v, i) => [v, SAMPLES[(i + k * 2) % SAMPLES.length] + k * 0.13]))) : [{}];
  try {
    const f = new Function('V', `return (${c.js})`);
    const out = pts.map(p => f(p));
    return out.every(Number.isFinite) || out.every(v => v === Infinity || v === -Infinity) ? {vars: vs, values: out} : null;
  } catch { return null; }
}
const close = (a, b) => Math.abs(a - b) <= 1e-6 * Math.max(1, Math.abs(a), Math.abs(b));
export function sameValue(student, answer, {exact = false, tolerance = 0} = {}) {
  const a = norm(student), b = norm(answer);
  if (!a) return false;
  if (a === b) return true;
  if (exact) return false;
  const ea = evaluate(a), eb = evaluate(b);
  if (!ea || !eb || ea.vars.join() !== eb.vars.join()) return false;
  return ea.values.every((v, i) => tolerance ? Math.abs(v - eb.values[i]) <= tolerance : close(v, eb.values[i]));
}

// blanks: array of parsed blank objects, values: array of student strings
export function checkBlanks(blanks, values) {
  const result = blanks.map(() => false), used = new Map();
  blanks.forEach((b, i) => {
    const v = values[i] ?? '';
    if (b.group) return;
    result[i] = b.select ? b.answers.includes(v) : b.answers.some(a => sameValue(v, a, {exact: b.exact, tolerance: b.tol}));
  });
  const groups = new Map();
  blanks.forEach((b, i) => { if (b.group) { if (!groups.has(b.group)) groups.set(b.group, []); groups.get(b.group).push(i); } });
  for (const idxs of groups.values()) {
    const pool = idxs.flatMap(i => blanks[i].answers.slice(0, 1));
    const taken = new Set();
    idxs.forEach(i => {
      const k = pool.findIndex((a, j) => !taken.has(j) && sameValue(values[i] ?? '', a, {exact: blanks[i].exact, tolerance: blanks[i].tol}));
      if (k >= 0) { taken.add(k); result[i] = true; }
    });
  }
  return result;
}

// ---------- student input -> LaTeX preview ----------
export function toTex(s) {
  let t = String(s ?? '').trim();
  if (!/[\^/*]|sqrt|pi|<=|>=|\\/.test(t) && !/\d\(|\)\(/.test(t)) return '';
  t = t.replace(/[−–]/g, '-').replace(/\bpi\b/g, '\\pi');
  const operand = '(sqrt\\([^()]*\\)|\\([^()]*\\)|[A-Za-z0-9.]+)';
  t = t.replace(new RegExp(operand + '\\s*/\\s*' + operand, 'g'), (m, a, b) => `\\frac{${a.replace(/^\((.*)\)$/, '$1')}}{${b.replace(/^\((.*)\)$/, '$1')}}`);
  t = t.replace(/sqrt\(([^()]*)\)/g, '\\sqrt{$1}');
  t = t.replace(/\^(\([^()]*\)|[A-Za-z0-9.]+)/g, (m, a) => `^{${a.replace(/^\((.*)\)$/, '$1')}}`).replace(/\*/g, '\\cdot ').replace(/<=/g, '\\le ').replace(/>=/g, '\\ge ');
  return t;
}
const tex = (s, display = false) => { try { return katex.renderToString(s, {throwOnError: false, strict: 'ignore', displayMode: display}); } catch { return esc(s); } };

// ---------- DOM markup ----------
// Lines are rendered by KaTeX as ONE formula (so blanks may sit inside fractions/powers); each blank is a
// placeholder slot that wireFill() swaps for a real <input>/<select>.
const TRUST = c => ['\\htmlClass', '\\htmlData'].includes(c.command);
const texSlots = (s, display = false, strict = false) => katex.renderToString(s, {throwOnError: strict, strict: 'ignore', displayMode: display, trust: TRUST});
const slotTex = b => `\\htmlData{slot=${b.index}}{\\phantom{${'0'.repeat(Math.min(6, Math.max(2, Math.max(...b.answers.map(a => a.length)))))}}}`;
export const lineTex = segments => segments.map(s => s.kind === 'tex' ? s.value : slotTex(s)).join('');
const widthFor = b => Math.max(3, Math.min(16, Math.max(...b.answers.map(a => a.length)) + 2));
function blankHtml(b, prefix) {
  const id = `${prefix}-${b.index}`;
  if (b.select) return `<select class="fill-blank fill-select" data-blank="${b.index}" id="${id}" aria-label="اختيار · choice ${b.index + 1}"><option value="">؟</option>${b.select.map(o => `<option value="${esc(o)}">${esc(o)}</option>`).join('')}</select>`;
  return `<input class="fill-blank" data-blank="${b.index}" id="${id}" size="${widthFor(b)}" dir="ltr" autocomplete="off" autocapitalize="off" spellcheck="false" inputmode="text" aria-label="فراغ ${b.index + 1} · blank ${b.index + 1}"><span class="fill-tex" aria-hidden="true"></span>`;
}
// one value table; the endpoint column (t.end) is labelled so students know the 3rd point is the boundary point
function tableHtml(t, cell) {
  const head = (x, i) => i === t.end ? `<td class="fill-end">${tex(x)}<small>${esc(t.end_label || 'endpoint · نقطة الحد')}</small></td>` : `<td>${tex(x)}</td>`;
  const cap = t.caption ? `<div class="fill-table-cap" dir="ltr"><b>${esc(t.caption)}</b> ${t.caption_tex ? tex(t.caption_tex) : ''}</div>` : '';
  return `${cap}<table class="fill-table" dir="ltr"><tr><th>${tex(t.xlabel || 'x')}</th>${t.xs.map(head).join('')}</tr><tr><th>${tex(t.ylabel || 'y')}</th>${t.cells.map(c => `<td>${cell(c)}</td>`).join('')}</tr></table>`;
}
export function fillMarkup(spec, prefix) {
  const p = parseBlanks(spec);
  const lines = p.lines.map(l => `<div class="fill-line" dir="ltr">${texSlots(lineTex(l.segments))}</div>`).join('');
  const cell = c => `<span class="fill-slot" data-slot="${c.index}"></span>`;
  const table = p.tables.map(t => tableHtml(t, cell)).join('');
  return {html: `<div class="fill-box" data-prefix="${esc(prefix)}">${lines}${table}</div>`, parsed: p};
}
export function validateLines(spec) {
  const p = parseBlanks(spec);
  p.lines.forEach(l => texSlots(lineTex(l.segments), false, true));
  return p;
}
export function flatBlanks(parsed) {
  return [...parsed.lines.flatMap(l => l.segments.filter(s => s.kind === 'blank')), ...(parsed.tables || []).flatMap(t => t.cells)].sort((a, b) => a.index - b.index);
}
export function answerText(b) { return b.select ? b.answers[0] : b.answers[0]; }

// Wire a rendered .fill-box: returns {check(), reveal(), reset(), values()}
export function wireFill(root, parsed, onChange = () => {}) {
  const blanks = flatBlanks(parsed);
  const prefix = root.dataset.prefix || 'fb';
  blanks.forEach(b => { const slot = root.querySelector(`[data-slot="${b.index}"]`); if (slot && !slot.querySelector('.fill-blank')) { slot.innerHTML = blankHtml(b, prefix); slot.classList.add('is-live'); } });
  const el = i => root.querySelector(`[data-blank="${i}"]`);
  const values = () => blanks.map(b => (el(b.index)?.value ?? '').trim());
  root.querySelectorAll('input.fill-blank').forEach(inp => inp.addEventListener('input', () => {
    inp.classList.remove('fill-ok', 'fill-bad');
    const t = toTex(inp.value); const out = inp.nextElementSibling;
    if (out) out.innerHTML = t ? tex(t) : '';
    onChange();
  }));
  root.querySelectorAll('select.fill-blank').forEach(s => s.addEventListener('change', () => { s.classList.remove('fill-ok', 'fill-bad'); onChange(); }));
  return {
    values,
    check() {
      const res = checkBlanks(blanks, values());
      blanks.forEach((b, i) => { const e = el(b.index); e.classList.toggle('fill-ok', res[i]); e.classList.toggle('fill-bad', !res[i]); e.setAttribute('aria-invalid', String(!res[i])); });
      return {correct: res.filter(Boolean).length, total: res.length, all: res.every(Boolean), res};
    },
    reveal() { blanks.forEach(b => { const e = el(b.index); e.value = answerText(b); e.classList.remove('fill-bad'); e.classList.add('fill-ok', 'fill-revealed'); const t = e.nextElementSibling; if (t && t.classList.contains('fill-tex')) t.innerHTML = ''; }); },
    reset() { blanks.forEach(b => { const e = el(b.index); e.value = ''; e.classList.remove('fill-ok', 'fill-bad', 'fill-revealed'); e.removeAttribute('aria-invalid'); const t = e.nextElementSibling; if (t && t.classList.contains('fill-tex')) t.innerHTML = ''; }); },
    setValues(v) { blanks.forEach((b, i) => { if (v?.[i] != null) el(b.index).value = v[i]; }); }
  };
}

// ---------- completed solution (answers boxed) ----------
export function solvedMarkup(spec) {
  const p = parseBlanks(spec);
  const box = b => b.select ? `\\boxed{\\text{${b.answers[0].replace(/[{}\\%$#&_^~]/g, '')}}}` : `\\boxed{${answerTex(b.answers[0])}}`;
  const lines = p.lines.map(l => `<div class="solved-line" dir="ltr">${tex(l.segments.map(s => s.kind === 'tex' ? s.value : box(s)).join(''))}</div>`).join('');
  const table = p.tables.map(t => tableHtml(t, c => tex(answerTex(c.answers[0])))).join('');
  return `<div class="solved-box">${lines}${table}</div>`;
}
// ascii answer ("-x^2/2+2x", "sqrt(39)") -> LaTeX for display
export function answerTex(a) {
  let t = String(a).replace(/sqrt\(([^()]*)\)/g, '\\sqrt{$1}').replace(/\*/g, '\\cdot ');
  t = t.replace(/(-?[A-Za-z0-9.]+(?:\^\d+)?)\/(\d+)/g, '\\frac{$1}{$2}').replace(/\^(\d{2,})/g, '^{$1}');
  return t;
}

// Coordinate-plane plotting for graphing questions: a value table (the student chooses x) and a plane
// (the student clicks the points). Both are checked against the equation, not against fixed answers.
const NS = 'http://www.w3.org/2000/svg';
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const EPS = 1e-6;

export const snap = v => Math.round(v * 2) / 2;
export function num(text) {
  const t = String(text ?? '').trim().replace(/[−–]/g, '-');
  if (!t) return null;
  const f = t.match(/^(-?\d+(?:\.\d+)?)\s*\/\s*(-?\d+(?:\.\d+)?)$/);
  if (f) return Number(f[2]) ? Number(f[1]) / Number(f[2]) : null;
  return /^-?\d*\.?\d+$/.test(t) ? Number(t) : null;
}
export const lineY = (line, x) => line.m * x + line.b;
const fmt = v => Number.isInteger(v) ? String(v) : String(+v.toFixed(2));

// ---- pure checking ----
export function checkTable(spec, rows) {
  const filled = rows.filter(r => String(r.x).trim() || String(r.y).trim());
  const res = filled.map(r => { const x = num(r.x), y = num(r.y); return {ok: x !== null && y !== null && Math.abs(lineY(spec.line, x) - y) < 0.01, x, y}; });
  const good = res.filter(r => r.ok), distinct = new Set(good.map(r => r.x)).size;
  return {rows: res, good: good.length, filled: filled.length, distinct, ok: filled.length >= spec.min_points && good.length === filled.length && distinct >= spec.min_points, points: good.map(r => ({x: r.x, y: r.y}))};
}
const onLine = (m, b, p) => Math.abs(m * p.x + b - p.y) < EPS;
export function pieceEnd(piece) { return {x: piece.x0, y: piece.m * piece.x0 + piece.b, open: !piece.closed}; }
export function pointValid(spec, p) {
  if (spec.kind === 'line') return onLine(spec.line.m, spec.line.b, p);
  return spec.pieces.some(pc => {
    if (!onLine(pc.m, pc.b, p)) return false;
    if (Math.abs(p.x - pc.x0) < EPS) return Boolean(p.open) === !pc.closed;
    return pc.side === 'right' ? p.x > pc.x0 : p.x < pc.x0;
  });
}
export function checkPlot(spec, tableRows, points) {
  const table = spec.kind === 'line' ? checkTable(spec, tableRows) : null;
  const marks = points.map(p => ({...p, ok: pointValid(spec, p)}));
  let missing = [];
  if (spec.kind === 'line') {
    const need = table?.points?.length ? table.points : [];
    missing = need.filter(t => !points.some(p => Math.abs(p.x - t.x) < EPS && Math.abs(p.y - t.y) < EPS));
    const distinct = new Set(marks.filter(m => m.ok).map(m => m.x)).size;
    const plotted = distinct >= spec.min_points && marks.every(m => m.ok) && missing.length === 0 && Boolean(table?.ok);
    return {table, marks, missing, ok: plotted};
  }
  const ends = spec.pieces.map(pieceEnd);
  missing = ends.filter(e => !points.some(p => Math.abs(p.x - e.x) < EPS && Math.abs(p.y - e.y) < EPS && Boolean(p.open) === e.open));
  const inner = spec.pieces.map(pc => marks.some(m => m.ok && onLine(pc.m, pc.b, m) && Math.abs(m.x - pc.x0) > EPS && (pc.side === 'right' ? m.x > pc.x0 : m.x < pc.x0)));
  return {table: null, marks, missing, inner, ok: marks.every(m => m.ok) && missing.length === 0 && inner.every(Boolean)};
}

// ---- markup ----
export function plotMarkup(spec, id) {
  const rowsN = spec.kind === 'line' ? Math.max(3, spec.min_points) : 0;
  const table = spec.kind === 'line' ? `<div class="plot-table-wrap"><p class="q-fill-label"><b>١.</b> <span lang="ar" dir="rtl">اختر قيم x بنفسك واحسب y من المعادلة</span> · Choose your own x values and compute y</p><table class="plot-table" dir="ltr"><tr><th>x</th>${Array.from({length: rowsN}, (_, i) => `<td><input class="plot-x" inputmode="decimal" dir="ltr" autocomplete="off" aria-label="x ${i + 1}"></td>`).join('')}</tr><tr><th>y</th>${Array.from({length: rowsN}, (_, i) => `<td><input class="plot-y" inputmode="decimal" dir="ltr" autocomplete="off" aria-label="y ${i + 1}"></td>`).join('')}</tr></table></div>` : '';
  const tools = spec.kind === 'piecewise' ? `<div class="plot-tools" role="group" aria-label="نوع النقطة · Point type"><button type="button" class="plot-mode" data-open="0" aria-pressed="true">● نقطة مغلقة · Closed</button><button type="button" class="plot-mode" data-open="1" aria-pressed="false">○ نقطة مفتوحة · Open</button></div>` : '';
  return `<div class="plot-box" id="${esc(id)}" data-kind="${spec.kind}">${table}<p class="q-fill-label"><b>${spec.kind === 'line' ? '٢.' : '١.'}</b> <span lang="ar" dir="rtl">${spec.kind === 'line' ? 'ضع نقاط الجدول على المستوى (اضغط على التقاطع؛ اضغط على النقطة لحذفها)' : 'ضع نقطتي البداية وعلى الأقل نقطة واحدة داخل كل جزء (اضغط لوضع النقطة؛ اضغط عليها لحذفها)'}</span></p>${tools}<svg class="plot-plane" role="img" tabindex="0" aria-label="المستوى الإحداثي · coordinate plane"></svg><div class="plot-points" dir="ltr" aria-live="polite"></div><div class="q-fill-actions"><button type="button" data-plot="check" class="btn-primary">تحقّق من الجدول والرسم · Check</button><button type="button" data-plot="line">ارسم الخط · Draw</button><button type="button" data-plot="reveal">أظهر الحل · Show</button><button type="button" data-plot="reset">مسح · Clear</button></div><div class="plot-feedback q-fill-feedback" role="status" aria-live="polite"></div></div>`;
}

export function wirePlot(root, spec) {
  const [xmin, xmax, ymin, ymax] = spec.bounds, S = 28, pad = 30;
  const W = (xmax - xmin) * S + pad * 2, H = (ymax - ymin) * S + pad * 2;
  const svg = root.querySelector('.plot-plane'), fb = root.querySelector('.plot-feedback'), list = root.querySelector('.plot-points');
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  const X = x => pad + (x - xmin) * S, Y = y => pad + (ymax - y) * S;
  let points = [], open = false, drawn = false, shown = null, marks = [];
  const el = (n, a, t) => { const e = document.createElementNS(NS, n); for (const [k, v] of Object.entries(a)) e.setAttribute(k, v); if (t != null) e.textContent = t; return e; };
  const stepLabel = (xmax - xmin) > 14 ? 2 : 1;
  const readRows = () => [...root.querySelectorAll('.plot-x')].map((x, i) => ({x: x.value, y: root.querySelectorAll('.plot-y')[i].value}));
  function draw() {
    svg.replaceChildren();
    const g = el('g', {stroke: '#d3dfe6', 'stroke-width': 1});
    for (let x = xmin; x <= xmax; x++) g.append(el('path', {d: `M${X(x)} ${Y(ymin)}V${Y(ymax)}`}));
    for (let y = ymin; y <= ymax; y++) g.append(el('path', {d: `M${X(xmin)} ${Y(y)}H${X(xmax)}`}));
    svg.append(g);
    const ax = el('g', {stroke: '#27475c', 'stroke-width': 2});
    ax.append(el('path', {d: `M${X(xmin)} ${Y(0)}H${X(xmax)}`}), el('path', {d: `M${X(0)} ${Y(ymin)}V${Y(ymax)}`}));
    svg.append(ax);
    const lab = el('g', {fill: '#34556a', 'font-size': 11, 'font-family': 'Arial'});
    for (let x = xmin; x <= xmax; x += 1) if (x && x % stepLabel === 0) lab.append(el('text', {x: X(x), y: Y(0) + 14, 'text-anchor': 'middle'}, x));
    for (let y = ymin; y <= ymax; y += 1) if (y && y % stepLabel === 0) lab.append(el('text', {x: X(0) - 6, y: Y(y) + 4, 'text-anchor': 'end'}, y));
    lab.append(el('text', {x: X(xmax) + 2, y: Y(0) + 14, 'font-style': 'italic'}, 'x'), el('text', {x: X(0) + 8, y: Y(ymax) + 2, 'font-style': 'italic'}, 'y'));
    svg.append(lab);
    // reference / drawn lines
    const segs = shown || (drawn ? currentSegments() : []);
    for (const s of segs) svg.append(el('path', {d: `M${X(s.x1)} ${Y(s.y1)}L${X(s.x2)} ${Y(s.y2)}`, stroke: shown ? '#17683a' : '#b45a3c', 'stroke-width': 2.5, 'stroke-dasharray': shown ? '6 4' : '0', fill: 'none'}));
    const reveal = shown?.points || [];
    for (const p of reveal) svg.append(el('circle', {cx: X(p.x), cy: Y(p.y), r: 7, fill: p.open ? '#fff' : '#17683a', stroke: '#17683a', 'stroke-width': 2, opacity: .55}));
    points.forEach((p, i) => { const m = marks[i]; const c = m === undefined ? '#1f5d99' : m ? '#17683a' : '#a02323'; svg.append(el('circle', {cx: X(p.x), cy: Y(p.y), r: 7, fill: p.open ? '#fff' : c, stroke: c, 'stroke-width': 3, 'data-i': i})); });
    list.textContent = points.length ? 'النقاط: ' + points.map(p => `${p.open ? '○' : '●'}(${fmt(p.x)}, ${fmt(p.y)})`).join('  ') : '';
  }
  function currentSegments() {
    const lo = xmin, hi = xmax;
    if (spec.kind === 'line') return [{x1: lo, y1: lineY(spec.line, lo), x2: hi, y2: lineY(spec.line, hi)}];
    return spec.pieces.map(pc => { const e = pc.side === 'right' ? hi : lo; return {x1: pc.x0, y1: pc.m * pc.x0 + pc.b, x2: e, y2: pc.m * e + pc.b}; });
  }
  svg.addEventListener('pointerdown', e => {
    const r = svg.getBoundingClientRect(), k = W / r.width;
    const x = snap(xmin + ((e.clientX - r.left) * k - pad) / S), y = snap(ymax - ((e.clientY - r.top) * k - pad) / S);
    if (x < xmin || x > xmax || y < ymin || y > ymax) return;
    const at = points.findIndex(p => Math.abs(p.x - x) < EPS && Math.abs(p.y - y) < EPS);
    if (at >= 0) points.splice(at, 1); else points.push({x, y, open});
    marks = []; drawn = false; shown = null; draw();
  });
  root.querySelectorAll('.plot-mode').forEach(b => b.onclick = () => { open = b.dataset.open === '1'; root.querySelectorAll('.plot-mode').forEach(o => o.setAttribute('aria-pressed', String(o === b))); });
  const say = (cls, html) => { fb.className = 'plot-feedback q-fill-feedback ' + cls; fb.innerHTML = html; };
  const api = {
    check() {
      const r = checkPlot(spec, readRows(), points);
      marks = r.marks.map(m => m.ok);
      root.querySelectorAll('.plot-x,.plot-y').forEach(i => i.classList.remove('fill-ok', 'fill-bad'));
      if (r.table) r.table.rows.forEach((row, i) => { const xi = root.querySelectorAll('.plot-x')[i], yi = root.querySelectorAll('.plot-y')[i]; const cls = row.ok ? 'fill-ok' : 'fill-bad'; xi.classList.add(cls); yi.classList.add(cls); });
      const msgs = [];
      if (spec.kind === 'line') {
        msgs.push(`الجدول: ${r.table.good} من ${Math.max(r.table.filled, spec.min_points)} صحيح${r.table.filled < spec.min_points ? ` (أكمل ${spec.min_points} نقاط على الأقل)` : ''}`);
        msgs.push(`الرسم: ${r.marks.filter(m => m.ok).length} من ${points.length} نقاط على الخط${r.missing.length ? ` · ينقص رسم ${r.missing.length} من نقاط الجدول` : ''}`);
      } else {
        msgs.push(`النقاط الصحيحة: ${r.marks.filter(m => m.ok).length} من ${points.length}`);
        if (r.missing.length) msgs.push(`ضع نقطتي البداية بالنوع الصحيح (مغلقة/مفتوحة) — ينقص ${r.missing.length}`);
        if (r.inner.some(v => !v)) msgs.push('أضف نقطة واحدة على الأقل داخل كل جزء');
      }
      say(r.ok ? 'is-right' : 'is-wrong', (r.ok ? 'ممتاز! الجدول والرسم صحيحان. اضغط «ارسم الخط». ' : 'راجع الأحمر: ') + msgs.join(' · '));
      draw();
      return {ok: r.ok, all: r.ok, empty: !points.length && !r.table?.filled};
    },
    reset() { points = []; marks = []; drawn = false; shown = null; root.querySelectorAll('.plot-x,.plot-y').forEach(i => { i.value = ''; i.classList.remove('fill-ok', 'fill-bad'); }); say('', ''); draw(); },
    reveal() {
      const pts = spec.kind === 'line' ? [-2, 0, 2].map(x => ({x, y: lineY(spec.line, x)})).filter(p => p.y >= ymin && p.y <= ymax) : spec.pieces.map(pieceEnd);
      shown = Object.assign(currentSegments(), {points: pts});
      say('', 'الخط المرجعي والنقاط الخضراء الشفافة هي الحل المرجعي.'); draw();
    },
    values: () => ({rows: readRows(), points})
  };
  root.querySelector('[data-plot=check]').onclick = api.check;
  root.querySelector('[data-plot=reset]').onclick = api.reset;
  root.querySelector('[data-plot=reveal]').onclick = api.reveal;
  root.querySelector('[data-plot=line]').onclick = () => { const r = checkPlot(spec, readRows(), points); if (!r.marks.some(m => m.ok)) { say('is-wrong', 'ضع نقاطًا صحيحة أولًا.'); return; } marks = r.marks.map(m => m.ok); drawn = true; shown = null; draw(); say('', 'تم رسم الخط/الأجزاء بالمعادلة الصحيحة؛ قارنه بنقاطك.'); };
  draw();
  return api;
}

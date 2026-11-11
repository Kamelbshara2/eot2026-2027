// Number-line answers for inequality questions (e.g. compound "and" inequalities).
// The student places endpoints (closed ● = included, open ○ = excluded), then clicks the pieces of the line to
// shade them; a shaded piece that reaches the end of the line is drawn with an arrow (it continues forever).
// "No solution ∅" is a separate button. Everything is checked against the exact solution set:
//   spec = {bounds: [lo, hi], step: 1 | 0.5, answer: [{a, b, ac, bc}, ...]}   a/b = null means −∞/+∞, ac/bc = endpoint included.
//   answer [] = empty set.
const NS = 'http://www.w3.org/2000/svg';
const EPS = 1e-9;
const fmt = v => Number.isInteger(v) ? String(v) : String(+v.toFixed(2));
const ltr = t => `<bdi dir="ltr">${String(t).replace(/[&<>]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;'}[c]))}</bdi>`;

export const inSet = (answer, x) => answer.some(iv =>
  (iv.a === null || x > iv.a + EPS || (Math.abs(x - iv.a) < EPS && iv.ac)) &&
  (iv.b === null || x < iv.b - EPS || (Math.abs(x - iv.b) < EPS && iv.bc)));

// finite endpoints the answer needs, with whether each is included
export function answerEnds(answer) {
  const ends = [];
  for (const iv of answer) for (const [x, inc] of [[iv.a, iv.ac], [iv.b, iv.bc]]) if (x !== null && !ends.some(e => Math.abs(e.x - x) < EPS)) ends.push({x, closed: inSet(answer, x) || Boolean(inc)});
  return ends.sort((p, q) => p.x - q.x);
}

// regions between sorted points: index 0 = left ray, k = right ray
export const regionSample = (xs, i) => i === 0 ? xs.length ? xs[0] - 1 : 0 : i === xs.length ? xs[xs.length - 1] + 1 : (xs[i - 1] + xs[i]) / 2;

export function checkNumberLine(spec, state) {
  const ans = spec.answer, pts = [...state.points].sort((p, q) => p.x - q.x), xs = pts.map(p => p.x);
  if (!ans.length) {
    const ok = Boolean(state.empty) && !state.shaded.size;
    return {ok, msgs: ok ? [] : [state.empty ? 'لا تظلل أي جزء عندما لا يوجد حل' : 'التقاطع فارغ: لا يوجد عدد يحقق المتباينتين معاً · The two sets do not overlap']};
  }
  if (state.empty) return {ok: false, msgs: ['يوجد حل؛ لا تختر ∅ · There is a solution']};
  const need = answerEnds(ans), msgs = [];
  const missing = need.filter(e => !pts.some(p => Math.abs(p.x - e.x) < EPS));
  const extra = pts.filter(p => !need.some(e => Math.abs(p.x - e.x) < EPS));
  const wrongType = pts.filter(p => need.some(e => Math.abs(p.x - e.x) < EPS && e.closed === p.open));
  if (missing.length) msgs.push(`ينقص ${missing.length} من نقاط الحدود · endpoint missing`);
  if (extra.length) msgs.push(`نقطة زائدة عند ${extra.map(p => ltr(fmt(p.x))).join('، ')} · extra point`);
  if (wrongType.length) msgs.push(`نوع النقطة خطأ عند ${wrongType.map(p => ltr(fmt(p.x))).join('، ')}: مغلقة ● لـ ≤ و≥، مفتوحة ○ لـ < و> · open/closed`);
  let shadeOk = true;
  if (!missing.length && !extra.length) {
    for (let i = 0; i <= xs.length; i++) if (inSet(ans, regionSample(xs, i)) !== state.shaded.has(i)) shadeOk = false;
    if (!shadeOk) msgs.push('التظليل لا يطابق مجموعة الحل · shading');
  } else shadeOk = false;
  return {ok: !msgs.length && shadeOk, msgs, missing, extra, wrongType};
}

export function intervalText(answer) {
  if (!answer.length) return '∅';
  return answer.map(iv => `${iv.a === null ? '(−∞' : (iv.ac ? '[' : '(') + fmt(iv.a)}, ${iv.b === null ? '∞)' : fmt(iv.b) + (iv.bc ? ']' : ')')}`).join(' ∪ ').replace(/-/g, '−');
}

export function numberLineMarkup(spec, id) {
  return `<div class="nl-box" id="${id}"><p class="q-fill-label"><span lang="ar" dir="rtl">ضع نقطتي الحدود (مغلقة ● أو مفتوحة ○) بالضغط على خط الأعداد، ثم اختر «تظليل» واضغط على الجزء الذي يمثل الحل.</span> · Place the endpoints, then shade the solution.</p><div class="plot-tools" role="group" aria-label="أداة · Tool"><button type="button" class="nl-mode" data-mode="closed" aria-pressed="true">● نقطة مغلقة · Closed</button><button type="button" class="nl-mode" data-mode="open" aria-pressed="false">○ نقطة مفتوحة · Open</button><button type="button" class="nl-mode" data-mode="shade" aria-pressed="false">▬ تظليل · Shade</button><button type="button" class="nl-empty" aria-pressed="false">∅ لا يوجد حل · No solution</button></div><svg class="nl-svg" role="img" tabindex="0" aria-label="خط الأعداد · number line"></svg><div class="plot-points" dir="ltr" aria-live="polite"></div><div class="q-fill-actions"><button type="button" data-nl="check" class="btn-primary">تحقّق · Check</button><button type="button" data-nl="reveal">أظهر الحل · Show</button><button type="button" data-nl="reset">مسح · Clear</button></div><div class="plot-feedback q-fill-feedback" role="status" aria-live="polite"></div></div>`;
}

export function wireNumberLine(root, spec, saved = null, onChange = () => {}) {
  const [lo, hi] = spec.bounds, step = spec.step || 1, U = Math.max(22, Math.min(46, 620 / (hi - lo))), pad = 24, W = (hi - lo) * U + pad * 2, H = 74, Y0 = 34;
  const svg = root.querySelector('.nl-svg'), fb = root.querySelector('.plot-feedback'), list = root.querySelector('.plot-points'), emptyBtn = root.querySelector('.nl-empty');
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  const X = x => pad + (x - lo) * U;
  let mode = 'closed', state = {points: [], shaded: new Set(), empty: false}, shown = false, verdict = null;
  if (saved) state = {points: saved.points || [], shaded: new Set(saved.shaded || []), empty: Boolean(saved.empty)};
  const store = () => onChange({points: state.points, shaded: [...state.shaded], empty: state.empty});
  const el = (n, a, t) => { const e = document.createElementNS(NS, n); for (const [k, v] of Object.entries(a)) e.setAttribute(k, v); if (t != null) e.textContent = t; return e; };
  const xsSorted = () => state.points.map(p => p.x).sort((a, b) => a - b);
  function seg(a, b, color, dashed) {   // a/b null = runs to the arrow end
    const x1 = a === null ? X(lo) + 2 : X(a), x2 = b === null ? X(hi) - 2 : X(b), g = el('g', {stroke: color, fill: color});
    g.append(el('path', {d: `M${x1} ${Y0}H${x2}`, 'stroke-width': 7, 'stroke-linecap': 'butt', opacity: dashed ? .45 : .9}));
    if (a === null) g.append(el('path', {d: `M${X(lo) - 6} ${Y0}l12 -9v18z`, stroke: 'none', opacity: dashed ? .45 : 1}));
    if (b === null) g.append(el('path', {d: `M${X(hi) + 6} ${Y0}l-12 -9v18z`, stroke: 'none', opacity: dashed ? .45 : 1}));
    svg.append(g);
  }
  function draw() {
    svg.replaceChildren();
    svg.append(el('path', {d: `M${X(lo) - 8} ${Y0}H${X(hi) + 8}`, stroke: '#27475c', 'stroke-width': 2}),
      el('path', {d: `M${X(lo) - 12} ${Y0}l8 -5v10zM${X(hi) + 12} ${Y0}l-8 -5v10z`, fill: '#27475c'}));
    const every = (hi - lo) > 18 ? 2 : 1;
    for (let x = lo; x <= hi + EPS; x += 1) {
      svg.append(el('path', {d: `M${X(x)} ${Y0 - 6}V${Y0 + 6}`, stroke: '#27475c', 'stroke-width': 1.5}));
      if (Math.round(x) % every === 0) svg.append(el('text', {x: X(x), y: Y0 + 24, 'text-anchor': 'middle', 'font-size': 12, 'font-family': 'Arial', fill: '#34556a'}, String(x).replace('-', '−')));
    }
    if (step < 1) for (let x = lo + step; x < hi; x += 1) svg.append(el('path', {d: `M${X(x)} ${Y0 - 3}V${Y0 + 3}`, stroke: '#7d95a5', 'stroke-width': 1}));
    if (shown) {
      for (const iv of spec.answer) seg(iv.a, iv.b, '#17683a', true);
      for (const e of answerEnds(spec.answer)) svg.append(el('circle', {cx: X(e.x), cy: Y0, r: 7, fill: e.closed ? '#17683a' : '#fff', stroke: '#17683a', 'stroke-width': 3, opacity: .7}));
    }
    const xs = xsSorted(), shadeColor = verdict === null ? '#1f5d99' : verdict ? '#17683a' : '#a02323';
    for (const i of state.shaded) if (i <= xs.length) seg(i === 0 ? null : xs[i - 1], i === xs.length ? null : xs[i], shadeColor, false);
    for (const p of state.points) svg.append(el('circle', {cx: X(p.x), cy: Y0, r: 7, fill: p.open ? '#fff' : shadeColor, stroke: shadeColor, 'stroke-width': 3}));
    list.textContent = state.empty ? 'الحل: ∅ · No solution' : state.points.length ? 'النقاط: ' + [...state.points].sort((a, b) => a.x - b.x).map(p => `${p.open ? '○' : '●'}${fmt(p.x)}`).join('  ') : '';
    emptyBtn.setAttribute('aria-pressed', String(state.empty));
  }
  svg.addEventListener('pointerdown', e => {
    const r = svg.getBoundingClientRect(), k = W / r.width, raw = lo + ((e.clientX - r.left) * k - pad) / U;
    if (raw < lo - 0.6 || raw > hi + 0.6) return;
    verdict = null; shown = false; state.empty = false;
    if (mode === 'shade') {
      const xs = xsSorted(); if (xs.some(x => Math.abs(x - raw) < 0.2)) return;
      const i = xs.filter(x => x < raw).length;
      state.shaded.has(i) ? state.shaded.delete(i) : state.shaded.add(i);
    } else {
      const x = Math.min(hi, Math.max(lo, Math.round(raw / step) * step)), at = state.points.findIndex(p => Math.abs(p.x - x) < EPS);
      if (at >= 0) state.points.splice(at, 1);
      else { if (state.points.length >= 4) return; state.points.push({x, open: mode === 'open'}); }
      state.shaded.clear();
    }
    store(); draw();
  });
  root.querySelectorAll('.nl-mode').forEach(b => b.onclick = () => { mode = b.dataset.mode; root.querySelectorAll('.nl-mode').forEach(o => o.setAttribute('aria-pressed', String(o === b))); });
  emptyBtn.onclick = () => { state = {points: [], shaded: new Set(), empty: !state.empty}; verdict = null; shown = false; store(); draw(); };
  const say = (cls, html) => { fb.className = 'plot-feedback q-fill-feedback ' + cls; fb.innerHTML = html; };
  const api = {
    check() {
      const r = checkNumberLine(spec, state); verdict = r.ok; draw();
      say(r.ok ? 'is-right' : 'is-wrong', r.ok ? `ممتاز! التمثيل صحيح: ${ltr(intervalText(spec.answer))} · Correct.` : 'راجع: ' + r.msgs.join(' · '));
      return r;
    },
    reveal() { shown = true; draw(); say('', `الحل المرجعي (أخضر شفاف): ${ltr(intervalText(spec.answer))}`); },
    reset() { state = {points: [], shaded: new Set(), empty: false}; verdict = null; shown = false; store(); say('', ''); draw(); },
    values: () => ({points: state.points, shaded: [...state.shaded], empty: state.empty})
  };
  root.querySelector('[data-nl=check]').onclick = api.check;
  root.querySelector('[data-nl=reveal]').onclick = api.reveal;
  root.querySelector('[data-nl=reset]').onclick = api.reset;
  draw();
  return api;
}

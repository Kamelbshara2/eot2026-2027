// Tool ribbon (side tabs on PC, top bar on phones) and the "worked example" window.
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));

const MODES = {
  manual: {key: 'manual', ar: 'حل يدوي', en: 'By hand', hint: 'الحل بالتفكير والكتابة؛ الحاسبة للتحقق فقط.'},
  calculator: {key: 'calculator', ar: 'حل بالحاسبة', en: 'Calculator', hint: 'يكفي إدخال العملية في الحاسبة ثم كتابة الناتج.'},
  hybrid: {key: 'hybrid', ar: 'حل هجين: يدوي + حاسبة', en: 'Hybrid', hint: 'جهّز المسألة يدويًا، ثم استخدم الحاسبة للحساب أو التحقق.'}
};
const ROLE_MODE = {reasoning: 'manual', manual_setup: 'manual', evaluate: 'calculator', calculation: 'calculator', solve: 'calculator', quadratic: 'calculator', floor: 'calculator',
  check: 'hybrid', numerical_check: 'hybrid', function_check: 'hybrid', table: 'hybrid', vertical: 'hybrid', ssa: 'hybrid'};
export function solutionMode(q) {
  const role = q?.calculatorSupport?.role;
  if (role) return MODES[ROLE_MODE[role] || 'hybrid'];
  return MODES[q?.calculator?.applicable ? 'hybrid' : 'manual'];
}
export const modeBadge = q => { const m = solutionMode(q); return `<span class="solution-mode mode-${m.key}" title="${esc(m.hint)}"><b>${m.ar}</b> · ${m.en}</span>`; };

export const ribbonMarkup = () => `<nav class="study-ribbon" aria-label="أدوات الدرس · Lesson tools">
  <button type="button" id="open-example-window" aria-expanded="false" aria-controls="example-window"><span class="rb-icon" aria-hidden="true">✎</span><span class="rb-text">المثال والحل<small>Example</small></span></button>
  <button type="button" id="open-floating-calculator" class="calculator-launch" aria-expanded="false" aria-controls="floating-calculator"><span class="rb-icon" aria-hidden="true">⌗</span><span class="rb-text">الحاسبة<small>Calculator</small></span></button>
  <button type="button" id="open-calculator-demos" aria-controls="calculator-examples"><span class="rb-icon" aria-hidden="true">▶</span><span class="rb-text">شرح مصوّر<small>Demos</small></span></button>
</nav>`;

// parts: {title, question (html), manual (html), calculator (html), badge (html)}
export const windowMarkup = parts => `<aside id="example-window" class="example-window" role="dialog" aria-labelledby="ew-title" hidden>
  <header><h2 id="ew-title">المثال المحلول · Worked example</h2><button type="button" id="close-example-window" aria-label="إغلاق · Close">×</button></header>
  <div class="ew-body"><div class="ew-question"><span class="study-label">السؤال · QUESTION</span>${parts.question}${parts.badge}</div>
  <div class="ew-tabs" role="tablist" aria-label="طريقة الحل · Solution method"><button type="button" role="tab" id="ew-tab-manual" aria-selected="true" aria-controls="ew-manual">الحل اليدوي · By hand</button><button type="button" role="tab" id="ew-tab-calculator" aria-selected="false" aria-controls="ew-calculator" tabindex="-1">الحل بالحاسبة · Calculator</button></div>
  <section id="ew-manual" role="tabpanel" aria-labelledby="ew-tab-manual">${parts.manual}</section>
  <section id="ew-calculator" role="tabpanel" aria-labelledby="ew-tab-calculator" hidden>${parts.calculator}</section></div></aside>`;

export function setupExampleWindow(root) {
  const win = root.querySelector('#example-window'), open = root.querySelector('#open-example-window');
  if (!win || !open) return;
  const tabs = [...win.querySelectorAll('[role=tab]')];
  const show = tab => tabs.forEach(t => { const on = t === tab; t.setAttribute('aria-selected', String(on)); t.tabIndex = on ? 0 : -1; win.querySelector('#' + t.getAttribute('aria-controls')).hidden = !on; });
  tabs.forEach(t => t.onclick = () => show(t));
  win.querySelector('[role=tablist]').addEventListener('keydown', e => { if (!['ArrowLeft', 'ArrowRight'].includes(e.key)) return; const i = tabs.indexOf(document.activeElement); const next = tabs[(i + 1) % tabs.length]; show(next); next.focus(); });
  const close = () => { win.hidden = true; open.setAttribute('aria-expanded', 'false'); document.body.classList.remove('example-window-open'); open.focus(); };
  const openIt = () => { win.hidden = false; open.setAttribute('aria-expanded', 'true'); document.body.classList.add('example-window-open'); win.querySelector('#close-example-window').focus(); };
  open.onclick = () => (win.hidden ? openIt() : close());
  win.querySelector('#close-example-window').onclick = close;
  win.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
  root.querySelector('#open-calculator-demos')?.addEventListener('click', () => { const d = root.querySelector('.calculator-examples'); if (d && !d.hidden) { d.open = true; d.scrollIntoView({behavior: 'smooth', block: 'start'}); } });
  return {open: openIt, close};
}

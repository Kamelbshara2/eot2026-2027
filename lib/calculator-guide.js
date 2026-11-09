import {calculatorSupport} from './calculator-support.js';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function quadraticModeGuide(g) {
 if (g.kind !== 'quadratic') return '';
 const match = /^\((-?\d+)\)\^2-4\*\((-?\d+)\)\*\((-?\d+)\)$/.exec(g.expressions?.[0] || '');
 if (!match) return '';
 const [, b, a, c] = match;
 return `<section class="calculator-quadratic" lang="en"><h4>Solve a quadratic in ClassWiz</h4><p>First rearrange the equation into <b>ax² + bx + c = 0</b>. For this question: <b>a = ${esc(a)}, b = ${esc(b)}, c = ${esc(c)}</b>.</p><ol><li>Press <kbd>MENU</kbd> and choose <b>Equation/Func</b>.</li><li>Choose <b>2: Polynomial</b>, then <b>2: Degree 2</b>.</li><li>Enter <b>a = ${esc(a)}</b> and press <kbd>=</kbd>; enter <b>b = ${esc(b)}</b> and press <kbd>=</kbd>; enter <b>c = ${esc(c)}</b> and press <kbd>=</kbd>. Use the negative key for negative coefficients.</li><li>Display the solutions and press <kbd>=</kbd> to move between roots. Write each value of x and check it by substitution. A repeated root may appear once; complex roots depend on calculator settings.</li></ol><p>Use the discriminant below as a check. If the question asks for a particular method, show that method too.</p></section>`;
}
export function calculatorGuide(q,base){
 if(q.calculatorSupport)return calculatorSupport(q);
 const g=q.calculator;if(!g?.applicable)return '';
 const image=/^calculator\/[A-Za-z0-9_-]+\.png$/.test(g.image||'')?`<img loading="lazy" src="${base}${g.image}" alt="${esc(g.model)} key guide for question ${esc(q.display_number)}" class="calculator-guide-image">`:'';
 return `<details class="calculator-guide"><summary>الحل باستخدام ${esc(g.model)} · Calculator steps</summary><p lang="ar" dir="rtl">شرح تعليمي للأزرار؛ تحقق من وضع الزوايا قبل الحساب. ${g.kind==='check'?'التعويض للتحقق العددي؛ البرهان الجبري مطلوب لإثبات التكافؤ.':''}</p>${quadraticModeGuide(g)}${image}<ol>${g.steps.map(s=>`<li><b>${esc(s.title)}</b><div class="calculator-keys">${s.keys.map(k=>`<kbd>${esc(k)}</kbd>`).join('')}</div><p>${esc(s.text)}</p>${s.expression?`<code dir="ltr">${esc(s.expression.replaceAll('**','^'))}</code>`:''}</li>`).join('')}</ol>${g.table?(g.branch_tables||[g.table]).map(t=>`<table class="calculator-table"><caption>Table results ${esc(t.condition||'')} · نتائج الجدول بعد الحل</caption><tr><th>X</th>${t.x.map(v=>`<td>${v}</td>`).join('')}</tr><tr><th>f(X)</th>${t.y.map(v=>`<td>${v}</td>`).join('')}</tr></table>`).join(''):''}<p class="calculator-caption">Instructional key diagram, not an official Casio emulator · مخطط تعليمي للأزرار</p></details>`;
}

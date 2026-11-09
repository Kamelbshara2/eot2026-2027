const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
// Schematic illustrations show only the supplied key sequence; they do not
// imitate the calculator firmware or infer a result from the expression.
function stepIllustration(step, index){
 const keys = step.keys || [];
 const width = Math.max(260, Math.min(620, keys.length * 76 + 40));
 const cells = keys.map((key,i)=>`<g transform="translate(${20+i*76} 54)"><rect width="66" height="38" rx="8" fill="#d48438"/><text x="33" y="24" text-anchor="middle" fill="white" font-size="${String(key).length>7?10:14}" font-weight="700">${esc(key)}</text></g>`).join('');
 return `<svg class="calculator-step-image" viewBox="0 0 ${width} 110" role="img" aria-label="Step ${index+1}: ${esc(keys.join(', '))}"><rect x="1" y="1" width="${width-2}" height="108" rx="14" fill="#193e4c"/><rect x="15" y="12" width="${width-30}" height="29" rx="4" fill="#dce8d6"/><text x="25" y="31" font-size="13" fill="#193e4c">${esc(step.title)}</text>${cells}</svg>`;
}
export function calculatorGuide(q,base){
 const g=q.calculator;if(!g?.applicable)return '';
 const image=/^calculator\/[A-Za-z0-9_-]+\.png$/.test(g.image||'')?`<img loading="lazy" src="${base}${g.image}" alt="${esc(g.model)} key guide for question ${esc(q.display_number)}" class="calculator-guide-image">`:'';
 return `<details class="calculator-guide"><summary>الحل باستخدام ${esc(g.model)} · Calculator steps</summary><p lang="ar" dir="rtl">شرح تعليمي للأزرار؛ تحقق من وضع الزوايا قبل الحساب. ${g.kind==='check'?'التعويض للتحقق العددي؛ البرهان الجبري مطلوب لإثبات التكافؤ.':''}</p>${image}<ol>${g.steps.map((s,i)=>`<li><b>${esc(s.title)}</b>${stepIllustration(s,i)}<div class="calculator-keys">${s.keys.map(k=>`<kbd>${esc(k)}</kbd>`).join('')}</div><p>${esc(s.text)}</p>${s.expression?`<code dir="ltr">${esc(s.expression.replaceAll('**','^'))}</code>`:''}</li>`).join('')}</ol>${g.table?(g.branch_tables||[g.table]).map(t=>`<table class="calculator-table"><caption>Table results ${esc(t.condition||'')} · نتائج الجدول بعد الحل</caption><tr><th>X</th>${t.x.map(v=>`<td>${v}</td>`).join('')}</tr><tr><th>f(X)</th>${t.y.map(v=>`<td>${v}</td>`).join('')}</tr></table>`).join(''):''}<p class="calculator-caption">Instructional key diagram, not an official Casio emulator · مخطط تعليمي للأزرار</p></details>`;
}

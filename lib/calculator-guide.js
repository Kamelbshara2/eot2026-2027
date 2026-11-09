const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
// The device is a teaching illustration, not an image of calculator firmware.
// Show only inputs supplied by the reviewed guide; never invent screen results.
function stepIllustration(step, index, guide){
 const keys = step.keys || [];
 const expression = step.expression?.replaceAll('**','^') || (/Enter f\(X\)/i.test(step.title) ? guide.table?.expression : '');
 const rows = expression ? String(expression).match(/.{1,28}/g) || [] : [];
 const screen = rows.slice(0,3).map((line,i)=>`<text x="50" y="${79+i*19}" font-size="13" fill="#203827" font-family="monospace">${esc(line)}</text>`).join('');
 const keyLabels = ['SHIFT','ALPHA','MENU','OPTN','CALC','∫','x²','^','÷','7','8','9','×','4','5','6','−','1','2','3','+','0','.','(−)','='];
 const keyboard = keyLabels.map((key,i)=>{const x=40+(i%5)*43,y=178+Math.floor(i/5)*35;const active=keys.includes(key);return `<g><rect x="${x}" y="${y}" width="37" height="27" rx="5" fill="${active?'#d37b28':'#536273'}"/><text x="${x+18.5}" y="${y+18}" text-anchor="middle" font-size="${key.length>4?7:10}" fill="white">${esc(key)}</text></g>`}).join('');
 return `<svg class="calculator-step-image" viewBox="0 0 285 375" role="img" aria-label="Illustration, step ${index+1}. Keys: ${esc(keys.join(', '))}${expression?'. Input: '+esc(expression):''}"><rect x="19" y="3" width="247" height="368" rx="22" fill="#243647" stroke="#91a3ac" stroke-width="3"/><text x="37" y="30" fill="#fff" font-size="11">CLASSWIZ · تعليمية</text><rect x="35" y="43" width="215" height="93" rx="4" fill="#d8e5c9"/><text x="50" y="61" font-size="10" fill="#36503c">${expression?'INPUT · إدخال':'SCREEN · شاشة'}</text>${screen}<rect x="35" y="144" width="215" height="23" rx="4" fill="#182b38"/><text x="143" y="160" text-anchor="middle" fill="#fff" font-size="10">${esc(keys.join('  →  '))}</text>${keyboard}</svg>${expression && rows.length>3?`<p dir="ltr">${esc(expression)}</p>`:''}`;
}
export function calculatorGuide(q,base){
 const g=q.calculator;if(!g?.applicable)return '';
 const image=/^calculator\/[A-Za-z0-9_-]+\.png$/.test(g.image||'')?`<img loading="lazy" src="${base}${g.image}" alt="${esc(g.model)} key guide for question ${esc(q.display_number)}" class="calculator-guide-image">`:'';
 return `<details class="calculator-guide"><summary>الحل باستخدام ${esc(g.model)} · Calculator steps</summary><p lang="ar" dir="rtl">شرح تعليمي للأزرار؛ تحقق من وضع الزوايا قبل الحساب. ${g.kind==='check'?'التعويض للتحقق العددي؛ البرهان الجبري مطلوب لإثبات التكافؤ.':''}</p>${image}<ol>${g.steps.map((s,i)=>`<li><b>${esc(s.title)}</b>${stepIllustration(s,i,g)}<div class="calculator-keys">${s.keys.map(k=>`<kbd>${esc(k)}</kbd>`).join('')}</div><p>${esc(s.text)}</p>${s.expression?`<code dir="ltr">${esc(s.expression.replaceAll('**','^'))}</code>`:''}</li>`).join('')}</ol>${g.table?(g.branch_tables||[g.table]).map(t=>`<table class="calculator-table"><caption>Table results ${esc(t.condition||'')} · نتائج الجدول بعد الحل</caption><tr><th>X</th>${t.x.map(v=>`<td>${v}</td>`).join('')}</tr><tr><th>f(X)</th>${t.y.map(v=>`<td>${v}</td>`).join('')}</tr></table>`).join(''):''}<p class="calculator-caption">Instructional illustration, not an official Casio emulator or firmware screen · رسم تعليمي للحاسبة والشاشة وليس محاكيًا رسميًا</p></details>`;
}

const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

export async function renderCalculatorExamples(root, base = '/') {
  try {
    const response = await fetch(`${base}data/calculator-examples/examples.json`);
    if (!response.ok) throw new Error('Examples unavailable');
    const examples = await response.json();
    let exampleIndex = 0, stepIndex = 0;
    function draw() {
      const example = examples[exampleIndex];
      const [key, explanation] = example.steps[stepIndex];
      root.innerHTML = `<label>اختر المثال · Choose an example<select id="calculator-example-select">${examples.map((item,i)=>`<option value="${i}" ${i===exampleIndex?'selected':''}>${escape(item.title)}</option>`).join('')}</select></label><div class="calculator-example-card"><p class="calculator-example-problem" dir="auto">${escape(example.problem)}</p><p role="status">الخطوة ${stepIndex+1} من ${example.steps.length} · بعد الضغط على <b dir="ltr">${escape(key)}</b></p><p dir="rtl">${escape(explanation)}</p><img src="${base}data/calculator-examples/${encodeURIComponent(example.id)}/${stepIndex+1}.png" alt="شاشة المحاكي بعد الخطوة ${stepIndex+1}؛ الزر المستخدم محدد بالبرتقالي"><div class="study-slide-actions"><button type="button" id="calculator-step-prev" ${stepIndex===0?'disabled':''}>السابق · Previous</button><button type="button" id="calculator-step-next" ${stepIndex===example.steps.length-1?'disabled':''}>التالي · Next</button></div><details><summary>كيف أكتب النتيجة في الحل؟</summary><p dir="auto">${escape(example.result)}</p></details></div>`;
      root.querySelector('#calculator-example-select').onchange = e => { exampleIndex=Number(e.target.value); stepIndex=0; draw(); };
      root.querySelector('#calculator-step-prev').onclick = () => { stepIndex--; draw(); };
      root.querySelector('#calculator-step-next').onclick = () => { stepIndex++; draw(); };
    }
    draw();
  } catch {
    root.textContent = 'تعذّر تحميل الأمثلة المصوّرة. أعد تحميل الصفحة للمحاولة مجددًا.';
  }
}

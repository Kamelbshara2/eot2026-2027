const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const PAGE_SIZE = 6;

export async function renderCalculatorExamples(root, base = '/') {
  try {
    const response = await fetch(`${base}data/calculator-examples/examples.json`);
    if (!response.ok) throw new Error('Examples unavailable');
    const examples = await response.json();
    let exampleIndex = 0, pageIndex = 0, activeIndex = 0, timer = null;
    const stop = () => { if (timer !== null) clearInterval(timer); timer = null; };
    const imagePath = (example, i) => `${base}data/calculator-examples/${encodeURIComponent(example.id)}/${i+1}.png`;
    function draw() {
      stop();
      const example = examples[exampleIndex];
      const pages = Math.ceil(example.steps.length / PAGE_SIZE);
      const start = pageIndex * PAGE_SIZE;
      const visible = example.steps.slice(start, start + PAGE_SIZE);
      activeIndex = start;
      root.innerHTML = `<label>اختر المثال · Choose an example<select id="calculator-example-select">${examples.map((item,i)=>`<option value="${i}" ${i===exampleIndex?'selected':''}>${escape(item.title)}</option>`).join('')}</select></label><div class="calculator-example-card"><p class="calculator-example-problem" dir="auto">${escape(example.problem)}</p><p dir="rtl">ست خطوات في كل صفحة. اختر أي صورة أو شغّل العرض المتحرك لمتابعة الخطوات.</p><div class="calculator-animation"><div><h3>عرض متحرك للخطوات</h3><p id="calculator-active-step" role="status"></p><button type="button" id="calculator-play" aria-pressed="false">▶ تشغيل الخطوات</button></div><img id="calculator-animation-image" src="${imagePath(example,start)}" alt=""></div><div class="calculator-frame-grid" aria-label="صور خطوات الحاسبة">${visible.map(([key,explanation],i)=>{const n=start+i;return `<button type="button" class="calculator-frame" data-frame="${n}" aria-label="الخطوة ${n+1}: ${escape(explanation)}" ${i===0?'aria-current="step"':''}><img src="${imagePath(example,n)}" alt="" loading="lazy"><span>الخطوة ${n+1} · <b dir="ltr">${escape(key)}</b></span><span dir="rtl">${escape(explanation)}</span></button>`}).join('')}</div><nav class="study-slide-actions" aria-label="صفحات خطوات الحاسبة"><button type="button" id="calculator-page-prev" ${pageIndex===0?'disabled':''}>الصفحة السابقة</button><span>صفحة ${pageIndex+1} من ${pages}</span><button type="button" id="calculator-page-next" ${pageIndex===pages-1?'disabled':''}>الصفحة التالية</button></nav><details><summary>كيف أكتب النتيجة في الحل؟</summary><p dir="auto">${escape(example.result)}</p></details></div>`;
      const update = () => {
        const [key, explanation] = example.steps[activeIndex];
        const image = root.querySelector('#calculator-animation-image');
        image.src = imagePath(example, activeIndex);
        image.alt = `شاشة المحاكي بعد الخطوة ${activeIndex+1}؛ الزر المستخدم محدد بالبرتقالي`;
        root.querySelector('#calculator-active-step').textContent = `الخطوة ${activeIndex+1} من ${example.steps.length} · ${key}: ${explanation}`;
        root.querySelectorAll('[data-frame]').forEach(button => {
          if (Number(button.dataset.frame) === activeIndex) button.setAttribute('aria-current','step');
          else button.removeAttribute('aria-current');
        });
      };
      update();
      const play = root.querySelector('#calculator-play');
      root.querySelector('#calculator-example-select').onchange = e => { exampleIndex=Number(e.target.value); pageIndex=0; draw(); };
      root.querySelector('#calculator-page-prev').onclick = () => { pageIndex--; draw(); };
      root.querySelector('#calculator-page-next').onclick = () => { pageIndex++; draw(); };
      root.querySelectorAll('[data-frame]').forEach(button => button.onclick = () => { stop(); play.textContent='▶ تشغيل الخطوات'; play.setAttribute('aria-pressed','false'); activeIndex=Number(button.dataset.frame); update(); });
      play.onclick = () => {
        if (timer !== null) { stop(); play.textContent='▶ تشغيل الخطوات'; play.setAttribute('aria-pressed','false'); return; }
        if (activeIndex >= start + visible.length - 1) { activeIndex=start; update(); }
        play.textContent='⏸ إيقاف مؤقت'; play.setAttribute('aria-pressed','true');
        timer = setInterval(() => {
          if (!root.isConnected || document.hidden || !root.closest('details')?.open) { stop(); if (root.isConnected) { play.textContent='▶ تشغيل الخطوات'; play.setAttribute('aria-pressed','false'); } return; }
          if (activeIndex >= start + visible.length - 1) { stop(); play.textContent='▶ إعادة تشغيل الصفحة'; play.setAttribute('aria-pressed','false'); return; }
          activeIndex++; update();
        }, 1800);
      };
    }
    draw();
  } catch {
    root.textContent = 'تعذّر تحميل الأمثلة المصوّرة. أعد تحميل الصفحة للمحاولة مجددًا.';
  }
}

const PAGE_SIZE = 6;
const labels = {EQ:'=',NEG:'(−)',MUL:'×',DIV:'÷',ADD:'+',SUB:'−',LP:'(',RP:')',POW:'xʸ',RIGHT:'→',SQRT:'√'};
const esc = s => String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

// Each frame is a fresh, isolated instance of the same emulator used by the student.
export function setupQuestionWalkthrough(root, base='/') {
  root._walkthroughController?.abort();
  root._walkthroughController = new AbortController();
  root.addEventListener('toggle', event => {
    const panel=event.target;
    if (!panel.matches?.('.question-walkthrough') || !panel.open || panel.dataset.initialized) return;
    panel.dataset.initialized='true';
    const sequences=JSON.parse(panel.dataset.sequences), content=panel.querySelector('.question-walkthrough-content');
    let selected=0, page=0;
    function draw() {
      const seq=sequences[selected], pages=Math.ceil(seq.keys.length/PAGE_SIZE), start=page*PAGE_SIZE;
      content.innerHTML=`<p>Question-specific emulator frames. Each frame shows the screen after the highlighted key. Six steps per page.</p><label>Choose a calculation <select class="walkthrough-select">${sequences.map((s,i)=>`<option value="${i}" ${i===selected?'selected':''}>${esc(s.label)}</option>`).join('')}</select></label><div class="question-walkthrough-grid">${seq.keys.slice(start,start+PAGE_SIZE).map((key,i)=>`<figure><iframe title="Step ${start+i+1}: press ${esc(labels[key]||key)}" tabindex="-1"></iframe><figcaption>Step ${start+i+1} · Press <kbd>${esc(labels[key]||key)}</kbd><span class="walkthrough-screen" aria-live="polite">Loading screen…</span></figcaption></figure>`).join('')}</div><nav class="study-slide-actions" aria-label="Calculator walkthrough pages"><button type="button" class="walkthrough-prev" ${page===0?'disabled':''}>Previous</button><span>Page ${page+1} of ${pages}</span><button type="button" class="walkthrough-next" ${page===pages-1?'disabled':''}>Next</button></nav>`;
      content.querySelector('.walkthrough-select').onchange=e=>{selected=Number(e.target.value);page=0;draw();};
      content.querySelector('.walkthrough-prev').onclick=()=>{page--;draw();};
      content.querySelector('.walkthrough-next').onclick=()=>{page++;draw();};
      content.querySelectorAll('iframe').forEach((frame,i)=>{
        const step=start+i;
        frame.onload=()=>{try{
          const win=frame.contentWindow;
          if (!win.fx) throw Error('Emulator unavailable');
          for(const key of seq.keys.slice(0,step+1)) win.fx.press(key);
          const key=seq.keys[step], button=frame.contentDocument.querySelector(`[data-key="${key}"]`);
          if(button){button.style.outline='4px solid #ff7900';button.style.outlineOffset='2px';}
          frame.parentElement.querySelector('.walkthrough-screen').textContent=win.fx.text() || 'Calculator ready';
        }catch{frame.parentElement.querySelector('.walkthrough-screen').textContent='Could not load this frame. Use the key sequence below.';}};
        frame.src=`${base}vendor/fx991ce/src/index.html?walkthrough=1`;
      });
    }
    draw();
  },{capture:true,signal:root._walkthroughController.signal});
}

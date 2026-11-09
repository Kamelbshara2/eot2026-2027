export function setupFloatingCalculator(root, base = '/') {
 const open = root.querySelector('#open-floating-calculator');
 const panel = root.querySelector('#floating-calculator');
 const bar = panel.querySelector('.floating-calculator-bar');
 const frame = panel.querySelector('iframe');
 const close = () => { panel.hidden = true; open.setAttribute('aria-expanded','false'); open.focus(); };
 open.onclick = () => { if (!frame.src) frame.src = `${base}vendor/fx991ce/src/index.html`; panel.hidden = false; open.setAttribute('aria-expanded','true'); panel.querySelector('#calculator-close').focus(); };
 panel.querySelector('#calculator-close').onclick = close;
 const dock = side => { panel.style.left = side === 'left' ? '8px' : `${Math.max(8, window.innerWidth-panel.offsetWidth-8)}px`; panel.style.top = `${Math.min(Math.max(8, panel.offsetTop), Math.max(8,window.innerHeight-panel.offsetHeight-8))}px`; panel.style.right='auto'; panel.style.bottom='auto'; };
 panel.querySelector('#calculator-dock-left').onclick = () => dock('left');
 panel.querySelector('#calculator-dock-right').onclick = () => dock('right');
 let drag = null;
 bar.addEventListener('pointerdown', e => { if(e.button !== 0 || e.target.closest('button')) return; const rect=panel.getBoundingClientRect(); drag={x:e.clientX-rect.left,y:e.clientY-rect.top}; bar.setPointerCapture(e.pointerId); });
 bar.addEventListener('pointermove', e => { if(!drag)return; panel.style.left=`${Math.max(0,Math.min(window.innerWidth-panel.offsetWidth,e.clientX-drag.x))}px`; panel.style.top=`${Math.max(0,Math.min(window.innerHeight-45,e.clientY-drag.y))}px`; panel.style.right='auto'; panel.style.bottom='auto'; });
 bar.addEventListener('pointerup', () => { drag=null; });
 bar.addEventListener('pointercancel', () => { drag=null; });
 panel.addEventListener('keydown', e => { if(e.key==='Escape') close(); });
 window.addEventListener('resize', () => { if(!panel.isConnected)return; const rect=panel.getBoundingClientRect(); if(rect.right>innerWidth || rect.top>innerHeight-45) dock('right'); });
}

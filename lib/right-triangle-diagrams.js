const text=(s,x,y)=>`<text x="${x}" y="${y}" text-anchor="middle">${String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}</text>`;
const path=(a,b)=>`<path d="M${a[0]} ${a[1]}L${b[0]} ${b[1]}"/>`;
const right=(v,a,b)=>{const u=p=>{const l=Math.hypot(p[0]-v[0],p[1]-v[1]);return [(p[0]-v[0])/l,(p[1]-v[1])/l]},r=u(a),s=u(b),n=15;return `<path class="angle-mark" d="M${v[0]+n*r[0]} ${v[1]+n*r[1]}l${n*s[0]} ${n*s[1]}l${-n*r[0]} ${-n*r[1]}"/>`};
export function rightTriangleDiagram(q){const g=q.rightTriangleDiagram;if(!g)return '';let shape='',labels='',marks='';
 if(g.kind==='right'){
  const scale=Math.min(340/g.legs[1],210/g.legs[0]),w=g.legs[1]*scale,h=g.legs[0]*scale,A=[100,260-h],B=[100,260],C=[100+w,260];shape=path(A,B)+path(B,C)+path(C,A);marks=right(B,A,C);labels=text(g.labels[0],65,260-h/2)+text(g.labels[1],100+w/2,292)+text(g.labels[2],100+w/2+32,260-h/2-12);if(g.angleC)labels+=text(g.angleC+'°',C[0]-38,249);if(g.angleA)labels+=text(g.angleA+'°',117,A[1]+48);
 }else if(g.kind==='square'){
  const A=[160,40],B=[400,40],C=[400,280],D=[160,280];shape=path(A,B)+path(B,C)+path(C,D)+path(D,A)+path(A,C);marks=right(B,A,C);if(g.number===33)labels=text('x',280,27)+text('13',300,140)+text('y°',363,266);else labels=text('12',125,160)+text('y',300,140)+text('x°',203,60);
 }else if(g.kind==='special34'){
  const A=[100,250],B=[300,50],C=[500,250],D=[300,250];shape=path(A,B)+path(B,C)+path(C,A)+path(B,D);marks=right(B,A,C)+right(D,B,C);labels=text('6',175,135)+text('x',320,170)+text('y',300,290)+text('45°',457,241);
 }else if(g.kind==='special35'){
  const A=[80,40],B=[440,40],C=[440,40+120*Math.sqrt(3)],D=[350,40+90*Math.sqrt(3)];shape=path(A,B)+path(B,C)+path(C,A)+path(B,D);marks=right(B,A,C)+right(D,A,B);labels=text('2√3',250,25)+text('30°',128,57)+text('60°',424,210)+text('x',220,132)+text('y',412,247);
 }else if(g.kind==='special36'){
  const A=[100,40],B=[500,40],C=[500,240],D=[100,240],M=[300,240];shape=path(A,B)+path(B,C)+path(C,D)+path(D,A)+path(A,M)+path(B,M);marks=right(M,A,B)+right(C,B,D)+right(D,A,C);labels=text('y',300,27)+text('x',532,153)+text('5√2',412,155);shape+='<path d="m190 135 14-10 M396 135l14 10"/>';
 }else if(g.kind==='special37'){
  const A=[100,40],B=[100,240],C=[100+200*Math.sqrt(3),240],H=[100+50*Math.sqrt(3),90];shape=path(A,B)+path(B,C)+path(C,A)+path(B,H);marks=right(B,A,C)+right(H,A,B);labels=text('60°',117,90)+text('30°',C[0]-43,229)+text('x',275,275)+text('y',134,50)+text('9',335,164)+text('3√3',124,170);
 }
 return `<figure class="right-triangle-figure"><svg viewBox="0 0 600 330" role="img" aria-label="Right-triangle diagram with given lengths, unknowns and angle markings"><g fill="none" stroke="#197e97" stroke-width="2.8">${shape}</g><g fill="none" stroke="#ba4c88" stroke-width="2">${marks}</g><g font-family="Arial,sans-serif" font-size="22" fill="#244557">${labels}</g></svg><figcaption>Use the labelled lengths and angle markings. · استعمل الأطوال وعلامات الزوايا المعطاة.</figcaption></figure>`;
}
export function validRightTriangleDiagram(g){return g&&(['right'].includes(g.kind)?Array.isArray(g.legs)&&g.legs.length===2&&g.legs.every(n=>Number.isFinite(n)&&n>0&&n<10000)&&Array.isArray(g.labels)&&g.labels.length===3&&g.labels.every(s=>typeof s==='string'&&s.length<50)&&[undefined,30,45,60].includes(g.angleA)&&[undefined,30,45,60].includes(g.angleC):g.kind==='square'?[33,38].includes(g.number):['special34','special35','special36','special37'].includes(g.kind))}
export function doubleExactTex(s){if(s.includes('circ'))return '90^\\circ';if(/^\d+$/.test(s))return String(2*Number(s));const radical=s.match(/^(\d+)\\sqrt([23])$/);if(radical)return `${2*Number(radical[1])}\\sqrt${radical[2]}`;const fraction=s.match(/^\\frac\{(\d+)(\\sqrt[23])?\}\{(\d+)\}$/);if(fraction){let n=2*Number(fraction[1]),d=Number(fraction[3]);const gcd=(a,b)=>b?gcd(b,a%b):a,g=gcd(n,d);n/=g;d/=g;const numerator=String(n)+(fraction[2]||'');return d===1?numerator:`\\frac{${numerator}}{${d}}`}return `2\\left(${s}\\right)`}
export const pairOptionTex=(x,y)=>`$\\begin{gathered}x=${x}\\\\y=${y}\\end{gathered}$`;

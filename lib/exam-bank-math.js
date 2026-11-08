import katex from 'katex';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const bankMath=latex=>katex.renderToString(latex,{throwOnError:false,strict:'ignore',output:'htmlAndMathml'});
export const bankStem=q=>`<p class="term-bank-stem">${esc(q.math_latex?q.instruction:q.stem)}</p>${q.math_latex?`<div class="term-bank-math">${bankMath(q.math_latex)}</div>`:''}${q.source?`<p class="term-bank-source">Reveal · p. ${Number(q.source.printed_page)} · ${esc(q.source.exercise)}${q.source_kind==='concept_application'?' · Concept application':q.source_kind==='example_variant'?' · Example variant':q.source.adaptation==='mcq'?' · MCQ adaptation':''}</p>`:''}`;
export const bankOption=o=>o.math_latex?bankMath(o.math_latex):esc(o.text);

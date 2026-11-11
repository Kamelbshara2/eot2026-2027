import {classroomLabels} from './branding.js';
import {calculatorGuide} from './calculator-guide.js';
import {bankStem,bankOption,bankMath} from './exam-bank-math.js';
import {renderTermMockExam,stopTermMockExam} from './term-mock-ui.js';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const bankConfigs={
 '10A1':{id:'10a1-term1',outcomes:25,questions:108,studyQuestions:205,mcq:88,frq:20,mockNamespace:'10a1-term1-exam-review-v2'},
 '9G3':{id:'9g3-term1',outcomes:26,questions:126,studyQuestions:238,mcq:173,frq:65,mockNamespace:'9g3-term1-exam-review-v2'},
 '10G3':{id:'10g3-term1',outcomes:25,questions:155,studyQuestions:155,mcq:134,frq:21,mockNamespace:'10g3-term1-exam-review-v2'},
 '9A':{id:'9a-term1',outcomes:25,questions:188,studyQuestions:188,mcq:141,frq:47,mockNamespace:'9a-term1-study-v1',upper:true},
 '11G':{id:'11g-term1',outcomes:26,questions:137,studyQuestions:137,mcq:105,frq:32,mockNamespace:'11g-term1-study-v1',upper:true},
 '11A':{id:'11a-term1',outcomes:25,questions:154,studyQuestions:154,mcq:122,frq:32,mockNamespace:'11a-term1-study-v1',upper:true},
 '12G':{id:'12g-term1',outcomes:25,questions:282,studyQuestions:282,mcq:246,frq:36,mockNamespace:'12g-term1-study-v1',upper:true},
 '12A':{id:'12a-term1',outcomes:26,questions:180,studyQuestions:180,mcq:144,frq:36,mockNamespace:'12a-term1-study-v1',upper:true}
};
const bankBase=classroom=>`${import.meta.env?.BASE_URL||'/'}data/exam-banks/${bankConfigs[classroom].id}/`;
export const examBankPath=(id,classroom='10A1')=>`#/classrooms/${classroom}/banks/term1${id?'/outcomes/'+encodeURIComponent(id):''}`;
export const examBankMockPath=(classroom='10A1')=>examBankPath(null,classroom)+'/mock';
export function examBankRoute(hash){const m=hash.match(/^#?\/?classrooms\/(10A1|10G3|9G3|9A|11G|11A|12G|12A)\/banks\/term1(?:\/(mock)|\/(print)|\/(quiz)(?:\?([^#]*))?|\/outcomes\/([^/]+))?\/?$/);if(!m)return null;const [,classroom,mock,print,quiz,query,id]=m;return {classroom,outcomeId:id||null,valid:!id||/^LO\d{2}$/.test(id)&&Number(id.slice(2))>=1&&Number(id.slice(2))<=bankConfigs[classroom].outcomes,...(mock?{mock:true}:{}),...(print?{print:true}:{}),...(quiz?{quiz:true,query:query||''}:{})}}
export function validateExamBank(bank){const c=bankConfigs[bank?.classroom];if(!c||bank.id!==c.id||!Array.isArray(bank.learning_outcomes)||bank.learning_outcomes.length!==c.outcomes||!Array.isArray(bank.questions)||bank.questions.length!==c.questions)return false;const ids=new Set(bank.questions.map(q=>q.id));return ids.size===c.questions&&new Set(bank.learning_outcomes.map(o=>o.id)).size===c.outcomes&&bank.learning_outcomes.every((o,i)=>o.id===`LO${String(i+1).padStart(2,'0')}`&&o.question_ids.length===o.question_count&&o.question_ids.every(id=>ids.has(id)&&bank.questions.find(q=>q.id===id).learning_outcome_id===o.id))}
export function bankAssetUrl(src,classroom='10A1'){if(!bankConfigs[classroom]||!/^assets\/[a-z0-9_]+\.(?:svg|png)$/.test(src))throw Error('Invalid bank image path');return bankBase(classroom)+src}
export const bankStorageKey=(id,classroom='10A1')=>classroom==='10A1'?`forma-term1-bank-${id}`:`forma-term1-bank-${bankConfigs[classroom].id}-${id}`;
const bankPromises=new Map();let active=null;
export function clearExamBankSession(id,storage){if(!id)return;if(active?.studentKey===id){stopTermMockExam();active=null}try{const local=storage??globalThis.sessionStorage;for(const classroom of Object.keys(bankConfigs)){local?.removeItem(bankStorageKey(id,classroom));if(bankConfigs[classroom].mockNamespace)local?.removeItem(`forma-term1-mock-${bankConfigs[classroom].mockNamespace}-${id}`);local?.removeItem(classroom==='10A1'?`forma-term1-mock-${id}`:`forma-term1-mock-${bankConfigs[classroom].id}-${id}`)}}catch{}}
async function loadBank(classroom){if(!bankPromises.has(classroom))bankPromises.set(classroom,fetch(bankBase(classroom)+'index.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error('Question bank unavailable');return r.json()}).then(bank=>{if(!validateExamBank(bank)||bank.classroom!==classroom)throw Error('Invalid question bank');return bank}).catch(e=>{bankPromises.delete(classroom);throw e}));return bankPromises.get(classroom)}
const answered=d=>Boolean(d?.choice||d?.working?.trim()||Object.values(d?.parts||{}).some(v=>typeof v==='string'&&v.trim()));
const downloadUrl=(o,BASE)=>/^LO(?:0[1-9]|1[0-9]|2[0-5])\.json$/.test(o.download)?BASE+o.download:BASE+'source.json';
const refs=o=>o.textbook_references.map(r=>`p. ${r.printed_page} · ${r.exercises_or_section}`).join(' / ');
export function examBankEntryMarkup(classroom='10A1'){const c=bankConfigs[classroom];if(!c)return '';return `<a class="term-bank-entry" href="${examBankPath(null,classroom)}"><span><b>مذاكرة الهيكل الاختبار النهائي للفصل الاول</b><small>${classroomLabels[classroom]?.ar||''} · ${c.outcomes} دروس · شرح باللغتين · أمثلة ومساعد للمذاكرة</small></span><span aria-hidden="true">↗</span></a>${classroom==='10A1'?`<a class="term-bank-entry" href="${import.meta.env?.BASE_URL||'/'}exams/10a1-four-outcomes-assessment-practice.html"><span><b>Four-outcome assessment practice · بنك تدريب المخرجات الأربعة</b><small>38 MCQs + 12 written tasks · الصور الأصلية وخطوات الحل</small></span><span aria-hidden="true">↗</span></a>`:''}`}
export async function renderExamBank(context) {
 stopTermMockExam();
 const {renderStudyBooklet} = await import('./study-booklet.js');
 return renderStudyBooklet(context);
}

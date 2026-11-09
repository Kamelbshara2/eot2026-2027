// Learning-outcome quiz builder and grader (pure logic, no DOM).
import {parseBlanks, flatBlanks, checkBlanks} from './study-fill.js';

export const QUIZ_SIZES = [5, 10, 15, 20];
export const hasBlanks = q => q.type === 'frq' && q.parts.some(p => p.blanks);
// Written questions are auto-gradable only when every part that needs a typed answer has blanks.
export const gradableFrq = q => q.type === 'frq' && q.parts.some(p => p.blanks);

const shuffle = (items, random) => { const a = [...items]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };

export function quizPool(bank, {los, mix = 'all'}) {
  const wanted = new Set(los);
  return bank.questions.filter(q => wanted.has(q.learning_outcome_id) && (q.type === 'mcq' ? mix !== 'frq' : mix !== 'mcq' && gradableFrq(q)));
}

// Round-robin across learning outcomes so every selected outcome is represented.
export function buildQuiz(bank, {los, count = 10, mix = 'all', random = Math.random, onlyIds = null}) {
  let pool = quizPool(bank, {los, mix});
  if (onlyIds) pool = pool.filter(q => onlyIds.includes(q.id));
  const byLo = new Map();
  for (const q of shuffle(pool, random)) { if (!byLo.has(q.learning_outcome_id)) byLo.set(q.learning_outcome_id, []); byLo.get(q.learning_outcome_id).push(q); }
  const lists = shuffle([...byLo.values()], random), picked = [];
  while (picked.length < count && lists.some(l => l.length)) for (const l of lists) if (l.length && picked.length < count) picked.push(l.shift());
  const ordered = shuffle(picked, random);
  return {
    version: 1, bankId: bank.id, startedAt: Date.now(), los: [...los], mix,
    ids: ordered.map(q => q.id),
    options: Object.fromEntries(ordered.filter(q => q.type === 'mcq').map(q => [q.id, shuffle(q.options.map(o => o.id), random)])),
    answers: {}, finished: false
  };
}

export function partBlankList(part) { return part.blanks ? flatBlanks(parseBlanks(part.blanks)) : []; }

// answer shapes: mcq -> option id string; frq -> {partId: [values]}
export function gradeQuestion(q, answer) {
  if (q.type === 'mcq') {
    const ok = answer === q.answer.correct_option_id;
    return {score: ok ? 1 : 0, max: 1, answered: Boolean(answer), correct: ok};
  }
  let right = 0, total = 0, answered = false;
  for (const part of q.parts) {
    const blanks = partBlankList(part); if (!blanks.length) continue;
    const values = answer?.[part.id] || [];
    if (values.some(v => String(v ?? '').trim())) answered = true;
    const res = checkBlanks(blanks, blanks.map((_, i) => values[i] ?? ''));
    right += res.filter(Boolean).length; total += res.length;
  }
  return {score: total ? right / total : 0, max: 1, answered, correct: total > 0 && right === total, right, total};
}

export function gradeQuiz(quiz, bank) {
  const byId = new Map(bank.questions.map(q => [q.id, q]));
  const per = quiz.ids.map(id => { const q = byId.get(id); return {id, lo: q.learning_outcome_id, ...gradeQuestion(q, quiz.answers[id])}; });
  const score = per.reduce((s, r) => s + r.score, 0), max = per.length;
  const los = {};
  for (const r of per) { (los[r.lo] ||= {score: 0, max: 0}); los[r.lo].score += r.score; los[r.lo].max += 1; }
  return {per, score, max, percent: max ? Math.round(score / max * 100) : 0, los, wrongIds: per.filter(r => !r.correct).map(r => r.id)};
}

export function validQuiz(quiz, bank) {
  if (!quiz || quiz.version !== 1 || quiz.bankId !== bank.id || !Array.isArray(quiz.ids) || !quiz.ids.length || !quiz.answers || typeof quiz.answers !== 'object') return false;
  const byId = new Map(bank.questions.map(q => [q.id, q]));
  return quiz.ids.every(id => byId.has(id)) && new Set(quiz.ids).size === quiz.ids.length &&
    quiz.ids.every(id => { const q = byId.get(id); if (q.type !== 'mcq') return gradableFrq(q); const o = quiz.options?.[id]; return Array.isArray(o) && o.length === q.options.length && o.every(x => q.options.some(y => y.id === x)); });
}

export const quizHash = (classroom, los, count, mix) => `#/classrooms/${classroom}/banks/term1/quiz?lo=${los.join(',')}&n=${count}&mix=${mix}`;
export function parseQuizQuery(query = '') {
  const p = new URLSearchParams(query);
  const los = (p.get('lo') || '').split(',').filter(x => /^LO\d{2}$/.test(x));
  const n = Number(p.get('n')); const mix = p.get('mix');
  return {los, count: QUIZ_SIZES.includes(n) ? n : 10, mix: ['all', 'mcq', 'frq'].includes(mix) ? mix : 'all', timed: p.get('t') === '1'};
}

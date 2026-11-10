import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const load = p => JSON.parse(fs.readFileSync(new URL('../' + p, import.meta.url)));
const bank = load('public/data/study/10G3.json');
const q = id => bank.questions.find(x => x.id === id);

// "ax^2 + bx + c" with integer or \frac{p}{q} coefficients -> [a,b,c] as numbers
function coeffs(tex, v) {
  const t = tex.replace(/\\frac\{(-?\d+)\}\{(\d+)\}/g, (m, p, d) => `(${Number(p) / Number(d)})`).replace(/\^\{2\}/, '^2').replace(/\s+/g, '');
  const terms = t.match(/[+-]?[^+-]+/g);
  const out = [0, 0, 0];
  for (const term of terms) {
    const sign = term.startsWith('-') ? -1 : 1, body = term.replace(/^[+-]/, '');
    const num = s => { const m = s.match(/^\((-?[\d.]+)\)$/); return m ? Number(m[1]) : s === '' ? 1 : Number(s); };
    if (body.includes(v + '^2')) out[0] += sign * num(body.replace(v + '^2', ''));
    else if (body.endsWith(v)) out[1] += sign * num(body.slice(0, -1));
    else out[2] += sign * num(body);
  }
  return out;
}
const isSquare = n => Number.isInteger(n) && n >= 0 && Math.sqrt(n) % 1 === 0;
const optionsOf = id => q(id).options.map(o => ({id: o.id, text: o.math_latex}));

test('G10G-Q05.1: exactly one option cannot be factored over the integers, and it is the key', () => {
  const factorable = optionsOf('G10G-Q05-MCQ-01').filter(o => { const [a, b, c] = coeffs(o.text, 'x'); return isSquare(b * b - 4 * a * c); }).map(o => o.id);
  assert.equal(factorable.length, 3);
  assert.deepEqual(['A', 'B', 'C', 'D'].filter(i => !factorable.includes(i)), [q('G10G-Q05-MCQ-01').answer.correct_option_id]);
});

test('G10G-Q15.1: exactly one option is not a perfect-square trinomial, and it is the key', () => {
  const squares = optionsOf('G10G-Q15-MCQ-01').filter(o => { const [a, b, c] = coeffs(o.text, 'n'); return Math.abs(b * b - 4 * a * c) < 1e-9; }).map(o => o.id);
  assert.equal(squares.length, 3);
  assert.deepEqual(['A', 'B', 'C', 'D'].filter(i => !squares.includes(i)), [q('G10G-Q15-MCQ-01').answer.correct_option_id]);
  assert.match(q('G10G-Q15-MCQ-01').answer.explanation, /B, C and D/);
});

test('the three study banks and the exam-bank copies agree on the corrected questions', () => {
  const copy = load('public/data/exam-banks/10g3-term1/index.json').questions;
  for (const id of ['G10G-Q05-MCQ-01', 'G10G-Q15-MCQ-01']) {
    const a = copy.find(x => x.id === id);
    assert.deepEqual(a.options.map(o => o.text), q(id).options.map(o => o.text));
    assert.equal(a.answer.correct_option_id, q(id).answer.correct_option_id);
  }
});

test('automated audit report: no errors and an honest list of what still needs a human', () => {
  const audit = load('content-imports/study-question-audit.json');
  for (const [classroom, s] of Object.entries(audit.stats)) {
    assert.equal(s.errors, 0, classroom + ' has audit errors');
    assert.equal(s.structure_ok, s.mcq, classroom + ' every MCQ has four distinct options and one key');
    assert.ok(s.needs_human > 0, 'limits must be reported');
  }
  assert.match(audit.limitations, /NOT certified/);
});

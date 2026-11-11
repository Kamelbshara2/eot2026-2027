import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import katex from 'katex';
import {sameValue, parseBlanks, flatBlanks, checkBlanks, solvedMarkup, fillMarkup, validateLines} from '../lib/study-fill.js';
import {buildQuiz, gradeQuiz, gradeQuestion, quizPool, validQuiz, parseQuizQuery, quizHash} from '../lib/study-quiz.js';
import {examBankRoute} from '../lib/exam-bank-ui.js';

const load = c => JSON.parse(fs.readFileSync(new URL(`../public/data/study/${c}.json`, import.meta.url)));
const seeded = () => { let s = 7; return () => (s = (s * 16807) % 2147483647) / 2147483647; };

test('blank checker accepts equivalent algebra but keeps exact blanks strict', () => {
  assert.ok(sameValue('12+2r', '2r+12'));
  assert.ok(sameValue('5q-11', '-15+5q+4'));
  assert.ok(sameValue('1/2', '0.5'));
  assert.ok(sameValue('-\\frac{\\sqrt{3}}{2}', '-sqrt(3)/2'));
  assert.ok(sameValue('x^{10}', 'x^10'));
  assert.ok(!sameValue('68', '2+66', {exact: true}));
  assert.ok(!sameValue('2x', '2x-6'));
  assert.ok(sameValue('3.46', '3.5', {tolerance: 0.06}));
});

test('unordered groups cannot be filled with the same answer twice', () => {
  const p = parseBlanks({lines: ['(x[[+2#z]])(x[[-6#z]])']});
  const b = flatBlanks(p);
  assert.deepEqual(checkBlanks(b, ['-6', '2']), [true, true]);
  assert.deepEqual(checkBlanks(b, ['2', '2']), [true, false]);
});

for (const c of ['9G3', '9A', '10G3', '10A1']) {
  test(`${c}: every authored blank template parses, renders and accepts its own answers`, () => {
    const bank = load(c); let parts = 0;
    for (const q of bank.questions.filter(q => q.type === 'frq')) for (const part of q.parts) {
      if (!part.blanks) continue; parts++;
      const parsed = parseBlanks(part.blanks), blanks = flatBlanks(parsed);
      assert.ok(blanks.length > 0, q.id + part.id);
      assert.ok(blanks.every((b, i) => b.index === i), 'contiguous indexes ' + q.id);
      const values = blanks.map(b => b.answers[0]);
      assert.ok(checkBlanks(blanks, values).every(Boolean), `${q.id}${part.id} rejects its own answers`);
      assert.ok(!checkBlanks(blanks, blanks.map(() => '')).some(Boolean), `${q.id}${part.id} accepts empty input`);
      validateLines(part.blanks);
      assert.ok(fillMarkup(part.blanks, 't').html.includes('fill-box'));
      assert.ok(!solvedMarkup(part.blanks).includes('katex-error'), `${q.id}${part.id} solved view renders`);
    }
    assert.ok(parts >= 20, 'most written questions should be interactive');
  });
}

test('10A1 sin B = 1 triangle is corrected to a single right triangle everywhere in the study data', () => {
  const q = load('10A1').questions.find(q => q.id === 'G10A-BOOK-Q25-FRQ-04');
  assert.match(q.parts[0].answer.model_answer_and_marking, /Exactly one solution/);
  assert.doesNotMatch(q.parts[1].answer.model_answer_and_marking, /B≈90°.*B≈90°/);
});

for (const c of ['9G3', '9A', '10G3', '10A1']) {
  test(`${c}: quiz builder balances outcomes, shuffles options and grades correct answers as 100%`, () => {
    const bank = load(c), los = bank.learning_outcomes.map(l => l.id);
    const quiz = buildQuiz(bank, {los, count: 20, mix: 'all', random: seeded()});
    assert.equal(quiz.ids.length, 20); assert.equal(new Set(quiz.ids).size, 20);
    assert.ok(new Set(quiz.ids.map(id => bank.questions.find(q => q.id === id).learning_outcome_id)).size >= 15, 'spread across outcomes');
    assert.ok(validQuiz(quiz, bank));
    for (const id of quiz.ids) {
      const q = bank.questions.find(x => x.id === id);
      if (q.type === 'mcq') { assert.equal(new Set(quiz.options[id]).size, 4); quiz.answers[id] = q.answer.correct_option_id; }
      else quiz.answers[id] = Object.fromEntries(q.parts.filter(p => p.blanks).map(p => [p.id, flatBlanks(parseBlanks(p.blanks)).map(b => b.answers[0])]));
    }
    const r = gradeQuiz(quiz, bank);
    assert.equal(r.percent, 100); assert.equal(r.wrongIds.length, 0);
    const wrong = {...quiz, answers: {}}; assert.equal(gradeQuiz(wrong, bank).percent, 0);
  });
}

test('mix filter and single-outcome pools', () => {
  const bank = load('9G3');
  assert.ok(quizPool(bank, {los: ['LO21'], mix: 'mcq'}).length === 0);
  assert.ok(quizPool(bank, {los: ['LO21'], mix: 'frq'}).length >= 4);
  assert.ok(quizPool(bank, {los: ['LO01'], mix: 'all'}).every(q => q.type === 'mcq'));
  const q = bank.questions.find(q => q.id === 'G9G-BOOK-Q22-FRQ-01');
  const half = gradeQuestion(q, {a: ['2w', 'P-2w', '2'], b: ['', '', '']});
  assert.ok(half.score > 0 && half.score < 1);
});

test('quiz routes and queries', () => {
  const h = quizHash('9G3', ['LO01', 'LO02'], 10, 'mcq');
  assert.deepEqual(examBankRoute(h), {classroom: '9G3', outcomeId: null, valid: true, quiz: true, query: 'lo=LO01,LO02&n=10&mix=mcq'});
  assert.deepEqual(parseQuizQuery('lo=LO01,xx&n=99&mix=zzz&t=1'), {los: ['LO01'], count: 10, mix: 'all', timed: true});
});

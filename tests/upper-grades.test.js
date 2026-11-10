import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {parseBlanks, checkBlanks} from '../lib/study-fill.js';

const CLASSES = {'11G': 26, '11A': 25, '12G': 25, '12A': 26};
const load = c => JSON.parse(fs.readFileSync(new URL(`../public/data/study/${c}.json`, import.meta.url)));
const exists = p => fs.existsSync(new URL(`../public/${p}`, import.meta.url));

for (const [c, outcomes] of Object.entries(CLASSES)) {
  test(`${c}: structure outcomes are complete, typed correctly and have at least five questions each`, () => {
    const bank = load(c), byId = new Map(bank.questions.map(q => [q.id, q]));
    assert.equal(bank.learning_outcomes.length, outcomes);
    assert.equal(new Set(bank.questions.map(q => q.id)).size, bank.questions.length);
    bank.learning_outcomes.forEach((lo, i) => {
      assert.equal(lo.id, `LO${String(i + 1).padStart(2, '0')}`);
      assert(lo.title_ar && lo.rule_ar && lo.rule_summary, `${lo.id} needs Arabic title and rule`);
      const right = lo.question_ids.map(id => byId.get(id)).filter(q => q.type === lo.question_type);
      assert(right.length >= 5, `${c} ${lo.id} has ${right.length} ${lo.question_type}`);
      assert.equal(right.length, lo.question_ids.length, `${lo.id} mixes question types`);
    });
  });
  test(`${c}: MCQ keys exist, options are distinct, and every picture is on disk`, () => {
    const bank = load(c);
    for (const q of bank.questions) {
      for (const id of q.diagram_asset_ids) assert(exists(bank.assets[id].src), `${q.id}: ${id}`);
      if (q.type !== 'mcq') continue;
      assert.equal(q.options.length, 4);
      assert(q.options.some(o => o.id === q.answer.correct_option_id), q.id);
      if (!q.embedded_options) assert.equal(new Set(q.options.map(o => o.math_latex)).size, 4, `${q.id} has duplicate options`);
      for (const o of q.options) if (o.image) assert(exists(bank.assets[o.image].src), `${q.id} option ${o.id}`);
    }
  });
  test(`${c}: every auto-checked blank accepts its own reference answer`, () => {
    const bank = load(c);
    for (const q of bank.questions) for (const p of q.parts || []) {
      if (!p.blanks) continue;
      const pb = parseBlanks(p.blanks), all = [...pb.lines.flatMap(l => l.segments.filter(s => s.kind === 'blank')), ...(pb.table ? pb.table.cells : [])].sort((a, b) => a.index - b.index);
      assert(all.length, `${q.id} ${p.id}`);
      assert(checkBlanks(all, all.map(b => b.answers[0])).every(Boolean), `${q.id} ${p.id}`);
    }
  });
}

test('written questions: text-only ones are all auto-checked; image cards are auto-checked except seven documented paper-only ones', () => {
  let textOnly = 0, cards = 0, auto = 0; const paper = [];
  for (const c of Object.keys(CLASSES)) for (const q of load(c).questions.filter(q => q.type === 'frq')) {
    const has = q.parts.some(p => p.blanks);
    if (q.figure_in_image) { cards++; assert(q.parts.length && q.diagram_asset_ids.length); } else { textOnly++; assert(has, `${c} ${q.id} has no auto-checked blanks`); }
    if (has) auto++; else paper.push(q.id);
  }
  assert.equal(textOnly, 69); assert.equal(cards, 67); assert.equal(auto, 129);
  assert.deepEqual(paper.sort(), ['12A-p63-Q3-1', '12A-p63-Q4-1', '12A-p63-Q5-1', '12A-p64-Q6-1', '12A-p64-Q7-1', '12A-p64-Q8-1', '12G-p54-32/19-1']);
});

test('imported question totals match the supplied package (753 eligible of 760)', () => {
  const total = Object.keys(CLASSES).reduce((n, c) => n + load(c).questions.length, 0);
  assert.equal(total, 753);
});

test('every text question and written-part prompt of Grades 11-12 has an Arabic translation', async () => {
  const {translate} = await import('../lib/study-translate.js');
  const table = JSON.parse(fs.readFileSync(new URL('../public/data/study/translations-ar.json', import.meta.url)));
  for (const c of Object.keys(CLASSES)) for (const q of load(c).questions) {
    if (q.figure_in_image) continue;
    assert(translate(table, 'instruction', q.instruction), `${q.id}: ${q.instruction}`);
    for (const p of q.parts || []) assert(translate(table, 'part', p.prompt), `${q.id}: ${p.prompt}`);
  }
});

test('reviewed corrections stay applied (no stray "5k" in the 11G hypotenuse explanations)', () => {
  const q = load('11G').questions.filter(q => q.id.startsWith('11G-Q09-added'));
  assert.equal(q.length, 2);
  for (const x of q) assert.match(x.answer.explanation, /^c=√\(a²\+b²\)=√\(\d+²\+\d+²\)=√\d+=\d+\.$/);
});

// solution derived from the card disagrees with the keyed option; listed for teacher review in UPPER_GRADES_KEY_ISSUES.md
const KNOWN_KEY_CONFLICTS = ['12G-en-Q057'];

test('worked solutions: every authored solution has steps with LaTeX and the final answer matches the key', () => {
  let n = 0;
  for (const c of Object.keys(CLASSES)) for (const q of load(c).questions) {
    const steps = q.answer?.steps; if (!steps) continue; n++;
    assert(steps.length >= 2 && steps.every(s => s.text && s.latex), q.id);
    if (!KNOWN_KEY_CONFLICTS.includes(q.id)) assert.equal(q.answer.steps_verified, true, `${q.id}: derived answer differs from the key`);
  }
  assert(n >= 100);
});

test('corrected answer keys stay corrected', () => {
  const q = Object.fromEntries(load('12G').questions.map(q => [q.id, q]));
  assert.equal(q['12G-en-Q059'].answer.correct_option_id, 'B');
  assert.equal(q['12G-en-Q060'].answer.correct_option_id, 'C');
});

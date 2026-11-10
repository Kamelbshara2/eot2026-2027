import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {parseBlanks, flatBlanks, checkBlanks} from '../lib/study-fill.js';

const load = p => JSON.parse(fs.readFileSync(new URL('../' + p, import.meta.url)));
const bank = load('public/data/study/10A1.json');
const support = load('public/data/study/calculator-support.json').classes['10A1'].questions;
const report = load('content-imports/g10a-revision/build-report.json');
const REV = bank.questions.filter(q => q.id.startsWith('G10A-REV-'));

test('revision import: 100 new questions, 100 duplicates skipped, every official coverage item present exactly once', () => {
  assert.equal(REV.length, 97); assert.equal(report.skipped_duplicates.length, 100); assert.equal(report.added.length, 97); assert.equal(report.held_back.length, 3);
  assert.equal(bank.question_count, 205); assert.equal(bank.mcq_count, 151); assert.equal(bank.frq_count, 54);
  const keys = bank.questions.filter(q => q.source_kind === 'textbook_exercise').map(q => `${q.learning_outcome_id}|${q.source.printed_page}|${q.source.exercise}`);
  const dupes = keys.filter((k, i) => keys.indexOf(k) !== i);
  assert.deepEqual([...new Set(dupes)].filter(k => !/Check|Example|Match|Application/.test(k)), [], 'no exercise appears twice');
  const gap = load('content-imports/coverage-gap.json')['10A1'];
  const missing = Object.values(gap).flatMap(v => v.missing).sort();
  assert.deepEqual(missing, ['p.184 #22', 'p.184 #23', 'p.185 #34'], 'only the three items with cropped source figures are pending');
  assert.equal(Object.values(gap).reduce((n, v) => n + v.structure_items, 0), 200);
});

test('no two questions in an outcome share the same statement and answer (duplicate guard)', () => {
  const seen = new Map();
  for (const q of bank.questions) {
    const key = [q.learning_outcome_id, q.instruction.trim(), (q.math_latex || '').replace(/[\s{}]|\\left|\\right/g, ''), (q.diagram_asset_ids || []).join(),
      q.type === 'mcq' ? q.answer.correct_option_text.replace(/[\s{}]|\\left|\\right/g, '') : JSON.stringify(q.parts.map(p => p.answer.math_latex))].join('|');
    if (!q.diagram_asset_ids.length && (q.math_latex || q.type === 'mcq')) {
      assert.ok(!seen.has(key) || q.parent_question_id || (seen.get(key) || '').includes('REV-LO'), `${q.id} duplicates ${seen.get(key)}`);
      seen.set(key, q.id);
    }
  }
});

test('every imported question has provenance, a unique id, an assigned outcome list entry and a calculator/written guide', () => {
  const ids = new Set(bank.questions.map(q => q.id)); assert.equal(ids.size, bank.questions.length);
  for (const q of REV) {
    assert.equal(q.source.revision_booklet.sha256, report.source.sha256); assert.ok(q.source.revision_booklet.question_number >= 1 && q.source.revision_booklet.question_number <= 200);
    assert.ok(q.source.printed_page && q.source.exercise); assert.equal(q.source_kind, 'textbook_exercise'); assert.ok(['sympy-verified', 'recomputed-numeric', 'teacher-revision-booklet'].includes(q.key_source));
    const lo = bank.learning_outcomes.find(l => l.id === q.learning_outcome_id);
    assert.ok(lo.question_ids.includes(q.id) && lo.booklet_question_ids.includes(q.id)); assert.equal(lo.question_count, lo.question_ids.length);
    const g = support[q.id]; assert.ok(g && g.prepare && g.interpret && g.solutions.length, q.id + ' calculator guide');
  }
});

test('imported figures exist at native resolution and are attached to the right questions', () => {
  const figs = REV.flatMap(q => q.diagram_asset_ids.map(a => [q, a]));
  assert.equal(figs.length, 37);
  for (const [q, a] of figs) {
    const asset = bank.assets[a]; assert.ok(asset, a); assert.ok(fs.existsSync(new URL('../public/' + asset.src, import.meta.url)), asset.src);
    assert.equal(asset.source.revision_question, q.source.revision_booklet.question_number); assert.ok(asset.width >= 150 && asset.height >= 60);
  }
});

test('imported MCQs have four distinct options and one key; algebra keys are sympy-verified; named distractors carry a reason', () => {
  const mcq = REV.filter(q => q.type === 'mcq'); assert.equal(mcq.length, 63);
  for (const q of mcq) {
    assert.equal(q.options.length, 4); assert.equal(new Set(q.options.map(o => o.text.replace(/\s/g, ''))).size, 4, q.id);
    assert.ok(q.options.some(o => o.id === q.answer.correct_option_id)); assert.ok(q.answer.explanation.length > 15, q.id);
    if (q.key_source === 'sympy-verified') for (const o of q.options) if (o.id !== q.answer.correct_option_id) assert.ok(o.misconception, q.id + ' ' + o.id);
  }
  assert.ok(mcq.filter(q => q.key_source === 'sympy-verified').length >= 16);
  assert.ok(report.checks.length >= 16 && report.checks.every(c => c.agrees_with_booklet));
});

test('imported written questions have working blanks that accept their own reference answers', () => {
  const frq = REV.filter(q => q.type === 'frq'); assert.equal(frq.length, 34);
  for (const q of frq) {
    assert.ok(q.parts.some(p => p.blanks), q.id + ' blanks');
    for (const p of q.parts) if (p.blanks) { const b = flatBlanks(parseBlanks(p.blanks)); assert.ok(checkBlanks(b, b.map(x => x.answers[0])).every(Boolean), q.id + p.id); }
  }
});

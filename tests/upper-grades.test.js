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

test('all text-only written questions have an auto-checked solution space; the rest keep the original image and a workspace', () => {
  let auto = 0, card = 0;
  for (const c of Object.keys(CLASSES)) for (const q of load(c).questions.filter(q => q.type === 'frq')) {
    if (q.figure_in_image) { card++; assert(q.parts.length && q.diagram_asset_ids.length); continue; }
    assert(q.parts.some(p => p.blanks), `${c} ${q.id} has no auto-checked blanks`); auto++;
  }
  assert.equal(auto, 129 - card);
  assert.equal(card, 69 - 0);
});

test('imported question totals match the supplied package (753 eligible of 760)', () => {
  const total = Object.keys(CLASSES).reduce((n, c) => n + load(c).questions.length, 0);
  assert.equal(total, 753);
});

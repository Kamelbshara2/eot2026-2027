import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

// Whole-platform completeness checks (teacher request 2026-11-11); scripts/audit-all-questions.py has the full audit.
const load = c => JSON.parse(fs.readFileSync(new URL(`../public/data/study/${c}.json`, import.meta.url)));
const norm = s => String(s ?? '').replace(/\s|\\[,;!: ]|\\left|\\right/g, '').toLowerCase();
for (const c of ['9G3', '9A', '10G3', '10A1', '11G', '11A', '12G', '12A']) {
  test(`${c}: every question is complete (key, options, parts, outcome, figures)`, () => {
    const b = load(c), ids = new Set(b.questions.map(q => q.id)), listed = b.learning_outcomes.flatMap(l => l.question_ids);
    assert.deepEqual([...new Set(listed)].sort(), [...ids].sort(), 'outcome lists match the questions');
    assert.equal(listed.length, new Set(listed).size, 'no question listed twice');
    for (const q of b.questions) {
      assert.ok((q.instruction || '').trim().length >= 8, q.id + ' instruction');
      for (const a of q.diagram_asset_ids || []) assert.ok(b.assets[a] && fs.existsSync(new URL(`../public/${b.assets[a].src}`, import.meta.url)), `${q.id} figure ${a}`);
      if (q.type === 'mcq') {
        const o = q.options || [], key = q.answer?.correct_option_id;
        assert.ok(o.length >= 2 && o.length <= 4, q.id + ' option count');
        assert.equal(new Set(o.map(x => x.id)).size, o.length, q.id + ' option ids');
        assert.ok(o.some(x => x.id === key), `${q.id} key ${key} is an option`);
        for (const x of o) assert.ok(String(x.text || '').trim() || x.math_latex || x.image, `${q.id} option ${x.id} empty`);
        if (!q.embedded_options) assert.equal(new Set(o.map(x => norm(x.math_latex || x.text) + (x.image || ''))).size, o.length, q.id + ' duplicate options');
        assert.ok(q.answer.explanation || q.answer.steps, q.id + ' explanation');
      } else {
        assert.ok(q.parts?.length, q.id + ' parts');
        for (const p of q.parts) {
          assert.ok((p.prompt || '').trim(), `${q.id}${p.id} prompt`);
          assert.ok(p.answer?.model_answer_and_marking || p.answer?.math_latex || p.answer?.steps, `${q.id}${p.id} model answer`);
        }
      }
    }
  });
}

test('every question on all eight classes has worked steps (MCQ answer or every written part), each step with text and a why', () => {
  for (const c of ['9G3', '9A', '10G3', '10A1', '11G', '11A', '12G', '12A']) for (const q of load(c).questions) {
    const lists = q.type === 'mcq' ? [q.answer.steps] : q.parts.map(p => p.answer.steps);
    for (const st of lists) {
      assert.ok(st && st.length >= 1, `${c} ${q.id} has no steps`);
      for (const s of st) { assert.ok((s.text || '').trim(), `${q.id} step text`); assert.ok(s.why, `${q.id} step why`); assert.ok(!String(s.latex || '').includes('\\boxed{!'), `${q.id} leaked exact marker`); }
    }
  }
});

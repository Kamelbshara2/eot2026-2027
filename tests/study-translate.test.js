import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {translate, translationKey} from '../lib/study-translate.js';

const table = JSON.parse(fs.readFileSync(new URL('../public/data/study/translations-ar.json', import.meta.url)));
const gap = JSON.parse(fs.readFileSync(new URL('../content-imports/coverage-gap.json', import.meta.url)));

test('numbers are carried into the Arabic translation in order', () => {
  assert.equal(translate(table, 'instruction', 'Evaluate if g=2, r=3, and t=11.'), 'أوجد قيمة التعبير إذا كانت g=2 و r=3 و t=11.');
  assert.equal(translate(table, 'instruction', 'Solve for x. Assume a≠0. Which expression is correct?').includes('a≠0'), true);
  assert.equal(translate(table, 'option', 'Arithmetic: every difference is −3.'), 'حسابية: كل فرق يساوي −3.');
  assert.equal(translate(table, 'option', 'No such option'), '');
  assert.equal(translationKey('Find the 7th term.'), 'Find the #th term.');
});

for (const c of ['9G3', '10G3', '10A1']) {
  test(`${c}: every question instruction and written-part prompt has an Arabic translation`, () => {
    const bank = JSON.parse(fs.readFileSync(new URL(`../public/data/study/${c}.json`, import.meta.url)));
    for (const q of bank.questions) {
      assert.ok(translate(table, 'instruction', q.instruction), q.id + ' instruction');
      for (const p of q.parts || []) assert.ok(translate(table, 'part', p.prompt), q.id + ' part ' + p.id);
      const ar = translate(table, 'instruction', q.instruction);
      assert.equal((ar.match(/#/g) || []).length, 0, q.id + ' unfilled number placeholder');
    }
  });
}

test('coverage gap report is consistent with the study data (no item counted both present and missing)', () => {
  for (const [c, los] of Object.entries(gap)) for (const [lo, v] of Object.entries(los)) {
    assert.equal(v.in_site_data + v.missing.length, v.structure_items, `${c} ${lo}`);
  }
});

test('bidi never splits an HTML entity (a&lt;0 and “quoted” text stay intact)', async () => {
  const {bidi} = await import('../lib/study-translate.js');
  const out = bidi('فتحة لأعلى a&lt;0 و &quot;abc&quot;');
  assert(out.includes('&lt;') && out.includes('&quot;'));
  assert(!/<bdi[^>]*>[^<]*(?:lt|quot|amp)<\/bdi>/.test(out.replace('<bdi dir="ltr">a&lt;0</bdi>', '')));
});

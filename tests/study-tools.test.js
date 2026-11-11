import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {checkTable, checkPlot, pieceEnd, pointValid, num, snap} from '../lib/study-plot.js';
import {solutionMode} from '../lib/study-window.js';
import {createFocusGuard} from '../lib/study-mock.js';
import {createTermMock, validTermMock, gradeTermMock} from '../lib/term-mock-core.js';
import {graphPaper, printableQuestion} from '../lib/study-print.js';
import {examBankRoute} from '../lib/exam-bank-ui.js';

const load = c => JSON.parse(fs.readFileSync(new URL(`../public/data/study/${c}.json`, import.meta.url)));
const support = JSON.parse(fs.readFileSync(new URL('../public/data/study/calculator-support.json', import.meta.url)));

test('plot: table accepts any correct x chosen by the student and rejects wrong y', () => {
  const spec = {kind: 'line', line: {m: -1, b: 10}, min_points: 3, bounds: [-12, 12, -12, 12]};
  assert.ok(checkTable(spec, [{x: '0', y: '10'}, {x: '4', y: '6'}, {x: '-2', y: '12'}]).ok);
  assert.ok(checkTable(spec, [{x: '1/2', y: '9.5'}, {x: '2', y: '8'}, {x: '3', y: '7'}]).ok);
  assert.ok(!checkTable(spec, [{x: '0', y: '10'}, {x: '4', y: '5'}, {x: '8', y: '2'}]).ok);
  assert.ok(!checkTable(spec, [{x: '0', y: '10'}, {x: '0', y: '10'}, {x: '8', y: '2'}]).ok, 'repeated x does not count as three points');
  assert.ok(!checkTable(spec, [{x: '0', y: '10'}]).ok);
  assert.equal(num('−3/2'), -1.5); assert.equal(num('abc'), null); assert.equal(snap(1.26), 1.5);
});

test('plot: points on the plane must match the table and the equation', () => {
  const spec = {kind: 'line', line: {m: 0.5, b: 1}, min_points: 3, bounds: [-12, 12, -12, 12]};
  const rows = [{x: '-2', y: '0'}, {x: '0', y: '1'}, {x: '2', y: '2'}];
  assert.ok(checkPlot(spec, rows, [{x: -2, y: 0}, {x: 0, y: 1}, {x: 2, y: 2}]).ok);
  assert.ok(!checkPlot(spec, rows, [{x: -2, y: 0}, {x: 0, y: 1}]).ok, 'a table point is missing on the plane');
  assert.ok(!checkPlot(spec, rows, [{x: -2, y: 0}, {x: 0, y: 1}, {x: 2, y: 3}]).ok, 'off-line point');
});

test('plot: piecewise needs both endpoints with the right open/closed style and an interior point on each piece', () => {
  const spec = {kind: 'piecewise', bounds: [-6, 10, -6, 8], pieces: [{m: 0.5, b: -1, x0: 3, side: 'right', closed: false}, {m: -2, b: 3, x0: 3, side: 'left', closed: true}]};
  assert.deepEqual(pieceEnd(spec.pieces[0]), {x: 3, y: 0.5, open: true});
  const good = [{x: 3, y: 0.5, open: true}, {x: 3, y: -3, open: false}, {x: 5, y: 1.5}, {x: 1, y: 1}];
  assert.ok(checkPlot(spec, [], good).ok);
  assert.ok(!checkPlot(spec, [], good.map(p => ({...p, open: false}))).ok, 'open endpoint drawn closed');
  assert.ok(!checkPlot(spec, [], good.slice(0, 3)).ok, 'no interior point on the left piece');
  assert.ok(!pointValid(spec, {x: 5, y: 2}));
});

for (const c of ['9G3']) {
  test(`${c}: stored plot specs agree with the authored blanks and the reference answers`, () => {
    const bank = load(c);
    for (const q of bank.questions.filter(q => q.parts?.some(p => p.plot))) {
      const plot = q.parts.find(p => p.plot).plot;
      assert.ok(plot.bounds[0] < plot.bounds[1] && plot.bounds[2] < plot.bounds[3]);
      if (plot.kind === 'line') {
        assert.ok(checkTable(plot, plot.xs.map(x => ({y: String(plot.line.m * x + plot.line.b)}))).ok);
      } else {
        for (const pc of plot.pieces) { const e = pieceEnd(pc); assert.ok(e.x >= plot.bounds[0] && e.x <= plot.bounds[1] && e.y >= plot.bounds[2] && e.y <= plot.bounds[3], q.id + ' endpoint inside plane'); }
        const model = q.parts[0].blanks.lines.join(' ');
        for (const pc of plot.pieces) assert.ok(model.includes(String(pc.m === 1 / 3 ? '1/3' : pc.m)) || pc.m === 1 / 3 || model.includes(String(+pc.m.toFixed(3))), q.id + ' slope blank matches plot');
      }
    }
  });
}

test('solution mode labels: manual, calculator and hybrid come from the calculator role', () => {
  const modes = {};
  for (const [c, v] of Object.entries(support.classes)) for (const q of Object.values(v.questions)) modes[q.role] = solutionMode({calculatorSupport: q}).key;
  assert.equal(modes.reasoning, 'manual'); assert.equal(modes.evaluate, 'calculator'); assert.equal(modes.check, 'hybrid'); assert.equal(modes.table, 'hybrid');
  assert.equal(solutionMode({}).key, 'manual');
});

test('focus guard counts each departure once and accumulates away time', () => {
  let t = 1000; const g = createFocusGuard(() => t);
  g.leave(); g.leave(); t += 4000; g.back(); g.back(); g.leave(); t += 1000; g.back();
  assert.deepEqual(g.state, {leaves: 2, awayMs: 5000}); assert.equal(g.away(), false);
});

for (const c of ['9G3', '10G3', '10A1']) {
  test(`${c}: mock exam = 20 MCQs, one per outcome, 60 minutes, valid and gradable`, () => {
    const bank = load(c); let n = 0;
    for (let i = 0; i < 25; i++) {
      const s = createTermMock(bank, 1000 + i);
      assert.equal(s.ids.length, 20); assert.equal(s.deadline - s.startedAt, 3600000); assert.ok(validTermMock(s, bank));
      const qs = s.ids.map(id => bank.questions.find(q => q.id === id));
      assert.equal(new Set(qs.map(q => q.learning_outcome_id)).size, 20); assert.ok(qs.every(q => q.type === 'mcq'));
      for (const q of qs) s.answers[q.id] = q.answer.correct_option_id;
      n = gradeTermMock(s, bank);
    }
    assert.equal(n, 20);
  });
}

test('print sheet covers every written question with working space, graph paper and blank tables', () => {
  const bank = load('9G3'); const frqs = bank.questions.filter(q => q.type === 'frq');
  const html = frqs.map(q => printableQuestion(bank, q)).join('');
  assert.equal((html.match(/class="print-q"/g) || []).length, frqs.length);
  assert.ok((html.match(/print-lines/g) || []).length >= frqs.reduce((n, q) => n + q.parts.length, 0));
  assert.equal((html.match(/print-graph/g) || []).length, 11); assert.equal((html.match(/print-table/g) || []).length, 5);
  assert.ok(!html.includes('model_answer') && !/Substitution \(3\)/.test(html), 'no answer key on the student sheet');
  assert.ok(graphPaper([-5, 5, -5, 5]).includes('<svg'));
  const a = load('9A'), nl = a.questions.filter(q => q.parts?.some(p => p.numberline));
  assert.equal(nl.length, 8); assert.equal((nl.map(q => printableQuestion(a, q)).join('').match(/print-numberline/g) || []).length, 8);
});

test('exam bank routes include mock and print', () => {
  assert.equal(examBankRoute('#/classrooms/9G3/banks/term1/mock').mock, true);
  assert.equal(examBankRoute('#/classrooms/10A1/banks/term1/print').print, true);
  assert.equal(examBankRoute('#/classrooms/10G3/banks/term1/outcomes/LO05').outcomeId, 'LO05');
});

test('plot: x values given by the question — student supplies y; all given points must be plotted', () => {
  const spec = {kind: 'line', xs: [0, 5, 10], line: {m: -1, b: 10}, min_points: 3, bounds: [-12, 12, -12, 12]};
  assert.ok(checkTable(spec, [{y: '10'}, {y: '5'}, {y: '0'}]).ok);
  assert.ok(!checkTable(spec, [{y: '10'}, {y: '5'}, {y: '1'}]).ok);
  assert.ok(!checkTable(spec, [{y: '10'}, {y: ''}, {y: '0'}]).ok);
  const pts = [{x: 0, y: 10}, {x: 5, y: 5}, {x: 10, y: 0}];
  assert.ok(checkPlot(spec, [{y: '10'}, {y: '5'}, {y: '0'}], pts).ok);
  assert.ok(!checkPlot(spec, [{y: '10'}, {y: '5'}, {y: '0'}], pts.slice(0, 2)).ok, 'a given point is not plotted');
  const bank = JSON.parse(fs.readFileSync(new URL('../public/data/study/9G3.json', import.meta.url)));
  for (const q of bank.questions.filter(q => q.parts?.[0]?.plot?.kind === 'line')) {
    const p = q.parts[0].plot; assert.equal(p.xs.length, 3, q.id);
    assert.ok(p.xs.every(x => Number.isInteger(p.line.m * x + p.line.b)), q.id + ': y values should be exact integers for the given x');
  }
});

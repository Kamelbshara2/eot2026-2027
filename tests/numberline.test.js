import test from 'node:test';
import assert from 'node:assert/strict';
import {checkNumberLine, answerEnds, intervalText} from '../lib/study-numberline.js';

const spec = {bounds: [2, 14], answer: [{a: 6, b: 11, ac: true, bc: false}]};   // 6 ≤ f < 11
const st = (points, shaded, empty = false) => ({points, shaded: new Set(shaded), empty});

test('number line: closed 6, open 11, middle piece shaded is correct', () => {
  assert.equal(checkNumberLine(spec, st([{x: 6, open: false}, {x: 11, open: true}], [1])).ok, true);
  assert.equal(intervalText(spec.answer), '[6, 11)');
});
test('number line: wrong endpoint type, wrong piece, extra point and ∅ are rejected', () => {
  assert.equal(checkNumberLine(spec, st([{x: 6, open: true}, {x: 11, open: true}], [1])).ok, false);
  assert.equal(checkNumberLine(spec, st([{x: 6, open: false}, {x: 11, open: true}], [0])).ok, false);
  assert.equal(checkNumberLine(spec, st([{x: 6, open: false}, {x: 11, open: true}], [1, 2])).ok, false);
  assert.equal(checkNumberLine(spec, st([{x: 6, open: false}, {x: 9, open: false}, {x: 11, open: true}], [1, 2])).ok, false);
  assert.equal(checkNumberLine(spec, st([], [], true)).ok, false);
});
test('number line: empty intersection needs ∅ and no shading; rays are the outer pieces', () => {
  const none = {bounds: [-8, 8], answer: []};
  assert.equal(checkNumberLine(none, st([], [], true)).ok, true);
  assert.equal(checkNumberLine(none, st([{x: -4, open: false}, {x: 4, open: true}], [])).ok, false);
  const ray = {bounds: [-6, 6], answer: [{a: null, b: 0.5, ac: false, bc: true}]};
  assert.deepEqual(answerEnds(ray.answer), [{x: 0.5, closed: true}]);
  assert.equal(checkNumberLine(ray, st([{x: 0.5, open: false}], [0])).ok, true);
  assert.equal(checkNumberLine(ray, st([{x: 0.5, open: false}], [1])).ok, false);
});

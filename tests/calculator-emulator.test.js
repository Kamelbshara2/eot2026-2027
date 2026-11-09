import test from 'node:test';
import assert from 'node:assert/strict';
import {Calculator} from '../public/vendor/fx991ce/src/calc/calculator.js';
import {MODES} from '../public/vendor/fx991ce/src/calc/modes/index.js';

function run(sequence) {
 const calc = new Calculator({modes: MODES, storage: null});
 for (const key of sequence.split(' ')) calc.press(key);
 return calc;
}
test('calculator solves a quadratic, generates a table and solves a linear equation', () => {
 const quadratic = run('MENU NEG 2 2 1 EQ NEG 3 EQ 2 EQ EQ');
 assert.equal(quadratic.mode, 'eqn');
 assert.deepEqual(quadratic.top.items.slice(0, 2).map(item => item.value.d.toString()).sort(), ['1', '2']);
 const table = run('MENU 9 ALPHA RP SQR EQ EQ 0 EQ 2 EQ 1 EQ EQ');
 assert.equal(table.mode, 'table');
 assert.equal(table.top.spec.rowCount(), 3);
 assert.deepEqual([0,1,2].map(i => table.top.spec.get(i,1).d.toString()), ['0','1','4']);
 const linear = run('2 ALPHA RP ADD 3 ALPHA CALC 7 SHIFT CALC 0 EQ EQ');
 assert.equal(linear.top.constructor.name, 'SolveResult');
 assert.equal(linear.top.x.d.toString(), '2');
});

import test from 'node:test';
import assert from 'node:assert/strict';
import {isBlockedKey} from '../lib/content-shield.js';

test('screenshot, save and devtools shortcuts are blocked; normal typing is not', () => {
  assert.equal(isBlockedKey({key: 'PrintScreen'}), true);
  assert.equal(isBlockedKey({key: 'S', metaKey: true, shiftKey: true}), true);
  assert.equal(isBlockedKey({key: '4', metaKey: true, shiftKey: true}), true);
  assert.equal(isBlockedKey({key: 'u', ctrlKey: true}), true);
  assert.equal(isBlockedKey({key: 'F12'}), true);
  assert.equal(isBlockedKey({key: 'a'}), false);
  assert.equal(isBlockedKey({key: 'c', ctrlKey: true}), false);
});

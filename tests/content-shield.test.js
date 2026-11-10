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

test('Ctrl+Shift+I / J / C are blocked regardless of key case or layout', () => {
  assert.equal(isBlockedKey({key: 'I', code: 'KeyI', ctrlKey: true, shiftKey: true}), true);
  assert.equal(isBlockedKey({key: 'ا', code: 'KeyI', ctrlKey: true, shiftKey: true}), true);
  assert.equal(isBlockedKey({key: 'J', code: 'KeyJ', ctrlKey: true, shiftKey: true}), true);
  assert.equal(isBlockedKey({key: 'c', code: 'KeyI', ctrlKey: true, altKey: true, metaKey: true}), true);
});

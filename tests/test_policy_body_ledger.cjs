const test = require('node:test');
const assert = require('node:assert/strict');
const {spawnSync} = require('node:child_process');
const path = require('node:path');
const os = require('node:os');
const script = path.resolve(__dirname, '../scripts/ppg_policy_body_ledger.mjs');

test('a valid list UUID cannot bypass either private-path guard', () => {
  const local = path.join(os.tmpdir(), '.local');
  const uuid = '11111111-2222-3333-4444-555555555555';
  for (const args of [
    [path.join(os.tmpdir(), 'outside.mjs'), path.join(local, 'receipt.json'), uuid],
    [path.join(local, 'adapter.mjs'), path.join(os.tmpdir(), 'outside.json'), uuid],
    [path.join(local, 'adapter.mjs'), path.join(local, 'receipt.json'), 'invalid-list-id'],
  ]) {
    const result = spawnSync(process.execPath, [script, ...args], {encoding: 'utf8'});
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Supply private adapter\/new receipt paths/);
    assert.doesNotMatch(result.stderr, /ERR_MODULE_NOT_FOUND/);
  }
});

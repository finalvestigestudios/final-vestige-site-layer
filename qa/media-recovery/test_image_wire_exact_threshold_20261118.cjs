'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { meetsReduction76, displayReductionPercent } = require('./image_wire_exact_threshold_20261118.cjs');
test('exact 76 percent qualifies', () => assert.equal(meetsReduction76(35500, 8520), true));
test('one byte above threshold is rejected despite rounded 76.00 display', () => {
  assert.equal(displayReductionPercent(35500, 8521), 76);
  assert.equal(meetsReduction76(35500, 8521), false);
});
test('at 66-post scale rounding cannot admit shortfall', () => {
  assert.equal(displayReductionPercent(36100, 8665), 76);
  assert.equal(meetsReduction76(36100, 8665), false);
});
test('reduced transfer greater than threshold qualifies', () => assert.equal(meetsReduction76(35500, 8000), true));
test('improvement below 76 percent is rejected', () => assert.equal(meetsReduction76(35500, 9000), false));
test('unmeasured zero-byte after cannot pass', () => assert.equal(meetsReduction76(35500, 0), false));
test('unmeasured baseline cannot pass', () => assert.equal(meetsReduction76(0, 1), false));
test('negative values cannot pass', () => assert.equal(meetsReduction76(-35500, -8520), false));
test('fractional values cannot pass', () => assert.equal(meetsReduction76(35500.5, 8520), false));
test('strings cannot pass', () => assert.equal(meetsReduction76('35500', '8520'), false));
test('unsafe >2^53 byte totals cannot pass', () => assert.equal(meetsReduction76(Number.MAX_SAFE_INTEGER+1, 1), false));
test('BigInt comparison stays accurate near safe integer boundary', () => {
  const before = Number.MAX_SAFE_INTEGER;
  const accepted = Number((BigInt(before) * 24n) / 100n);
  assert.equal(meetsReduction76(before, accepted), true);
  assert.equal(meetsReduction76(before, accepted + 1), false);
});
test('display summary is not gate evidence', () => assert.equal(displayReductionPercent(0, 1), null));

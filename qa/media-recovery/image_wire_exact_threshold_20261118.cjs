'use strict';
// Bytes come from measured CDP transfers, never original CMS media sizes.
// Avoid Math.round(75.997, 2) == 76 false positives in publication gates.
const safePositive = n => Number.isSafeInteger(n) && n > 0;
function meetsReduction76(beforeBytes, afterBytes) {
  return safePositive(beforeBytes) && safePositive(afterBytes) &&
    BigInt(afterBytes) * 100n <= BigInt(beforeBytes) * 24n;
}
function displayReductionPercent(beforeBytes, afterBytes) {
  if (!safePositive(beforeBytes) || !safePositive(afterBytes)) return null;
  return Math.round((1 - afterBytes / beforeBytes) * 10000) / 100;
}
module.exports = { meetsReduction76, displayReductionPercent };

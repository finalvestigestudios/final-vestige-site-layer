'use strict';

// Offline-only review of the Focus landing page's inline gift-state logic.
// This is an observational test, NOT a Jetpack delivery test or a login gate.
const fs = require('node:fs');
const vm = require('node:vm');

const SCRIPT_RE = /<script\b[^>]*>([\s\S]*?)<\/script\s*>/gi;
const GIFT_LOOKUP_RE = /getElementById\s*\(\s*['"]fvf-gift['"]\s*\)/;

function extractGiftScript(html) {
  const matches = [...String(html).matchAll(SCRIPT_RE)]
    .map(match => match[1])
    .filter(script => GIFT_LOOKUP_RE.test(script));
  if (matches.length !== 1) {
    throw new Error(`Expected exactly one Focus gift-state inline script; found ${matches.length}`);
  }
  const script = matches[0];
  if (script.length > 3000 || /\b(?:require|import|fetch|XMLHttpRequest|WebSocket|eval|Function|constructor)\b/.test(script)) {
    throw new Error('Unexpected script content: review manually; do not execute');
  }
  return script;
}

function simulateGift(script, search, subscriberClass = '') {
  const gift = { hidden: true };
  const subscription = { className: subscriberClass };
  const document = {
    getElementById: id => id === 'fvf-gift' ? gift : null,
    querySelector: selector => selector === '.wp-block-jetpack-subscriptions__container' ? subscription : null,
  };
  const window = { location: { search }, MutationObserver: null };
  // Only a short, locally supplied/sanitized WordPress export is accepted.
  // Node's vm timeout and restricted globals reduce accidents; vm is NOT a security sandbox.
  vm.runInNewContext(script, { document, window, URLSearchParams }, {
    timeout: 150,
    contextCodeGeneration: { strings: false, wasm: false },
  });
  return !gift.hidden;
}

function audit(html) {
  const script = extractGiftScript(html);
  const scenarios = {
    clean: simulateGift(script, ''),
    arbitrary: simulateGift(script, '?subscribe=qa_not_a_real_jetpack_state'),
    falseLike: simulateGift(script, '?subscribe=0'),
    explicitError: simulateGift(script, '?subscribe=error'),
    apparentSuccess: simulateGift(script, '?subscribe=success'),
    existingSubscriber: simulateGift(script, '', 'wp-block-jetpack-subscriptions__container is-subscriber'),
  };
  return {
    status: scenarios.arbitrary || scenarios.falseLike
      ? 'REVIEW_ARBITRARY_SUBSCRIBE_QUERY_REVEALS_GIFT'
      : 'NO_ARBITRARY_QUERY_REVEAL_IN_TESTED_CASES',
    scenarios,
    qualification: 'Saved-inline-script simulation only; neither live-browser Jetpack behavior nor email delivery was tested.',
  };
}

if (require.main === module) {
  const path = process.argv[2];
  if (!path || process.argv.length !== 3) {
    console.error('Usage: node qa/focus/subscribe_state_guard.cjs /path/to/sanitized-focus-html-export');
    process.exitCode = 2;
  } else {
    try {
      const result = audit(fs.readFileSync(path, 'utf8'));
      console.log(JSON.stringify(result, null, 2));
      process.exitCode = result.status.startsWith('REVIEW_') ? 1 : 0;
    } catch (error) {
      console.error(`INCONCLUSIVE: ${error.message}`);
      process.exitCode = 2;
    }
  }
}

module.exports = { extractGiftScript, simulateGift, audit };

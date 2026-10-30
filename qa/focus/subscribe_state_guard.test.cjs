'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const { audit, extractGiftScript, simulateGift } = require('./subscribe_state_guard.cjs');

// A minimal fixture matching the actual inline gift-state pattern observed in
// WordPress /focus/ on 2026-10-30. No real subscribers or credentials included.
const observedScript = `(function(){var g=document.getElementById('fvf-gift');if(!g){return;}
var bad=['invalid_email','error','blocked_email','opted_out','blocked'];
function show(){g.hidden=false;}
var q=null;try{q=new URLSearchParams(window.location.search).get('subscribe');}catch(e){}
if(q&&bad.indexOf(q)<0){show();}
var c=document.querySelector('.wp-block-jetpack-subscriptions__container');
function check(){if(c&&/\\bis-subscriber\\b/.test(c.className)){show();}}
check();if(c&&window.MutationObserver){new MutationObserver(check).observe(c,{attributes:true,attributeFilter:['class']});}})();`;
const wrap = js => `<!-- wp:html --><div id="fvf-gift" hidden></div><script>${js}</script><!-- /wp:html -->`;

test('extracts only the marked gift-state script', () => {
  assert.equal(extractGiftScript(wrap(observedScript)), observedScript);
});
test('initial anonymous visit keeps gift hidden', () => {
  assert.equal(simulateGift(observedScript, ''), false);
});
test('legitimate-looking success query reveals gift', () => {
  assert.equal(simulateGift(observedScript, '?subscribe=success'), true);
});
test('arbitrary unrecognized query also reveals gift', () => {
  assert.equal(simulateGift(observedScript, '?subscribe=qa_not_a_real_jetpack_state'), true);
});
test('numeric false-like query also reveals gift', () => {
  assert.equal(simulateGift(observedScript, '?subscribe=0'), true);
});
test('known explicit errors do not reveal gift', () => {
  for (const val of ['invalid_email', 'error', 'blocked_email', 'opted_out', 'blocked']) {
    assert.equal(simulateGift(observedScript, `?subscribe=${val}`), false);
  }
});
test('is-subscriber DOM class can reveal gift independently', () => {
  assert.equal(simulateGift(observedScript, '', 'wp-block-jetpack-subscriptions__container is-subscriber'), true);
});
test('audit flags unrecognized query behavior, not a confirmed signup', () => {
  const result = audit(wrap(observedScript));
  assert.equal(result.status, 'REVIEW_ARBITRARY_SUBSCRIBE_QUERY_REVEALS_GIFT');
  assert.equal(result.scenarios.clean, false);
  assert.equal(result.scenarios.arbitrary, true);
});
test('conservative failure when no focus script exists', () => {
  assert.throws(() => extractGiftScript('<script>console.log("unrelated")</script>'), /exactly one/);
});
test('conservative failure when multiple focus scripts exist', () => {
  assert.throws(() => extractGiftScript(wrap(observedScript) + wrap(observedScript)), /found 2/);
});
test('refuses oversized and privileged code instead of executing', () => {
  assert.throws(() => extractGiftScript(wrap(observedScript + ' '.repeat(3001))), /Unexpected script/);
  assert.throws(() => extractGiftScript(wrap(observedScript + ' require("fs")')), /Unexpected script/);
});
test('a strict success-only fixture avoids arbitrary-query finding', () => {
  const strict = observedScript.replace('if(q&&bad.indexOf(q)<0){show();}', "if(q==='success'){show();}");
  const result = audit(wrap(strict));
  assert.equal(result.scenarios.arbitrary, false);
  assert.equal(result.scenarios.apparentSuccess, true);
  assert.equal(result.status, 'NO_ARBITRARY_QUERY_REVEAL_IN_TESTED_CASES');
});

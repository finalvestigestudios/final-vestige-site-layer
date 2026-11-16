'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const {PUBLISHED_SCRIPT,reproduce,evidenceClass} = require('./focus_gift_signal.cjs');

test('no query and no subscriber class keeps gift hidden', () => {
  assert.equal(reproduce().giftVisible,false);
});
for (const value of ['success','confirmed','arbitrary','0','false','paid','definitely_not_subscribed']) {
  test('untrusted subscribe='+value+' displays the gift', () => {
    assert.equal(reproduce({search:'?subscribe='+value}).giftVisible,true);
  });
}
for (const value of ['invalid_email','error','blocked_email','opted_out','blocked']) {
  test('explicit failure subscribe='+value+' remains hidden', () => {
    assert.equal(reproduce({search:'?subscribe='+value}).giftVisible,false);
  });
}
test('uppercase ERROR is not one of the five exact failure strings', () => {
  assert.equal(reproduce({search:'?subscribe=ERROR'}).giftVisible,true);
});
test('first duplicate query parameter wins', () => {
  assert.equal(reproduce({search:'?subscribe=blocked&subscribe=success'}).giftVisible,false);
});
test('is-subscriber CSS class reveals gift without provider proof', () => {
  assert.equal(reproduce({subscriberClass:'is-subscriber'}).giftVisible,true);
});
test('MutationObserver can reveal gift upon later CSS class change', () => {
  const res=reproduce();
  assert.equal(res.mutationCallbackInstalled,true);
  assert.equal(res.changeContainerClass('foo is-subscriber bar'),true);
});
test('hyphen-delimited class text unexpectedly matches word boundaries', () => {
  assert.equal(reproduce({subscriberClass:'maybe-is-subscriber-later'}).giftVisible,true);
});
test('unrelated class without matching substring remains hidden', () => {
  assert.equal(reproduce({subscriberClass:'unrelated-other'}).giftVisible,false);
});
test('absence of gift element does not crash or reveal it', () => {
  assert.equal(reproduce({search:'?subscribe=confirmed',giftExists:false}).giftVisible,false);
});
test('absence of container does not crash and query still works', () => {
  assert.equal(reproduce({search:'?subscribe=accepted',hasContainer:false}).giftVisible,true);
});
test('the exact published code tests a query string and class rather than authenticated provider state', () => {
  assert.ok(PUBLISHED_SCRIPT.includes("get('subscribe')"));
  assert.ok(PUBLISHED_SCRIPT.includes('is-subscriber'));
  assert.ok(!PUBLISHED_SCRIPT.includes('confirmed_at'));
});
for(const field of ['urlFlag','giftVisible','pdfClick']) {
  test(field+' cannot be counted as confirmed_signup',()=>{
    assert.equal(evidenceClass({[field]:true}),'CLIENT_ONLY_NOT_CONFIRMED_SIGNUP');
  });
}
test('even a claimed provider record requires private authentication',()=>{
  assert.equal(evidenceClass({providerRecord:true}),'PROVIDER_RECORD_REQUIRES_PRIVATE_AUTHENTICATION');
});
test('no evidence cannot generate a subscriber event',()=>{
  assert.equal(evidenceClass({}),'NO_SUBSCRIPTION_EVIDENCE');
});

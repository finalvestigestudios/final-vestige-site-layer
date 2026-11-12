'use strict';
/**
 * FV Mind R318 — Node 18+ source-level release guard.
 * Run: node mind/r318/verify_r318.cjs
 * It is NOT a browser, WordPress sanitizer, marketing authorization or payment test.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const base = __dirname;
const read = n => fs.readFileSync(path.join(base,n), 'utf8');
const names = {
  article:'THE-VOICE-YOUR-EYES-REWROTE-UNPUBLISHED.md',
  A:'ZEN12-A-INDEPENDENT-TEXT-BUYER-GUIDE-REVIEW.html',
  B:'ZEN12-B-OPTIONAL-42S-FILM-BUYER-GUIDE-REVIEW.html',
  hub:'MIND-FOUR-STREAM-WP-HTML-REVIEW-ONLY.html',
  vtt:'ORIGINAL-42S-CAPTIONS.vtt',
  matrix:'SOURCE-PRODUCT-CLAIM-AND-AUTHORIZATION-MATRIX.json',
  dossier:'ONE-OFFER-CONVERSION-FUNNEL-AND-RELEASE-ACCEPTANCE.md'
};
const sources = Object.fromEntries(Object.entries(names).map(([k,n]) => [k,read(n)]));
function commercialGuard(html) {
  assert.match(html,/<!doctype html>/i,'doctype required');
  assert.match(html,/<html lang="en">/,'lang must be declared');
  assert.match(html,/<meta name="viewport"/,'responsive viewport required');
  assert.match(html,/<meta name="robots" content="noindex,nofollow">/,'review only not indexed');
  assert.doesNotMatch(html,/<script\b|<iframe\b|<form\b|<video\b|autoplay\b|<input\b/i,'no active code/video/forms');
  assert.doesNotMatch(html,/href\s*=\s*["'](?:https?:)?\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i,'no merchant CTA');
  assert.doesNotMatch(html,/data-(?:pixel|track)|onclick\s*=|onerror\s*=/i,'no event/pixel injection');
  assert.match(html,/<button[^>]*\bdisabled\b[^>]*>/i,'disabled button required');
  assert.match(html,/aria-disabled="true"/,'disabled ARIA state required');
  assert.match(html,/purchase link unavailable|merchant offer unavailable/i,'gated CTA visible');
  assert.match(html,/If you purchase through an earning link|If a future product recommendation contains an earning link/i,'plain prospective commission disclosure required');
  assert.match(html,/https:\/\/finalvestige\.com\/focus\//,'preserve exact single Focus route');
  assert.doesNotMatch(html,/guaranteed 100% improved|cures anxiety|proven to reprogram|limited spots available/i,'unsupported marketing language');
  return true;
}
function buyerCore(html) {
  const marker = '<div id="buyer-copy" role="main">';
  assert.ok(html.includes(marker),'buyer section exists');
  return html.slice(html.indexOf(marker),html.lastIndexOf('</main>'));
}
function main() {
  let n=0;const pass=(message,fn)=>{fn();n++;console.log('PASS',message)};
  pass('A source guard',()=>commercialGuard(sources.A));
  pass('B source guard',()=>commercialGuard(sources.B));
  pass('hub source guard',()=>commercialGuard(sources.hub));
  pass('A B core identical',()=>assert.equal(buyerCore(sources.A),buyerCore(sources.B)));
  pass('video B is optional static treatment',()=>{
    assert.match(sources.B,/Optional 42-second original explainer/);
    assert.match(sources.B,/<svg role="img"/);
    assert.match(sources.B,/<details>/);
    assert.doesNotMatch(sources.B,/<video\b/i);
  });
  pass('captions include exact 42-second end',()=>{
    assert.match(sources.vtt,/^WEBVTT/);
    assert.match(sources.vtt,/00:00:35.000 --> 00:00:42.000/);
    assert.equal((sources.vtt.match(/ --> /g)||[]).length,6);
  });
  pass('article source boundaries',()=>{
    assert.match(sources.article,/Original full text not represented as inspected|original full text not represented as inspected/i);
    assert.match(sources.article,/2018|Magnotti/);
    assert.match(sources.article,/Puységur/);
    assert.match(sources.article,/It is not evidence that someone can control thoughts|Neither is an alternative version of Zen12/i);
    assert.doesNotMatch(sources.article,/https?:\/\/affiliates\.inspire3\.com\/\?/, 'no invented URL');
  });
  pass('matrix authenticity and gates',()=>{
    const m=JSON.parse(sources.matrix);
    assert.equal(m.sources.length,20);
    assert.equal(m.claims.length,38);
    assert.equal(m.commercial_gates.length,18);
    assert.ok(m.commercial_gates.every(g=>g.status==='HARD_HOLD'));
    assert.ok(m.products.every(p=>p.referral_url===null));
    assert.equal(new Set(m.claims.map(c=>c.id)).size,m.claims.length);
    const ids=new Set(m.sources.map(s=>s.id));
    assert.ok(m.claims.every(c=>c.support.every(id=>ids.has(id))));
    assert.equal(m.measurement.status,'NOT_COMPUTABLE');
  });
  pass('no fake zero revenue outcome',()=>{
    assert.match(sources.dossier,/NOT COMPUTABLE|not computable/i);
    assert.match(sources.dossier,/affiliate_click/);
    assert.match(sources.dossier,/partner_reported_affiliate_conversion/);
    assert.match(sources.dossier,/do not install a second analytics script|Never install a second analytics script/i);
  });
  pass('solo free subscriber flow',()=>{[sources.A,sources.B,sources.hub].forEach(h=>assert.ok((h.match(/https:\/\/finalvestige\.com\/focus\//g)||[]).length>=1))});
  const attacks=[
    ['script','<script src="//bad.invalid"></script>'],
    ['iframe','<iframe src="https://bad.invalid"></iframe>'],
    ['form','<form action="/subscribe">test</form>'],
    ['video','<video src="/film.mp4"></video>'],
    ['autoplay','<video autoplay></video>'],
    ['email-input','<input type="email">'],
    ['zen12-link','<a href="https://zen12.com/getstarted">BUY</a>'],
    ['inspire3-link','<a href="https://inspire3.com/abc">BUY</a>'],
    ['hypnosis-link','<a href="https://hypnosislive.com/mental-skills/total-focus">BUY</a>'],
    ['brainwave-link','<a href="https://brainwaveshots.com/focus-shot">BUY</a>'],
    ['affiliate-link','<a href="https://affiliates.inspire3.com/?id=XXX">BUY</a>'],
    ['injected-analytics','<p data-track="affiliate">sale</p>'],
    ['onclick','<button onclick="location.href=\'/checkout\'">BUY</button>'],
    ['onerror','<img onerror="alert(1)" src="x">'],
    ['misleading-cure','<p>cures anxiety</p>'],
    ['fake-urgency','<p>limited spots available</p>'],
    ['claim-100','<p>guaranteed 100% improved</p>'],
    ['medical-claim','<p>proven to reprogram your brain</p>']
  ];
  let rejected=0;
  for(const [name,attack] of attacks) {
    assert.throws(()=>commercialGuard(sources.A+attack),undefined,name+' must be blocked');
    rejected++;
  }
  const removals=[
    ['remove-disclosure',s=>s.replace(/If you purchase through an earning link/,'Unclear link note')],
    ['remove-gated-CTA',s=>s.replace(/purchase link unavailable/ig,'buy now')],
    ['remove-disabled',s=>s.replace(/(<button class="disabled" )disabled /,'$1')],
    ['remove-aria-disabled',s=>s.replace('aria-disabled="true"','')],
    ['remove-Focus',s=>s.replace('https://finalvestige.com/focus/','')],
    ['remove-noindex',s=>s.replace('<meta name="robots" content="noindex,nofollow">','')],
    ['remove-lang',s=>s.replace('<html lang="en">','<html>')],
    ['remove-responsive',s=>s.replace('<meta name="viewport"','<meta name="notviewport"')]
  ];
  for(const [name,mutate] of removals) {
    assert.throws(()=>commercialGuard(mutate(sources.A)),undefined,name+' must be blocked');
    rejected++;
  }
  console.log('RESULT',n,'baseline assertions and',rejected,'negative controls passed');
  console.log('LIMIT: Source regex + JSON assertions are not real-browser/WordPress/payment tests.');
}
main();

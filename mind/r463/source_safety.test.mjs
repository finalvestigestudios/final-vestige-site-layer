import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const load = async file => readFile(new URL(file, import.meta.url), 'utf8');
const [a,b,hub,nav,matrixRaw,vtt,article,acceptance] = await Promise.all([
  'ZEN12_A_EVIDENCE_GUIDE.html','ZEN12_B_OPTIONAL_FILM_GUIDE.html',
  'MIND_HUB_WP_BLOCK_DRAFT.html','INTERNAL_LINK_NAVIGATION_PLAN.md',
  'CLAIM_SOURCE_PARTNER_RELEASE_MATRIX.json','ZEN12_42S_CAPTIONS.vtt',
  'THE_ROOM_OUTSIDE_THE_PHOTOGRAPH.md','CONVERSION_FIT_ATTRIBUTION_AB_ACCEPTANCE.md'
].map(load));
const m=JSON.parse(matrixRaw);
const shared=[a,b];
test('A and B have identical substantive reading content outside optional module',()=>{
  const withoutFilm=b.replace(/<section id="optional-film">[\s\S]*?<\/section>/,'');
  assert.equal(a,withoutFilm);
});
for (const [i,x] of shared.entries()) {
  test('variant '+i+' is noindex and WCAG language/viewport declared',()=>{
    assert.match(x,/lang="en"/);assert.match(x,/name="viewport"/);assert.match(x,/noindex,nofollow/);
  });
  test('variant '+i+' has no scripts/forms/embedded trackers',()=>{
    assert.doesNotMatch(x,/<script\b|<form\b|<iframe\b|<img\b[^>]*src="https?:/i);
    assert.doesNotMatch(x,/googletagmanager|analytics\.js|pixel\.gif|utm_source=/i);
  });
  test('variant '+i+' has a natively disabled commercial CTA',()=>{
    assert.match(x,/<button[^>]*type="button"[^>]*disabled[^>]*>/);
    assert.match(x,/Partner-approved offer not available/);
  });
  test('variant '+i+' has adjacent plain language prospective disclosure',()=>{
    const start=x.indexOf('<section class="offer"'), end=x.indexOf('</section>',start);
    const s=x.slice(start,end);
    assert.match(s,/may receive a commission at no extra cost/);
    assert.match(s,/<button[^>]*disabled/);
    assert.ok(s.indexOf('commission')<s.indexOf('<button'));
  });
  test('variant '+i+' contains no clickable seller/affiliate destination',()=>{
    assert.doesNotMatch(x,/<a\b[^>]*href="https?:\/\/(?:www\.)?(?:inspire3|zen12|hypnosislive|brainwaveshots|affiliates\.inspire3)\.com/i);
    assert.doesNotMatch(x,/hop\.clickbank|refersion\?/, 'No earning links');
  });
  test('variant '+i+' does not display price, payout or guarantee numbers',()=>{
    assert.doesNotMatch(x,/\$\s*\d|\b\d+\s*%\s*(?:commission|payout)|\bguaranteed results\b/i);
  });
  test('variant '+i+' retains free existing Focus route and not another subscriber stack',()=>{
    assert.match(x,/https:\/\/finalvestige\.com\/focus\//);assert.match(x,/Jetpack/);
  });
}
test('optional B video is really optional, transcript present, no false playable media',()=>{
  assert.match(b,/<details>/);assert.match(b,/<summary>/);assert.match(b,/<svg/);
  assert.match(b,/Complete narration text/);
  assert.doesNotMatch(b,/<video\b|<(?:video|audio)[^>]*\bautoplay\b/i);
});
test('timed WebVTT covers exactly 0–42 sec in contiguous nonoverlapping spans',()=>{
  const spans=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.\d{3} --> (\d\d):(\d\d):(\d\d)\.\d{3}/g)].map(x=>[+x[1]*3600 + +x[2]*60 + +x[3],+x[4]*3600 + +x[5]*60 + +x[6]]);
  assert.equal(spans.length,6); assert.equal(spans[0][0],0); assert.equal(spans.at(-1)[1],42);
  for(let i=1;i<spans.length;i++)assert.equal(spans[i-1][1],spans[i][0]);
});
test('merchant matrix all gates hold, no invented approved URL',()=>{
  assert.ok(m.gates.length>=30);assert.ok(m.gates.every(x=>x.status==='HOLD'));
  assert.equal(m.exact_sales_destination,'NOT AUTHENTICATED');
});
test('claims label efficacy unverified and historical analogy not product proof',()=>{
  for(const n of ['C06','C07','C08','C11','C14','C16','C21'])assert.match(m.claims.find(x=>x.id===n).decision,/BLOCK/);
  assert.match(article,/boundary/i);assert.match(article,/Puységur/);
});
test('hub has one h1 and all published editorial routes',()=>{
  assert.equal((hub.match(/<h1\b/g)||[]).length,1);
  for(const suffix of ['/focus/','/2026/11/02/change-blindness/','/2026/11/02/mesmerism/','/free-resources/puysegurs-animal-magnetism-files/'])assert.ok(hub.includes(suffix));
  assert.doesNotMatch(hub,/<form\b|<script\b/);
});
test('acceptance plan separates affiliate clicks and paid settlements',()=>{
  assert.match(acceptance,/affiliate_outbound/);assert.match(acceptance,/merchant_confirmed_paid_order/);
  assert.match(acceptance,/NOT COMPUTABLE/);
  assert.match(nav,/do not bulk rewrite/i);
});

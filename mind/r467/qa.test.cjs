// Mind R467 native Node release-hold regression tests.
// Run manually from repository root: node --test mind/r467/qa.test.cjs
// This suite is a guard, not proof of live browser, merchant approval, or sales.
'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const here=__dirname;
const read=name=>fs.readFileSync(path.join(here,name),'utf8');
const a=read('ZEN12_A_TEXT_ONLY.html'),b=read('ZEN12_B_OPTIONAL_FILM.html');
const hub=read('MIND_ARCHIVE_SOURCE_ONLY.html'),vtt=read('ZEN12_B_42S_CAPTIONS.vtt');
const report=read('THE_STATEMENT_YOU_SAW_FIVE_TIMES.md');
const matrix=JSON.parse(read('CLAIM_SOURCE_MERCHANT_MATRIX.json'));
const acceptance=read('OFFER_FUNNEL_EXPERIMENT_AND_REVENUE_ACCEPTANCE.md');
const htmls=[a,b,hub];
test('all HTML language, responsive viewport and unpublished noindex',()=>{
 for(const x of htmls){assert.match(x,/<!doctype html>/i);assert.match(x,/<html lang="en">/);assert.match(x,/name="viewport"/);assert.match(x,/noindex,nofollow/);}
});
test('no JavaScript, iframe, forms, autoplay, or offsite media',()=>{
 for(const x of htmls){assert.doesNotMatch(x,/<script|<iframe|<form|autoplay|<video|<audio|<img[^>]*src=["']https?:/i);}
});
test('A and B remain identical outside optional original media and title',()=>{
 const rem=x=>x.replace(/<section class="panel" aria-label="Optional original short-film concept">[\s\S]*?<\/section>/,'').replace(/<title>Zen12 independent buyer guide [^<]+<\/title>/,'');
 assert.equal(rem(a),rem(b));
});
test('both are native-disabled with no live seller href',()=>{
 for(const x of [a,b]){assert.match(x,/<button type="button" disabled aria-disabled="true">/);assert.doesNotMatch(x,/href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\./i);}
});
test('prominent adjacent prospective FTC disclosure',()=>{
 for(const x of [a,b]){const i=x.indexOf('Affiliate disclosure for any future activated recommendation:');const j=x.indexOf('<button type="button" disabled');assert.ok(i>0 && j>i && j-i<550);}
});
test('no unsubstantiated effectiveness stated affirmatively',()=>{
 for(const x of [a,b]){assert.match(x,/not product trials of Zen12/);assert.match(x,/seller's assertions|seller promise|unsubstantiated/i);assert.match(x,/twelve minutes equals an hour of meditation/);}
});
test('exact promotional vs standard checkout separation',()=>{
 for(const x of [a,b]){assert.match(x,/zen12.com\/about/);assert.match(x,/zen12.com\/secret/);assert.match(x,/separate seller presentations/);}
});
test('no email list duplication',()=>{for(const x of htmls){assert.doesNotMatch(x,/<input|type=["']email|<form/i);assert.match(x,/Fieldbook/);}});
test('optional film is explicitly unencoded and unplayable',()=>{assert.match(b,/not encoded or playable/);assert.doesNotMatch(a,/poster-title/);assert.match(b,/poster-title/);});
test('B includes accessible poster text and complete transcript',()=>{assert.match(b,/aria-labelledby="poster-title poster-desc"/);assert.match(b,/<details>/);assert.match(b,/00:35–00:42/);});
test('VTT has six contiguous cues to 42s',()=>{
 const cues=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.000 --> (\d\d):(\d\d):(\d\d)\.000/g)];
 assert.equal(cues.length,6);
 let expected=0;
 for(const cue of cues){const start=Number(cue[1])*3600+Number(cue[2])*60+Number(cue[3]),end=Number(cue[4])*3600+Number(cue[5])*60+Number(cue[6]);assert.equal(start,expected);assert.equal(end-start,7);expected=end;}
 assert.equal(expected,42);
});
test('article has primary-paper source trail and historical caveat',()=>{
 for(const x of ['1977','2015','2020','2021','2024','Puységur','not','https://doi.org/10.5334/joc.161'])assert.ok(report.includes(x),x);
});
test('matrix full source IDs and closed merchant approval',()=>{
 assert.ok(matrix.sources.length>=15);
 const ids=new Set(matrix.sources.map(x=>x.id));
 for(const claim of matrix.claims)for(const s of claim.source_ids)assert.ok(ids.has(s),s);
 assert.equal(matrix.merchant_status.inspire3_account_specific_approval,'NOT VERIFIED');
 assert.equal(matrix.merchant_status.exact_product_offer_link,'WITHHELD');
 assert.ok(matrix.release_gates.length>=30);
 assert.equal(matrix.merchant_status.revenue_per_1000_qualified_sessions,'NOT COMPUTABLE');
});
test('attribution discriminates affiliate clicks from paid sales',()=>{
 for(const s of ['affiliate_click','paid_order_verified','refund_or_adjustment','qualified_human_sessions','NOT COMPUTABLE','UNVERIFIED','Praxxis','Jetpack'])assert.ok(acceptance.includes(s),s);
});
test('hub links live historical and free resource routes only',()=>{
 for(const s of ['change-blindness/','mesmerism/','puysegurs-animal-magnetism-files/','/focus/'])assert.ok(hub.includes(s),s);
 assert.doesNotMatch(hub,/href=["']https?:\/\/(?:www\.)?zen12\./i);
});
test('no one can infer tests or published conversion',()=>{
 for(const x of [a,b,acceptance])assert.match(x,/not|unpublished|pending|HOLD|unverified/i);
});

import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
import {ENABLED,aggregateSynthetic} from './attribution-hard-off.mjs';
const dir=dirname(fileURLToPath(import.meta.url));
const get=f=>readFileSync(join(dir,f),'utf8');
const a=get('zen12-a-text.wp.html'),b=get('zen12-b-film.wp.html'),h=get('mind-hub-alternative.wp.html'),i=get('thatcher-investigation.wp.html'),g=get('zen12-evidence-guide.md');
const claim=get('claims-and-permissions.tsv'),src=get('source-register.tsv'),vtt=get('film-captions.vtt');
const guide=x=>x.match(/<div data-guide-core="r37">([\s\S]*?)<\/div><aside class="card" aria-labelledby="order-hold">/)?.[1];
test('presell substantive guide cores are identical',()=>assert.equal(guide(a),guide(b)));
for(const [n,x] of [['article',i],['hub',h],['text',a],['film',b]]){
 test(n+' no script, form, tracker, pixel, iframe or autoplay',()=>{for(const word of ['<script','<form','<iframe','autoplay','gtag(','fbq(','dataLayer','sendBeacon','localStorage','<video']) assert.ok(!x.includes(word),word)});
 test(n+' contains focus-safe links and no extra subscription',()=>assert.ok(!x.includes('type="email"')));
 test(n+' contrast and responsive CSS',()=>{assert.match(x,/prefers-reduced-motion/);assert.match(x,/max-width:390px/);assert.match(x,/focus-visible/)});
}
for(const [n,x] of [['text',a],['film',b]]){
 test(n+' has nearby disclosure before disabled control',()=>{
   const disclosure=x.lastIndexOf('If you purchase through this link, Final Vestige may earn a commission at no additional cost to you.');
   const control=x.lastIndexOf('aria-disabled="true"');assert.ok(disclosure>0 && disclosure<control && control-disclosure<700);
   assert.ok(!/<a[^>]+(?:zen12\.com\/getstarted|affiliates\.|clickbank|hoplink)/i.test(x))
 });
 test(n+' is legible without JS',()=>assert.ok(x.includes('data-guide-core="r37"')&&x.includes('Offer link not yet available')));
}
test('article has zero Zen12 recommendation',()=>assert.ok(!/earn a commission|View Zen12 options/.test(i)));
test('video has static poster and full transcript, no faux video control',()=>{assert.match(b,/film-transcript/);assert.match(b,/<summary>/);assert.match(b,/APPROVED-FIRST-PARTY-SVG-POSTER-URL-REQUIRED/);assert.ok(!b.includes('play-button'))});
test('text-only variant has no film block',()=>assert.ok(!a.includes('film-stage')));
test('seller claims qualified',()=>{assert.match(g,/seller efficacy claims/);assert.match(g,/did not evaluate Zen12/);assert.match(g,/without the Hype|without the hype|What You Actually Get/);assert.ok(!/we (used|tried|tested) Zen12/i.test(g))});
test('specific tiers and four styles',()=>{for(const w of ['Beginner','Premium','Advanced','24 MP3s','48 MP3s','four audio styles'])assert.ok(g.includes(w),w)});
test('matrix has at least 45 distinct rows and forbidden claims',()=>{const rows=claim.trim().split('\n');assert.ok(rows.length>=46);assert.ok(new Set(rows.slice(1).map(x=>x.split('\t')[0])).size===rows.length-1);for(const w of ['C23','C24','C32','C33','C36','C40'])assert.match(claim,new RegExp(w))});
test('source register has primary FTC seller and independent sources',()=>{for(const w of ['zen12.com/hnp','inspire3.com/','ftc.gov','10.1068/p090483','10.1371/journal.pone.0286023'])assert.ok(src.includes(w))});
test('film timed caption blocks are six and end at exactly 40 sec',()=>{assert.equal((vtt.match(/-->/g)||[]).length,6);assert.match(vtt,/00:00:34.000 --> 00:00:40.000/)});
test('attribution always off and excludes identifiers',()=>{assert.equal(ENABLED,false);assert.deepEqual(aggregateSynthetic([]),[]);assert.throws(()=>aggregateSynthetic([{variant:'text',source:'organic',topic:'zen12',action:'guide',email:'bad@x.com'}]));assert.throws(()=>aggregateSynthetic([{variant:'text',source:'organic',topic:'zen12',action:'guide',user_id:'123'}]));assert.throws(()=>aggregateSynthetic([{variant:'text',source:'organic',topic:'zen12',action:'guide',ip:'127.0.0.1'}]));assert.throws(()=>aggregateSynthetic([],1))});
test('suppresses small synthetic groups',()=>{const e={variant:'text',source:'organic',topic:'zen12',action:'offer-intent'};assert.deepEqual(aggregateSynthetic(Array(9).fill(e)),[]);assert.deepEqual(aggregateSynthetic(Array(10).fill(e)),[{group:'text|organic|zen12|offer-intent',count:10}])});
test('clean local events and source categories only',()=>{assert.throws(()=>aggregateSynthetic([{variant:'unknown',source:'organic',topic:'zen12',action:'guide'}]));assert.throws(()=>aggregateSynthetic([null]));assert.throws(()=>aggregateSynthetic([[]]));assert.throws(()=>aggregateSynthetic('oops'))});

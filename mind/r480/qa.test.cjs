'use strict';
/* Mind R480 offline regression. Run: node --test mind/r480/qa.test.cjs
   Source checks only; not browser, WordPress, merchant or WCAG certification. */
const { test }=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const read=(n)=>fs.readFileSync(path.join(__dirname,n),'utf8');
const A=read('ZEN12_GUIDE_A_EVIDENCE_TEXT.html');
const B=read('ZEN12_GUIDE_B_OPTIONAL_FILM.html');
const M=JSON.parse(read('PRODUCT_CLAIM_PERMISSION_MATRIX.json'));
const hub=read('MIND_ARCHIVE_FOUR_STREAM_SOURCE_ONLY.html');
const article=read('THE_PENDULUM_THAT_MOVED_WITHOUT_PERMISSION.md');
const vtt=read('OPTIONAL_42S_CAPTIONS.vtt');
const poster=read('OPTIONAL_42S_POSTER.svg');
const docket=read('OFFER_TO_SETTLED_NET_REVENUE_ACCEPTANCE.md');
test('source trail is substantive',()=>{
 assert.ok(article.trim().split(/\s+/).length>=1800);
 for(const x of ['Chevreul','1975','1976','1977','Puységur','https://pubmed.ncbi.nlm.nih.gov/28136225/'])assert.ok(article.includes(x));
});
test('A and B share identical substantive copy',()=>{
 const stripped=B.replace(/\s*<section aria-labelledby="film-heading" class="media">[\s\S]*?<\/section>/,'');
 assert.equal(A.replace(/\s+/g,' ').trim(),stripped.replace(/\s+/g,' ').trim());
});
for(const [id,html] of [['A',A],['B',B]]){
 test(id+' hard hold and adjacent disclosure',()=>{
   assert.match(html,/<button\b[^>]*\sdisabled(?:\s|>)/);
   assert.match(html,/If you purchase through a future qualifying link, Final Vestige may earn a commission/);
   const d=html.indexOf('class="disclosure"'), b=html.indexOf('<button');
   assert.ok(d>0 && b>d && b-d<600);
   assert.doesNotMatch(html,/<a\b[^>]*href\s*=\s*["'][^"']*(zen12\.com|inspire3\.com|refersion|clickbank)[^"']*["']/i);
 });
 test(id+' privacy and accessibility source gates',()=>{
   assert.match(html,/<html lang="en">/);
   assert.match(html,/href="#main"/);
   assert.match(html,/prefers-reduced-motion:reduce/);
   assert.match(html,/noindex,nofollow/);
   assert.doesNotMatch(html,/<(script|iframe|form|input)\b/i);
   assert.doesNotMatch(html,/\b(autoplay|onload|onclick|onerror)\s*=/i);
   assert.doesNotMatch(html,/VZ54YTD6|\$37|\$87/);
 });
}
test('B video concept is optional, non-playable and fully transcribed',()=>{
 assert.match(B,/film-heading/);
 assert.match(B,/<details><summary>/);
 assert.match(B,/no encoded or hosted video/);
 assert.match(B,/OPTIONAL_42S_POSTER.svg/);
 assert.match(poster,/^<svg/);
 assert.doesNotMatch(poster,/<script\b/i);
});
test('WebVTT exactly six contiguous cues through 42 seconds',()=>{
 const cues=[...vtt.matchAll(/^(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})$/gm)];
 assert.equal(cues.length,6);
 const ms=(a,b,c,d)=>Number(a)*3600000+Number(b)*60000+Number(c)*1000+Number(d);
 let last=0;
 for(const c of cues){const start=ms(...c.slice(1,5)),end=ms(...c.slice(5,9)); assert.equal(start,last);assert.ok(end>start);last=end;}
 assert.equal(last,42000);
});
test('merchant and owned SKU all in hard hold',()=>{
 assert.equal(M.claims.length,24);
 assert.equal(M.commercial_release_gates.length,28);
 assert.ok(M.commercial_release_gates.every(x=>x.passed===false&&x.proof===null));
 assert.equal(M.partner_account_evidence.approved_link,null);
 assert.equal(M.owned_product_fallback.payable_status,'not_authenticated');
});
test('hub source-only, existing routes, no takeover',()=>{
 for(const s of ['/focus/','/2026/11/02/change-blindness/','/2026/11/02/mesmerism/','/free-resources/puysegurs-animal-magnetism-files/'])assert.ok(hub.includes(s));
 assert.match(hub,/noindex,nofollow/);
 assert.doesNotMatch(hub,/<(script|form|iframe)\b/i);
});
test('docket recognizes settled revenue only',()=>{
 for(const s of ['NOT COMPUTABLE','affiliate_outbound','refund','7- and 30-day','Prax','Grok'])assert.ok(docket.includes(s));
});

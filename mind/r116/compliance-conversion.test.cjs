'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {test} = require('node:test');
const root = path.resolve(__dirname,'..','..');
const files = {
 article: fs.readFileSync(path.join(__dirname,'the-glass-that-wasnt-there.md'),'utf8'),
 offer: fs.readFileSync(path.join(__dirname,'one-offer-merchant-authorization.md'),'utf8'),
 matrix: JSON.parse(fs.readFileSync(path.join(__dirname,'source-and-claim-ledger.json'),'utf8')),
 a: fs.readFileSync(path.join(root,'mind/r114/zen12-text-A.html'),'utf8'),
 b: fs.readFileSync(path.join(root,'mind/r114/zen12-film-B.html'),'utf8'),
 vtt: fs.readFileSync(path.join(root,'mind/r114/film-40s.vtt'),'utf8')
};
test('manuscript original sourced with independent primary experiments',()=>{
 assert.ok(files.article.split(/\s+/).length>=1500);
 for(const u of ['10.1016/S0022-5371','34110859','16027179','168877'])assert.ok(files.article.includes(u),u);
 assert.ok(files.article.includes('unvalidated')||files.article.includes('not a validated'));
 assert.ok(!/affiliate link|purchase through|earn a commission/i.test(files.article));
});
test('exact seller + FTC source and claim registry completeness',()=>{
 const m=files.matrix;
 assert.equal(m.metadata.earning_link,null);
 assert.equal(m.metadata.net_revenue_per_1000_qualified_humans,null);
 assert.equal(m.sources.length,15);
 assert.equal(m.claims.length,18);
 assert.ok(m.sources.some(s=>s.url==='https://zen12.com/hnp'));
 assert.ok(m.claims.every(c=>c.proof.length&&c.proof.every(id=>m.sources.some(s=>s.id===id))));
 assert.ok(m.claims.some(c=>c.status==='not_product_substantiated'));
 assert.ok(m.claims.some(c=>c.status==='confirmed_policy_risk'));
});
test('every commercial / privacy / release approval gate is closed',()=>{
 assert.ok(Object.values(files.matrix.gating).every(x=>x===false));
 assert.ok(files.offer.includes('NOT COMPUTABLE (NULL)'));
 assert.ok(files.offer.includes('HARD HOLD'));
});
test('no affiliate destination / autoplay or duplicate signup in canonical prototypes',()=>{
 for(const h of [files.a,files.b]){
  assert.ok(h.includes('https://zen12.com/hnp'));
  assert.ok(!/<a\b[^>]+href\s*=\s*["'][^"']*(?:zen12\.com|affiliates\.inspire3\.com)/i.test(h));
  assert.ok(!/<iframe\b|<form\b|<script\b|autoplay\s*=/i.test(h));
  assert.ok(/<button\b[^>]*disabled/i.test(h));
  assert.ok(/commission/i.test(h));
 }
});
test('film remains captioned optional concept and not an untested autoplay embed',()=>{
 assert.ok(files.vtt.startsWith('WEBVTT'));
 assert.ok(files.b.includes('transcript')||files.b.includes('Transcript'));
 assert.ok(!files.a.includes('<!-- BEGIN OPTIONAL FILM'));
 assert.ok(!/<video\b|<iframe\b/i.test(files.b));
});
test('conversion contract has actual human sessions and settlement fail-closed',()=>{
 const c=files.offer;
 for(const term of ['qualified human','refund','fee','7- and 30-day','asset_id','Grok','Praxxis','Dispatch'])assert.ok(c.toLowerCase().includes(term.toLowerCase()),term);
 assert.ok(c.includes('not a paid product')||c.includes('free'));
});

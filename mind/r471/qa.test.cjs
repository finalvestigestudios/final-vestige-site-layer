'use strict';
// R471 reproducible offline static checks. Run: node --test mind/r471/qa.test.cjs
// Does NOT replace native browser/WP sanitizer/merchant verification.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const dir = __dirname;
const read = name => fs.readFileSync(path.join(dir,name),'utf8');
const A=read('ZEN12_A_TEXT_GUIDE.html');
const B=read('ZEN12_B_OPTIONAL_FILM_GUIDE.html');
const H=read('MIND_HUB_SOURCE_ONLY.html');
const M=JSON.parse(read('CLAIM_OFFER_PERMISSION_MATRIX.json'));
const X=read('THE_FACE_THAT_CHANGED_WHEN_TURNED_UPRIGHT.md');
const P=read('ZEN12_FILM_POSTER.svg');
const V=read('ZEN12_FILM_CAPTIONS.vtt');
const R=read('CREATOR_TO_SETTLED_REVENUE_ACCEPTANCE.md');
const noHtmlScripts = v => !/<script\b|onload\s*=|onclick\s*=|<iframe\b|<form\b/i.test(v);
const stripOptional = v => v.replace(/<section class="optional-film panel"[\s\S]*?<\/section>/,'');
test('seller promotion has no earning URL or checkout anchors in either public buyer variant',()=>{
 for (const v of [A,B]) {
  assert.doesNotMatch(v,/https?:\/\/(?:www\.)?(?:zen12|inspire3)\.com/i);
  assert.doesNotMatch(v,/<a\b[^>]*href\s*=\s*["'][^"']*affiliat/i);
 }
});
test('both variants retain no script, form, embed, iframe or inline event handler',()=>{assert.ok(noHtmlScripts(A));assert.ok(noHtmlScripts(B));});
test('both variants have native disabled purchase controls',()=>{for(const v of [A,B])assert.match(v,/<button\b[^>]*disabled\b[^>]*>/);});
test('commission disclosure is adjacent to purchase control',()=>{for (const v of [A,B]){const i=v.indexOf('Prospective affiliate disclosure');const j=v.indexOf('<button');assert.ok(i>=0 && j>i && j-i<800);}});
test('no unsupported seller outcomes are presented as tested product facts',()=>{for(const v of [A,B]){assert.match(v,/did[\s\S]{0,35}not[\s\S]{0,35}evaluate Zen12/i);assert.match(v,/seller claims|seller makes assertions|seller-reported/i);}});
test('A and B have exactly the same substantive buyer copy',()=>{assert.equal(stripOptional(B).replace(/\s+/g,' ').trim(),A.replace(/\s+/g,' ').trim());});
test('B is optional and has transcript but no autoplay or media fetch',()=>{assert.match(B,/optional-film/);assert.match(B,/<details>/);assert.doesNotMatch(B,/autoplay|<video\b|<audio\b/i);});
test('poster original SVG without external resources or scripting',()=>{assert.match(P,/<svg\b/);assert.match(P,/<title\b/);assert.match(P,/<desc\b/);assert.doesNotMatch(P,/<script\b|<foreignObject\b|xlink:href|\shref=|<image\b/i);});
test('VTT begins WEBVTT and reaches final 42 seconds',()=>{assert.match(V,/^WEBVTT/);assert.match(V,/00:00:35\.000 --> 00:00:42\.000/);});
test('VTT has six cue segments and no overlapping ranges',()=>{const ranges=[...V.matchAll(/(\d{2}):(\d{2}):(\d{2})\.\d+ --> (\d{2}):(\d{2}):(\d{2})\.\d+/g)];assert.equal(ranges.length,6);let prior=0;for(const v of ranges){const start=(+v[1])*3600+(+v[2])*60+(+v[3]);const end=(+v[4])*3600+(+v[5])*60+(+v[6]);assert.equal(start,prior);assert.ok(end>start);prior=end;}assert.equal(prior,42);});
test('article is substantive and sourced to multiple primary experiments',()=>{assert.ok(X.trim().split(/\s+/).length>1700);for(const id of ['10.1068/p090483','20942363','17564200','25301017'])assert.ok(X.includes(id));});
test('article has explicit historic evidence / mechanisms boundary',()=>{assert.match(X,/does not automatically prove/i);assert.match(X,/Puységur/);});
test('Mind hub has four coherent streams and only existing permitted live route links',()=>{for(const s of ['Perception & attention','History of suggestion','Practice & reflection','Tools under review'])assert.ok(H.includes(s));assert.ok(H.includes('/focus/'));assert.ok(H.includes('/mesmerism/'));});
test('Hub has no commerce activation or signup duplication',()=>{assert.ok(noHtmlScripts(H));assert.doesNotMatch(H,/https?:\/\/(zen12|inspire3)\.com|<form\b/i);});
test('all public HTML variants contain mobile layout, keyboard and reduced-motion consideration',()=>{for(const v of [A,B,H]){assert.match(v,/@media\(max-width:/);assert.match(v,/:focus-visible/);assert.match(v,/prefers-reduced-motion/);}});
test('source matrix valid and cited',()=>{assert.ok(M.claims.length>=20);for(const c of M.claims)assert.ok(c.source);assert.ok(M.sources.ftc&&M.sources.review&&M.sources.seller);});
test('all merchant release gates are held',()=>{assert.ok(M.release_gates.length>=30);assert.ok(M.release_gates.every(g=>g.status==='HOLD'));});
test('merchant price, earning link and paid ownership remain unverified',()=>{assert.equal(M.seller_offer_distinction.price,null);assert.equal(M.seller_offer_distinction.issued_earning_url,null);assert.equal(M.FV_owned_purchasable_Mind_product,'NOT_AUTHENTICATED');});
test('do not confuse outbound clicks and leads with orders',()=>{assert.equal(M.measurement.lead_is_not_sale,true);assert.equal(M.measurement.outbound_click_is_not_sale,true);assert.equal(M.measurement.net_revenue_per_1000,'NOT_COMPUTABLE');});
test('owner plan separates creator, engineering, commerce and Site QA lanes',()=>{for(const s of ['Praxxis / Grok','Founder / Commerce','Claude / Dispatch','Mind / Site QA'])assert.ok(R.includes(s));});
test('owner plan records alternative product blockers and net-revenue formula',()=>{assert.match(R,/Products 001–015/);assert.match(R,/refunds/);assert.match(R,/NOT COMPUTABLE/);});
test('no reviewer or seller financial exaggerations in HTML',()=>{for(const v of [A,B])assert.doesNotMatch(v,/guaranteed wealth|i used Zen12|i tested Zen12|buy now|limited time/i);});

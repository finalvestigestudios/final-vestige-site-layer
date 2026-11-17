#!/usr/bin/env node
// R439 independent, offline and deterministic fixture checks. No network, writes or paid calls.
// Run from repo root: node mind/r439/verify.mjs
import { readFileSync } from 'node:fs';
import { strict as assert } from 'node:assert';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
const dir=dirname(fileURLToPath(import.meta.url));
const read=n=>readFileSync(join(dir,n),'utf8');
const article=read('THE_LABEL_THAT_CHANGED_THE_TRANCE.md');
const A=read('ZEN12_A_TEXT_ONLY.html');
const B=read('ZEN12_B_FILM_CONCEPT.html');
const hub=read('MIND_ARCHIVE_WP_SOURCE_ONLY.html');
const svg=read('R439_ORIGINAL_POSTER.svg');
const vtt=read('R439_FILM_42S.vtt');
const matrix=JSON.parse(read('CLAIM_SOURCE_PARTNER_AND_RELEASE_MATRIX.json'));
const plan=read('OFFER_CREATOR_ATTRIBUTION_AND_REVENUE_ACCEPTANCE.md');
let passed=0;
function check(name,fn){try{fn();passed++;console.log('PASS',name)}catch(e){console.error('FAIL',name,e.message);process.exitCode=1}}
const contains=(s,x)=>assert.ok(s.includes(x),x);
const no=(s,re)=>assert.equal(re.test(s),false,re.source);
const sellerHref=/href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|inspire3\.com|affiliates\.inspire3\.com)/i;
const srcOutsideFilm=B.replace(/<section class="film"[\s\S]*?<\/section>/,'').replace('B: optional film concept','A: text-only control').replace('draft B','draft A');
check('buyer copy identical except isolated film treatment',()=>assert.equal(srcOutsideFilm,A));
for(const [name,data] of [['A',A],['B',B]]){
check(name+' complete HTML semantics',()=>{contains(data,'<!doctype html>');contains(data,'<html lang="en">');contains(data,'<main id="main">');contains(data,'<article>');contains(data,'</html>')});
check(name+' does not link merchant',()=>no(data,sellerHref));
check(name+' no checkout, redirection, iframe, form, script, autoplay, tracker or injected analytics',()=>no(data,/<(?:script|iframe|form|video|audio)\b|autoplay\s*=|onclick\s*=|onload\s*=|googletagmanager|gtag\s*\(|fbq\s*\(/i));
check(name+' commercial disabled',()=>{contains(data,'disabled aria-disabled="true"');contains(data,'purchase link unavailable')});
check(name+' disclosure adjacent to disabled CTA',()=>{let d=data.indexOf('Prospective affiliate disclosure:');let c=data.indexOf('Zen12 purchase link unavailable');assert.ok(d>=0&&c>d&&c-d<700)});
check(name+' factual seller claims properly qualified',()=>{contains(data,'seller-described');contains(data,'seller');contains(data,'not established');contains(data,'different offers')});
check(name+' direct existing free 52-page route',()=>{contains(data,'https://finalvestige.com/focus/');contains(data,'52-page')});
check(name+' responsive and focus visible',()=>{contains(data,'width=device-width');contains(data,':focus-visible');contains(data,'prefers-reduced-motion')});
check(name+' no personal product use claims',()=>no(data,/\b(I used Zen12|we tested the product|we bought Zen12|guaranteed income)\b/i));
}
check('B has one optional poster and readable transcript',()=>{contains(B,'R439_ORIGINAL_POSTER.svg');contains(B,'<details>');contains(B,'Read the complete film transcript');contains(B,'not encoded')});
check('poster original accessible SVG',()=>{contains(svg,'viewBox="0 0 960 540"');contains(svg,'<title');contains(svg,'<desc');contains(svg,'role="img"');no(svg.replace('http://www.w3.org/2000/svg',''),/<script\b|<foreignObject\b|<image\b|https?:\/\//i)});
check('six caption cues over 42 seconds',()=>{assert.equal((vtt.match(/--> /g)||[]).length,6);contains(vtt,'00:00:42.000');contains(vtt,'WEBVTT')});
check('article primary study and full sources',()=>{contains(article,'10.1111/psyp.70183');contains(article,'46 people');contains(article,'3.41');contains(article,'2025');contains(article,'Puységur');contains(article,'10.1016/j.concog.2025.103948');assert.ok(article.trim().split(/\s+/).length>1500)});
check('article no affiliate sale link',()=>no(article,/\]\(https?:\/\/(?:www\.)?(?:zen12|hypnosislive|brainwaveshots)\.com\/(?:buy|cart|checkout)/i));
check('hub has four streams and canonical live paths',()=>{for(const term of ['Perception &amp; attention','History of suggestion','Practice &amp; reflection','Tools under review','https://finalvestige.com/focus/','https://finalvestige.com/2026/11/02/change-blindness/','https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'])contains(hub,term)});
check('hub source only no analytics or opt-in duplication',()=>no(hub,/<script\b|<iframe\b|<form\b|autoplay\s*=|googletagmanager|gtag\s*\(/i));
check('matrix 28 well-scoped claims',()=>{assert.equal(matrix.claims.length,28);assert.equal(new Set(matrix.claims.map(c=>c.id)).size,28);assert.ok(matrix.claims.every(c=>c.approved_copy&&c.classification&&c.limit_or_needed_proof))});
check('matrix sources non-empty and absolute',()=>assert.ok(Object.values(matrix.source_inventory).every(x=>x.startsWith('https://'))));
check('matrix all source keys exist',()=>assert.ok(matrix.claims.every(c=>c.source_keys.every(k=>Object.hasOwn(matrix.source_inventory,k)))));
check('all 28 release gates HARD HOLD',()=>{assert.equal(matrix.release_gates.length,28);assert.ok(matrix.release_gates.every(g=>g.status==='HOLD'));assert.equal(matrix.release_status,'HARD_HOLD')});
check('publisher commission and verified sale unknown',()=>{assert.equal(matrix.commerce_findings.issued_affiliate_url,null);assert.equal(matrix.commerce_findings.settled_affiliate_commission,null);assert.equal(matrix.commerce_findings.net_revenue_per_1000_qualified_sessions,null)});
check('conversion ledger does not conflate clicks and purchases',()=>{contains(plan,'affiliate_click');contains(plan,'confirmed_paid_affiliate_sale');contains(plan,'settled_net_revenue');contains(plan,'NOT COMPUTABLE');contains(plan,'refunds/fees')});
check('three candidate media matches are unverified',()=>{contains(plan,'UNMATCHED');contains(plan,'Puységur');contains(plan,'change blindness');contains(plan,'hypnosis framing')});
check('commercial authorization and release controls explicit',()=>{for(const s of ['PR #49/#172','Founder / Commerce','no newsletter','not permission to publish'])contains(plan,s)});
console.log(`R439: ${passed} checks passed; status ${process.exitCode===1?'FAIL':'PASS'}. No browser, WordPress, CI or merchant execution is part of this script.`);
if(process.exitCode===1)process.exit(1);

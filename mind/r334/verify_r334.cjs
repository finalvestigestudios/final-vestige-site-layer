#!/usr/bin/env node
'use strict';
/* Reproducible no-dependency source/a11y/security guardrail suite.
   Run from any directory: node mind/r334/verify_r334.cjs
   Does not replace browser WCAG or actual merchant/partner confirmation. */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const dir = __dirname;
const read = f => fs.readFileSync(path.join(dir,f),'utf8');
const a=read('zen12-A-text-only.html'),b=read('zen12-B-optional-film.html');
const hub=read('MIND-HUB-EDITORIAL-REVIEW-ONLY.html');
const article=read('THE-RECORDING-IN-THE-TRIAL-WAS-NOT-THE-RECORDING-ON-THE-SALES-PAGE.md');
const matrix=JSON.parse(read('CLAIMS-PARTNER-PROOF-MATRIX.json'));
const vtt=read('zen12-42s.vtt'),svg=read('zen12-poster.svg');
const render=read('render_zen12_film.py');
let pass=0;
function check(title,fn){try{fn();pass++; console.log('PASS',title)}catch(e){console.error('FAIL',title,':',e.message);process.exitCode=1}}
const merchantHost=/https?:\/\/(?:www\.)?(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i;
const activeMerchant=x=>/<a\b[^>]*href=["'][^"']*(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(x);
const illegalTags=x=>(/<\s*(?:script|form|iframe)\b/i.test(x));
const buyerBody=x=>{const match=x.match(/<section class="chapter" id="question"[\s\S]*?(?=<footer)/);assert.ok(match,'buyer body missing');return match[0]};
const disclosureNearButton=x=>{const p=x.indexOf('id="commission"');const q=x.indexOf('<button type="button" disabled');return p>=0&&q>p&&q-p<900&&x.includes('aria-describedby="commission hold"')};
const linkCount=(x,host)=>[...x.matchAll(new RegExp('href="https://'+host.replace(/[.*+?^$()|[\]{}]/g,'\\$&')+'[^"]*"','g'))].length;
function allPageSafety(x){
 assert.match(x,/<html lang="en">/);
 assert.match(x,/<meta name="viewport"/);
 assert.match(x,/<meta name="robots" content="noindex,nofollow"/);
 assert.match(x,/<h1 id="hero-title">/);
 assert.match(x,/@media\(max-width:650px\)/);
 assert.match(x,/@media\(prefers-reduced-motion:reduce\)/);
 assert.ok(!illegalTags(x),'forbidden executable/embedded form/iframe');
 assert.ok(!activeMerchant(x),'merchant hyperlink active');
 assert.match(x,/<button type="button" disabled/);
 assert.ok(disclosureNearButton(x),'immediate, accessible prospective material-connection disclosure missing');
 assert.ok(x.includes('https://finalvestige.com/focus/'));
 assert.ok(!/\bautoplay\b/i.test(x),'no autoplay even in markup');
 assert.ok(!/href="\.\/(?:THE-|zen12-42s\.mp4)/.test(x),'no unpublished article destinations');
}
check('A safe HTML and disabled affiliate CTA',()=>allPageSafety(a));
check('B safe HTML and disabled affiliate CTA',()=>allPageSafety(b));
check('Same substantive buyer copy in A and B',()=>assert.equal(buyerBody(a),buyerBody(b)));
check('No video player in A',()=>assert.ok(!/<video\b/.test(a)));
check('B uses native user-controls, no preload/autoplay, poster and captions',()=>{
 assert.match(b,/<video controls preload="none" playsinline poster="\.\/zen12-poster\.svg"/);
 assert.match(b,/<track kind="captions"[^>]*src="\.\/zen12-42s\.vtt"/);
 assert.match(b,/<summary>Read the complete 42-second transcript<\/summary>/);
});
check('No new sign-up stack, script or iframe on all three HTML documents',()=>{for(const x of [a,b,hub])assert.ok(!illegalTags(x));});
check('Hub has four streams and links to only real published investigative routes',()=>{
 for(const label of ['Perception &amp; Attention','History of Suggestion','Practice &amp; Reflection','Tools Under Review'])assert.ok(hub.includes(label));
 assert.ok(hub.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'));
 assert.ok(hub.includes('https://finalvestige.com/2026/11/02/change-blindness/'));
 assert.ok(!activeMerchant(hub));
 assert.ok(!/href="https:\/\/finalvestige\.com\/mind\//.test(hub));
});
check('Hub mobile/reduced motion/no-JS/a11y source signatures',()=>{
 assert.match(hub,/<html lang="en">/);assert.match(hub,/<meta name="viewport"/);
 assert.match(hub,/@media\(max-width:720px\)/);assert.match(hub,/@media\(prefers-reduced-motion:reduce\)/);
 assert.match(hub,/a:focus-visible/);
});
check('VTT exactly six 7-second captions ending 42s',()=>{
 const cues=[...vtt.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)];
 assert.equal(cues.length,6);
 for(let i=0;i<6;i++){assert.equal(cues[i][1],`00:00:${String(i*7).padStart(2,'0')}.000`);assert.equal(cues[i][2],`00:00:${String((i+1)*7).padStart(2,'0')}.000`);}
 assert.ok(vtt.startsWith('WEBVTT'));
});
check('Original SVG includes accessible description, no external dependencies',()=>{
 assert.match(svg,/role="img" aria-labelledby=/);
 assert.match(svg,/<title id=/);assert.ok(!/<script|<image[^>]+href=/i.test(svg));
});
check('Offline film renderer has six frames, 42 second guard, no remote download',()=>{
 assert.ok(render.includes('PAGES = [')&&render.includes('for i in range(6)'));
 assert.ok(render.includes('duration 7'));assert.ok(render.includes('41.8 <= float(duration) <= 42.5'));
 assert.ok(!/https:\/\//.test(render));assert.ok(!/subprocess\.run\(.*(?:curl|wget)/.test(render));
});
check('Deep original article cites bounded trials and source limits',()=>{
 assert.ok(article.split(/\s+/).length>=1700);
 for(const u of ['10.1177/13524585251329820','41217756','s41598-025-88517-z','Puységur','Fatigue','FTC'])assert.ok(article.toLowerCase().includes(u.toLowerCase()),'missing '+u);
});
check('Claims registry: 16 real source links and at least 24 typed claims',()=>{
 assert.ok(matrix.sources.length>=16&&matrix.claims.length>=24);
 assert.ok(matrix.sources.every(s=>/^https:\/\//.test(s.url)));
 assert.ok(matrix.claims.every(c=>c.id&&c.classification&&c.allowed));
});
check('Commercial 18/18 gates all remain unverified',()=>{
 assert.equal(matrix.authorization_gates.length,18);
 assert.ok(matrix.authorization_gates.every(g=>g.status==='HOLD_UNVERIFIED'));
});
check('Creator routes are proposals with no fabricated asset IDs',()=>{
 assert.equal(matrix.proposed_social_fit.length,3);
 assert.ok(matrix.proposed_social_fit.every(x=>x.asset_id===null&&x.asset_url===null));
});
check('Conversion metric not fabricated',()=>{
 assert.equal(matrix.measurement_contract.status,'NOT_COMPUTABLE');
 assert.ok(matrix.measurement_contract.events.includes('merchant_verified_paid_order'));
});
check('Price and refund descriptions explicitly qualified',()=>{
 assert.ok(a.includes('<strong>not</strong> confirmed cart totals'));assert.ok(a.includes('seller advertises a one-year'));
});
function rejectMutation(name,mutate,valid){const changed=mutate(a);assert.ok(!valid(changed),name+' was not detected');}
check('Negative 1 - stripped commission disclosure rejected',()=>rejectMutation('disclosure',x=>x.replace('id="commission"','id="missing"'),disclosureNearButton));
check('Negative 2 - enabled purchase control rejected',()=>rejectMutation('button',x=>x.replace('<button type="button" disabled','<button type="button"'),x=>/<button type="button" disabled/.test(x)));
check('Negative 3 - merchant direct link rejected',()=>rejectMutation('merchant',x=>x+'<a href="https://zen12.com/">buy</a>',x=>!activeMerchant(x)));
check('Negative 4 - affiliate redirect link rejected',()=>rejectMutation('affiliate',x=>x+'<a href="https://affiliates.inspire3.com/example">buy</a>',x=>!activeMerchant(x)));
check('Negative 5 - injected form rejected',()=>rejectMutation('form',x=>x+'<form><input></form>',x=>!illegalTags(x)));
check('Negative 6 - injected script rejected',()=>rejectMutation('script',x=>x+'<script>alert(1)</script>',x=>!illegalTags(x)));
check('Negative 7 - iframe pixel rejected',()=>rejectMutation('iframe',x=>x+'<iframe src="https://example.com/track"></iframe>',x=>!illegalTags(x)));
check('Negative 8 - auto-playing video rejected',()=>{const x=b.replace('controls preload="none"','autoplay controls');assert.ok(/\bautoplay\b/i.test(x));});
check('Negative 9 - incorrect package tier rejected',()=>{const x=a.replace('12 levels · 48 MP3s','12 levels · 24 MP3s');assert.notEqual(buyerBody(x),buyerBody(b));});
check('Negative 10 - false partner approval rejected',()=>{const m=structuredClone(matrix);m.authorization_gates[0].status='APPROVED';assert.ok(!m.authorization_gates.every(g=>g.status==='HOLD_UNVERIFIED'));});
check('Negative 11 - fabricated Grok asset ID rejected',()=>{const m=structuredClone(matrix);m.proposed_social_fit[0].asset_id='made-up';assert.ok(!m.proposed_social_fit.every(x=>x.asset_id===null));});
check('Negative 12 - captions removed rejected',()=>{const x=b.replace('<track kind="captions"','<track kind="descriptions"');assert.ok(!/<track kind="captions"/.test(x));});
if(process.exitCode)process.exit(1);
console.log('SOURCE VALIDATION COMPLETE',pass,'assertions and adversarial mutations passed; not browser or merchant QA.');

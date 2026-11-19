'use strict';
// R484 portable native Node.js regression tests. Run after cloning:
// node --test mind/r484/qa.test.cjs
// IMPORTANT: Only an actual execution counts as Native Node PASS.
// If executed only via another JavaScript interpreter, report accordingly.
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const dir=__dirname;
const read=(file)=>fs.readFileSync(path.join(dir,file),'utf8');
const A=read('FOCUS_SHOT_GUIDE_A_TEXT.html');
const B=read('FOCUS_SHOT_GUIDE_B_OPTIONAL_FILM.html');
const article=read('THE_SOUND_BETWEEN_TWO_EARS.md');
const hub=read('MIND_HUB_GUTENBERG_ADDITIVE_SOURCE_ONLY.html');
const docket=read('CONVERSION_LEDGER_GROK_CROSSWALK_AND_QA.md');
const vtt=read('OPTIONAL_FILM_CAPTIONS.vtt');
const matrix=JSON.parse(read('FOCUS_SHOT_CLAIM_AND_MERCHANT_RELEASE_MATRIX.json'));
const buyer=txt=>{const m=txt.match(/<main id="buyer-guide">[\s\S]*?<\/main>/);assert.ok(m,'missing complete buyer main');return m[0];};
const checks=[
 ['substantive A/B copy byte-identical',()=>assert.equal(buyer(A),buyer(B))],
 ['A/B distinct variant markers',()=>{assert.match(A,/data-variant="text"/);assert.match(B,/data-variant="video-concept"/)}],
 ['both FTC disclosure texts exist',()=>[A,B].forEach(x=>assert.match(x,/may earn a commission at no additional cost/))],
 ['both disclosures precede button',()=>[A,B].forEach(x=>assert.ok(x.indexOf('may earn a commission')<x.indexOf('<button')))],
 ['both CTA buttons natively disabled',()=>[A,B].forEach(x=>assert.match(x,/<button type="button" disabled/))],
 ['no merchant hrefs',()=>[A,B].forEach(x=>assert.doesNotMatch(x,/href=["']https?:\/\/(?:www\.)?(?:brainwaveshots\.com|zen12\.com|hypnosislive\.com|affiliates\.inspire3\.com)/i))],
 ['no scripts, iframes, forms or inline event listeners',()=>[A,B].forEach(x=>assert.doesNotMatch(x,/<script|<iframe|<form|onload=|onclick=/i))],
 ['no video autoplay',()=>assert.doesNotMatch(B,/<video[^>]*autoplay/i)],
 ['B original semantic visual',()=>assert.match(B,/<svg[^>]*role="img"[^>]*aria-label/)],
 ['B accessible transcript',()=>{assert.match(B,/<details>/);assert.match(B,/Read the full video transcript/)}],
 ['B clearly not playable',()=>assert.match(B,/no hosted or encoded film yet/i)],
 ['no extra signup',()=>[A,B,hub].forEach(x=>assert.doesNotMatch(x,/<form/i))],
 ['scoped media styles',()=>assert.match(A,/\.mind484\s*\{/)],
 ['responsive and reduced motion',()=>[A,B].forEach(x=>{assert.match(x,/@media\(max-width:650px\)/);assert.match(x,/prefers-reduced-motion/);})],
 ['free first-party Focus',()=>[A,B,article,hub].forEach(x=>assert.match(x,/https:\/\/finalvestige\.com\/focus\//))],
 ['Puységur first-party bridge',()=>[A,B,article,hub].forEach(x=>assert.match(x,/puysegurs-animal-magnetism-files/))],
 ['research uses recent counterevidence',()=>{assert.match(article,/2019/);assert.match(article,/2023/);assert.match(article,/2026/);assert.match(article,/monaural/i)}],
 ['article length >= 1900 words',()=>assert.ok(article.split(/\s+/).length>=1900)],
 ['commercial separation in article',()=>assert.match(article,/Commercial separation/i)],
 ['matrix counts internally consistent',()=>{assert.equal(matrix.claim_count,matrix.claims.length);assert.equal(matrix.source_count,matrix.sources.length);assert.equal(matrix.release_gate_count,matrix.release_gates.length)}],
 ['all matrix source references resolve',()=>{const ids=new Set(matrix.sources.map(s=>s.id));matrix.claims.forEach(c=>c.source_ids.forEach(id=>assert.ok(ids.has(id),id)))}],
 ['matrix explicitly has no affiliate url',()=>assert.equal(matrix.commercial_controls.affiliate_url,null)],
 ['matrix zero active buying control',()=>assert.equal(matrix.commercial_controls.active_checkout_cta,false)],
 ['matrix 30+ gates held',()=>assert.ok(matrix.release_gates.length>=30&&matrix.release_gates.every(g=>g.status==='NOT_CLEARED'))],
 ['matrix 30+ claims',()=>assert.ok(matrix.claims.length>=30)],
 ['matrix paid revenue missing',()=>assert.equal(matrix.commercial_controls.realized_net_revenue,null)],
 ['VTT valid start',()=>assert.match(vtt,/^WEBVTT\n/)],
 ['VTT ends at 42 secs',()=>assert.match(vtt,/00:00:34\.000 --> 00:00:42\.000/)],
 ['hub has four editorial streams',()=>['Perception','History of Suggestion','Practice','Tools Under Review'].forEach(s=>assert.ok(hub.includes(s)))],
 ['hub existing routes only',()=>assert.doesNotMatch(hub,/href=["']https?:\/\/(?:www\.)?brainwaveshots\.com/i)],
 ['Grok IDs explicitly unverified',()=>assert.match(docket,/UNMATCHED/)],
 ['no duplicate instrument implementation',()=>assert.match(docket,/do NOT install another tag manager/i)],
 ['7 and 30 day cohorts',()=>assert.match(docket,/7\/30-day/)],
 ['net revenue distinct from clicks',()=>assert.match(docket,/NOT COMPUTABLE/)],
 ['no covered live deployment authorized',()=>assert.match(docket,/Not allowed: WordPress drafts\/published changes/i)]
];
checks.forEach(([name,fn])=>test(name,fn));

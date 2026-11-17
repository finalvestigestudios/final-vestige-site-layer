#!/usr/bin/env node
// Mind R438. Read-only source verifier; execute: node mind/r438/verify.mjs from repo root.
// Uses built-in Node only. Does not access network, emails, WordPress, affiliate or analytics.
// Source-level assertions are NOT WCAG audits, real-browser tests, merchant validation or science peer review.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const root = new URL('./', import.meta.url);
const get = (name) => readFileSync(new URL(name,root),'utf8');
const article = get('THE_GORILLA_WAS_THERE_THE_WHOLE_TIME.md');
const a = get('ZEN12_A_TEXT_GUIDE.html');
const b = get('ZEN12_B_OPTIONAL_FILM_CONCEPT.html');
const captions = get('R438_42S_CAPTIONS.vtt');
const hub = get('MIND_ARCHIVE_WORDPRESS_SOURCE_ONLY.html');
const matrix = JSON.parse(get('CLAIM_SOURCE_PERMISSION_MATRIX.json'));
const conversion = get('CONVERSION_ACCEPTANCE_AND_CREATOR_FIT.md');
let pass = 0;
const check=(name,fn)=>{try{fn();pass++;}catch(e){console.error('FAIL '+name+': '+e.message);process.exitCode=1;}};
const absent=(text,needle)=>assert.equal(text.includes(needle),false);
for(const [k,el] of Object.entries({article,a,b,captions,hub,conversion}))check('nonempty '+k,()=>assert.ok(el.length>500));
check('status',()=>assert.equal(matrix.status,'DRAFT_HARD_HOLD'));
check('35 claims',()=>assert.equal(matrix.claims.length,35));
check('19 sources',()=>assert.equal(Object.keys(matrix.sources).length,19));
check('28 gates',()=>assert.equal(Object.keys(matrix.release_gates).length,28));
for(const [key,gate] of Object.entries(matrix.release_gates))check('gate '+key,()=>assert.equal(gate.status,'HOLD'));
for(const claim of matrix.claims)check('claim sources '+claim.id,()=>{assert.ok(claim.source_ids.length);for(const id of claim.source_ids)assert.ok(matrix.sources[id]);});
for(const source of ['https://doi.org/10.1068/p281059','https://doi.org/10.1068/i0386','https://doi.org/10.1111/1467-9280.00303','https://finalvestige.com/focus/','https://finalvestige.com/2026/11/02/change-blindness/'])check('article source '+source,()=>assert.ok(article.includes(source)));
check('long original article',()=>assert.ok(article.split(/\s+/).length>2000));
check('no imported copyright footage',()=>absent(article,'<iframe'));
check('article no merchant referral',()=>absent(article,'affiliates.inspire3.com/?'));
check('buyer exactly one disabled CTA A',()=>assert.equal((a.match(/<button type="button" disabled/g)||[]).length,1));
check('buyer exactly one disabled CTA B',()=>assert.equal((b.match(/<button type="button" disabled/g)||[]).length,1));
check('prospective disclosure A',()=>assert.ok(a.includes('may earn a commission at no additional cost to you')));
check('prospective disclosure B',()=>assert.ok(b.includes('may earn a commission at no additional cost to you')));
check('disclosure adjacent A',()=>assert.ok(a.indexOf('id="cta-disclosure"')<a.indexOf('<button type="button" disabled')));
check('disclosure adjacent B',()=>assert.ok(b.indexOf('id="cta-disclosure"')<b.indexOf('<button type="button" disabled')));
check('no merchant href A',()=>assert.ok(!/href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com)/i.test(a)));
check('no merchant href B',()=>assert.ok(!/href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com)/i.test(b)));
for(const [name,txt] of Object.entries({a,b,hub})) {
 check('no script '+name,()=>assert.ok(!/<script\b/i.test(txt)));
 check('no iframe '+name,()=>assert.ok(!/<iframe\b/i.test(txt)));
 check('no tracking '+name,()=>assert.ok(!/googletagmanager|gtag\(|fbq\(|analytics\.js/i.test(txt)));
 check('no email collection '+name,()=>assert.ok(!/<input\b/i.test(txt)));
 check('no autoplay '+name,()=>assert.ok(!/<(?:audio|video)\b[^>]*\sautoplay\b/i.test(txt)));
 check('page lang '+name,()=>assert.ok(txt.includes('<html lang="en">')));
 check('skip link '+name,()=>assert.ok(txt.includes('class="skip"')));
 check('reduced motion '+name,()=>assert.ok(txt.includes('prefers-reduced-motion')));
 check('responsive viewport '+name,()=>assert.ok(txt.includes('name="viewport"')));
}
check('optional media localized, buyer texts otherwise identical',()=>{
 const withoutMedia=b.replace(/<figure class="media"[\s\S]*?<\/figure><details class="transcript">[\s\S]*?<\/details>/,'');
 assert.equal(withoutMedia,a);
});
check('B original static poster',()=>assert.ok(b.includes('<svg ')&&b.includes('aria-labelledby="arttitle artdesc"')));
check('B transcript',()=>assert.ok(b.includes('<summary>Read the complete optional-film transcript (42 seconds)</summary>')));
check('VTT header',()=>assert.ok(captions.startsWith('WEBVTT\n')));
check('6 VTT cues',()=>assert.equal((captions.match(/-->/g)||[]).length,6));
check('VTT starts at zero',()=>assert.ok(captions.includes('00:00:00.000 --> 00:00:07.000')));
check('VTT ends 42 seconds',()=>assert.ok(captions.includes('00:00:35.000 --> 00:00:42.000')));
check('no active merchant CTA',()=>assert.ok(!/href=["'](?:https?:\/\/)?(?:www\.)?(?:zen12\.com|inspire3\.com)/i.test(b)));
check('hub existing free Focus',()=>assert.ok(hub.includes('https://finalvestige.com/focus/')));
check('hub historical archive',()=>assert.ok(hub.includes('puysegurs-animal-magnetism-files')));
check('hub separate tools stream',()=>assert.ok(hub.includes('Tools Under Review')));
check('hub no fictitious live Mind route',()=>assert.ok(hub.includes('Future editorial pillar (not published)')));
check('conversion no sale claim',()=>assert.ok(conversion.includes('NOT COMPUTABLE')&&conversion.includes('UNMATCHED')));
check('brand protection',()=>assert.ok(conversion.includes('homepage PR #49')));
console.log('Source assertions: '+pass+' checked, '+(process.exitCode===1?'FAILED':'PASS')+'.');
if(process.exitCode===1)process.exit(1);

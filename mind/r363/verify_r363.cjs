#!/usr/bin/env node
'use strict';
// Run from repository root: node mind/r363/verify_r363.cjs
// Independent static/preflight checks only. NOT browser, WCAG, sanitizer, checkout or WP tests.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const dir=__dirname;
const read=(x)=>fs.readFileSync(path.join(dir,x),'utf8');
const files={article:read('THE_HAND_THAT_BECAME_YOURS.md'),a:read('ZEN12_A_TEXT_GUIDE.html'),b:read('ZEN12_B_OPTIONAL_FILM_GUIDE.html'),hub:read('MIND_HUB_WP_REVIEW_ONLY.html'),vtt:read('ORIGINAL_FILM_42S.vtt'),matrix:JSON.parse(read('CLAIM_SOURCE_RELEASE_MATRIX.json')),plan:read('CONVERSION_ACCEPTANCE.md')};
let passes=0;const check=(name,f)=>{f();passes++;};
check('A semantic HTML',()=>assert.match(files.a,/<!doctype html>.*<html lang="en">/s));
check('B semantic HTML',()=>assert.match(files.b,/<!doctype html>.*<html lang="en">/s));
check('A noindex',()=>assert.match(files.a,/<meta name="robots" content="noindex,nofollow">/));
check('B noindex',()=>assert.match(files.b,/<meta name="robots" content="noindex,nofollow">/));
check('A no active merchant links',()=>assert.doesNotMatch(files.a,/<a[^>]+href="https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i));
check('B no active merchant links',()=>assert.doesNotMatch(files.b,/<a[^>]+href="https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i));
check('A truly disabled CTA',()=>assert.match(files.a,/<button type="button" disabled aria-disabled="true">/));
check('B truly disabled CTA',()=>assert.match(files.b,/<button type="button" disabled aria-disabled="true">/));
for(const key of ['a','b','hub']){check(key+' no scripts',()=>assert.doesNotMatch(files[key],/<script\b/i));check(key+' no forms',()=>assert.doesNotMatch(files[key],/<form\b/i));check(key+' no autoplay media',()=>assert.doesNotMatch(files[key],/<video[^>]+autoplay|<audio[^>]+autoplay/i));check(key+' no tracker',()=>assert.doesNotMatch(files[key],/<iframe\b|googletagmanager|facebook\.net\/tr/i));}
check('A disclosure adjacent button',()=>assert.match(files.a,/<p class="disclose">[\s\S]{0,550}<\/p><button type="button" disabled/));
check('B disclosure adjacent button',()=>assert.match(files.b,/<p class="disclose">[\s\S]{0,550}<\/p><button type="button" disabled/));
check('conditional language',()=>assert.ok(files.a.includes('If an approved earning link is added')));
check('A focus route',()=>assert.ok(files.a.includes('https://finalvestige.com/focus/')));
check('B focus route',()=>assert.ok(files.b.includes('https://finalvestige.com/focus/')));
check('A price qualified',()=>assert.ok(files.a.includes('not a checkout-verified price')));
check('A efficacy caution',()=>assert.ok(files.a.includes('not a Final Vestige finding')));
check('Film poster accessible',()=>assert.match(files.b,/<svg[^>]+role="img" aria-labelledby/));
check('Film title+desc',()=>assert.match(files.b,/<title id="posterTitle">[\s\S]+<desc id="posterDesc">/));
check('Film transcript readable',()=>assert.match(files.b,/<details><summary>Read the complete 42-second narration transcript/));
check('No embedded video falsely advertised',()=>assert.doesNotMatch(files.b,/<video\b|<source\b/));
check('Six caption cues',()=>assert.equal((files.vtt.match(/-->/g)||[]).length,6));
check('42-second last cue',()=>assert.ok(files.vtt.includes('00:00:42.000')));
check('Matrix has 16 source records',()=>assert.equal(files.matrix.source_count,16));
check('Matrix has 30 claim rows',()=>assert.equal(files.matrix.claim_count,30));
check('Matrix release all HOLD',()=>assert.ok(files.matrix.release_gates.every(g=>g.status==='HOLD')));
check('All claims cite known source ids',()=>{const s=new Set(files.matrix.sources.map(x=>x.id));for(const c of files.matrix.claims)assert.ok(c.source_ids.every(x=>s.has(x)),c.id)});
check('Article primary DOI',()=>assert.ok(files.article.includes('https://doi.org/10.1038/35784')));
check('Article separates historical from proof',()=>assert.ok(files.article.includes('does not independently establish')));
check('No personal use endorsement',()=>assert.doesNotMatch(files.a+files.b,/I tested Zen12|I used Zen12|we tried Zen12/i));
check('Plan paid-order boundary',()=>assert.ok(files.plan.includes('affiliate_click')&&files.plan.includes('merchant_paid_conversion_verified')));
check('Plan 7/30-day periods',()=>assert.ok(files.plan.includes('7-day/30-day')));
check('Plan owner limits',()=>assert.ok(files.plan.includes('homepage PR #49')&&files.plan.includes('Mind hub PR #172')));
check('Plan not actual purchase',()=>assert.ok(files.plan.includes('NOT COMPUTABLE')));
check('Article not medical promise',()=>assert.ok(files.article.includes('not a clinical recommendation')));
check('Hub review only',()=>assert.ok(files.hub.includes('not a WordPress CMS draft or deployed')));
check('B extra film does not alter buyer core',()=>{const start='<div class="eyebrow">Final Vestige Studios · Independent Tools Under Review</div>';assert.equal(files.a.slice(files.a.indexOf(start),files.a.indexOf('</main>')),files.b.slice(files.b.indexOf(start),files.b.indexOf('</main>')));});
const adversarial=[
['merchant link',x=>x.replace('<button type="button" disabled','<a href="https://zen12.com/buy">buy</a><button type="button" disabled'),x=>/<a[^>]+href="https?:\/\/(?:www\.)?zen12\.com/i.test(x)],
['enabled button',x=>x.replace('<button type="button" disabled','<button type="button"'),x=>!/<button type="button" disabled/.test(x)],
['new form',x=>x+'<form action="/lead"></form>',x=>/<form\b/.test(x)],
];
let rejected=0;
for(const [name,mutate,detector] of adversarial.slice(0,2)){assert.ok(detector(mutate(files.a)),name);rejected++;}
assert.ok(/<form\b/.test(files.a+'<form action="/lead"></form>'));rejected++;
assert.ok(/<script\b/i.test(files.a+'<script src="tracker.js"></script>'));rejected++;
assert.ok(/autoplay/.test(files.b+'<video autoplay></video>'));rejected++;
assert.equal(rejected,5);
console.log(JSON.stringify({passed:passes,adversarial_rejected:rejected,scope:'static-only; not native browser, no network or merchant test'},null,2));

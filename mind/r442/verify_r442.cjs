#!/usr/bin/env node
// R442 source-only regression verifier. Run: node mind/r442/verify_r442.cjs
// No network, dependencies, external events or CMS writes.
'use strict';
const assert = require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=__dirname;
const read=n=>fs.readFileSync(path.join(root,n),'utf8');
let checks=0;
const ok=(test,msg)=>{assert.ok(test,msg);checks++};
const equal=(a,b,msg)=>{assert.deepEqual(a,b,msg);checks++};
const a=read('ZEN12_A_TEXT_ONLY.html'),b=read('ZEN12_B_OPTIONAL_FILM_CONCEPT.html');
const hub=read('MIND_ARCHIVE_WORDPRESS_SOURCE_ONLY.html');
const article=read('THE_FREQUENCY_THAT_PROMISED_FOCUS.md');
const vtt=read('R442_CAPTIONS.vtt');
const matrix=JSON.parse(read('CLAIM_SOURCE_PERMISSION_MATRIX.json'));
const acceptance=read('OFFER_FUNNEL_CREATOR_REVENUE_ACCEPTANCE.md');
function normalized(s){return s.replace(/<title>[\s\S]*?<\/title>/,'<title>VARIANT</title>').replace(/<section class="panel" aria-label="Optional 42-second short-film storyboard and transcript">[\s\S]*?<\/section>/,'');}
equal(normalized(a),normalized(b),'Variant B must retain precisely the same substantive buyer text as A');
for(const [name,html] of [['A',a],['B',b],['hub',hub]]){
ok(/^<!doctype html>/i.test(html),name+': proper doctype');
ok(/<html lang="en">/.test(html),name+': lang declaration');
ok(/name="viewport"/.test(html),name+': responsive viewport');
ok(/name="robots" content="noindex,nofollow"/.test(html),name+': offline noindex');
ok(!/<script\b/i.test(html),name+': no scripts');
ok(!/<iframe\b/i.test(html),name+': no iframe');
ok(!/<form\b/i.test(html),name+': no duplicate signup');
ok(!/<video\b/i.test(html),name+': no fake playable film');
ok(!/autoplay/i.test(html.replace(/no auto-play/gi,'')),name+': no autoplay tag');
ok(!/https?:\/\/(?:zen12|inspire3|hypnosislive|brainwaveshots)\.com[^"\s]*"/i.test(html),name+': no merchant links or scripts');
ok(!/href="(?!https:\/\/finalvestige\.com\/|#)[^"]+"/i.test(html),name+': first-party links only');
ok(/focus\//.test(html),name+': free resource path');
ok(!/pixel|gtag\s*\(|analytics\.js|googletagmanager/i.test(html),name+': no tracking code');
ok(/:focus-visible/.test(html),name+': visible keyboard focus style');
ok(/max-width:650px/.test(html),name+': narrow viewport CSS');
}
for(const [name,html] of [['A',a],['B',b]]){
ok(/<button type="button" disabled aria-disabled="true">/.test(html),name+': truly disabled native CTA');
ok(/Final Vestige may earn a commission if you buy through that link/.test(html),name+': explicit prospective commission');
ok(html.indexOf('Final Vestige may earn a commission') < html.indexOf('<button type="button" disabled'),name+': disclosure before CTA');
ok(html.indexOf('Final Vestige may earn a commission') > html.indexOf('id="decision"'),name+': disclosure in decision unit');
ok(/The brand.s promise that twelve minutes can substitute for an hour/.test(html),name+': qualify unsupported claim');
ok(/not a demonstrated equivalence for Zen12/.test(html),name+': explicit substantiation boundary');
ok(!/we (personally )?(used|tested|love) Zen12/i.test(html),name+': no fabricated endorsement');
ok(!/\$\d|£\d|coupon code|limited time|guaranteed results/i.test(html),name+': no unverified price/urgency/results');
}
ok(b.includes('Optional 42-second'), 'B: film concept is optional');
ok(/<svg role="img"/.test(b),'B: accessible original poster');
ok(/<figcaption>/.test(b),'B: descriptive poster caption');
ok(/Full transcript/.test(b),'B: full transcript');
ok(!a.includes('Optional 42-second'),'A: no extra film element');
ok(vtt.startsWith('WEBVTT'),'VTT: valid header');
const cues=vtt.match(/\d\d:\d\d:\d\d\.\d{3} --> \d\d:\d\d:\d\d\.\d{3}/g)||[];
equal(cues.length,6,'VTT: six timed cues');
ok(cues[0].startsWith('00:00:00.000'),'VTT: zero start');
ok(cues[5].endsWith('00:00:42.000'),'VTT: 42-second end');
equal(matrix.sources.length,13,'matrix: 13 source records');
equal(matrix.claims.length,34,'matrix: 34 claim assessments');
equal(matrix.release_gates.length,28,'matrix: 28 gate records');
ok(matrix.release_gates.every(g=>g.status==='HOLD'),'matrix: every release gate must remain HOLD');
ok(matrix.assertions.affiliate_active===false,'matrix: no active affiliate');
ok(matrix.assertions.merchant_href_count_allowed===0,'matrix: no active seller links');
ok(matrix.assertions.verified_paid_sales===null,'matrix: no invented paid sales');
ok(matrix.assertions.revenue_per_1000_sessions===null,'matrix: no invented net RPM');
ok(matrix.claims.some(c=>c.classification==='unsupported-product-efficacy'),'matrix: unsupported claims explicitly categorized');
ok(matrix.claims.some(c=>c.classification==='independently-supported-context'),'matrix: independent source classification');
for(const id of ['s1','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11','s12','s13']){
ok(matrix.sources.some(s=>s.id===id),'matrix source '+id);
}
for(const marker of ['01 · Perception & Attention','02 · History of Suggestion','03 · Practice & Reflection','04 · Tools Under Review'])ok(hub.includes(marker),'hub: '+marker);
ok(hub.includes('canonical Mind PR #172'),'hub protects original Mind PR');
ok(article.includes('Five questions before spending'),'investigation has practical objections');
ok(article.includes('five studies'),'article retains 2023 positive evidence');
ok(article.includes('eight contradicted'),'article retains 2023 contradictory evidence');
ok(article.includes('vigilance decrement'),'article retains unfavorable 2025 finding');
ok(article.includes('Puységur'),'article connects historical archive');
ok(acceptance.includes('net_revenue_per_1000'),'acceptance: actual revenue KPI');
ok(acceptance.includes('NOT COMPUTABLE'),'acceptance: correct missing-data state');
ok(acceptance.includes('HARD HOLD'),'acceptance: release blocked');
console.log('R442 PASS '+checks+'/'+checks+' static assertions, source only. Native Node run is not hosted browser/merchant proof.');

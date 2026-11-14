#!/usr/bin/env node
// Mind R381 source-only verifier. Run with: node mind/r381/verify.mjs
// Static checks do not replace real-browser WCAG, CMS, partner checkout or settlement tests.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const read = f => fs.readFileSync(path.join(here,f),'utf8');
const A = read('ZEN12_A_TEXT_BUYER_GUIDE.html');
const B = read('ZEN12_B_OPTIONAL_FILM_CONCEPT.html');
const hub = read('MIND_HUB_WP_REVIEW_ONLY.html');
const poster = read('R381_ORIGINAL_POSTER.svg');
const vtt = read('R381_ORIGINAL_CAPTIONS.vtt');
const article = read('THE_DOORWAY_THAT_STOLE_THE_REASON.md');
const dossier = read('CONVERSION_DECISION_AND_HANDOFF.md');
const matrix = JSON.parse(read('CLAIM_SOURCE_AUTHORIZATION_MATRIX.json'));
let passed = 0;
const assert=(value,msg)=>{if(!value)throw Error('FAIL: '+msg); passed++;};
const nativeDisabled = s => /<button\b(?=[^>]*\sdisabled(?:\s|>|=))[^>]*>Zen12 offer link unavailable<\/button>/i.test(s);
const noMerchantAnchors = s=> !/href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)(?:\/|["'])/i.test(s);
const noScripts = s=> !/<\s*(?:script|iframe|form|video|audio)\b/i.test(s) && !/\bon\w+\s*=/i.test(s) && !/javascript:/i.test(s);
const hasDisclosure=s=> s.includes('If you purchase through a qualifying link, Final Vestige may earn a commission at no additional cost to you.');
const checkPage=(s,id)=>{
  assert(/<!doctype html>/i.test(s),id+' document type');
  assert(/<html lang="en">/i.test(s),id+' language');
  assert(/<meta name="robots" content="noindex,nofollow,noarchive">/i.test(s),id+' unpublished robots');
  assert(/<main id="main"/.test(s)&&/<article class="copy">/.test(s),id+' semantic content');
  assert(/Skip to content/.test(s),id+' skip link');
  assert(/@media\(max-width:790px\)/.test(s),id+' responsive CSS intent');
  assert(/prefers-reduced-motion:reduce/.test(s),id+' reduced motion intent');
  assert(nativeDisabled(s),id+' native disabled buying control');
  assert(hasDisclosure(s),id+' adjacent commission disclaimer');
  assert(s.indexOf('class="disclosure"')>0&&s.indexOf('class="disclosure"')<s.indexOf('class="disabled"'),id+' disclaimer preceding control');
  assert(noMerchantAnchors(s),id+' withholding ALL merchant outbound anchors');
  assert(noScripts(s),id+' no scripts forms embeds or unexpected event handlers');
  assert(!/(autoplay|\btracking-pixel\b)/i.test(s.replace(/no autoplay|no tracking-pixel/gi,'')),id+' no active autoplay/tracker');
  assert(s.includes('https://finalvestige.com/focus/'),id+' existing Focus path');
  assert(s.includes('pubmed.ncbi.nlm.nih.gov/17128613'),id+' exact experimental primary record');
};
checkPage(A,'A');checkPage(B,'B');
const copy=s=>{let t=s.slice(s.indexOf('<section id="story">'),s.indexOf('</article>'));return t.replace(/<section class="film"[\s\S]*?<\/section>/,'');};
assert(copy(A)===copy(B),'only optional film differs in substantive buyer copy');
assert(!A.includes('class="film"')&&B.includes('class="film"'),'film is B-only');
assert(B.includes('R381_ORIGINAL_POSTER.svg')&&B.includes('R381_ORIGINAL_CAPTIONS.vtt'),'B names the accessible original media');
assert(B.includes('not')&&B.includes('encoded'),'B honestly labels film as concept');
assert(!/<script|<foreignObject|onload\s*=|xlink:href|https?:\/\//i.test(poster),'original SVG is inert and contains no external fetch');
assert(/<title id="title">/.test(poster)&&/<desc id="desc">/.test(poster),'SVG accessible title and description');
assert(vtt.startsWith('WEBVTT\n'),'valid VTT header');
const timings=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g)];
assert(timings.length===6,'six exact caption cues');
const sec=(h,m,s,ms)=>Number(h)*3600+Number(m)*60+Number(s)+Number(ms)/1000;
const spans=timings.map(m=>[sec(...m.slice(1,5)),sec(...m.slice(5,9))]);
assert(spans.every(([a,b],i)=>a===i*7&&b===(i+1)*7),'captions contiguous seven-second cues');
assert(spans[5][1]===42,'complete 42-second caption coverage');
assert(!/<script|<form|<iframe/i.test(hub)&&hub.includes('Perception &amp; attention')&&hub.includes('History of suggestion')&&hub.includes('Practice &amp; reflection')&&hub.includes('Tools under review'),'four-stream inert hub');
assert(hub.includes('noindex,nofollow,noarchive'),'hub review-only');
assert(article.split(/\s+/).length>1700,'deep investigation length');
for(const pub of ['17128613','21563019','26556012','25412111'])assert(article.includes(pub),'article includes study '+pub);
assert(article.includes('https://finalvestige.com/focus/'),'free resource in article');
assert(article.includes('Puységur')&&article.includes('not')&&article.includes('proof'),'historical bridge and limitation');
assert(matrix.claims.length>=30,'30+ source/claim dispositions');
assert(Object.keys(matrix.sources).length>=12,'multiple distinct reference URLs');
assert(matrix.claims.every(x=>x.id&&x.source&&x.status&&x.disposition),'every claim audited');
assert(matrix.commercial_release_gates.length>=36&&matrix.commercial_release_gates.every(x=>x.result==='HOLD_NOT_PROVEN'),'all 36 release gates held');
assert(dossier.includes('NOT COMPUTABLE')&&dossier.includes('verified')&&dossier.includes('merchant_confirmed_purchase'),'non-click paid KPI policy documented');
assert(dossier.includes('A/B')&&dossier.includes('Grok')&&dossier.includes('Jetpack'),'experiment and lane ownership documented');

// Mutation checks: the checker must fail closed for dangerous modifications.
const mut=[
  ['enable button',A.replace('type="button" disabled','type="button"')],
  ['insert merchant affiliate anchor',A.replace('</article>','<a href="https://zen12.com/">BUY</a></article>')],
  ['insert seller root anchor',A.replace('</article>','<a href="https://inspire3.com/">BUY</a></article>')],
  ['remove disclosure',A.replace('If you purchase through a qualifying link, Final Vestige may earn a commission at no additional cost to you.','')],
  ['add form',A.replace('</article>','<form action="/subscribe"></form></article>')],
  ['add JS',A.replace('</article>','<script>alert(1)</script></article>')],
  ['add iframe',A.replace('</article>','<iframe src="https://example.com"></iframe></article>')],
  ['replace native disabled with aria-disabled',A.replace('type="button" disabled','type="button" aria-disabled="true"')],
  ['add handler',A.replace('</article>','<p onclick="track()">event</p></article>')],
  ['strip Focus link',A.replaceAll('https://finalvestige.com/focus/','#disabled')]
];
const checks=s=> nativeDisabled(s)&&noMerchantAnchors(s)&&hasDisclosure(s)&&noScripts(s)&&s.includes('https://finalvestige.com/focus/');
for(const [name,s] of mut)assert(!checks(s),'mutation caught: '+name);
console.log('PASS Mind R381 static checks: '+passed+' assertions, including '+mut.length+' unsafe mutations rejected.');
console.log('NOT TESTED: native-browser WCAG, true playback, WordPress sanitizer, Jetpack lead, merchant approval/checkout, paid commission, settlement, live release.');

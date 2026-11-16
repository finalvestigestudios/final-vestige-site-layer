#!/usr/bin/env node
/* FV Mind R418 source-only release preflight. No network, dependencies, storage, or production calls. */
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import assert from 'node:assert/strict';
const dir=path.dirname(fileURLToPath(import.meta.url));
const read=n=>readFileSync(path.join(dir,n),'utf8');
let checks=0;function check(ok,msg){checks++;assert.ok(ok,msg)}
const a=read('ZEN12_A_TEXT_ONLY.html'),b=read('ZEN12_B_OPTIONAL_FILM.html');
const hub=read('MIND_HUB_SOURCE_ONLY.html'),svg=read('zen12-evidence-poster.svg');
const vtt=read('zen12-42s-captions.vtt'),claims=JSON.parse(read('CLAIM_SOURCE_AUTHORIZATION_MATRIX.json'));
const article=read('TEN_MINUTES_NOT_A_CHECKOUT.md'),memo=read('CONVERSION_ACCEPTANCE_AND_CREATOR_FIT.md');
const stripped=s=>s.replace(/Unpublished Variant [AB]/g,'Unpublished Variant').replace(/<section class="film"[^]*?<\/section>/,'');
function safe(s){return !/<script\b|<form\b|\bonclick\s*=|<iframe\b|\bautoplay\b|window\.location|localStorage|<audio\b|<video\b/i.test(s)}
function noMerchantAnchor(s){return !/<a\b[^>]*href\s*=\s*["'][^"']*(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(s)}
for(const [name,s] of [['A',a],['B',b],['Hub',hub]]){
 check(s.includes('<!doctype html>'),name+' full document');
 check(s.includes('name="viewport"'),name+' mobile viewport');
 check(s.includes('name="robots" content="noindex,nofollow"'),name+' unpublished noindex');
 check(s.includes('href="#content"'),name+' skip link');
 check(s.includes('prefers-reduced-motion'),name+' reduced motion');
 check(s.includes(':focus-visible'),name+' keyboard visible');
 check(safe(s),name+' no active scripts/forms/media');
 check(noMerchantAnchor(s),name+' no merchant outbound anchors');
}
for(const s of [a,b]){
 check(s.includes('disabled type="button"'), 'merchant CTA native disabled');
 check(s.includes('Affiliate disclosure:'), 'adjacent disclosure present');
 check(s.indexOf('Affiliate disclosure:') < s.indexOf('Offer link unavailable'), 'disclosure before disabled CTA');
 check(s.includes('https://finalvestige.com/focus/'), 'existing Focus funnel only');
 check(!/\$[0-9]+(?:\.[0-9]+)?/.test(s), 'no stale price');
 check(!/utm_|affiliate_click|pixel|analytics\./i.test(s), 'no embedded attribution script');
}
check(stripped(a)===stripped(b),'identical substantive A/B guide after removing optional storyboard');
check(b.includes('aria-labelledby="filmhead"'),'B film heading');
check(b.includes('<details>')&&b.includes('<summary>'),'B keyboard accessible optional open');
check(b.includes('complete narrated storyboard'),'B described accurately');
check(b.includes('No video file has been encoded'),'B not falsely described as playable');
check(svg.includes('<title')&&svg.includes('<desc'),'accessible SVG title/desc');
check(!/<script|<foreignObject|(?:href|url)\s*=\s*["']https?:/i.test(svg),'no active or remote SVG');
check(vtt.startsWith('WEBVTT\n'),'VTT header');
const cues=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.\d{3} --> (\d\d):(\d\d):(\d\d)\.\d{3}/g)].map(m=>[+m[1]*3600 + +m[2]*60 + +m[3],+m[4]*3600 + +m[5]*60 + +m[6]]);
check(cues.length===6,'six VTT cues');
check(cues[0]?.[0]===0&&cues.at(-1)?.[1]===42,'zero through 42s');
check(cues.every((c,i)=>c[0]===i*7&&c[1]===(i+1)*7),'continuous seven-second captions');
check(claims.claims.length>=30,'detailed claim ledger');
check(claims.commercial_release_gates.length>=25,'complete fail-closed release gate list');
check(claims.commercial_release_gates.every(x=>x.status==='HOLD'&&x.proof===null),'all commercial gates held');
check(claims.authorization.status==='UNVERIFIED','no invented merchant authorization');
check(claims.analytics.missing_not_zero===true,'missing not zero in paid telemetry');
check(Object.keys(claims.sources).length>=15,'source links');
check(article.length>14000,'substantive original manuscript');
check(article.includes('Corrigendum')&&article.includes('Puységur'),'research corrections and historical bridge');
check(memo.includes('NOT COMPUTABLE')&&memo.includes('actual_asset_id'),'conversion denominator held and creator IDs not invented');
const unsafe=[
  a.replace('disabled type="button"','type="button"'),
  a.replace('Affiliate disclosure:','Disclosure omitted:'),
  a.replace('https://finalvestige.com/focus/','https://zen12.com/order'),
  a.replace('</main>','<script>alert(1)</script></main>'),
  a.replace('name="robots" content="noindex,nofollow"','name="robots" content="index,follow"'),
  b.replace('No video file has been encoded','Video is available to play')
];
check(!unsafe[0].includes('disabled type="button"'),'mutation disabled toggle detected');
check(!unsafe[1].includes('Affiliate disclosure:'),'mutation disclosure removed detected');
check(!noMerchantAnchor(unsafe[2]),'mutation checkout link detected');
check(!safe(unsafe[3]),'mutation active script detected');
check(!unsafe[4].includes('name="robots" content="noindex,nofollow"'),'mutation indexable detected');
check(!unsafe[5].includes('No video file has been encoded'),'mutation fake playback detected');
console.log('FV R418 native static preflight PASS: '+checks+' assertions; 6/6 deliberately unsafe changes detected. This does not constitute browser, WordPress, checkout or real-video QA.');
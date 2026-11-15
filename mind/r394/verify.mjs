// Node 20+; run: node mind/r394/verify.mjs  (repo root; no external dependencies)
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
const dir=path.dirname(new URL(import.meta.url).pathname);
const get=p=>fs.readFileSync(path.join(dir,p),'utf8');
const a=get('ZEN12_TEXT_A.html'), b=get('ZEN12_FILM_B.html');
const hub=get('MIND_HUB_DRAFT.html'), poster=get('ATTENTION_BLINK_POSTER.svg'), captions=get('ATTENTIONAL_BLINK_42S.vtt');
const article=get('THE_SECOND_NUMBER.md'), acceptance=get('CONVERSION_ACCEPTANCE.md');
const claims=JSON.parse(get('CLAIM_SOURCE_MATRIX.json'));
const middle=x=>x.split('<!-- CONTENT_START -->')[1]?.split('<!-- CONTENT_END -->')[0];
let n=0;const pass=(condition,message)=>{assert.ok(condition,message);n++;};
pass(middle(a)===middle(b),'A/B buyer copy parity');
for(const [name,html] of [['A',a],['B',b],['hub',hub]]) {
 pass(html.includes('lang="en"'),name+' lang');
 pass(html.includes('name="viewport"'),name+' viewport');
 pass(!/<script\b/i.test(html),name+' no script');
 pass(!/<form\b/i.test(html),name+' no new form');
 pass(!/\bautoplay\b\s*(?:=|>)/i.test(html),name+' no autoplay attribute');
 pass(html.includes('prefers-reduced-motion'),name+' reduced motion');
 pass(html.includes('noindex,nofollow'),name+' no indexing');
}
for(const html of [a,b]){
 pass(/<button[^>]+\bdisabled\b/.test(html),'native disabled CTA');
 pass(html.indexOf('Affiliate disclosure:')<html.indexOf('View Zen12 at the seller'),'disclosure precedes CTA');
 pass(html.includes('seller descriptions'),'seller framing');
 pass(!/href="https:\/\/affiliates\.inspire3\.com\/[^"]+"/.test(html),'no merchant tracking');
 pass(!/href="https:\/\/zen12\.com\/secret\/"/.test(html),'no promo urgency');
 pass(html.includes('https://finalvestige.com/focus/'),'single free route');
}
pass(b.includes('ATTENTION_BLINK_POSTER.svg')&&b.includes('ATTENTIONAL_BLINK_42S.vtt'),'B storyboard assets');
pass(b.includes('not a playable video'),'truthful status');
pass(poster.includes('xmlns="http://www.w3.org/2000/svg"'),'standalone SVG');
pass(poster.includes('aria-labelledby'),'SVG accessible label');
pass(captions.startsWith('WEBVTT'),'VTT syntax marker');
pass((captions.match(/-->/g)||[]).length===6,'VTT has 6 cues');
pass(article.includes('17 retreat participants')||article.includes('Seventeen experienced practitioners'),'article cohort caveat');
pass(article.includes('self-selected'),'self selection');
pass(article.includes('No commercial link'),'commercial hold');
pass(claims.release==='HARD_HOLD','matrix hard hold');
pass(Object.values(claims.release_gates).every(x=>x===false),'all release gates unverified');
pass(claims.claims.length>=20,'claim coverage');
pass(acceptance.includes('NOT COMPUTABLE'),'revenue epistemics');
pass(acceptance.includes('Grok retains creator/publication role'),'role isolation');
console.log('PASS '+n+'/'+n+' offline static assertions; NOT browser, CMS, video, email or merchant validation');

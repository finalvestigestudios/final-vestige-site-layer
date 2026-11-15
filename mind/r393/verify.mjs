#!/usr/bin/env node
// Offline, dependency-free QA on source-only R393 files. Run: node mind/r393/verify.mjs
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
const dir=path.dirname(new URL(import.meta.url).pathname);
const read=(name)=>fs.readFileSync(path.join(dir,name),'utf8');
const A=read('ZEN12_A_BUYER_GUIDE.html'),B=read('ZEN12_B_OPTIONAL_FILM_GUIDE.html');
const art=read('TWELVE_MINUTE_PROMISE_EVIDENCE_REVIEW.md'),hub=read('MIND_HUB_WORDPRESS_FRAGMENT.html');
const matrix=JSON.parse(read('CLAIMS_RIGHTS_RELEASE_MATRIX.json'));
const vtt=read('R393_CAPTIONS.vtt'),poster=read('R393_POSTER.svg');
const dossier=read('CONVERSION_PROOF_CREATOR_ROUTE_AND_QA.md');
let n=0;function check(test,reason){assert.ok(test,reason);n++}
function body(s){return s.match(/<body>([\s\S]*)<\/body>/)?.[1]||''}
function canonical(s){return body(s).replace(/<details class="film"[\s\S]*?<\/details>/,'').trim()}
function tags(s,name){return (s.match(new RegExp('<'+name+'\\b','g'))||[]).length}
function anchors(s){return [...s.matchAll(/<a\b[^>]*href="([^"]+)"/g)].map(x=>x[1])}
function cues(v){return [...v.matchAll(/(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)\n([\s\S]*?)(?=\n\n|$)/g)]}
const toSeconds=t=>{const [h,m,s]=t.split(':');return +h*3600+ +m*60+ +s};
for(const [label,s] of [['A',A],['B',B]]){
check(s.startsWith('<!doctype html>'),label+' valid HTML start');
check(s.includes('lang="en"'),label+' language');
check(s.includes('name="viewport"'),label+' responsive');
check(s.includes('noindex,nofollow'),label+' private draft hint');
check(tags(s,'h1')===1,label+' single primary heading');
check(s.includes('prefers-reduced-motion:reduce'),label+' reduced-motion handling');
check(s.includes('a:focus-visible'),label+' keyboard focus style');
check(s.includes('@media(max-width:390px)'),label+' narrow mobile fallback');
check(tags(s,'form')===0,label+' no extra subscription form');
check(tags(s,'script')===0,label+' no injected tracking JS');
check(tags(s,'iframe')===0,label+' no external embed');
check(!/<(?:video|audio)\b[^>]*autoplay/i.test(s),label+' no autoplay');
check(s.includes('data-cta-id="mind_r393_focus_fieldbook"'),label+' noncommercial CTA key');
check(anchors(s).includes('https://finalvestige.com/focus/'),label+' existing Fieldbook CTA');
check(s.includes('Affiliate disclosure:'),label+' plain conspicuous disclosure');
check(s.indexOf('Affiliate disclosure:')<s.indexOf('<button type="button" disabled'),label+' disclosure before seller control');
check(s.includes('<button type="button" disabled aria-disabled="true">'),label+' natively disabled merchant control');
check(!anchors(s).some(h=>/inspire3\.com|zen12\.com|affiliates\./i.test(h)),label+' no active seller URL');
check(!/href="[^"]*(?:ref=|aff_id=|affiliate=|utm_)/i.test(s),label+' no invented affiliate link');
check(!/<a\b[^>]*target="_blank"(?![^>]*rel=)/i.test(s),label+' no external target without rel');
}
check(canonical(A)===canonical(B),'identical substantive A/B buyer DOM');
check(tags(A,'details')===0,'A no film');
check(tags(B,'details')===1,'B one optional film details');
check(B.includes('not yet a playable video'),'B does not claim playable media');
check(B.includes('<summary>'),'B user initiated storyboard view');
check(B.includes('src="./R393_POSTER.svg"'),'B original local poster');
check(B.includes('href="./R393_CAPTIONS.vtt"'),'B captions linked');
check(B.includes('Full transcript:'),'B visible transcript');
check(poster.includes('<title id="t">')&&poster.includes('<desc id="d">'),'SVG accessible name');
check(!/<(?:image|script|foreignObject)\\b/i.test(poster)&&!/(?:href|src)="https?:/i.test(poster),'SVG no remote asset requests');
check(vtt.startsWith('WEBVTT'),'WebVTT file header');
const c=cues(vtt);check(c.length===6,'six caption cues');
check(c[0][1]==='00:00:00.000'&&c.at(-1)[2]==='00:00:42.000','42 second full coverage');
for(let i=0;i<c.length;i++){check(toSeconds(c[i][2])>toSeconds(c[i][1]),'cue duration positive '+i);if(i)check(c[i-1][2]===c[i][1],'continuous cues '+i)}
check(art.split(/\s+/).length>=2500,'substantive original 2500+ word article');
check(art.includes('19 studies')&&art.includes('1,654 participants'),'review scope qualified');
check(/five/i.test(art)&&/eight/i.test(art)&&/one/i.test(art),'binaural review mixed counts in narrative');
check(art.includes('2020 adverse-event review'),'safety consideration');
check(hub.includes('class="fvmind-r393"'),'WordPress CSS scoped');
for(const q of ['Perception &amp; Attention','History of Suggestion','Practice &amp; Reflection','Tools Under Review'])check(hub.includes(q),'4-stream hub '+q);
check(!/<(?:script|form|iframe)\b/i.test(hub),'hub adds no scripts/forms/embed');
check(hub.includes('https://finalvestige.com/focus/'),'hub keeps only existing funnel');
check(matrix.claims.length>=35,'matrix claim coverage');
check(matrix.release_requirements.length>=30,'release gate coverage');
check(matrix.release_requirements.every(g=>g.status==='HOLD'),'all activation gates closed');
check(matrix.merchant_affiliate_url===null,'no invented merchant URL');
check(matrix.commercial_activation===false,'commercial off');
check(matrix.claims.some(x=>x.classification==='ACCESS_FAILURE'),'Puységur access marked');
check(matrix.claims.some(x=>x.classification==='INVALID_SALES_INFERENCE'),'outbound click not sale');
check(dossier.includes('N/A')&&dossier.includes('refund'),'net revenue missing properly');
check(dossier.includes('asset_id')&&dossier.includes('utm_content'),'real asset gating');
check(dossier.includes('Dispatch Issue #174'),'dispatch ownership preserved');
check(dossier.includes('Issue #820')===false || dossier.includes('Mind'),'cross-lane coordination labels');
console.log('R393 exact-file offline Node QA: '+n+'/'+n+' assertions PASS.');

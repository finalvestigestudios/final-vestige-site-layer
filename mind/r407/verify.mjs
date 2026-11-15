#!/usr/bin/env node
// Offline source-only static audit. No network, CMS, account or merchant interactions.
// Run: node mind/r407/verify.mjs ; Node >=18.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
const root=new URL('.',import.meta.url);
const read=async n=>readFile(new URL(n,root),'utf8');
const [a,b,hub,svg,vtt,matrixRaw,guide,acceptance]=await Promise.all([
 'ZEN12_A_TEXT.html','ZEN12_B_OPTIONAL_FILM.html','MIND_HUB_SOURCE_DRAFT.html',
 'poster.svg','captions.vtt','CLAIMS_RIGHTS_AND_SOURCE_MATRIX.json',
 'BEFORE_YOU_PAY_FOR_FOCUS.md','CONVERSION_RELEASE_AND_GROK_CROSSWALK.md'
].map(read));
let checks=0; const ok=(v,msg)=>{assert.ok(v,msg);checks++};
const reject=x=>/\<script\b|on(?:load|error|click|mouseover)\s*=|<iframe\b|<form\b|autoplay\b|href\s*=\s*["'](?:javascript:|data:)/i.test(x);
const article=s=>(s.match(/<article>([\s\S]*?)<\/article>/)||[])[1];
const film=s=>(s.match(/<details class="film"[\s\S]*?<\/details>/)||[])[0];
const removeFilm=s=>s.replace(/<details class="film"[\s\S]*?<\/details>/,'');
const validate=s=>{
 ok(s.includes('<html lang="en">'),'language');
 ok(s.includes('name="viewport"'),'viewport');
 ok(s.includes('noindex,nofollow'),'nonindexed source prototype');
 ok(!reject(s),'forbidden script/event/form/autoplay/unsafe scheme');
 ok(/<button\b[^>]*\sdisabled\b/.test(s),'native disabled purchase control');
 ok(s.includes('Affiliate disclosure for a future authorized link:'),'adjacent earning disclosure');
 const section=(s.match(/<section class="offer"[\s\S]*?<\/section>/)||[])[0]||'';
 ok(section.includes('If you purchase through this link, Final Vestige may earn a commission'),'disclosure in offer block');
 ok(!/<a\b[^>]*href=/i.test(section),'no outgoing merchant CTA');
 ok(s.includes('https://finalvestige.com/focus/'),'existing Focus funnel');
 ok(!/\butm_source=|ref=affiliate|aff_id=|affiliate_click=/i.test(s),'no invented attribution link');
};
validate(a);validate(b);
ok(!!article(a)&&!!article(b),'both buyer articles');
ok(removeFilm(article(b))===article(a),'substantive buyer-copy parity');
ok(!!film(b)&&!film(a),'only B contains optional film');
ok(b.includes('No video starts automatically'),'video is openly nonplayable concept');
ok(b.includes('figcaption'),'image caption');
ok(b.includes('alt="A calm editorial'),'original alt text');
ok(svg.startsWith('<svg xmlns="http://www.w3.org/2000/svg"'),'inline original SVG');
ok(!reject(svg)&&!/<image\b|<foreignObject\b|xlink:href|https?:\/\//i.test(svg.replace('http://www.w3.org/2000/svg','')),'SVG no external asset or active content');
ok(svg.length<2048,'lightweight poster');
const match=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d\d\d) --> (\d\d):(\d\d):(\d\d)\.(\d\d\d)/g)];
const sec=z=>Number(z[1])*3600+Number(z[2])*60+Number(z[3])+Number(z[4])/1000;
const cues=match.map(m=>({start:sec(m.slice(1,5)),end:sec(m.slice(5,9))}));
ok(cues.length===6,'six caption cues');
ok(cues[0].start===0&&cues.at(-1).end===42,'42s exact storyboard');
ok(cues.every((c,i)=>c.end>c.start&&(i===0||cues[i-1].end===c.start)),'contiguous monotonic captions');
const transcript=(film(b).match(/<h3>Proposed 42-second narration and transcript<\/h3><p>([^<]+)<\/p>/)||[])[1];
const normalized=s=>s.replace(/\s+/g,' ').trim();
const cueText=vtt.split(/\n\s*\n/).slice(1).map(p=>p.replace(/^.*?-->([^\n]+)\n/,'').trim()).join(' ');
ok(normalized(transcript)===normalized(cueText),'VTT matches visible transcript');
const m=JSON.parse(matrixRaw);
ok(m.claims.length>=28,'full claim matrix');
ok(Object.keys(m.source_definitions).length>=18,'18+ actual source references');
ok(m.release_gates.length>=26&&m.release_gates.every(g=>g.status==='HOLD'&&g.proof===null),'all commerce gates closed');
ok(m.claims.every(c=>c.sources.length&&c.sources.every(s=>m.source_definitions[s])),'every claim points to a real source key');
ok(m.claims.some(c=>c.id==='B03'&&c.status==='seller_modality_only'),'isochronic != binaural caution');
ok(m.claims.some(c=>c.id==='Z07'&&c.status.startsWith('unsubstantiated')),'zen12 efficacy gated');
ok(m.claims.some(c=>c.id==='H02'&&c.status==='price_snapshot_only'),'Total Focus price drift gated');
for(const t of ['Perception &amp; attention','History of suggestion','Practice &amp; reflection','Tools under review'])ok(hub.includes(t),'hub stream '+t);
ok(!reject(hub)&&hub.includes('noindex,nofollow'),'no script/form in hub');
ok(hub.includes('https://finalvestige.com/2026/11/02/change-blindness/')&&hub.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'),'existing valid editorial destinations');
ok(guide.includes('## Sources and scope')&&guide.includes('https://pubmed.ncbi.nlm.nih.gov/17488185/'),'independent source trail');
ok(acceptance.includes('NOT COMPUTABLE')&&acceptance.includes('realized paid net revenue'),'financial outcomes not faked');
// Mutation safety checks: prove the validator rejects unsafe edits.
for(const unsafe of [
 a.replace(' type="button" disabled',' type="button"'),
 a.replace('disabled aria-describedby','aria-describedby'),
 a.replace('If you purchase through this link, Final Vestige may earn a commission','No disclosure needed'),
 a.replace('<main>','<script>alert(1)</script><main>'),
 a.replace('<main>','<form action="/subscribe"><input type="email"></form><main>'),
 a.replace('<main>','<iframe src="https://seller.example"></iframe><main>'),
 a.replace('<main>','<img src=x onerror="alert(1)"><main>')
]){let caught=false;try{const sec=(unsafe.match(/<section class="offer"[\s\S]*?<\/section>/)||[])[0]||'';if(reject(unsafe)||!/<button\b[^>]*\sdisabled\b/.test(unsafe)||!sec.includes('If you purchase through this link, Final Vestige may earn a commission'))throw Error('unsafe');}catch{caught=true;}ok(caught,'unsafe mutation rejected');}
console.log('R407 offline source audit PASS: '+checks+' checks; no production or merchant test run.');

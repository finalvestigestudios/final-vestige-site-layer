#!/usr/bin/env node
'use strict';
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=__dirname;
const read=name=>fs.readFileSync(path.join(root,name),'utf8');
const files={
 article:read('THE-HAND-THAT-WASNT-YOURS-UNPUBLISHED.md'),
 matrix:read('CLAIM-SOURCE-OFFER-AUTHORIZATION-MATRIX.json'),
 a:read('ZEN12-A-TEXT-BUYER-REVIEW.html'),
 b:read('ZEN12-B-OPTIONAL-42S-FILM-REVIEW.html'),
 hub:read('MIND-FOUR-STREAM-WORDPRESS-REVIEW.html'),
 captions:read('ORIGINAL-42S-CAPTIONS.vtt'),
 dossier:read('CONVERSION-ATTRIBUTION-RELEASE-ACCEPTANCE.md')
};
function safeHTML(s){
 assert.match(s,/<!doctype html>/i);
 assert.match(s,/<html lang="en">/);
 assert.match(s,/<meta name="viewport"/);
 assert.match(s,/prefers-reduced-motion/);
 assert.match(s,/focus-visible/);
 assert.doesNotMatch(s,/<script\b|<iframe\b|<form\b|<input\b|<video\b|<audio\b|javascript:|data:text\/html|onerror=|onclick=|<img[^>]+src="https?:/i);
 const links=[...s.matchAll(/href="([^"]+)"/g)].map(m=>m[1]);
 assert(links.every(h=>/^https:\/\/(?:finalvestige\.com|doi\.org|www\.ftc\.gov)\//.test(h)), 'Unsafe, affiliate or unapproved anchor URL');
}
function commercialSafe(s){
 assert.match(s,/<button type="button" disabled aria-disabled="true">/);
 const b=s.indexOf('<button type="button" disabled');
 const disclosure=s.indexOf('may earn a commission',b);
 assert(b>=0 && disclosure>b && disclosure-b<650,'Disclosure missing or not near inactive CTA');
 assert.match(s,/No earning link is active here/);
 assert.match(s,/https:\/\/finalvestige\.com\/focus\//);
 assert.doesNotMatch(s,/href="https:\/\/(?:zen12|hypnosislive|brainwaveshots|affiliates\.inspire3)/);
}
function coreOf(html){return html.replace(/<figure class="media"[\s\S]*?<\/figure>/,'')
.replace(/— A review only/g,'— X review only').replace(/— B review only/g,'— X review only')
.replace(/Text control/g,'VARIANT').replace(/Optional film hypothesis/g,'VARIANT');}
function checks(f){
 for(const n of ['a','b','hub'])safeHTML(f[n]);
 for(const n of ['a','b'])commercialSafe(f[n]);
 assert.equal(coreOf(f.a),coreOf(f.b),'A/B must be identical outside optional film & labels');
 assert.match(f.b,/42-second/);
 assert.match(f.b,/<svg[^>]+viewBox=/);
 assert.match(f.b,/<details>/);
 assert.match(f.b,/00:35–00:42/);
 assert.doesNotMatch(f.a,/<figure class="media"/);
 for(const token of ['Perception & Attention','History of Suggestion','Practice & Reflection','Tools Under Review','/focus/','Puységur','rubber-hand']) assert(f.hub.toLowerCase().includes(token.toLowerCase()),'Missing hub stream '+token);
 for(const token of ['Botvinick','Rohde','Lush','Puységur','2021','suggestion']) assert(f.article.toLowerCase().includes(token.toLowerCase()),'Missing research '+token);
 assert.match(f.captions,/^WEBVTT/);
 assert.match(f.captions,/00:00:35.000 --> 00:00:42.000/);
 const cues=[...f.captions.matchAll(/(\d\d):(\d\d):(\d\d)\.\d\d\d --> (\d\d):(\d\d):(\d\d)\.\d\d\d/g)];
 assert.equal(cues.length,6);
 assert(cues.every((c,i)=>Number(c[1])*3600+Number(c[2])*60+Number(c[3])===i*7),'Caption timing sequence');
 const m=JSON.parse(f.matrix);
 assert.equal(m.commercial_activation,'HARD_HOLD');
 assert.equal(m.commercial_holds.length,18);
 assert(m.commercial_holds.every(x=>x.status==='HARD_HOLD'));
 const ids=new Set(m.sources.map(x=>x.id));
 assert.equal(ids.size,m.sources.length);
 assert(m.sources.every(x=>x.url.startsWith('https://')));
 assert(m.claims.length>=25);
 assert(m.claims.every(x=>x.sources.every(id=>ids.has(id))));
 assert(m.claims.filter(x=>x.decision==='EXCLUDE').length>=5);
 assert.equal(m.alternate_owned_offer.status,'NOT_AUTHENTICATED');
 for(const n of ['NOT COMPUTABLE','affiliate_outbound','merchant_confirmed_purchase','actual Grok asset_id','HARD HOLD']) assert(f.dossier.includes(n),'Missing commercial contract '+n);
}
checks(files);
console.log('R321 BASELINE PASS: 7 exact source files; buyer controls, sources, 18 holds, 6 caption cues, A/B parity');
let rejected=0;
const adversarial=[
 ['activated button',f=>f.a=f.a.replace('disabled aria-disabled="true"','')],
 ['missing disclosure',f=>f.a=f.a.replace('may earn a commission','may receive money')],
 ['commercial anchor',f=>f.b=f.b.replace('href="https://finalvestige.com/focus/"','href="https://zen12.com/getstarted"')],
 ['external JS',f=>f.hub+='<script src="https://tracker.example/x.js"></script>'],
 ['extra form',f=>f.a+='<form action="/subscribe"></form>'],
 ['affiliate link',f=>f.a+='<a href="https://affiliates.inspire3.com/ref=321">purchase</a>'],
 ['autoplay media',f=>f.b+='<video autoplay></video>'],
 ['short film captions',f=>f.captions=f.captions.replace('00:00:42.000','00:00:40.000')],
 ['missing film',f=>f.b=f.b.replace(/<figure class="media"[\s\S]*?<\/figure>/,'')],
 ['variant extra sales claim',f=>f.b=f.b.replace('independently validated outcomes','proven commercial results')],
 ['hub missing route',f=>f.hub=f.hub.replaceAll('https://finalvestige.com/focus/','')],
 ['gate removed',f=>{let j=JSON.parse(f.matrix);j.commercial_holds.pop();f.matrix=JSON.stringify(j)}],
 ['invented source',f=>{let j=JSON.parse(f.matrix);j.claims[0].sources=['FAKE'];f.matrix=JSON.stringify(j)}],
 ['commercial activation',f=>{let j=JSON.parse(f.matrix);j.commercial_activation='LIVE';f.matrix=JSON.stringify(j)}],
 ['article unsupported',f=>f.article=f.article.replaceAll('Rohde','Unknown')],
 ['javascript anchor',f=>f.hub+='<a href="javascript:alert(1)">danger</a>'],
 ['pixel',f=>f.b+='<img src="https://tracker.example/pixel" alt="">'],
 ['variant changed text',f=>f.b=f.b.replace('can make a small habit','will guarantee a huge change')],
 ['caption mismatch',f=>f.captions=f.captions.replace('00:00:14.000 -->','00:00:11.000 -->')],
 ['loss of settlement term',f=>f.dossier=f.dossier.replaceAll('merchant_confirmed_purchase','generic_purchase')]
];
for(const [title,mutate] of adversarial){const f={...files};mutate(f);let caught=false;try{checks(f);}catch(e){caught=true;}if(!caught)throw new Error('UNDETECTED: '+title);rejected++;}
console.log('R321 ADVERSARIAL PASS: '+rejected+'/'+adversarial.length+' unsafe mutations rejected');

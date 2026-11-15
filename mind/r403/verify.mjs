#!/usr/bin/env node
// Offline, no network; run: node mind/r403/verify.mjs
import {readFileSync} from 'node:fs';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
const dir=dirname(fileURLToPath(import.meta.url));
const txt=n=>readFileSync(join(dir,n),'utf8');
const A=txt('ZEN12_A_TEXT_GUIDE.html'),B=txt('ZEN12_B_FILM_STORYBOARD.html'),H=txt('MIND_HUB_SOURCE_ONLY.html'),V=txt('ZEN12_42S_CAPTIONS.vtt'),M=JSON.parse(txt('CLAIM_SOURCE_RIGHTS_MATRIX.json')),R=txt('THE_WORD_THAT_STOPPED_BEING_A_WORD.md'),D=txt('CONVERSION_ACCEPTANCE.md');
let checks=0;const assert=(cond,msg)=>{checks++;if(!cond)throw new Error('FAIL '+checks+': '+msg)};
const core=s=>s.split('<!-- BUYER_COPY_START -->')[1]?.split('<!-- BUYER_COPY_END -->')[0];
assert(core(A)&&core(B)&&core(A)===core(B),'A/B substantive buyer text parity');
for(const [n,s] of [['A',A],['B',B],['Hub',H]]){
 assert(/<html lang="en">/.test(s),n+' English language');
 assert(/name="viewport"/.test(s),n+' responsive viewport');
 assert(/<meta name="robots" content="noindex,nofollow">/.test(s),n+' held noindex');
 assert(!/<script\b|<iframe\b|<form\b/i.test(s),n+' no script iframe or duplicate form');
 assert(!/<video[^>]*autoplay/i.test(s),n+' no autoplay');
 assert(!/https:\/\/(?:zen12\.com\/(?:getstarted|secret)|hypnosislive\.com\/mental-skills\/total-focus|brainwaveshots\.com\/focus-shot)[^"']*["']/i.test(s),n+' no active merchant destination');
 assert(/prefers-reduced-motion/.test(s),n+' reduced motion fallback');
 assert(/max-width:390px/.test(s),n+' narrow phone CSS');
 assert(/:focus-visible/.test(s),n+' keyboard focus style');
}
for(const [n,s] of [['A',A],['B',B]]){
 assert(/<button[^>]*\sdisabled\b/.test(s),n+' native disabled purchase button');
 assert(/Prospective affiliate disclosure/.test(s),n+' close disclosure');
 assert(/https:\/\/finalvestige\.com\/focus\//.test(s),n+' single established focus route');
 assert(/data-event="article_to_resource_click"/.test(s),n+' inert measurement contract');
 assert(!/\b(?:$|USD)\s*(?:37|87|17\.95)\b/.test(s.split('<!-- BUYER_COPY_START -->')[0]||''),n+' no price lure in hero');
}
assert(/data-film-variant="storyboard"/.test(B)&&!/data-film-variant="storyboard"/.test(A),'B-only film storyboard');
assert(/<svg[^>]*role="img"[^>]*aria-labelledby/.test(B),'poster accessible SVG');
assert(/<details open>/.test(B)&&/id="film-transcript"/.test(B),'visible no-JS transcript');
assert(/WEBVTT/.test(V)&&/00:00:42\.000/.test(V),'42-second caption timeline');
const cues=[...V.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)];
assert(cues.length===6,'six caption cues');
const sec=t=>{const [h,m,s]=t.split(':');return +h*3600 + +m*60 + +s};
assert(cues.every((m,i)=>sec(m[1])===i*7&&sec(m[2])===(i+1)*7),'contiguous 7-sec captions');
const captionText=V.split(/\r?\n/).filter(l=>l.trim()&&!l.startsWith('WEBVTT')&&!/-->/.test(l)).join(' ').replace(/\s+/g,' ').trim();
const transcript=(B.match(/<p id="film-transcript">([^<]*)<\/p>/)||[])[1]||'';
assert(captionText===transcript,'exact film transcript-captions parity');
assert(M.sources.length>=15&&M.claims.length>=25,'claim-source ledger breadth');
assert(M.claims.every(c=>c.id&&c.claim&&c.classification&&c.copy_policy&&Array.isArray(c.sources)),'claim schema');
assert(M.claims.filter(c=>/UNSUBSTANTIATED|FALSE|NOT_SUPPORTED/.test(c.classification)).every(c=>/DO_NOT_ASSERT|NEVER/.test(c.copy_policy)),'unsafe claims barred');
assert(M.release_gates.length>=20&&M.release_gates.every(g=>g.status==='HOLD'),'all release gates held');
assert(M.no_active_affiliate_url===true&&M.no_paid_sku_authenticated===true,'commercial blockers');
assert(R.includes('2025')&&(R.includes('without hypnotic induction')||R.includes('without a hypnosis induction')),'article differentiates recent evidence and induction');
assert(/#2547/.test(D)&&/NOT a second approved public Stroop destination/.test(D),'prior-article duplication flagged');
assert(/NOT COMPUTABLE/.test(D)&&/merchant_confirmed_paid_conversion/.test(D),'paid conversion not conflated with click');
console.log('PASS '+checks+'/'+checks+' offline source assertions; no network, browser or merchant tests executed.');

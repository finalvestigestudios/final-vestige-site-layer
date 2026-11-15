// R400 offline source verifier; run: node mind/r400/verify.mjs from repository root.
// This is a static unit audit, NOT browser WCAG, WordPress sanitizer, affiliate or paid-checkout validation.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const here = new URL('.', import.meta.url);
const get = n => readFileSync(new URL(n, here), 'utf8');
const A=get('ZEN12_TEXT_A.html'), B=get('ZEN12_OPTIONAL_FILM_B.html'), H=get('MIND_HUB_SOURCE_ONLY.html');
const V=get('ZEN12_CONTROL_FILM_42S.vtt'), M=JSON.parse(get('CLAIM_SOURCE_MATRIX.json'));
const T=get('THE_RECORDING_THAT_WORKED_WITHOUT_HYPNOSIS.md'), C=get('CONVERSION_ACCEPTANCE.md');
let count=0;
function check(test,description){assert.ok(test,description);count++;}
function normalize(s){return s.replace(/<section class="panel" aria-labelledby="movie-heading">[\s\S]*?<\/section>/,'').replace('Zen12 independent buyer guide B','Zen12 independent buyer guide A');}
check(normalize(B)===A,'buyer copy parity: only optional movie added');
for (const html of [A,B,H]){
 check(/<html lang="en">/.test(html),'lang present');
 check(/name="viewport"/.test(html),'responsive viewport');
 check(!/<script\b|<iframe\b|<form\b/i.test(html),'no scripts, iframes, duplicated signup forms');
 check(!/<(?:audio|video)\b[^>]*\bautoplay\b/i.test(html),'no media autoplay attributes');
 check(!/<a[^>]+href=["'][^"']*(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com)/i.test(html),'no active merchant links');
 check(!/\bon(?:click|load|error|mouseenter)\s*=/i.test(html),'no inline event handlers');
 check(/prefers-reduced-motion/.test(html),'reduced-motion CSS present');
}
for(const html of [A,B]){
 check(/<button\s+disabled\s+type="button"/.test(html),'native-disabled merchant control');
 check(/may earn a commission/.test(html),'plain adjacent disclosure');
 check(/https:\/\/finalvestige\.com\/focus\//.test(html),'same established free Focus');
 check(/<a[^>]+href="https:\/\/pmc\.ncbi\.nlm\.nih\.gov\/articles\/PMC12606380\//.test(html),'primary research link');
}
check(B.includes('id="movie-heading"'),'film component in B');
check(!A.includes('id="movie-heading"'),'no film in A');
const narrated=B.match(/<p id="narration">([\s\S]*?)<\/p>/)?.[1];
check(!!narrated,'visible B transcript');
const raw=V.trim().split(/\n\s*\n/).slice(1);
const cues=raw.map(block=>block.split('\n'));
check(cues.length===6,'six WebVTT cues');
let prev=0;let spoken=[];
for(const cue of cues){
 const m=cueTime(cue[0]); // parse exact HH:MM:SS.mmm
 check(m.start===prev,'contiguous cue boundaries');
 check(m.end>m.start,'positive cue time');
 prev=m.end;spoken.push(cue.slice(1).join(' '));
}
function cueTime(line){
 const parts=line.match(/^(\d\d):(\d\d):(\d\d)\.\d+ --> (\d\d):(\d\d):(\d\d)\.\d+$/);
 assert.ok(parts,'valid WebVTT time format');
 return {start:+parts[1]*3600 + +parts[2]*60 + +parts[3],end:+parts[4]*3600 + +parts[5]*60 + +parts[6]};
}
check(prev===42,'video caption runtime 42 seconds');
check(spoken.join(' ').replace(/\s+/g,' ').trim()===narrated.replace(/\s+/g,' ').trim(),'captions match entire narration');
check(M.sources.length===15,'15 grounded sources');
check(M.claims.length===36,'36 classified claims');
check(M.commercial_release_gates.length===24,'24 release gates');
check(M.commercial_release_gates.every(g=>g.state==='HOLD'),'all commercial release gates closed');
check(T.includes('53.4%')&&T.includes('40.9%'),'active and control findings retained');
check(T.includes('not a general')||T.includes('not a retail-product trial'),'qualify product transfer');
check(C.includes('NOT COMPUTABLE'),'net metric guarded');
console.log('PASS '+count+' offline static checks — no claim of native browser/merchant/WordPress verification');

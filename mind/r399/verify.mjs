// Source-only offline QA for R399. Run: node mind/r399/verify.mjs
// Static assurance only: NOT a real-browser WCAG, WordPress sanitizer, Jetpack, affiliate checkout or sale test.
import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
const f=n=>readFileSync(new URL(n,import.meta.url),'utf8');
const A=f('ZEN12_A_TEXT_PILOT.html'),B=f('ZEN12_B_OPTIONAL_FILM_PILOT.html');
const H=f('MIND_HUB_WORDPRESS_SOURCE_ONLY.html'),V=f('ZEN12_FILM_42S.vtt');
const J=JSON.parse(f('CLAIMS_AUTHORIZATION_AND_RELEASE_MATRIX.json'));
const research=f('THREE_AUDIO_PROGRAMS_EVIDENCE_BUYER_GUIDE.md');
const acceptance=f('CONVERSION_ACCEPTANCE_CREATOR_MATRIX.md');
let total=0;
function ck(value,message){assert.ok(value,message);total++;}
function safe(h){
  return !/<script\b|<iframe\b|<form\b|<video\b|<audio\b|\son[a-z]+=|javascript:|data:text\/html|<a[^>]+href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\./i.test(h);
}
const stripB=B.replace(/<section class="card" aria-label="Optional original 42-second video concept">[\s\S]*?<\/section>/,'').replace('guide — B','guide — A').replace('data-variant="B"','data-variant="A"');
ck(A===stripB,'A/B core buyer copy and layout identical apart from film concept');
ck(B.indexOf('</header>')<B.indexOf('Optional original 42-second'),'Film offered after hero');
for(const [i,h] of [A,B,H].entries()){
  ck(safe(h),'No commercial/surveillance vectors in HTML '+i);
  ck(/<html lang="en">/.test(h),'Language present '+i);
  ck(/name="viewport"/.test(h),'Mobile viewport present '+i);
  ck(/name="robots" content="noindex,nofollow"/.test(h),'Draft noindex '+i);
  ck(/prefers-reduced-motion/.test(h),'Reduced motion rule '+i);
  ck(/:focus-visible/.test(h),'Visible keyboard focus '+i);
}
for(const h of [A,B]){
  ck(/<button disabled type="button" aria-describedby="hold">/.test(h),'Native disabled merchant button');
  ck(/Affiliate disclosure:/.test(h),'Adjacent earning relationship disclosure');
  ck(/finalvestige.com\/focus\//.test(h),'Single existing free funnel');
  ck(!/guaranteed (focus|relief|health|wealth)/i.test(h),'No unsupported claimed guaranteed outcomes');
}
ck(!/<(?:form|script|iframe)\b/i.test(H),'Hub has no form/script/embed');
ck(/change-blindness\//.test(H),'Canonical change blindness route');
ck(/puysegurs-animal-magnetism-files/.test(H),'Canonical history archive');
ck(!/href=["'][^"']*\/mind\//i.test(H),'No invented live Mind page');
ck(/WEBVTT/.test(V),'Valid WebVTT header');
const ranges=[...V.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)];
ck(ranges.length===6,'Exactly six cues');
ck(ranges[0][1]==='00:00:00.000' && ranges.at(-1)[2]==='00:00:42.000','42 second duration');
for(let i=1;i<ranges.length;i++)ck(ranges[i-1][2]===ranges[i][1],'Cue boundaries contiguous '+i);
const narration=B.match(/<strong>Full accessible transcript:<\/strong>\s*([\s\S]*?)<\/p>/)?.[1]||'';
const cues=V.split('\n').filter(l=>l.trim()&&!/^WEBVTT|^\d\d:\d\d:\d\d\.\d{3} --> /.test(l)).join(' ').replace(/\s+/g,' ').trim();
ck(narration.replace(/\s+/g,' ').trim()===cues,'Exact spoken narration / caption parity');
ck(J.claims.length>=28,'At least 28 claim classifications');
ck(J.commercial_gates.length>=30,'At least 30 release gates');
ck(J.commercial_gates.every(g=>g.status==='HOLD'),'Commercial hold enforced');
ck(J.commercial_activation==='HARD_HOLD','Release guard set');
ck(J.claims.filter(c=>c.classif==='seller_effect_claim').every(c=>c.decision==='exclude'),'Unsupported seller efficacy omitted');
ck(research.trim().split(/\s+/).length>1600,'Substantive 1600+ word original review');
ck(acceptance.includes('NOT COMPUTABLE'),'Financial denominator honesty');
ck(acceptance.includes('Grok'),'Creator scope');
for(const bad of [
 '<script>alert(1)</script>','<form action="/capture"></form>','<iframe src="https://other.example"></iframe>',
 '<a href="https://zen12.com/getstarted">Buy</a>','<video autoplay></video>','<div onclick="sell()">Buy</div>'
 ]) ck(!safe(A+bad),'Injected unsafe markup rejected');
console.log('R399 static source audit: '+total+'/'+total+' PASS; 6/6 injected unsafe fixtures rejected; native Node run complete (if invoked directly).');

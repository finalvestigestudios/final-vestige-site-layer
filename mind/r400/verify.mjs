/**
 * R400 offline static source-level acceptance checks.
 * Run: node mind/r400/verify.mjs
 * Never substitutes for browser, WordPress, permission, consent, checkout or CI QA.
 */
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url));
const read=n=>fs.readFileSync(path.join(dir,n),'utf8');
const a=read('ZEN12_A_TEXT.html'),b=read('ZEN12_B_OPTIONAL_FILM.html'),hub=read('MIND_HUB_WORDPRESS_SOURCE_ONLY.html');
const vtt=read('ZEN12_42S_CAPTIONS.vtt'),matrix=JSON.parse(read('CLAIMS_PERMISSIONS_AND_RELEASE_MATRIX.json')),guide=read('SELF_HYPNOSIS_EVIDENCE_BUYER_GUIDE.md'),plan=read('CONVERSION_FIRST_ACCEPTANCE_AND_CREATOR_ROUTING.md');
let n=0; function ok(name,condition){assert.ok(condition,name);n++;console.log('PASS',name);}
function tags(s){return s.replace(/<!--[\s\S]*?-->/g,'');}
function unsafe(s){
 const html=tags(s);
 return /<script\b|<iframe\b|<form\b/i.test(html)
 || /<video\b[^>]*\bautoplay\b/i.test(html)
 || /<meta[^>]+http-equiv=["']?refresh\b/i.test(html)
 || /(?:href|action)=["']https?:\/\/(?:www\.)?(?:zen12|hypnosislive|brainwaveshots|inspire3)\./i.test(html)
 || /<a\b[^>]*\bonclick\s*=/i.test(html);
}
const extract=s=>{const k=s.indexOf('<p class="eyebrow">Final Vestige / Mind &amp; Perception');assert.ok(k>0);return s.slice(k,s.lastIndexOf('</main>'));};
ok('valid independent A',a.startsWith('<!doctype html>')&&a.includes('<html lang="en">'));
ok('valid independent B',b.startsWith('<!doctype html>')&&b.includes('<html lang="en">'));
ok('exact buyer copy parity',extract(a)===extract(b));
ok('film only B',!a.includes('id="film-title"')&&b.includes('id="film-title"'));
ok('B poster image with accessible explanation',b.includes('role="img"')&&b.includes('aria-label='));
ok('B accessible optional transcript',b.includes('<details>')&&b.includes('42-second transcript'));
ok('A no active affiliate/merchant',!unsafe(a));
ok('B no active affiliate/merchant',!unsafe(b));
ok('Hub no active affiliate/merchant',!unsafe(hub));
ok('native disabled CTA in both', [a,b].every(s=>/<button type="button" disabled\b/.test(s)));
ok('disclosures in both', [a,b].every(s=>s.includes('id="affiliate-disclosure"')&&s.includes('may earn a commission')));
ok('disclosure precedes nearby CTA', [a,b].every(s=>{const i=s.indexOf('id="affiliate-disclosure"'),j=s.indexOf('<button type="button" disabled');return i>=0&&j>i&&j-i<460;}));
ok('No third party video',!/<video\b|<iframe\b|<script\b/i.test(b));
ok('No auto-playing animated media',!/<audio\b[^>]*autoplay|<video\b[^>]*autoplay/i.test(b));
ok('A free verified Focus route',a.includes('href="https://finalvestige.com/focus/"'));
ok('B free verified Focus route',b.includes('href="https://finalvestige.com/focus/"'));
ok('No extra signup forms',[a,b,hub].every(s=>!/<form\b/i.test(s)));
ok('Hub four streams',["attention","history","practice","tools"].every(k=>hub.includes('id="'+k+'"')));
ok('Hub links only canonical published routes',hub.includes('/2026/11/02/change-blindness/')&&hub.includes('/2026/11/02/mesmerism/'));
ok('A and B noindex while source-only', [a,b].every(s=>s.includes('content="noindex,nofollow"')));
ok('Hub noindex',hub.includes('content="noindex,nofollow"'));
ok('Reduced-motion declaration',[a,b,hub].every(s=>s.includes('prefers-reduced-motion:reduce')));
ok('Visible focus indicators',[a,b,hub].every(s=>s.includes('focus-visible')));
ok('VTT header',vtt.startsWith('WEBVTT\n'));
const cueMatches=[...vtt.matchAll(/00:00:(\d{2})\.000 --> 00:00:(\d{2})\.000\n([^\n]+)/g)];
ok('Six timed subtitle cues',cueMatches.length===6);
ok('Cue starts zero',Number(cueMatches[0][1])===0);
ok('Cue ends 42 seconds',Number(cueMatches.at(-1)[2])===42);
ok('Cue coverage continuous',cueMatches.every((c,i)=>i===0||c[1]===cueMatches[i-1][2]));
const transcript=b.match(/<details><summary>Read the 42-second transcript<\/summary><p>([^<]+)<\/p><\/details>/)?.[1];
ok('Complete narration present',Boolean(transcript));
ok('Transcript exactly matches VTT words',cueMatches.map(m=>m[3]).join(' ')===transcript);
ok('Speech <=110 words in 42 seconds',transcript.split(/\s+/).length<=110);
ok('Claim matrix >=35 classified claims',matrix.claims.length>=35);
ok('Source matrix >=18 actual URLs',Object.values(matrix.source_index).filter(x=>x.startsWith('https://')).length>=18);
ok('Commercial release gates >=30',matrix.commercial_release_gates.length>=30);
ok('All release gates held',matrix.commercial_release_gates.every(x=>x.status==='HOLD'));
ok('No authenticated merchant terms',matrix.orders.confirmed_orders===null&&matrix.orders.net_revenue===null);
ok('Original guide >2000 words',guide.split(/\s+/).length>=2000);
ok('Guide references main historical primary-source archive',guide.includes('puysegurs-animal-magnetism-files'));
ok('Guide distinguishes seller from clinical trial',guide.includes('did not test a retail MP3')&&guide.includes('a product-specific advertised effect'));
ok('Plan specifies payout rather than clicks',plan.includes('merchant_confirmed_order')&&plan.includes('affiliate_click'));
ok('Plan preserves Grok and Dispatch roles',plan.includes('Grok')&&plan.includes('Dispatch #174'));
for (const [name,mutation] of [
 ['active seller link','<a href="https://zen12.com/getstarted">BUY</a>'],
 ['new form','<form action="/subscribe"></form>'],
 ['script injection','<script>window.bad=1</script>'],
 ['iframe','<iframe src="https://player.example.com"></iframe>'],
 ['autoplay','<video autoplay controls></video>'],
 ['redirect','<meta http-equiv="refresh" content="0;url=https://example.com">'],
 ['inline tracking','<a onclick="sendBeacon()">Track</a>']
])ok('unsafe fixture detected: '+name,unsafe(a+mutation));
console.log('R400 STATIC PASS',n,'SOURCE LEVEL ONLY — NOT LIVE/QA/MERCHANT EVIDENCE');

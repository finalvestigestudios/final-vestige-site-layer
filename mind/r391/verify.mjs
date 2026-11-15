/**
 * R391 offline source preflight. Run natively with:
 *    node mind/r391/verify.mjs
 * This is intentionally strict and limited to STATIC content; it is not WCAG/browser,
 * WordPress sanitizer, merchant checkout, actual sales or Jetpack QA.
 */
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
const root=dirname(fileURLToPath(import.meta.url));
const read=name=>readFileSync(join(root,name),'utf8');
const a=read('ZEN12_A_INDEPENDENT_BUYER_GUIDE.html');
const b=read('ZEN12_B_OPTIONAL_42S_STORYBOARD.html');
const hub=read('MIND_ARCHIVE_FOUR_STREAM_REVIEW_ONLY.html');
const art=read('THE_PENDULUM_THAT_ANSWERED_BEFORE_ANYONE_MOVED_IT.md');
const vtt=read('R391_CAPTIONS.vtt');
const poster=read('R391_PENDULUM_POSTER.svg');
const note=read('CONVERSION_FIRST_ACCEPTANCE_AND_CREATOR_ROUTING.md');
const matrix=JSON.parse(read('CLAIMS_SOURCES_RIGHTS_AND_GATES.json'));
let checks=0;
function ok(v,msg){checks++;assert.ok(v,msg)}
function eq(x,y,msg){checks++;assert.deepEqual(x,y,msg)}
function checkBuyer(s,which){
 ok(s.startsWith('<!doctype html>'),which+' HTML5');
 ok(/<html lang="en">/.test(s),which+' language');
 ok(/name="viewport"/.test(s),which+' viewport');
 ok(/<main>/.test(s),which+' main');
 ok(/<h1>/.test(s),which+' heading');
 ok(/focus-visible/.test(s),which+' focus style');
 ok(/prefers-reduced-motion/.test(s),which+' reduced motion');
 ok(/finalvestige.com\/focus\//.test(s),which+' existing free Focus');
 ok(/affiliate disclosure/i.test(s),which+' disclosure');
 ok(/may earn a commission/i.test(s),which+' plain commission disclosure');
 ok(/<button\b[^>]*\bdisabled\b/.test(s),which+' native disabled button');
 ok(!/<a[^>]+href="https?:\/\/(?:www\.)?(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|inspire3\.com|affiliates\.inspire3\.com)/i.test(s),which+' NO active merchant link');
 ok(!/<script\b|<iframe\b|<form\b|on\w+\s*=|<(?:video|audio)[^>]*\bautoplay\b/i.test(s),which+' no JS/form/autoplay/handlers');
 ok(!/add to cart|guaranteed (?:cure|memory)|100% guaranteed|earn \$\d+/i.test(s),which+' no invented guarantees');
 const pos=s.search(/affiliate disclosure/i),button=s.search(/<button\b/);
 ok(pos>=0&&button>pos&&button-pos<650,which+' adjacent disclosure');
}
checkBuyer(a,'A');checkBuyer(b,'B');
const extra=b.match(/<details class="film"[\s\S]*?<\/details>/);
ok(!!extra,'B optional details exists');
eq(b.replace(extra[0],''),a,'A/B buyer copy exactly matched');
ok(!a.includes('R391_PENDULUM_POSTER.svg'),'A is text only');
ok(b.includes('R391_PENDULUM_POSTER.svg'),'B own poster');
ok(b.includes('R391_CAPTIONS.vtt'),'B caption concept');
ok(!/<video\b|<audio\b|<(?:video|audio)[^>]*\bautoplay\b/.test(b),'B storyboard not simulated playback');
const transcript=b.match(/Proposed 42-second narration:<\/strong> ([\s\S]*?)<\/p>/);
ok(!!transcript,'transcript exists');
const cues=vtt.trim().split(/\n\n/).filter(x=>x.includes(' --> ')).map(x=>x.split('\n').slice(1).join(' ').trim());
eq(cues.length,6,'six VTT captions');
eq(cues.join(' '),transcript[1],'caption words match original narration');
ok(/^WEBVTT\s/.test(vtt),'VTT header');
ok(vtt.includes('00:00:42.000'),'VTT duration 42s');
ok(/<svg\b/.test(poster)&&/viewBox="0 0 1280 720"/.test(poster),'original 16:9 vector');
ok(!/<script\b|<foreignObject\b|on\w+\s*=|<image\b|href=/i.test(poster),'SVG safe no external assets');
ok(art.trim().split(/\s+/).length>=2000,'long original research');
for(const term of ['Chevreul','Gauchou','Moga','Dienes','2012','2022','Puységur','fieldbook'])ok(art.toLowerCase().includes(term.toLowerCase()),'article '+term);
ok(!/https:\/\/zen12\.com/.test(art),'article no active merchant URL');
eq(matrix.claims.length,34,'34 claims');
eq(matrix.sources.length,19,'19 sources');
eq(matrix.gates.length,36,'36 gates');
ok(matrix.gates.every(g=>g.status==='HOLD'),'all gates closed');
ok(matrix.claims.some(c=>c.id==='C21'&&c.decision==='HOLD'),'publisher authorization hold');
ok(matrix.claims.some(c=>c.id==='C15'&&c.decision==='OMIT'),'product efficacy inference omitted');
ok(matrix.sources.every(s=>/^https:\/\//.test(s.url)),'source URLs qualified');
for(const c of matrix.claims){ok(c.source_ids.every(id=>matrix.sources.some(s=>s.id===id)),'source IDs '+c.id)}
for(const id of ['perception','history','practice','tools'])ok(hub.includes('id="'+id+'"'),'hub section '+id);
ok(!/<script\b|<form\b|<iframe\b|autoplay\b/i.test(hub),'hub static accessible');
ok(!/href="https?:\/\/(?:www\.)?zen12\.com/.test(hub),'hub no merchant links');
for(const term of ['affiliate_click','merchant_confirmed_paid_order','realized_net_revenue','7/30-day','asset_id','Grok','Praxxis','HARD HOLD'])ok(note.includes(term),'conversion handoff '+term);
// Deliberate unsafe mutation detection; do not confuse with a real browser security audit.
const bad=[
a.replace('<button type="button" disabled','<button type="button"'),
a.replace('may earn a commission','may not earn anything'),
a.replace('</main>','<a href="https://zen12.com/getstarted">Buy</a></main>'),
a.replace('</main>','<script>bad()</script></main>'),
a.replace('</main>','<form action="https://example.org"></form></main>'),
a.replace('</main>','<video autoplay></video></main>'),
a.replace('href="https://finalvestige.com/focus/"','href="#missing"'),
a.replace('affiliate disclosure','commercial terms'),
a.replace('<html lang="en">','<html>'),
a.replace('prefers-reduced-motion','does-not-reduce-motion'),
];
function safe(s){
 return /<html lang="en">/.test(s)&&/prefers-reduced-motion/.test(s)
 && /affiliate disclosure/i.test(s)&&/may earn a commission/i.test(s)
 && /<button\b[^>]*\bdisabled\b/.test(s)
 && /finalvestige.com\/focus\//.test(s)
 && !/<a[^>]+href="https?:\/\/(?:www\.)?zen12\.com/i.test(s)
 && !/<script\b|<iframe\b|<form\b|autoplay\b/i.test(s);
}
eq(bad.filter(x=>!safe(x)).length,bad.length,'ten deliberately unsafe mutations rejected');
console.log('R391 native offline source checks PASS:',checks,'; malicious fixtures rejected',bad.length,'/10');
console.log('Not tested: hosted CI, real-browser WCAG/CWV, WP sanitization, playable video, Jetpack, publisher rights, checkout or settlement.');

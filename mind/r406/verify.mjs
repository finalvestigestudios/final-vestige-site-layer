// Offline source-only guardrails for Mind R406. Run: node mind/r406/verify.mjs
import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const root=new URL('.',import.meta.url);
const read=(n)=>readFileSync(new URL(n,root),'utf8');
const a=read('ZEN12_A.html'), b=read('ZEN12_B.html'),hub=read('MIND_ARCHIVE_SOURCE.html'),vtt=read('VIDEO_CAPTIONS.vtt'),svg=read('CHOICE_NOTE_POSTER.svg'),article=read('THE_CHOICE_THAT_CHANGED.md'),matrix=JSON.parse(read('CLAIM_PROOF_MATRIX.json')),accept=read('CONVERSION_ACCEPTANCE.md');
let checks=0;const check=(name,fn)=>{fn();checks++;process.stdout.write('PASS '+name+'\n');};
for(const [name,html] of [['A',a],['B',b]]) {
 check(name+' native disabled',()=>assert.match(html,/<button\b[^>]*\bdisabled\b[^>]*>/));
 check(name+' adjacent disclosure',()=>{const d=html.indexOf('Potential affiliate relationship:');const t=html.indexOf('purchase link unavailable');assert.ok(d>=0&&t>d&&t-d<650);});
 check(name+' no active merchant href',()=>assert.doesNotMatch(html,/<a\b[^>]+href=["']https?:\/\/(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i));
 check(name+' no tracker/forms',()=>{assert.doesNotMatch(html,/<(?:script|iframe|form)\b/i);});
 check(name+' no autoplay',()=>assert.doesNotMatch(html,/autoplay\b/i));
 check(name+' accessible single source CTA',()=>assert.match(html,/href="https:\/\/finalvestige\.com\/focus\/"/));
 check(name+' head metadata',()=>{assert.match(html,/<html lang="en">/);assert.match(html,/<meta name="viewport"/);assert.match(html,/noindex,nofollow/);});
}
check('A/B same core buyer copy',()=>{const block=s=>s.slice(s.indexOf('<header>'),s.indexOf('<footer>'));assert.equal(block(a),block(b));});
check('B optional storyboard only',()=>{assert.match(b,/<details>/);assert.match(b,/not playable video/);assert.doesNotMatch(b,/<video\b/);});
check('VTT six contiguous cues',()=>{const cues=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.\d{3} --> (\d\d):(\d\d):(\d\d)\.\d{3}/g)];assert.equal(cues.length,6);let last=0;for(const m of cues){const s=+m[1]*3600 + +m[2]*60 + +m[3],e=+m[4]*3600 + +m[5]*60 + +m[6];assert.equal(s,last);last=e;}assert.equal(last,42);});
check('VTT caption text matches visible transcript',()=>{const first=read('ZEN12_B.html');for(const m of vtt.split(/\n\n+/).slice(1)){const txt=m.split('\n').slice(2).join(' ');assert.ok(first.includes(txt));}});
check('Original poster no external assets',()=>{assert.match(svg,/<svg/);assert.match(svg,/<title/);assert.match(svg,/<desc/);assert.doesNotMatch(svg,/<(?:image|foreignObject|script)\b|xlink:href|(?:src|href)=[\"']https?:/i)});
check('Hub four streams',()=>{for(const term of ['Perception &amp; attention','History of suggestion','Practice &amp; reflection','Tools under review'])assert.ok(hub.includes(term));assert.doesNotMatch(hub,/<(?:script|form|iframe)\b/i)});
check('Source trail primary papers',()=>{for(const id of ['16210542','20637455'])assert.ok(article.includes(id));});
check('Claims sources integrity',()=>{const ids=new Set(matrix.sources.map(s=>s.id));for(const c of matrix.claims)if(c.source)assert.ok(ids.has(c.source),c.id);});
check('All commercial gates HOLD',()=>{assert.ok(matrix.release_gates.length>=20);assert.ok(matrix.release_gates.every(g=>g.status==='HOLD'));});
check('No invented revenue',()=>{assert.match(accept,/NOT COMPUTABLE/);assert.match(accept,/merchant_confirmed_order/);assert.match(accept,/refund/);});
console.log('PASS '+checks+' source assertions total; not browser, partner, Jetpack or merchant validation');

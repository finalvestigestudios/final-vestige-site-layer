// Offline static verifier: node mind/r401/verify.mjs (built-in modules only).
import fs from 'node:fs';import assert from 'node:assert/strict';import path from 'node:path';
const d=path.dirname(new URL(import.meta.url).pathname),read=n=>fs.readFileSync(path.join(d,n),'utf8');
let count=0;const ok=(f,msg)=>{assert.ok(f,msg);count++};const a=read('ZEN12_A_TEXT.html'),b=read('ZEN12_B_OPTIONAL_FILM.html'),h=read('MIND_HUB_WORDPRESS_SOURCE_ONLY.html'),m=JSON.parse(read('CLAIMS_AUTHORIZATION_MATRIX.json')),v=read('MIND_42S.vtt'),g=read('THREE_CLAIMS_FIELD_GUIDE.md');
for(const [name,html] of [['A',a],['B',b],['hub',h]]){ok(/<html lang="en">/.test(html),name+' lang');ok(/name="viewport"/.test(html),name+' viewport');ok(/noindex,nofollow/.test(html),name+' noindex');ok(!/<script\b/i.test(html),name+' no script');ok(!/<form\b/i.test(html),name+' no extra list');ok(!/autoplay/i.test(html.replace(/nothing autoplays/ig,'')),name+' no autoplay');}
for(const html of [a,b]){ok(/<button[^>]*disabled[^>]*>/.test(html),'native disabled');ok(!/<a[^>]+href="https?:\/\/(zen12\.com|affiliates\.inspire3\.com)/.test(html),'no purchase link');ok(html.indexOf('Prospective affiliate disclosure') < html.indexOf('Zen12 purchase link not authorized'),'disclosure adjacency');ok(html.includes('no active purchase link'),'disclosure readable');}
const cut=s=>s.slice(s.indexOf('<section id="buyer-copy"'),s.indexOf('</main>'));ok(cut(a)===cut(b),'identical buyer copy');
ok(b.includes('<svg')&&b.includes('film-transcript'),'optional poster+transcript');ok(!/<video\b|<iframe\b|<audio\b/i.test(b),'no claimed playable media');
ok(m.claims.length>=20,'source audit count');ok(m.release_gates.every(x=>x.status==='HOLD'),'gates closed');ok(m.claims.every(x=>x.url.startsWith('https://')),'claim source url');
ok(v.startsWith('WEBVTT'),'caption header');ok((v.match(/-->/g)||[]).length===6,'six caption cues');ok(v.includes('00:00:42.000'),'42 sec');ok(g.length>8500,'substantive guide');
console.log('PASS',count,'R401 offline assertions. Real-browser, merchant, CMS, video playback and Jetpack tests NOT performed.');

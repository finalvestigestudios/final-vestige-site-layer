import fs from 'node:fs';import assert from 'node:assert/strict';import path from 'node:path';
const dir=path.dirname(new URL(import.meta.url).pathname);const get=n=>fs.readFileSync(path.join(dir,n),'utf8');
const a=get('ZEN12_A_BUYER_GUIDE.html'),b=get('ZEN12_B_OPTIONAL_FILM_GUIDE.html'),h=get('MIND_HUB_SOURCE_ONLY.html'),m=JSON.parse(get('CLAIM_SOURCE_MATRIX.json')),v=get('ORIGINAL_CAPTIONS.vtt');
let pass=0;function ok(k,x){assert.ok(x,k);pass++}
for(const [name,html] of [['A',a],['B',b],['hub',h]]){ok(name+' noindex',html.includes('noindex,nofollow'));ok(name+' lang',html.includes('<html lang="en">'));ok(name+' no scripts',!/<script\b/i.test(html));ok(name+' no form',!/<form\b/i.test(html));ok(name+' no iframe',!/<iframe\b/i.test(html));ok(name+' no autoplay media',!/<video\b|<source\b|\bautoplay\b/i.test(html));}
for(const [name,html] of [['A',a],['B',b]]){ok(name+' disabled native',/<button type="button" disabled/.test(html));ok(name+' adjacent affiliate disclosure',html.indexOf('may earn a commission')<html.indexOf('<button')&&html.includes('at no additional cost to you'));ok(name+' no seller hyperlink',!/<a[^>]+href="https:\/\/(?:www\.)?(?:zen12|inspire3|affiliates\.inspire3)\.com/i.test(html));ok(name+' focus existing',html.includes('https://finalvestige.com/focus/'));}
ok('A-B parity',b.replace(/<!-- optional_film_start -->[\s\S]*?<!-- optional_film_end -->/,'')===a);
ok('six captions',(v.match(/-->/g)||[]).length===6);ok('42 seconds',v.includes('00:00:42.000'));
ok('32 held gates',m.gates.length===32 && m.gates.every(x=>x.status==='HOLD'));
ok('source claims',m.claims.length>=20);
ok('four streams',['Perception &amp; Attention','History of Suggestion','Practice &amp; Reflection','Tools Under Review'].every(x=>h.includes(x)));
console.log('PASS '+pass+'/'+pass+' static safety/source checks; NOT browser/CI/merchant proof.');

'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');const get=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
const a=get('ZEN12-A-TEXT-ONLY-REVIEW.html'),b=get('ZEN12-B-OPTIONAL-FILM-REVIEW.html'),hub=get('MIND-ARCHIVE-FOUR-STREAM-REVIEW.html'),captions=get('ORIGINAL-42S-CAPTIONS.vtt'),article=get('THE-SESSION-THAT-WORKED-IN-BOTH-GROUPS.md'),m=JSON.parse(get('CLAIM-PROOF-AND-RELEASE-HOLDS.json'));
let n=0;function test(name,fun){fun();console.log('PASS '+(++n)+' '+name)}
test('18 hard holds',()=>assert.ok(m.commercial_holds.length===18&&m.commercial_holds.every(x=>x.status==='HARD_HOLD'&&x.evidence===null)));
test('not computable financials',()=>assert.equal(m.net_revenue_per_1000_qualified_human_sessions,null));
test('24 source-referenced claims',()=>{const ids=new Set(m.sources.map(x=>x.id));assert.equal(m.claims.length,24);for(const c of m.claims)for(const sid of c.source_ids)assert.ok(ids.has(sid))});
test('buyer content parity',()=>assert.equal(a.split('<section><h2>Before you buy')[1],b.split('<section><h2>Before you buy')[1]));
test('merchant controls disabled/disclosed',()=>{for(const x of [a,b,hub]){const i=x.indexOf('class="disclosure"'),j=x.indexOf('disabled aria-disabled="true"');assert.ok(i>0&&j>i&&j-i<1800);assert.ok(x.includes('may earn a commission'))}});
test('a11y source requirements',()=>{for(const x of [a,b,hub]){assert.ok(x.includes('<main id="content">')&&x.includes(':focus-visible')&&x.includes('prefers-reduced-motion')&&x.includes('@media(max-width:640px)'))}});
test('no scripts or duplicate signup',()=>{for(const x of [a,b,hub])assert.ok(!/<script\b|<form\b|<iframe\b|<video\b|\bautoplay\s*(?:=|>)/i.test(x))});
test('captions 42 seconds contiguous',()=>{const rows=[...captions.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g)];assert.equal(rows.length,6);let end=0;const sec=p=>Number(p[0])*3600+Number(p[1])*60+Number(p[2])+Number(p[3])/1000;for(const row of rows){assert.equal(sec(row.slice(1,5)),end);end=sec(row.slice(5,9))}assert.equal(end,42)});
test('article evidence disclaimers',()=>{for(const marker of ['400 participants','153 healthy adults','1,000 people','not a cognitive diagnostic','not independently tested'])assert.ok(article.includes(marker))});
const malicious=['<script>alert(1)</script>','<form action="/subscribe">','<iframe src="x">','<video autoplay>','<a href="https://zen12.com/order?aff=fake">Buy</a>'];
test('five synthetic unsafe fixtures rejected',()=>{const guard=x=>!/<script\b|<form\b|<iframe\b|\bautoplay\s*>|aff=fake/.test(x);for(const x of malicious)assert.equal(guard(a+x),false)});
console.log('PASS: '+n+' native structural checks; 5/5 synthetic malicious fixtures rejected');

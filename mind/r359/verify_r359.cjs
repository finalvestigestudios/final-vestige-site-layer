#!/usr/bin/env node
'use strict';
const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const read=name=>fs.readFileSync(path.join(__dirname,name),'utf8');
const a=read('ZEN12_A_TEXT.html'),b=read('ZEN12_B_OPTIONAL_FILM.html');
const h=read('MIND_HUB_SOURCE_ONLY.html'),c=read('ORIGINAL_42S_CAPTIONS.vtt');
const m=JSON.parse(read('CLAIM_SOURCE_MATRIX.json'));const article=read('THE_FACE_THAT_LOOKED_NORMAL.md');
let n=0;function check(value,message){assert.ok(value,message);n++}
const substantive=x=>x.match(/<section id="buyer-core"[\s\S]*?<\/section>/)?.[0];
check(substantive(a)===substantive(b),'A and B buyer copy must be identical');
for(const [label,s] of [['A',a],['B',b],['hub',h]]){
check(s.includes('lang="en"'),label+' language');
check(s.includes('name="viewport"'),label+' viewport');
check(s.includes('<main'),label+' main landmark');
check(!/<script\b|<iframe\b|<form\b|<video[^>]*autoplay/i.test(s),label+' no tracking/form/autoplay');
check(!/<a[^>]*href="https:\/\/(zen12|hypnosislive|brainwaveshots|affiliates\.inspire3)/i.test(s),label+' no merchant link');
check(s.includes('button type="button" disabled'),label+' native merchant disabled');
}
for(const s of [a,b]){
const i=s.indexOf('Final Vestige may earn a commission'),j=s.indexOf('<button type="button" disabled',i);
check(i>0&&j>i&&j-i<250,'FTC disclosure immediately before withheld CTA');
}
check(!a.includes('optional-film'),'A text-only');
check(b.includes('id="optional-film"')&&b.includes('<summary>'),'B optional accessible treatment');
check(b.includes('not playable video'),'B truthful not-playing status');
check(b.includes('<svg')&&b.includes('aria-label='),'B original accessible SVG');
check((c.match(/-->/g)||[]).length===6,'six caption cues');
check(c.includes('00:00:42.000'),'42 second ending');
check(article.split(/\s+/).length>=1900,'substantive original research');
check((article.match(/https:\/\//g)||[]).length>=14,'sources');
check(m.claims.length>=30,'claims');
check(m.sources.length>=18,'source list');
check(m.release_gates.length>=30,'release gates');
check(m.release_gates.every(g=>g.status==='HOLD'&&g.passed===false),'all gates closed');
check(read('CONVERSION_ACCEPTANCE.md').includes('NOT COMPUTABLE'),'no invented revenue');
const unsafe=[
s=>s.replace('Final Vestige may earn a commission','No commercial relationship'),
s=>s.replace('type="button" disabled','type="button"'),
s=>s+'<script>alert(1)</script>',
s=>s+'<a href="https://zen12.com/">Buy</a>',
s=>s+'<form><input type="email"></form>'
];
for(const [i,f] of unsafe.entries()){
const s=f(a);
const valid=s.includes('Final Vestige may earn a commission')&&s.includes('button type="button" disabled')&&!/<script\b|<form\b|<a[^>]*href="https:\/\/zen12/i.test(s);
check(!valid,'unsafe mutation must fail '+i);
}
console.log('PASS '+n+' source and negative mutation assertions; native Node, not browser or merchant validation');

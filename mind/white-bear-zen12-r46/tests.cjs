'use strict';
const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const base=__dirname;const f=name=>fs.readFileSync(path.join(base,name),'utf8');
const a=f('zen12-guide-a.html'),b=f('zen12-guide-b.html'),i=f('investigation.html'),h=f('mind-hub-alternative.html'),m=f('CLAIM-MATRIX.csv'),source=f('SOURCE-REGISTER.md');
const privacy=require('./attribution.js');let count=0;function check(label,fn){fn();count++;console.log('PASS '+label);}
for(const [name,html] of [['guideA',a],['guideB',b],['article',i],['hub',h]]){
 check(name+' HTML semantics',()=>{assert.match(html,/<h1>/);assert.match(html,/<section/);assert.match(html,/focus-visible/);assert.match(html,/@media\(max-width:700px\)/);assert.match(html,/prefers-reduced-motion/);});
 check(name+' no merchant checkout link',()=>assert.doesNotMatch(html,/<a\s+[^>]*href=["'][^"']*(zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i));
 check(name+' no forms/scripts/redirect',()=>assert.doesNotMatch(html,/<(form|script|iframe)\b|on(click|load|error)\s*=|window\.location/i));
}
check('A and B substantive guide identical',()=>{const re=/<div id="fv-zen12-core">([\s\S]*?)<\/div>/;assert.equal(a.match(re)[1],b.match(re)[1]);});
for(const html of [a,b]){
 check('disclosure proximal and disabled hold',()=>{const disclosure=html.indexOf('If you purchase through a future authorized link');const hold=html.indexOf('aria-disabled="true"');assert(disclosure>0&&hold>disclosure&&hold-disclosure<700);assert.doesNotMatch(html,/<button\b|<a\b[^>]*\bhref=["'][^"']*checkout/);});
 check('no video autoplay fake play',()=>assert.doesNotMatch(html,/<video\b|\bautoplay\b|onclick=|<iframe\b/i));
}
check('article avoids shopping',()=>assert.doesNotMatch(i,/Zen12|Buy now|<form|affiliate disclosure/i));
check('variant B has transcript fallback',()=>assert.match(b,/<details>[\s\S]*full 40-second transcript/));
check('no alternate subscribe form',()=>assert.doesNotMatch(h,/<form|<input/));
check('source ledger contains exact official seller pages',()=>{assert.match(source,/https:\/\/zen12\.com\/hnp/);assert.match(source,/https:\/\/zen12\.com\/about/);});
check('matrix adequate claims',()=>assert(m.split('\n').length>=40));
check('privacy live hard off',()=>assert.equal(privacy.recordLiveEvent({}),false));
check('privacy rejects email',()=>assert.equal(privacy.normalize({channel:'direct',topic:'zen12',variant:'video',email:'a@b.com'}),null));
check('privacy rejects referrer/url',()=>assert.equal(privacy.normalize({channel:'direct',topic:'zen12',variant:'video',referrer:'https://foo.com/x'}),null));
check('privacy normalizes strict categorical fields',()=>assert.deepEqual({...privacy.normalize({channel:'direct',topic:'zen12',variant:'video'})},{channel:'direct',topic:'zen12',variant:'video'}));
check('privacy withholds small cells',()=>assert.equal(privacy.aggregateForReview(Array(19).fill({channel:'direct',topic:'zen12',variant:'video'})).length,0));
check('privacy emits 20 exactly',()=>assert.equal(privacy.aggregateForReview(Array(20).fill({channel:'direct',topic:'zen12',variant:'video'}))[0].count,20));
check('privacy minimum threshold',()=>assert.throws(()=>privacy.aggregateForReview([],10)));
check('privacy unknown channel rejected',()=>assert.equal(privacy.normalize({channel:'untrusted',topic:'zen12',variant:'video'}),null));
console.log('TOTAL '+count+' passed');
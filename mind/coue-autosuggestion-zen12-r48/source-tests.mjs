import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const read=f=>fs.readFileSync(new URL(f,import.meta.url),'utf8');
const A=read('zen12-text-a.html'), B=read('zen12-film-b.html'), I=read('investigation.html'),H=read('mind-hub-review.html');
const core=s=>s.match(/<div class="guide-core" id="substantive-guide">([\s\S]*?)<\/div>/)?.[1];
test('substantive guide identical A/B',()=>assert.equal(core(A),core(B)));
for(const [name,s] of [['A',A],['B',B]]){
 test(name+' disabled control',()=>assert.match(s,/<button[^>]*disabled[^>]*>/i));
 test(name+' disclosure near disabled button',()=>assert.match(s,/<section class="offer-hold"[\s\S]*?may earn a commission[\s\S]*?<button[^>]*disabled/i));
 test(name+' zero clickable merchant links',()=>assert.doesNotMatch(s,/<a\b[^>]*href=["'][^"']*(zen12\.com|inspire3\.com|hypnosislive\.com)/i));
 test(name+' no scripting, form, iframe or player',()=>assert.doesNotMatch(s,/<(?:script|form|iframe|video)\b/i));
 test(name+' one main heading',()=>assert.equal((s.match(/<h1\b/g)||[]).length,1));
}
test('original film concept readable',()=>{assert.match(B,/<svg/);assert.match(B,/Full proposed film transcript/);assert.match(read('film-captions.vtt'),/00:00:34\.000 --> 00:00:40\.000/)});
test('noncommercial historical article',()=>assert.doesNotMatch(I,/Zen12|Inspire3|affiliate|commission/i));
test('hub references single Focus, no new signup',()=>{assert.match(H,/finalvestige\.com\/focus\//);assert.doesNotMatch(H,/<form\b/i)});
test('merchant research URL in editor register',()=>assert.match(read('SOURCE-REGISTER.md'),/zen12\.com\/hnp/));

// R367 offline verification: node mind/r367/verify.mjs (run from repo root; no dependencies)
import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const dir=new URL('.',import.meta.url);
const read=p=>readFileSync(new URL(p,dir),'utf8');
const A=read('ZEN12_A_BUYER_GUIDE.html'), B=read('ZEN12_B_OPTIONAL_FILM_GUIDE.html'), H=read('MIND_ARCHIVE_SOURCE_ONLY.html'), M=JSON.parse(read('CLAIMS_SOURCES_RIGHTS.json')), V=read('ORIGINAL_42S_CAPTIONS.vtt'), C=read('CONVERSION_ACCEPTANCE.md'), N=read('THE_WORD_THAT_WASNT_THERE.md');
const tests=[];
const test=(name,fn)=>{try{fn();tests.push({name,pass:true});}catch(e){tests.push({name,pass:false,error:e.message});}};
const checkDoc=(s)=>{assert.match(s,/<meta name="robots" content="noindex,nofollow">/);assert.doesNotMatch(s,/<script\\b|<iframe\\b|<form\\b/ig);assert.doesNotMatch(s,/href="https?:\\/\\/(?:www\\.)?(?:zen12\\.com|affiliates\\.inspire3\\.com|hypnosislive\\.com|brainwaveshots\\.com)/ig);};
for(const [n,s] of [['A',A],['B',B],['hub',H]]){test(n+' noindex',()=>assert.match(s,/noindex,nofollow/));test(n+' no scripts/iframes/forms/merchant',()=>checkDoc(s));test(n+' native-disabled merchant',()=>assert.match(s,/<button[^>]+disabled>/));test(n+' accessible lang',()=>assert.match(s,/<html lang="en">/));}
const core=s=>s.match(/<main id="content">[\\s\\S]*?<\\/main>/)?.[0];
test('identical substantive main sections',()=>assert.equal(core(A),core(B)));
for(const [n,s] of [['A',A],['B',B]]){test(n+' nearby FTC disclosure',()=>assert.match(s,/<p><strong>Prospective affiliate disclosure:[\\s\\S]{0,500}<\\/p><button type="button" disabled>/));test(n+' accurate seller tier',()=>{assert.match(s,/48 MP3/);assert.match(s,/twelve-level/);});test(n+' no false endorsement',()=>assert.match(s,/has not purchased or used the course/));test(n+' free existing funnel',()=>assert.match(s,/https:\/\/finalvestige\.com\/focus\//));}
test('poster is static with transcript',()=>{assert.match(B,/<svg role="img"/);assert.match(B,/<details>/);assert.doesNotMatch(B,/<video|autoplay/ig);});
test('vtt six cues / 42 sec',()=>{assert.equal((V.match(/-->/g)||[]).length,6);assert.match(V,/00:00:35\.000 --> 00:00:42\.000/);});
test('matrix 32 claims',()=>assert.equal(M.claims.length,32));
test('matrix 32 gates all held',()=>{assert.equal(M.gates.length,32);assert.ok(M.gates.every(x=>x.status==='HOLD'));});
test('sources map to entries',()=>assert.ok(M.claims.every(x=>M.sources.some(s=>s.id===x.source_id))));
test('merchant absent from active guide links',()=>[A,B,H].forEach(s=>checkDoc(s)));
test('article credible historical and clinical boundary',()=>{assert.match(N,/Warren/);assert.match(N,/Samuel/);assert.match(N,/Leonard/);assert.match(N,/Puységur/);assert.match(N,/do not test Zen12/);});
test('first party events separate purchase/click',()=>{assert.match(C,/affiliate_click/);assert.match(C,/merchant_confirmed_purchase/);assert.match(C,/NOT COMPUTABLE/);});
const mutants=[A.replace(' disabled>','>'),A.replace('Prospective affiliate disclosure:',''),A.replace('noindex,nofollow','index,follow'),A+'<script>alert(1)</script>',A+'<form></form>',A+'<a href="https://zen12.com/">BUY</a>',A.replace('48 MP3','40 MP3'),B.replace(/<svg role="img"/,'<svg')];
const rejected=mutants.map((s,i)=>{try{if(i===0)assert.match(s,/<button type="button" disabled>/);if(i===1)assert.match(s,/Prospective affiliate disclosure:/);if(i===2)assert.match(s,/noindex,nofollow/);if(i>=3&&i<=5)checkDoc(s);if(i===6)assert.match(s,/48 MP3/);if(i===7)assert.match(s,/<svg role="img"/);return false;}catch{return true;}});
test('8 unsafe mutants rejected',()=>assert.ok(rejected.every(Boolean)));
const fails=tests.filter(x=>!x.pass);console.log(JSON.stringify({checks:tests.length,passed:tests.length-fails.length,rejected_mutants:rejected.filter(Boolean).length,errors:fails},null,2));if(fails.length)process.exitCode=1;
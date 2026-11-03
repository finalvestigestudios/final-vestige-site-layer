// Native test command: node --test mind/the-ink-refused-to-obey-r85/tests.mjs
import test from 'node:test'; import assert from 'node:assert/strict'; import {readFileSync} from 'node:fs';
import {acceptSyntheticCounter,summarizeSyntheticRows,MINIMUM_COHORT} from './privacy-model.mjs';
const read=x=>readFileSync(new URL(x,import.meta.url),'utf8');
const A=read('zen12-a-text.blocks.html'),B=read('zen12-b-optional-film.blocks.html'),core=read('zen12-guide-core.html');
const hub=read('mind-hub-noncanonical.blocks.html'),article=read('investigation.md'),matrix=JSON.parse(read('claim-source-permission-matrix.json'));
function coreMatch(x){return x.match(/<div class="fv-m85-guide"[^>]*>[\s\S]*?<\/div>/)?.[0];}
function guard(v){
 assert.equal((v.match(/<h1\b/g)||[]).length,1);
 assert.match(v,/<button\b[^>]*\sdisabled(?=\s|>)/);
 assert.match(v,/aria-disabled="true"/);
 assert.ok(v.indexOf('may earn a commission')>=0 && v.indexOf('may earn a commission')<v.indexOf('<button'));
 assert.doesNotMatch(v,/<(?:script|iframe|form|video|source)\b/i);
 assert.doesNotMatch(v,/href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com)/i);
 assert.doesNotMatch(v,/on(?:click|load|error|submit)\s*=/i);
}
test('guide core is exactly identical inside both variants',()=>{assert.equal(coreMatch(A),coreMatch(B));assert.equal(coreMatch(A),core)});
test('text-only and film candidates comply with disabled commerce, disclosure and inactive media constraints',()=>{guard(A);guard(B)});
test('film candidate contains six complete ordered caption/transcript scenes',()=>{assert.equal((B.match(/<time>/g)||[]).length,6);for(const t of ['0–6 s','6–13 s','13–20 s','20–27 s','27–34 s','34–40 s'])assert.ok(B.includes(t));});
test('no affiliate URL activation anywhere in core, variants or hub',()=>{for(const s of [A,B,hub])assert.doesNotMatch(s,/href=["']https?:\/\/(?:www\.)?(?:inspire3|zen12|affiliates\.inspire3)/i)});
test('hub has four streams, no new signup, and working existing editorial resource paths',()=>{assert.equal((hub.match(/class="card"/g)||[]).length,4);assert.match(hub,/finalvestige\.com\/focus\//);assert.match(hub,/puysegurs-animal-magnetism-files/);assert.doesNotMatch(hub,/<(?:form|script)\b/i)});
test('investigation remains commercial-free and historically sourced',()=>{assert.match(article,/47-second difference/);assert.match(article,/psychclassics\.yorku\.ca\/Stroop/);assert.doesNotMatch(article,/href=.*(?:zen12|inspire3)|affiliate commission|buy now/i)});
test('claims register records forbidden efficacy claims as non-adoptable',()=>{assert.ok(matrix.claims.length>=25);for(const id of ['hour_eq','auto_meditate','brainwaves','health_effect','earnings'])assert.match(matrix.claims.find(x=>x.id===id)?.decision||'',/OMIT/);assert.equal(matrix.affiliate_url,null);assert.ok(matrix.source_links.length>=17);});
test('all partner/release activation gates remain false',()=>{assert.ok(Object.keys(matrix.activation_gates).length>=15);assert.ok(Object.values(matrix.activation_gates).every(x=>x===false));});
test('privacy model rejects identifying and arbitrary fields',()=>{const x={topic:'stroop',variant:'text',source:'search',action:'offer_intent',count:5};assert.equal(acceptSyntheticCounter(x),true);for(const key of ['email','ip','visitor_id','url','user_agent','utm_campaign'])assert.equal(acceptSyntheticCounter({...x,[key]:'secret'}),false);assert.equal(acceptSyntheticCounter({...x,count:-1}),false)});
test('privacy synthetic aggregate suppresses groups smaller than twenty',()=>{const x={topic:'stroop',variant:'text',source:'search',action:'offer_intent'};assert.deepEqual(summarizeSyntheticRows([{...x,count:9},{...x,count:10}]),[]);assert.equal(summarizeSyntheticRows([{...x,count:11},{...x,count:9}])[0].count,MINIMUM_COHORT);});
test('adversarial mutations do not pass HTML safeguard',()=>{for(const p of [A,B]){assert.throws(()=>guard(p.replace(/\sdisabled(?=\s|>)/,'')),'removed native disabled must fail');assert.throws(()=>guard(p.replace('may earn a commission','may perhaps benefit')),'removed disclosure must fail');assert.throws(()=>guard(p.replace('</aside>','<form action="/collect"><input></form></aside>')),'inserted form must fail');assert.throws(()=>guard(p.replace('</aside>','<a href="https://zen12.com/hnp">Buy</a></aside>')),'inserted merchant link must fail');}});

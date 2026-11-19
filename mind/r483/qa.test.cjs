// R483 portable offline tests. Run with: node --test mind/r483/qa.test.cjs
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const get=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
test('commercial controls structurally disabled, disclosure adjacent and no purchase URL',()=>{
for(const file of ['ZEN12_A_BUYER_GUIDE.html','ZEN12_B_OPTIONAL_FILM_GUIDE.html']){
const x=get(file);
assert.match(x,/<button\b[^>]*\sdisabled\b/);
assert.match(x,/may earn a commission at no additional cost/);
assert.match(x,/No active affiliate link exists in this draft/);
assert.match(x,/<meta name="robots" content="noindex,nofollow">/);
assert.doesNotMatch(x,/<script\b|<form\b|\sautoplay(?:\s|=|>)/i);
const links=[...x.matchAll(/<a\b[^>]*href="([^"]+)"/g)].map(m=>m[1]);
assert.ok(links.every(h=>!/(?:affiliate_id|refersion|\/hop\/|[?&]hop=|[?&]ref=)/i.test(h)));
}
});
test('A/B preserve identical buyer text and B only adds film concept',()=>{
const a=get('ZEN12_A_BUYER_GUIDE.html'),b=get('ZEN12_B_OPTIONAL_FILM_GUIDE.html');
const begin=b.indexOf('<section class="panel" aria-labelledby="film-title">');
const end=b.indexOf('<section class="panel"><h2>Try a free twelve-minute baseline first</h2>');
assert.ok(begin>0&&end>begin);
assert.equal(b.slice(0,begin)+b.slice(end),a);
assert.match(b,/<details><summary>Read the complete 42-second scene transcript<\/summary>/);
assert.match(b,/role="img" aria-label=/);
});
test('six nonoverlapping captions cover exactly 42 seconds',()=>{
const c=get('R483_FILM_CAPTIONS.vtt');assert.match(c,/^WEBVTT/);
const a=[...c.matchAll(/00:00:(\d{2})\.\d{3} --> 00:00:(\d{2})\.\d{3}/g)].map(m=>[+m[1],+m[2]]);
assert.equal(a.length,6);assert.equal(a[0][0],0);assert.equal(a.at(-1)[1],42);
a.forEach((x,i)=>{assert.ok(x[1]>x[0]);if(i)assert.equal(x[0],a[i-1][1]);});
});
test('claim decision source IDs resolve; activation remains hard held',()=>{
const j=JSON.parse(get('PRODUCT_CLAIM_PERMISSION_MATRIX.json'));assert.equal(j.safe_to_activate,false);
const ids=new Set(j.sources.map(x=>x.id));j.claims.forEach(x=>assert.ok(ids.has(x.source_id)));
assert.ok(j.claims.length>=15);assert.ok(j.release_gates.every(x=>x.status==='NOT CLEARED'));
});
test('single existing Focus link; archive has no new form or scripts',()=>{
const h=get('MIND_HUB_SOURCE_ONLY.html');
assert.match(h,/finalvestige.com\/focus/);assert.match(h,/puysegurs-animal-magnetism-files/);
assert.doesNotMatch(h,/<form\b|<script\b/);
});
test('primary sources and commercial caveats',()=>{
const x=get('THE_CLOCK_THAT_STOLE_A_SECOND.md');
for(const key of ['35104551','01219-8','00413-5','s41598-020-73830-6','Puységur','did not test'])assert.ok(x.includes(key),key);
assert.ok(x.split(/\s+/).length>=1500);
});
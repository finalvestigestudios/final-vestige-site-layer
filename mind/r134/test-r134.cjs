// node mind/r134/test-r134.cjs from a repository checkout. No packages, network or secrets.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const get=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
const A=get('zen12-text-A.html'),B=get('zen12-optional-film-B.html');
const j=JSON.parse(get('source-claim-matrix.json'));const hub=get('wordpress-mind-hub-draft.html'),a=get('meditation-adverse-experiences.md'),plan=get('conversion-plan.md');
let passed=0;function ck(msg,fn){fn();passed++;}
ck('sources unique',()=>assert.equal(new Set(j.sources.map(x=>x.id)).size,j.sources.length));
ck('claims sourced',()=>assert(j.claims.every(x=>j.sources.some(s=>s.id===x.source))));
ck('partner not authorized',()=>assert.equal(j.affiliate_approval_verified,false));
ck('no approved earning URL',()=>assert.equal(j.approved_earning_link,null));
ck('all gates closed',()=>assert(j.gates.length>=12&&j.gates.every(x=>x.status==='CLOSED')));
for(const [name,h] of [['A',A],['B',B]]){
ck(name+' purchase disabled',()=>assert(/<button[^>]*disabled/.test(h)));
ck(name+' disclosure before CTA',()=>assert(/class="disclosure"[\s\S]*?<button/.test(h)));
ck(name+' no scripts or forms',()=>assert(!/<(?:script|form|iframe|video|audio)\b/i.test(h)));
ck(name+' free voluntary Focus',()=>assert(h.includes('https://finalvestige.com/focus/')));
ck(name+' no merchant earning anchors',()=>assert(!/<a[^>]*href="https:\/\/(zen12|inspire3)/i.test(h)));
ck(name+' accessible focus styles',()=>assert(h.includes(':focus-visible')));
ck(name+' no autoplay',()=>assert(!/autoplay\s*=|autoplay>/i.test(h)));
}
ck('B adds exactly the film section',()=>{let plain=B.replace(/<section class="film"[\s\S]*?<\/section>/,'').replace('Mind R134 B,','Mind R134 A,');assert.equal(plain,A);});
ck('B film transcript timecodes',()=>assert(B.includes('<details>')&&B.includes('34–40s')));
ck('A no video concept',()=>assert(!A.includes('Optional 40-second')));
ck('hub four streams',()=>assert(hub.includes('Perception & attention')&&hub.includes('Tools under review')&&hub.includes('History of suggestion')));
ck('hub no form script',()=>assert(!/<(?:script|form|iframe)\b/.test(hub)));
ck('investigation free of affiliate endorsement',()=>assert(a.includes('affiliate_endorsement: none')&&!a.includes('https://affiliates.inspire3.com/')));
ck('separate merchant opt-in',()=>assert(plan.includes('merchant newsletter')&&A.includes('separate opt-in')));
ck('click not purchase',()=>assert(plan.includes('not** paid orders')&&plan.includes('NOT_COMPUTABLE')));
ck('no analytics cookies',()=>assert(!/localStorage|document\.cookie|gtag\(/i.test(A+B+hub)));
ck('no merchant proof extrapolation',()=>assert(j.claims.some(x=>x.status==='REJECT_UNSUBSTANTIATED')));
console.log('R134 PASS '+passed+' structural checks');

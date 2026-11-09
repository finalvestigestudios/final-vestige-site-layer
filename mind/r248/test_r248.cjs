'use strict';
/** Final Vestige Mind R248: runnable source-level validation.
 * Run from full repo checkout: node mind/r248/test_r248.cjs
 * Does not perform hosted CI, live commerce, browser, WordPress or rendered-video QA.
 * Git blob SHA1 verifies a retrieved byte identity, not a digital signature.
 */
const fs=require('node:fs');
const crypto=require('node:crypto');
const assert=require('node:assert/strict');
const path=require('node:path');
const paths={
 article:'mind/r248/TWELVE-MINUTES-IS-A-DURATION-NOT-A-RESULT-UNPUBLISHED.md',
 A:'mind/r248/zen12-buyer-text-A-UNPUBLISHED.html',
 B:'mind/r248/zen12-buyer-optional-video-B-UNPUBLISHED.html',
 vtt:'mind/r248/zen12-evidence-42sec.vtt',
 matrix:'mind/r248/CLAIM-PROOF-PARTNER-COMMERCE-GATES.json',
 plan:'mind/r248/CONVERSION-RELEASE-ATTRIBUTION-AND-CANONICAL-ACCEPTANCE.md',
 r247article:'mind/r247/WHEN-HYPNOSIS-MET-A-FAIRER-COMPARISON-UNPUBLISHED.md',
 r247html:'mind/r247/total-focus-buyer-guide-WP-SOURCE-UNPUBLISHED.html',
 r247matrix:'mind/r247/PRODUCT-CLAIMS-2026-REVIEW-COMMERCIAL-GATES.json',
 r247plan:'mind/r247/OFFER-FUNNEL-CREATOR-AB-REVENUE-ACCEPTANCE.md',
 r247test:'mind/r247/test_r247.cjs'
};
const pins={
 article:'743daca5fdf6558bd30e6619fa709a1705e39481',
 A:'e920ea9c8983af2867b61f62a6d3e036fb8181a7',
 B:'7a2ed7ff9b784a721edf4e425613eb5d3aaf2ddc',
 vtt:'9879c96132ae2fb3241b8c0b79aa1d35b69406c5',
 matrix:'bfd1c6cd800bd5c1d8481a56a9f4c001cae32fdb',
 plan:'5ffda6c9445fc903de507774cee7df2bce6833d9',
 r247article:'bfbdda370a31c205f7233e127261940b5ca08c3c',
 r247html:'27637485f0ffa0e4391bff71a7b04168c9064ca6',
 r247matrix:'c17c2d010a8ae540bf9eb79ac7ef2113a7eab862',
 r247plan:'bbe3290c24bee041c00360a415761af754ddd5bf',
 r247test:'2f3876a74bd6f04e9d01a244ccb563943ab33b55'
};
function gitBlob(buf){return crypto.createHash('sha1').update('blob '+buf.length+'\0').update(buf).digest('hex');}
function read(root='.'){
 const result={};
 for(const [k,p] of Object.entries(paths)){
  const bytes=fs.readFileSync(path.join(root,p));
  assert.equal(gitBlob(bytes),pins[k],'Git blob identity '+k);
  result[k]=bytes.toString('utf8');
 }
 return result;
}
function check(data){
 const d=JSON.parse(data.matrix);
 assert.equal(d.scope,'UNPUBLISHED_SOURCE_ONLY');assert.equal(d.commerce_release,'HARD_HOLD');
 assert.equal(d.sources.length,20);assert.equal(d.claims.length,33);assert.equal(d.gates.length,16);
 const ids=a=>new Set(a.map(x=>x.id));
 assert.equal(ids(d.sources).size,d.sources.length,'unique source IDs');
 assert.equal(ids(d.claims).size,d.claims.length,'unique claim IDs');
 assert.equal(ids(d.gates).size,d.gates.length,'unique gate IDs');
 const src=ids(d.sources);
 for(const s of d.sources){assert.ok(/^https:\/\//.test(s.url),'https sources');assert.ok(s.what.length>25,'provenance');}
 for(const c of d.claims){assert.ok(src.has(c.source),'claim references real source '+c.id);assert.ok(c.statement.length>30,'claim content');}
 for(const g of d.gates){assert.equal(g.state,'HARD_HOLD');assert.equal(g.verified,false);assert.equal(g.proof,null);}
 assert.equal(d.primary_offer.earning_url,null);
 assert.equal(d.primary_offer.affiliate_approval,'UNKNOWN');
 assert.equal(d.fallback_owned.sku,null);
 assert.equal(d.commerce_metrics.status,'NOT_COMPUTABLE');
 for(const [k,v] of Object.entries(d.commerce_metrics))if(k!=='status')assert.equal(v,null,'invented metric '+k);
 assert.equal(d.claims.find(c=>c.id==='ZEN_CLAIM').policy,'DO_NOT_ASSERT');
 assert.equal(d.claims.find(c=>c.id==='AFF_ACCEPT').classification,'ACCOUNT_SPECIFIC_NOT_VERIFIED');
 assert.equal(d.claims.find(c=>c.id==='HYP_REFUND').statement.includes('five sessions'),true);
 assert.equal(d.claims.find(c=>c.id==='BWF_REFUND').statement.includes('six months'),true);

 const article=data.article;
 assert.ok(article.split(/\s+/).length>=2700,'original long-form article');
 for(const evidence of ['Twelve Minutes Is a Duration','Five reported findings','eight reported','twenty-eight eligible','2,574','Puységur','one-year','twelve minutes','not a blinded experiment','2026','https://pubmed.ncbi.nlm.nih.gov/37205669/','https://doi.org/10.1002/smi.3324','https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance'])assert.ok(article.includes(evidence),'article evidence '+evidence);
 assert.ok(article.includes('not a product endorsement')||article.includes('not a product endorsement'.replace('product','commercial')),'independence');
 assert.ok(article.includes('not a dose-conversion table'),'no false equivalence');

 function checkPage(h,name){
  assert.ok(/^<!doctype html>/i.test(h));assert.ok(h.includes('<html lang="en">'));
  assert.ok(h.includes('name="robots" content="noindex,nofollow"'));
  assert.ok(h.includes('prefers-reduced-motion:reduce')&&h.includes(':focus-visible'),'a11y scaffolding');
  assert.equal((h.match(/<h1\b/gi)||[]).length,1,'unique h1');
  assert.equal((h.match(/<button\b/gi)||[]).length,1,'one merchant decision control');
  const btn=h.match(/<button\b[^>]*>/i);assert.ok(btn,'native button');
  assert.ok(/\sdisabled(?:\s|>)/.test(btn[0]),'native disabled');
  assert.ok(btn[0].includes('aria-disabled="true"')&&btn[0].includes('aria-describedby="commercial-hold"'),'disabled reason');
  assert.ok(h.includes('id="commercial-hold"'));
  const disc=h.indexOf('Prospective affiliate disclosure:'),pos=h.indexOf('<button');
  assert.ok(disc>=0&&pos>disc&&pos-disc<550,'FTC disclosure adjacent');
  assert.ok(h.includes('may earn a commission at no additional cost to you'));
  assert.ok(h.includes('No earning link, redirect or payment tracking is active here.'));
  assert.ok(h.includes('https://finalvestige.com/focus/'),'one existing free path');
  assert.ok(!/<\s*(script|form|input|iframe|video|audio|source|track|embed|object|link|img)\b/i.test(h),'no tracking/form/external asset/pseudo video');
  assert.ok(!/\son[a-z][a-z0-9_-]*\s*=/i.test(h),'no inline event handler');
  assert.ok(!/javascript\s*:|data\s*:|@import|url\s*\(/i.test(h),'no external JS/css/data');
  assert.ok(!/https?:\/\/(?:www\.)?(?:zen12|inspire3|affiliates\.inspire3|hypnosislive|brainwaveshots)\.com/i.test((h.match(/<a\b[^>]*>/gi)||[]).join('\n')),'no active merchant href');
  const anchors=[...h.matchAll(/<a\b[^>]*href\s*=\s*(["'])(.*?)\1/gi)].map(m=>m[2]);
  for(const u of anchors){assert.ok(/^https:\/\/(?:finalvestige\.com|pubmed\.ncbi\.nlm\.nih\.gov|doi\.org|www\.nccih\.nih\.gov)\//.test(u),'restricted editorial link: '+u);}
  const svgIds=[...h.matchAll(/<(?:(?:title|desc))\s+id="([^"]+)"/g)].map(m=>m[1]);
  assert.equal(new Set(svgIds).size,svgIds.length,'unique SVG accessible labels');
  assert.equal((h.match(/<svg\b/gi)||[]).length,(h.match(/<desc\b/gi)||[]).length,'SVG descriptions');
  assert.ok(!/<video[^>]*\sautoplay(?:\s|>)/i.test(h),'no actual autoplay player attribute');
  return true;
 }
 checkPage(data.A,'A');checkPage(data.B,'B');
 assert.ok(!data.A.includes('<section id="short"'),'A text only');
 const section=data.B.match(/<section id="short"[\s\S]*?<\/section>/);
 assert.ok(section,'B optional video section');
 assert.equal(data.B.replace(section[0],''),data.A,'A/B identical except optional section');
 assert.ok(section[0].includes('not a rendered or playable video'),'no false render');
 assert.ok(section[0].includes('42-second')&&section[0].includes('0–6s:')&&section[0].includes('36–42s:'));
 assert.ok(section[0].includes('mind/r248/zen12-evidence-42sec.vtt'));
 const lines=data.vtt.trim().split(/\r?\n/);
 assert.equal(lines[0],'WEBVTT');
 const times=[...data.vtt.matchAll(/^(\d{2}):(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2}):(\d{2})\.(\d{3})$/gm)].map(m=>[Number(m[3])*1000+Number(m[4]),Number(m[7])*1000+Number(m[8])]);
 assert.equal(times.length,7,'seven captions');
 assert.equal(times[0][0],0);assert.equal(times.at(-1)[1],42000);
 for(let i=0;i<times.length;i++){assert.equal(times[i][1]-times[i][0],6000);if(i)assert.equal(times[i][0],times[i-1][1]);}

 const p=data.plan;
 for(const s of ['HARD_HOLD','NOT_COMPUTABLE','FV-owned fallback','Prospective affiliate disclosure','provider_confirmed_lead','affiliate_click','affiliate_settled_commission','refunds/chargebacks NOT already included','#150','PR #172','TASK-008','360/390/768/1440/1920px'])assert.ok(p.includes(s),'plan '+s);
 assert.ok(data.r247article.includes('I² = 65.4%'),'active comparator heterogeneity repair');
 assert.ok(data.r247article.includes('VERY LOW'),'Jones evidence certainty repair');
 assert.ok(data.r247article.includes('maximum of five refunded sessions per year'),'merchant exact FAQ repair');
 assert.ok(data.r247article.includes('R190'),'canonical overlap caveat');
 assert.ok(data.r247html.includes('five sessions per year'),'inherited buyer guide refund fix');
 assert.ok(data.r247plan.includes('fees NOT already netted'),'double deduction fix');
 assert.ok(JSON.parse(data.r247matrix).claims.find(x=>x.id==='SELLER_POLICY').statement.includes('five refunded sessions per year'),'matrix refund repair');
 assert.ok(data.r247test.includes('unique commerce gate IDs'),'inherited test stronger');
}
function negativeCases(d){
 const cases=[];
 const tamper=(k,fn)=>{const t={...d};t[k]=fn(t[k]);return t;};
 for(const gate of JSON.parse(d.matrix).gates){
  cases.push(()=>tamper('matrix',s=>{const x=JSON.parse(s);x.gates.find(g=>g.id===gate.id).state='PASS';return JSON.stringify(x);}));
 }
 cases.push(
  ()=>tamper('matrix',s=>{const x=JSON.parse(s);x.gates[1].id=x.gates[0].id;return JSON.stringify(x);}),
  ()=>tamper('matrix',s=>{const x=JSON.parse(s);x.primary_offer.earning_url='https://example.test/affiliate';return JSON.stringify(x);}),
  ()=>tamper('matrix',s=>{const x=JSON.parse(s);x.commerce_metrics.verified_paid_orders=1;return JSON.stringify(x);}),
  ()=>tamper('matrix',s=>{const x=JSON.parse(s);x.claims[0].source='FAKE';return JSON.stringify(x);}),
  ()=>tamper('matrix',s=>{const x=JSON.parse(s);x.claims[1].id=x.claims[0].id;return JSON.stringify(x);}),
  ()=>tamper('matrix',s=>{const x=JSON.parse(s);x.sources[0].url='http://not-secure.test';return JSON.stringify(x);}),
  ()=>tamper('matrix',s=>{const x=JSON.parse(s);x.claims.find(c=>c.id==='ZEN_CLAIM').policy='ALLOWED';return JSON.stringify(x);}),
  ()=>tamper('A',s=>s.replace(' disabled aria-disabled',' aria-disabled')),
  ()=>tamper('B',s=>s.replace(' disabled aria-disabled',' aria-disabled')),
  ()=>tamper('A',s=>s.replace('Prospective affiliate disclosure:','No disclosures:')),
  ()=>tamper('B',s=>s.replace('Prospective affiliate disclosure:','No disclosures:')),
  ()=>tamper('A',s=>s.replace('</main>','<a href="https://zen12.com/hnp">shop</a></main>')),
  ()=>tamper('B',s=>s.replace('</main>','<a href="https://hypnosislive.com/faq">shop</a></main>')),
  ()=>tamper('A',s=>s.replace('</main>','<script src="https://evil.test/x.js"></script></main>')),
  ()=>tamper('B',s=>s.replace('</main>','<form action="/subscribe"><input name="email"></form></main>')),
  ()=>tamper('A',s=>s.replace('</main>','<img src="https://evil.test/pixel"></main>')),
  ()=>tamper('B',s=>s.replace('</main>','<button disabled aria-disabled="true">second button</button></main>')),
  ()=>tamper('A',s=>s.replace('href="https://finalvestige.com/focus/"','href="javascript:alert(1)"')),
  ()=>tamper('B',s=>s.replace('id="viztitle-short"','id="viztitle"')),
  ()=>tamper('B',s=>s.replace('<section id="short"','<section id="second-video"')),
  ()=>tamper('vtt',s=>s.replace('00:00:42.000','00:00:41.000')),
  ()=>tamper('vtt',s=>s.replace('00:00:06.000','00:00:07.000')),
  ()=>tamper('article',s=>s.replace('not a dose-conversion table','a dose-conversion table')),
  ()=>tamper('article',s=>s.replace('https://doi.org/10.1002/smi.3324','https://example.test')),
  ()=>tamper('plan',s=>s.replace('refunds/chargebacks NOT already included','refunds/chargebacks')),
  ()=>tamper('r247article',s=>s.replace('VERY LOW','HIGH')),
  ()=>tamper('r247html',s=>s.replace('five sessions per year','unlimited refunds'))
 );
 return cases;
}
function run(data){
 check(data);let passed=0;
 for(const [i,fn] of negativeCases(data).entries()){
  assert.throws(()=>check(fn()),undefined,'unsafe mutation '+i+' escaped');
  passed++;
 }
 return {baseline:'PASS',negative_cases_rejected:passed,source_identities:Object.keys(paths).length};
}
if(require.main===module){const r=run(read('.'));console.log('FV Mind R248 source-level',r);}
module.exports={paths,pins,read,check,negativeCases,run};

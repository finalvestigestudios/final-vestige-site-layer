'use strict';
/** FV Mind R247 source-only regression.
 * Authentic local command from repository root: node mind/r247/test_r247.cjs
 * Requires Node + full checkout. Static PASS is not browser/WP/email/merchant proof.
 * Git blob SHA-1 identities are integrity pins, not digital signatures.
 */
const fs=require('node:fs'), crypto=require('node:crypto');
const paths=Object.freeze({
 article:'mind/r247/WHEN-HYPNOSIS-MET-A-FAIRER-COMPARISON-UNPUBLISHED.md',
 html:'mind/r247/total-focus-buyer-guide-WP-SOURCE-UNPUBLISHED.html',
 matrix:'mind/r247/PRODUCT-CLAIMS-2026-REVIEW-COMMERCIAL-GATES.json',
 plan:'mind/r247/OFFER-FUNNEL-CREATOR-AB-REVENUE-ACCEPTANCE.md',
 repairedArticle:'mind/r246/THE-FACE-THAT-CHANGED-WHEN-TURNED-UNPUBLISHED.md',
 repairedMatrix:'mind/r246/EVIDENCE-PRODUCT-CONVERSION-GATES.json',
 repairedTest:'mind/r246/test_r246.cjs'
});
const pins=Object.freeze({
 article:'8d6a391a61f776b5d3251fbd45cc949fd5cc0e4a',
 html:'294b8bf2e6e00580012846d27fe3fe7208937c64',
 matrix:'f33f8969b053106895aefc0f87be3d4c00f47278',
 plan:'fcc50a9e605bde8c9b1ccb4fcd06f83354e24df9',
 repairedArticle:'fe583b478c41aa3ebe7dddb8a05fdfb5a43ffea8',
 repairedMatrix:'78f1ac986c9ba4e28dd0b4c3e5eb09185b564622',
 repairedTest:'ce094c0210b8a9936835245755880f9222c02699'
});
function check(flag,why){if(!flag)throw Error('R247: '+why)}
function load(repoRoot='.'){
 const data={};
 for(const [key,path] of Object.entries(paths)){
  const buf=fs.readFileSync(repoRoot+'/'+path);
  const blob=crypto.createHash('sha1').update('blob '+buf.length+'\0').update(buf).digest('hex');
  check(blob===pins[key],'pinned source identity '+key+' got '+blob);
  data[key]=buf.toString('utf8');
 }
 return data;
}
function validate(data){
 check(Object.keys(paths).every(k=>typeof data[k]==='string'&&data[k].length>100),'all required inputs');
 const a=data.article;
 check(a.split(/\s+/).length>2300,'article deeply written');
 for(const s of ['Yim and Derbyshire','September 2, 2026','clinical pain','relaxation','Puységur','1784','14 studies','940 people','−0.13','−0.33','not a test of','Seven Day Focus Fieldbook','no need to mock']){
  check(a.includes(s),'article nuanced evidence '+s);
 }
 check(a.includes('https://pubmed.ncbi.nlm.nih.gov/39263007/') && a.includes('https://pubmed.ncbi.nlm.nih.gov/40649035/') && a.includes('https://pmc.ncbi.nlm.nih.gov/articles/PMC13535766/'),'original citations');
 check(a.includes('not a clinical')||a.includes('not medical advice'),'clinical caveat');
 const m=JSON.parse(data.matrix);
 check(m.scope==='UNPUBLISHED_SOURCE_ONLY'&&m.commerce_release==='HARD_HOLD','matrix scope');
 check(m.sources.length===16&&m.claims.length===26&&m.gates.length===16,'exact evidence record counts');
 const sources=new Set(m.sources.map(x=>x.id));
 check(sources.size===16 && new Set(m.claims.map(x=>x.id)).size===26,'unique evidence IDs');
 for(const x of m.sources)check(x.url.startsWith('https://')&&x.what.length>20,'actual source url/provenance '+x.id);
 for(const x of m.claims)check(sources.has(x.source)&&x.statement.length>30&&x.classification.length>5,'claim grounded '+x.id);
 for(const x of m.gates)check(x.state==='HARD_HOLD'&&x.verified===false&&x.proof===null,'commercial gate remains shut '+x.id);
 for(const [k,v] of Object.entries(m.commerce_metrics))if(k!=='status')check(v===null,'no invented earnings '+k);
 check(m.commerce_metrics.status==='NOT_COMPUTABLE','no invented zero numerator or denominator');
 check(m.claims.some(x=>x.id==='REV_ACTIVE'&&x.classification==='INDEPENDENT_SUPPORTED_BOUNDED'),'active comparator');
 check(m.claims.some(x=>x.id==='REV_PRODUCT'&&x.classification==='NOT_SUPPORTED_FOR_PRODUCT'),'no product extrapolation');
 check(m.claims.some(x=>x.id==='TH_REVIEW'&&x.source==='TH_CRIT'),'correction trace');

 const h=data.html;
 check(h.startsWith('<!doctype html>')&&h.includes('<html lang="en">')&&h.includes('name="viewport"'),'accessible document');
 check(h.includes('name="robots" content="noindex,nofollow"'),'draft not indexable');
 check(h.includes('prefers-reduced-motion:reduce')&&h.includes(':focus-visible'),'motion/focus');
 check(h.includes('role="img"')&&h.includes('<title id="pt">')&&h.includes('<desc id="pd">'),'original accessible poster');
 check(h.includes('<details>')&&h.includes('</details>')&&h.includes('0–7s:')&&h.includes('35–42s:'),'accessible 42s storyboard concept');
 check(!/<\s*(script|form|input|iframe|video|audio|track|source|picture|img|link|object|embed|canvas|template)\b/i.test(h),'no scripts/forms/remote loads/autoplay');
 check(!/\s+on[a-z][a-z0-9_-]*\s*=/i.test(h)&&!/javascript\s*:|data\s*:|@import\b|url\s*\(/i.test(h),'no handlers/JS/data URLs/css loads');
 check((h.match(/<button\b/gi)||[]).length===1,'one disclosure-adjacent CTA');
 check(/<button\b(?=[^>]*\sdisabled(?:\s|>))(?=[^>]*aria-disabled="true")(?=[^>]*aria-describedby="hold")[^>]*>/.test(h),'native disabled button');
 const disc=h.indexOf('Prospective affiliate disclosure:'),btn=h.indexOf('<button');
 check(disc>=0&&btn>disc&&btn-disc<600,'disclosure immediately preceding held CTA');
 check(h.includes('may earn a commission at no additional cost to you'),'FTC near-link language');
 check(h.includes('No affiliate tracking or payment link is active here'),'claims truthful');
 check(h.includes('existing Jetpack/Dispatch path')&&h.includes('No second signup'),'one approved funnel');
 check(!/href\s*=\s*["'][^"']*(zen12\.com|hypnosislive\.com|brainwaveshots\.com|inspire3\.com|awin1\.com|payhip\.com)/i.test(h),'no merchant link even informational');
 for(const found of h.matchAll(/<a\s+[^>]*href="([^"]+)"/gi)){
   const u=new URL(found[1]);
   check(u.protocol==='https:'&&['finalvestige.com','pmc.ncbi.nlm.nih.gov','pubmed.ncbi.nlm.nih.gov'].includes(u.hostname),'allowlisted editorial href '+u.hostname);
   check(!u.search&&!u.username&&!u.password,'no leaked query/credentials');
 }
 check(!/<a[^>]*\btarget=/i.test(h),'no target/noopener leak');
 const plan=data.plan;
 for(const s of ['16 commercial gates','NOT_COMPUTABLE','Grok','Praxxis','Dispatch #174','#1681','qualified-human','Seven Day Focus Fieldbook','A text-only','B identical']){
   check(plan.toLowerCase().includes(s.toLowerCase()),'acceptance scope '+s);
 }
 check(plan.includes('incremental attributable operating cost') && plan.includes('Never assign per-video attribution'),'not counted twice or fabricated video');
 check(data.repairedArticle.includes('p = .058')&&data.repairedArticle.includes('published 2014 commentary')&&data.repairedArticle.includes('between-region interaction test'),'scientific correction in article');
 const r=JSON.parse(data.repairedMatrix);
 check(r.sources.length===22&&r.claims.length===34&&r.sources.some(x=>x.id==='TH_REZ')&&r.claims.some(x=>x.id==='TH_CRITIQUE'&&x.source==='TH_REZ'),'scientific critique provenance');
 check(data.repairedTest.includes("['sources',22]")&&data.repairedTest.includes("'TH_CRITIQUE'"),'inherited regression repinned for corrections');
 return true;
}
function mutations(data){
 let count=0;const failures=[];
 function attack(label,fn){const c=Object.assign({},data);fn(c);try{validate(c);failures.push(label)}catch(e){count++}}
 const edit=(key,find,repl)=>attack(key+' '+find.slice(0,40),d=>{check(d[key].includes(find),'attack target exists: '+find);d[key]=d[key].replace(find,repl)});
 // Actual source and science edits
 for(const [a,b] of [
 ['14 studies','1400 studies'],['940 people','94000 people'],['−0.13','−1.3'],['−0.33','−3.3'],
 ['clinical pain','dramatically improved focus'],['September 2, 2026','September 2, 2025'],
 ['Puységur','a famous hypnotist'],['Seven Day Focus Fieldbook','Magic Focus Guarantee'],
 ['https://pubmed.ncbi.nlm.nih.gov/39263007/','https://example.com/claim'],
 ['no need to mock','no need to fact-check']
 ]) edit('article',a,b);
 // HTML dangerous activation and privacy regression
 for(const [a,b] of [
 [' disabled aria-disabled',' aria-disabled'],['aria-disabled="true"','aria-disabled="false"'],
 ['aria-describedby="hold"','aria-describedby="wrong"'],
 ['<button type="button"','<button type="button" onclick="pay()"'],
 ['</main>','<form action="/new-subscribe"><input type="email"></form></main>'],
 ['</main>','<script src="https://tracker.test/x.js"></script></main>'],
 ['</main>','<iframe src="https://tracker.test"></iframe></main>'],
 ['</main>','<video autoplay src="file.mp4"></video></main>'],
 ['</main>','<img src="https://tracker.test/pixel"></main>'],
 ['</main>','<button disabled>extra button</button></main>'],
 ['</main>','<a href="https://hypnosislive.com/mental-skills/total-focus">Merchant</a></main>'],
 ['</main>','<a href="https://phishing.test">Merchant</a></main>'],
 ['<details>','<section>'],['<title id="pt">','<title id="wrong">'],
 ['0–7s:','0–8s:'],['35–42s:','35–45s:'],
 ['Prospective affiliate disclosure:','No relationship information:'],
 ['may earn a commission at no additional cost to you','contains paid link'],
 ['No second signup','Join two new lists'],
 ['name="robots" content="noindex,nofollow"','name="robots" content="index,follow"'],
 ['prefers-reduced-motion:reduce','prefers-reduced-motion:false'],
 ['</main>','<link rel="preconnect" href="https://tracker.test"></main>'],
 ['</main>','<a href="https://finalvestige.com/focus/?email=private">Privacy leak</a></main>']
 ]) edit('html',a,b);
 for(const [a,b] of [
 ['16 commercial gates','16 cleared gates'],['NOT_COMPUTABLE','0.00'],['Grok','Mind agent posts'],
 ['Never assign per-video attribution','Assign every video a profile visit'],
 ['A text-only','A and B both videos'],['#1681','#123'],['incremental attributable operating cost','ignore fees']
 ]) edit('plan',a,b);
 edit('repairedArticle','p = .058','p < .05');
 edit('repairedArticle','between-region interaction test','settled fMRI region interaction');
 edit('repairedTest',"['sources',22]","['sources',21]");
 attack('forge affiliate eligibility',d=>{const j=JSON.parse(d.matrix);j.gates[0].verified=true;d.matrix=JSON.stringify(j)});
 attack('forge merchant revenue',d=>{const j=JSON.parse(d.matrix);j.commerce_metrics.realized_net_revenue=100;d.matrix=JSON.stringify(j)});
 attack('turn missing revenue to zero',d=>{const j=JSON.parse(d.matrix);j.commerce_metrics.status='ZERO';d.matrix=JSON.stringify(j)});
 attack('claim focus proven',d=>{const j=JSON.parse(d.matrix);j.claims.find(x=>x.id==='REV_PRODUCT').classification='INDEPENDENT_SUPPORTED';d.matrix=JSON.stringify(j)});
 attack('erase independent critique',d=>{const j=JSON.parse(d.repairedMatrix);j.sources=j.sources.filter(x=>x.id!=='TH_REZ');d.repairedMatrix=JSON.stringify(j)});
 attack('delete regulator',d=>{const j=JSON.parse(d.matrix);j.sources=j.sources.filter(x=>x.id!=='FTC_A');d.matrix=JSON.stringify(j)});
 attack('fake qualified sessions',d=>{const j=JSON.parse(d.matrix);j.commerce_metrics.qualified_human_sessions=2;d.matrix=JSON.stringify(j)});
 check(failures.length===0, 'unsafe mutations accepted: '+failures.join('; '));
 return {rejected:count,failures};
}
function run(){const data=load();validate(data);const out=mutations(data);console.log('R247 SOURCE VALIDATION PASS; '+Object.keys(paths).length+' identity pins; '+out.rejected+'/'+out.rejected+' malicious mutations REJECTED; NOT browser or partner proof');}
module.exports={paths,pins,load,validate,mutations};
if(require.main===module)run();

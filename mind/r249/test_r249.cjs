'use strict';
/** R249 source-level release guards. RUN from repository root:
 *   node mind/r249/test_r249.cjs
 * Native Node run requires the whole checkout. Separate browser, WP, merchant and CI QA is necessary.
 * Git blob SHA proves byte identity, not authorship, provenance or release permission.
 */
const fs=require('node:fs'), crypto=require('node:crypto'), path=require('node:path'), assert=require('node:assert/strict');
const pins={
 article:['mind/r249/THE-HALF-SECOND-YOUR-ATTENTION-COULD-NOT-HOLD-UNPUBLISHED.md','95a2a4905b5295d6cdbcbca03c1d711c85ededf4'],
 matrix:['mind/r249/ATTENTION-TO-OFFER-EVIDENCE-COMMERCIAL-HOLD.json','30c597f6a3701d45ea75d741bb0a843aa6fb0b92'],
 guide:['mind/r249/zen12-attentional-blink-presell-WP-PREVIEW-UNPUBLISHED.html','2a2900dca6b71e72fe0a5ea7d9ab599b2441bac3'],
 plan:['mind/r249/CONVERSION-OFFER-FUNNEL-ATTRIBUTION-ACCEPTANCE.md','9d6c26810dcba2a5fac91ee2f7d5f3daa3e8cde9'],
 correctedR248:['mind/r248/TWELVE-MINUTES-IS-A-DURATION-NOT-A-RESULT-UNPUBLISHED.md','648b26de43dd3832db0416fadbe63d621e813894'],
 correctedTest:['mind/r248/test_r248.cjs','b2d97b360bb45a4d468cea465efbafc75851bdc1']
};
function blob(bytes){return crypto.createHash('sha1').update('blob '+bytes.length+'\0').update(bytes).digest('hex');}
function read(root='.'){let data={};for(let [key,[p,sha]] of Object.entries(pins)){let b=fs.readFileSync(path.join(root,p));assert.equal(blob(b),sha,'Git blob '+key);data[key]=b.toString('utf8');}return data;}
function check(data){
 assert.ok(data.article.split(/\s+/).length>=2000,'long research');
 for(let word of ['17 practitioners','23 novices','10–12 hours per day','not a blinded','https://pubmed.ncbi.nlm.nih.gov/1500880/','https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.0050138','This is not a personal-use account'])assert.ok(data.article.includes(word),'source '+word);
 const d=JSON.parse(data.matrix);
 assert.equal(d.scope,'UNPUBLISHED_SOURCE_ONLY');assert.equal(d.release,'HARD_HOLD');
 assert.equal(d.sources.length,15);assert.equal(d.claims.length,19);assert.equal(d.gates.length,16);
 for(const arr of [d.sources,d.claims,d.gates])assert.equal(new Set(arr.map(x=>x.id)).size,arr.length,'unique IDs');
 const ids=new Set(d.sources.map(s=>s.id));for(const c of d.claims){assert.ok(ids.has(c.source),'valid claim source '+c.id);assert.ok(c.statement.length>38);}
 for(const g of d.gates){assert.equal(g.status,'HARD_HOLD');assert.equal(g.verified,false);assert.equal(g.evidence,null);}
 assert.equal(d.primary_offer.approval,'NOT_VERIFIED');
 assert.equal(d.primary_offer.account_earning_url,null);
 assert.equal(d.owned_fallback.sku,null);
 assert.equal(d.metrics.status,'NOT_COMPUTABLE');
 for(const [k,v] of Object.entries(d.metrics))if(k!=='status')assert.equal(v,null,'invented metric '+k);
 assert.equal(d.claims.find(x=>x.id==='ZEN_EQ').policy,'NEVER_ADOPT_AS_FACT');
 assert.equal(d.claims.find(x=>x.id==='AFF_PERMISSION').classification,'ACCOUNT_SPECIFIC_UNKNOWN');
 for(const s of d.sources)assert.ok(/^https:\/\//.test(s.url),'https source');
 const h=data.guide;
 assert.ok(/^<!doctype html>/i.test(h)&&h.includes('<html lang="en">'));
 assert.ok(h.includes('noindex,nofollow')&&h.includes('prefers-reduced-motion')&&h.includes(':focus-visible'));
 assert.equal((h.match(/<h1\b/g)||[]).length,1,'one H1');
 const btn=h.match(/<button\b[^>]*>/i);assert.ok(btn,'one button');
 assert.equal((h.match(/<button\b/gi)||[]).length,1,'one button only');
 assert.ok(/\sdisabled(?:\s|>)/.test(btn[0]),'native disabled button');
 assert.ok(btn[0].includes('aria-disabled="true"')&&btn[0].includes('aria-describedby="offerhold"'));
 assert.ok(h.includes('id="offerhold"'));
 const disc=h.indexOf('Prospective affiliate disclosure:'), bpos=h.indexOf('<button');assert.ok(disc>=0&&bpos>disc&&bpos-disc<550,'near-link FTC disclosure');
 assert.ok(h.includes('may earn a commission at no additional cost to you'));
 for(const re of [/<\s*(?:script|form|input|iframe|video|audio|source|track|embed|object|link|img)\b/i,/\son[a-z][a-z0-9_-]*\s*=/i,/javascript\s*:/i,/@import/i])assert.ok(!re.test(h),'forbidden active element/handler');
 assert.ok(!/<a\b[^>]*href=['"]https:\/\/(?:zen12|inspire3|affiliates\.inspire3|hypnosislive|brainwaveshots)\.com/i.test(h),'no merchant CTA');
 for(const match of h.matchAll(/<a\b[^>]*href="([^"]+)"/gi))assert.ok(/^https:\/\/(?:finalvestige\.com|pubmed\.ncbi\.nlm\.nih\.gov|journals\.plos\.org|www\.ftc\.gov)\//.test(match[1]),'only authorized research domains '+match[1]);
 assert.ok(h.includes('42-second film concept')&&h.includes('No playable, rendered or autoplay video'));
 assert.ok(h.includes('https://finalvestige.com/focus/'),'only established newsletter');
 for(const word of ['NOT_COMPUTABLE','HARD_HOLD','TASK-008','affiliate_click','qualified_human_sessions','7/30-day cohorts','#150','R248'])assert.ok(data.plan.includes(word),'plan '+word);
 assert.ok(data.correctedR248.includes('narrative synthesis')&&data.correctedR248.includes('Only 29%'),'Mandlik methodology repair');
 assert.ok(data.correctedTest.includes('Full WebVTT clock validation')&&data.correctedTest.includes('00:61:12.000'),'clock repair');
}
function negativeCases(d){
 const change=(k,f)=>{const x={...d};x[k]=f(d[k]);return x;};const matrix=(f)=>change('matrix',s=>{const x=JSON.parse(s);f(x);return JSON.stringify(x);});
 return [
 ...JSON.parse(d.matrix).gates.map(g=>()=>matrix(x=>x.gates.find(z=>z.id===g.id).status='PASS')),
 ()=>matrix(x=>x.gates[0].verified=true),
 ()=>matrix(x=>x.gates[0].evidence='claimed approval'),
 ()=>matrix(x=>x.gates[1].id=x.gates[0].id),
 ()=>matrix(x=>x.claims[0].source='NOT_IN_SOURCES'),
 ()=>matrix(x=>x.claims.find(c=>c.id==='ZEN_EQ').policy='ENDORSE'),
 ()=>matrix(x=>x.primary_offer.account_earning_url='https://example.test/aff'),
 ()=>matrix(x=>x.primary_offer.approval='APPROVED'),
 ()=>matrix(x=>x.metrics.independently_confirmed_paid_orders=1),
 ()=>matrix(x=>x.owned_fallback.sku='UNVERIFIED_SKU'),
 ()=>change('guide',s=>s.replace(' disabled aria-disabled',' aria-disabled')),
 ()=>change('guide',s=>s.replace('Prospective affiliate disclosure:','Omitted:')),
 ()=>change('guide',s=>s.replace('</main>','<a href="https://zen12.com/hnp">Buy</a></main>')),
 ()=>change('guide',s=>s.replace('</main>','<script src="https://pixel.test/x.js"></script></main>')),
 ()=>change('guide',s=>s.replace('</main>','<form><input name="email"></form></main>')),
 ()=>change('guide',s=>s.replace('href="https://finalvestige.com/focus/"','href="javascript:alert(1)"')),
 ()=>change('plan',s=>s.replace('affiliate_click','outbound')),
 ()=>change('correctedR248',s=>s.replace('Only 29%','Most')),
 ()=>change('correctedTest',s=>s.replace('Full WebVTT clock validation','Earlier vulnerable VTT')),
 ];
}
function run(d){check(d);let n=0;for(const fn of negativeCases(d)){assert.throws(()=>check(fn()),undefined,'unsafe change not rejected');n++;}return {baseline:'PASS',git_blob_ids:Object.keys(pins).length,negative_changes_rejected:n};}
if(require.main===module)console.log('R249 source-only regression',run(read('.')));
module.exports={pins,read,check,negativeCases,run};

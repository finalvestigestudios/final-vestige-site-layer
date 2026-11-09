'use strict';
/* R250 exact-source and negative mutation guard.
 * Full native local checkout: node mind/r250/test_r250.cjs
 * Includes inherited actual R248 and R249 runs, not merely marker checks.
 * Native Node execution is not implied by isolated V8 execution reports.
 * This suite does not test browser, WordPress, real commerce, paid transactions or video rendering.
 */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const pins={
 article:['mind/r250/THE-BROKEN-GLASS-NOBODY-SAW-UNPUBLISHED.md','86776abe24b464745de8f13ab062e796f7334531'],
 preview:['mind/r250/zen12-proof-before-play-PREVIEW-NO-COMMERCE.html','becb1ed7c2bf85b96b304badb9c634b8bdb51bdc'],
 matrix:['mind/r250/CLAIM-SOURCE-PARTNER-REVENUE-GATES.json','c94cc330b1c295b4463eb10451f60b133c28b366'],
 plan:['mind/r250/OFFER-FUNNEL-EXPERIMENT-CANONICAL-ACCEPTANCE.md','a37de9757f4c0c0e5ce6e0b9fb29f8080a2ce2b9'],
 r248test:['mind/r248/test_r248.cjs','c270327d69bc71e2cf27520a29f0c533f6347657'],
 r249test:['mind/r249/test_r249.cjs','ca92d29482259b1d98b33a0e5898b21d37c478e0']
};
function blob(b){return crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')}
function read(root='.'){const d={};for(const [k,[p,sha]] of Object.entries(pins)){const b=fs.readFileSync(path.join(root,p));assert.equal(blob(b),sha,'Git blob '+k);d[k]=b.toString('utf8')}return d}
function check(d){
 assert.ok(d.article.trim().split(/\s+/).length>=2650,'original long investigation');
 for(const w of ['The Broken Glass Nobody Saw','Loftus','1974','1978','1,242','2023','2019','Puységur','affiliate endorsement','https://pubmed.ncbi.nlm.nih.gov/621467/','https://doi.org/10.3389/fpsyg.2023.1201674'])assert.ok(d.article.includes(w),'source '+w);
 assert.ok(!/I (?:personally )?(?:used|tested|purchased) Zen12/i.test(d.article),'no fake trial');
 const m=JSON.parse(d.matrix);
 assert.equal(m.scope,'UNPUBLISHED_SOURCE_ONLY');assert.equal(m.release,'HARD_HOLD');
 assert.equal(m.sources.length,18);assert.equal(m.claims.length,22);assert.equal(m.gates.length,16);
 for(const rows of [m.sources,m.claims,m.gates])assert.equal(new Set(rows.map(x=>x.id)).size,rows.length,'unique source/claim/gate ids');
 const ids=new Set(m.sources.map(x=>x.id));
 for(const s of m.sources)assert.ok(/^https:\/\//.test(s.url),'https provenance');
 for(const c of m.claims){assert.ok(ids.has(c.source),'claim referenced real source '+c.id);assert.ok(c.statement.length>55); }
 for(const g of m.gates){assert.equal(g.status,'HARD_HOLD');assert.equal(g.verified,false);assert.equal(g.evidence,null)}
 assert.equal(m.primary_offer.approval,'NOT_VERIFIED');
 for(const key of ['account_earning_url','permitted_channels','net_commission','price_paid','refund_fulfillment'])assert.equal(m.primary_offer[key],null,'account-specific hold '+key);
 assert.equal(m.owned_fallback.sku,null);assert.equal(m.owned_fallback.commercial_activation,'NOT_AUTHORIZED');
 assert.equal(m.metrics.status,'NOT_COMPUTABLE');
 for(const [k,v] of Object.entries(m.metrics))if(k!=='status')assert.equal(v,null,'no invented revenue '+k);
 assert.equal(m.claims.find(c=>c.id==='C12').policy,'DO_NOT_ASSERT_AS_FACT');
 const h=d.preview;
 assert.ok(/^<!doctype html>/i.test(h)&&h.includes('<html lang="en">'),'valid document');
 assert.ok(h.includes('noindex,nofollow')&&h.includes(':focus-visible')&&h.includes('prefers-reduced-motion'),'preview a11y');
 assert.equal((h.match(/<h1\b/gi)||[]).length,1,'single heading');
 assert.equal((h.match(/<button\b/gi)||[]).length,1,'single decision control');
 const button=h.match(/<button\b[^>]*>/i);assert.ok(button);assert.ok(/\sdisabled(?:\s|>)/i.test(button[0]),'native disabled');
 assert.ok(button[0].includes('aria-disabled="true"')&&button[0].includes('aria-describedby="commercial-hold"'));
 assert.ok(h.includes('id="commercial-hold"'));
 const b=h.indexOf('<button'),disc=h.indexOf('Prospective affiliate disclosure:');
 assert.ok(disc>=0&&b>disc&&b-disc<950,'adjacent explicit FTC disclosure');
 assert.ok(h.includes('may earn a commission at no additional cost to you'));
 assert.ok(h.includes('No merchant purchase link is active on this draft.'));
 assert.ok(h.includes('https://finalvestige.com/focus/'),'preserves single Focus');
 assert.ok(h.includes('No rendered or playable video exists')&&h.includes('42-second'),'unrendered film labeled');
 assert.ok(!/<\s*(script|form|input|iframe|video|audio|source|track|embed|object|link|img)\b/i.test(h),'no active scripts/form/media/tracking');
 assert.ok(!/\son[a-z][a-z0-9_-]*\s*=/i.test(h),'no HTML handlers');
 assert.ok(!/javascript\s*:|data\s*:|@import|url\s*\(/i.test(h),'no hidden execution/remote assets');
 for(const a of h.matchAll(/<a\b[^>]*href=["']([^"']+)["']/gi)){
  assert.ok(/^https:\/\/(?:finalvestige\.com|pubmed\.ncbi\.nlm\.nih\.gov|www\.ftc\.gov)\//.test(a[1]),'research-only destinations '+a[1]);
 }
 assert.ok(h.includes('<svg')&&h.includes('<title id="a-title">')&&h.includes('<desc id="a-desc">'),'accessible original visual');
 const p=d.plan;
 for(const w of ['HARD_HOLD','NOT_COMPUTABLE','OFFER → FUNNEL STEP','TASK-008','R236','R248','47 unsafe','affiliate_click','utm_content=asset_id','360, 390, 768, 1440, 1920','Founder'])assert.ok(p.includes(w),'plan '+w);
 const cue=d.r248test.split('\n').find(x=>x.includes('const cuePattern='));
 assert.ok(cue,'clock parser');
 assert.ok(cue.includes('\\d{2}')&&cue.includes('\\.'),'actual regex must have digit and dot escapes');
 assert.ok(!cue.includes('\\\\d')&&!cue.includes('\\\\.'),'double escape regression');
 assert.ok(d.r249test.includes(pins.r248test[1]),'R249 pin accurate');
}
function negativeCases(d){
 const replace=(k,f)=>()=>({...d,[k]:f(d[k])});
 const m=(fn)=>replace('matrix',s=>{const v=JSON.parse(s);fn(v);return JSON.stringify(v)});
 return [
 ...JSON.parse(d.matrix).gates.map(g=>m(v=>{v.gates.find(t=>t.id===g.id).status='PASS'})),
 m(v=>v.gates[0].verified=true),m(v=>v.gates[0].evidence='fabricated approval'),
 m(v=>v.claims[0].source='FAKE_ID'),m(v=>v.claims[1].id=v.claims[0].id),
 m(v=>v.primary_offer.approval='APPROVED'),m(v=>v.primary_offer.account_earning_url='https://affiliate.example/track'),
 m(v=>v.primary_offer.permitted_channels=['website']),m(v=>v.metrics.verified_paid_orders=1),
 m(v=>v.owned_fallback.sku='UNVERIFIED_PRODUCT'),m(v=>v.claims.find(c=>c.id==='C12').policy='ENDORSE'),
 replace('preview',s=>s.replace(' disabled aria-disabled',' aria-disabled')),
 replace('preview',s=>s.replace('Prospective affiliate disclosure:','Disclosures omitted:')),
 replace('preview',s=>s.replace('</main>','<a href="https://zen12.com/hnp">Shop</a></main>')),
 replace('preview',s=>s.replace('</main>','<script src="https://pixel.example/x.js"></script></main>')),
 replace('preview',s=>s.replace('</main>','<form><input name="email"></form></main>')),
 replace('preview',s=>s.replace('</main>','<button disabled>Second button</button></main>')),
 replace('preview',s=>s.replace('href="https://finalvestige.com/focus/"','href="javascript:alert(1)"')),
 replace('preview',s=>s.replace('No rendered or playable video exists','Video plays automatically')),
 replace('article',s=>s.replace('1,242','12,420')),
 replace('plan',s=>s.replace('utm_content=asset_id','made-up-tag')),
 replace('r248test',s=>s.replace('Full WebVTT clock validation','Missing timestamp validation')),
 replace('r248test',s=>s.replace('const cuePattern=/^(','const cuePattern=/^(\\')),
 replace('r249test',s=>s.replace(pins.r248test[1],'incorrectsourcehash'))
 ];
}
function run(d){check(d);let count=0;for(const f of negativeCases(d)){assert.throws(()=>check(f()),undefined,'unsafe mutation was not rejected '+count);count++}return {baseline:'PASS',pins:Object.keys(pins).length,negative_cases_rejected:count}}
function runFullNative(){
 const r248=require('../r248/test_r248.cjs'), r249=require('../r249/test_r249.cjs');
 const a=r248.run(r248.read('.')), b=r249.run(r249.read('.')), c=run(read('.'));
 return {inherited_r248:a,inherited_r249:b,r250:c};
}
if(require.main===module)console.log('Mind R250 native full checkout',JSON.stringify(runFullNative()));
module.exports={pins,read,check,negativeCases,run,runFullNative};

'use strict';
/* Mind R251: exact-source, no-commerce, source-quality and mutation guard.
 * Native full checkout command: node mind/r251/test_r251.cjs
 * A passing source test is NOT actual browser/WP, merchant, consent, paid transaction,
 * or operational Core Web Vitals verification.
 */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const pins={
 article:['mind/r251/THE-HAND-THAT-WASNT-YOURS-UNPUBLISHED.md','cb8eff8a23811acff349777d42711a327614f221'],
 html:['mind/r251/MIND-ARCHIVE-UNPUBLISHED-WP-PREVIEW.html','a9f9372bce460c245e229972cd07f94d1d769baa'],
 matrix:['mind/r251/PRODUCT-CLAIM-AND-COMMERCE-AUTHORIZATION.json','9151185ee3571df8cbcda1af69fb966dc22bc8f6'],
 plan:['mind/r251/CANONICAL-OFFER-CREATOR-REVENUE-ACCEPTANCE.md','d75ff3630dc0a065d036fab14d3de686342e3b02']
};
function gitBlob(b){return crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')}
function read(root='.'){const out={};for(const [k,[p,hash]] of Object.entries(pins)){const b=fs.readFileSync(path.join(root,p));assert.equal(gitBlob(b),hash,'pinned original Git object: '+k);out[k]=b.toString('utf8')}return out}
function check(d){
 const article=d.article;
 assert.ok(article.trim().split(/\s+/).length>=2500,'deep original long-form article');
 for(const phrase of ['The Hand That Wasn\'t Yours','Botvinick','Cohen','1998','Rohde','2011','Lush','2020','2018','2024','Puységur','proprioceptive drift','demand characteristics','not a commercial hypnosis claim','https://doi.org/10.1525/collabra.325'])assert.ok(article.includes(phrase),'article source: '+phrase);
 assert.ok(article.includes('UNPUBLISHED')&&article.includes('no affiliate endorsement')===false,'article is held and not falsely marketed');
 assert.ok(!/I (?:personally )?(?:used|tested|bought) (?:Zen12|Hypnosis Live)/i.test(article),'no invented product experience');
 assert.ok(!/meditation (?:cures|guarantees)|(?:guaranteed|proven) (?:wealth|focus|healing)/i.test(article),'no ungrounded benefit claim');
 const m=JSON.parse(d.matrix);
 assert.equal(m.scope,'UNPUBLISHED_SOURCE_ONLY');assert.equal(m.release,'HARD_HOLD');assert.equal(m.version,'r251');
 assert.equal(m.sources.length,23);assert.equal(m.claims.length,26);assert.equal(m.gates.length,16);
 for(const entries of [m.sources,m.claims,m.gates])assert.equal(new Set(entries.map(x=>x.id)).size,entries.length,'unique IDs');
 const src=new Set(m.sources.map(x=>x.id));
 for(const s of m.sources)assert.ok(/^https:\/\//.test(s.url),'secure source');
 for(const c of m.claims){assert.ok(src.has(c.source),'claim provenance: '+c.id);assert.ok(c.statement.length>=40,'substantive claim');}
 for(const g of m.gates){assert.equal(g.status,'HARD_HOLD');assert.equal(g.verified,false);assert.equal(g.evidence,null);}
 assert.equal(m.primary_offer.approval,'NOT_VERIFIED');
 assert.equal(m.primary_offer.offer_id,'inspire3_zen12_premium');assert.equal(m.primary_offer.cta_status,'NATIVE_DISABLED_ONLY');
 for(const k of ['account_earning_url','permitted_channels','net_commission','price_paid','refund_fulfillment','commission_terms','promotion_approval'])assert.equal(m.primary_offer[k],null,'authorization held: '+k);
 assert.equal(m.primary_offer.advertised_price_usd,87.99);assert.equal(m.primary_offer.advertised_price_source,'S13');
 assert.equal(m.claims.find(x=>x.id==='C15').policy,'DO_NOT_ASSERT_FINAL_PRICE');
 assert.equal(m.claims.find(x=>x.id==='C17').policy,'DO_NOT_ASSERT_AS_FACT');
 for(const k of ['sku','rights','live_checkout','price','fulfillment','refund_policy'])assert.equal(m.owned_fallback[k],null,'owned fallback held');
 assert.equal(m.owned_fallback.commercial_activation,'NOT_AUTHORIZED');
 assert.equal(m.metrics.status,'NOT_COMPUTABLE');
 for(const [k,v] of Object.entries(m.metrics))if(k!=='status')assert.equal(v,null,'no fabricated conversion:'+k);
 for(const row of m.creator_paths){assert.equal(row.grok_asset_id,null);assert.equal(row.verified_native_mobile_url,null);}
 assert.equal(m.privacy.new_script,false);assert.equal(m.privacy.new_cookie,false);assert.equal(m.privacy.new_email_form,false);assert.equal(m.privacy.persist_pii,false);
 const h=d.html;
 assert.ok(/^<!doctype html>/i.test(h)&&h.includes('<html lang="en">')&&h.includes('noindex,nofollow'),'accessible unpublished doc');
 assert.equal((h.match(/<h1\b/gi)||[]).length,1,'one H1');
 assert.ok(h.includes(':focus-visible')&&h.includes('prefers-reduced-motion')&&h.includes('360'),'responsive concepts + a11y');
 const buttons=[...h.matchAll(/<button\b[^>]*>/gi)];
 assert.equal(buttons.length,1,'only one held commerce control');
 assert.ok(/\sdisabled(?=\s|>)/i.test(buttons[0][0]),'native disabled attribute mandatory');
 assert.ok(/\baria-disabled="true"/.test(buttons[0][0])&&/aria-describedby="disclosure-note hold-desc"/.test(buttons[0][0]),'a11y control description');
 assert.ok(h.includes('id="disclosure-note"')&&h.includes('id="hold-desc"'),'descriptions resolve');
 const b=h.indexOf('<button'),disc=h.indexOf('Prospective affiliate disclosure:');
 assert.ok(disc>=0 && b>disc && b-disc<850,'clear immediately adjacent affiliate disclosure');
 assert.ok(h.includes('may earn a commission at no additional cost to you'),'FTC material connection explained');
 assert.ok(h.includes('No merchant URL is attached to a purchasing control'),'no activated checkout');
 assert.ok(h.includes('https://finalvestige.com/focus/'),'one existing Focus funnel');
 assert.ok(h.includes('UNPUBLISHED')&&h.includes('42-second')&&h.includes('not a rendered film'),'no fictitious live video');
 assert.ok(!/<\s*(?:script|form|input|iframe|video|audio|source|track|embed|object|link|img)\b/i.test(h),'no executable/loaded widgets');
 assert.ok(!/\son[a-z][a-z0-9_-]*\s*=|javascript\s*:|data\s*:|@import|url\s*\(/i.test(h),'no remote assets/inline handlers');
 const ids=[...h.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
 assert.equal(new Set(ids).size,ids.length,'unique element IDs');
 assert.ok(h.includes('<title id="mind-viz-title">')&&h.includes('<desc id="mind-viz-desc">'),'original illustration has accessible description');
 assert.ok(h.includes('aria-labelledby="mind-viz-title mind-viz-desc"'),'SVG labelled by ID');
 for(const a of h.matchAll(/<a\b[^>]*href="([^"]+)"/g))assert.ok(/^https:\/\/(?:finalvestige\.com|www\.ftc\.gov)\/|^#(?:streams|fieldbook|buyers)$/.test(a[1]),'allowlist nonmerchant link: '+a[1]);
 const p=d.plan;
 for(const phrase of ['HARD_HOLD','NOT_COMPUTABLE','R185','R250','R236','R249','R248','OFFER → FUNNEL STEP','merchant-confirmed','utm_content','qualified human','refund','360, 390, 768, 1440, 1920','TASK-008','Grok','Founder'])assert.ok(p.includes(phrase),'plan completeness: '+phrase);
 assert.ok(p.includes('19 effect sizes across 12 studies'),'prior editorial QA correction preserved');
 return true;
}
function negativeCases(d){
 const change=(key,fn)=>()=>({...d,[key]:fn(d[key])});
 const j=(fn)=>change('matrix',s=>{const v=JSON.parse(s);fn(v);return JSON.stringify(v)});
 return [
 ...JSON.parse(d.matrix).gates.map(g=>j(v=>v.gates.find(x=>x.id===g.id).status='PASS')),
 j(v=>v.gates[0].verified=true),j(v=>v.gates[0].evidence='faked account'),
 j(v=>v.primary_offer.approval='APPROVED'),j(v=>v.primary_offer.account_earning_url='https://example.com/track'),
 j(v=>v.primary_offer.permitted_channels=['web']),j(v=>v.primary_offer.net_commission=100),
 j(v=>v.primary_offer.price_paid=87.99),j(v=>v.primary_offer.refund_fulfillment='VERIFIED'),
 j(v=>v.owned_fallback.sku='unsourced'),j(v=>v.metrics.confirmed_paid_orders=4),j(v=>v.metrics.net_revenue=150),
 j(v=>v.claims.find(x=>x.id==='C17').policy='ENDORSE'),j(v=>v.claims.find(x=>x.id==='C15').policy='ASSERT_FINAL_PRICE'),
 j(v=>v.claims[0].source='INVENTED'),j(v=>v.claims[1].id=v.claims[0].id),
 j(v=>v.creator_paths[0].grok_asset_id='FAKE_VIDEO_ID'),j(v=>v.privacy.new_script=true),
 change('html',s=>s.replace(' disabled aria-disabled',' aria-disabled')),
 change('html',s=>s.replace('Prospective affiliate disclosure:','Omitted:')),
 change('html',s=>s.replace('</main>','<a href="https://zen12.com/hnp">BUY</a></main>')),
 change('html',s=>s.replace('</main>','<form><input type="email"></form></main>')),
 change('html',s=>s.replace('</main>','<script src="https://pixel.test/p.js"></script></main>')),
 change('html',s=>s.replace('</main>','<iframe src="https://zen12.com/hnp"></iframe></main>')),
 change('html',s=>s.replace('</main>','<button disabled>SECOND</button></main>')),
 change('html',s=>s.replace('id="hold-desc"','id="disclosure-note"')),
 change('html',s=>s.replace('href="https://finalvestige.com/focus/"','href="javascript:alert(1)"')),
 change('html',s=>s.replace('No merchant URL is attached to a purchasing control','Merchant link activated')),
 change('html',s=>s.replace('not a rendered film','now autoplaying')),
 change('article',s=>s.replaceAll('proprioceptive drift','intuitive event')),
 change('article',s=>s.replace('https://doi.org/10.1525/collabra.325','fake unsupported publication')),
 change('plan',s=>s.replace('19 effect sizes across 12 studies','19 independent studies'))
 ];
}
function run(d){check(d);let n=0;for(const test of negativeCases(d)){assert.throws(()=>check(test()),undefined,'unsafe modification escaped '+n);n++}return {baseline:'PASS',authenticated_blob_count:Object.keys(pins).length,unsafe_mutations_rejected:n}}
if(require.main===module)console.log(JSON.stringify(run(read('.'))));
module.exports={pins,read,check,negativeCases,run};

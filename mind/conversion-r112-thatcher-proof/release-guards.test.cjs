/* R112 source-only checks. Reproduce with node --test mind/conversion-r112-thatcher-proof/release-guards.test.cjs. */
'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const read=p=>fs.readFileSync(path.join(__dirname,p),'utf8');
const ledger=JSON.parse(read('merchant-and-funnel-ledger.json'));
const article=read('thatcher-investigation.md'),memo=read('conversion-acceptance.md');
const A=read('../conversion-r110-revenue-gate/variant-a.html');
const B=read('../conversion-r110-revenue-gate/variant-b-video-concept.html');
test('evidence source identifiers resolve',()=>{const ids=new Set(ledger.source_records.map(x=>x.id));for(const c of ledger.claims){assert.ok(c.id&&c.claim&&c.status);for(const id of c.support)assert.ok(ids.has(id));}});
test('partner approval and paid FV SKU remain genuinely absent',()=>{assert.equal(ledger.eligibility.inspire3_named_fv_affiliate_acceptance,null);assert.equal(ledger.eligibility.inspire3_approved_earning_url,null);assert.equal(ledger.eligibility.inspire3_no_buyer_identifiers_agreement,null);assert.equal(ledger.eligibility.eligible_owned_paid_mind_sku,null);assert.equal(ledger.eligibility.affiliate_activation,false);assert.ok(Object.values(ledger.release_gates).every(x=>x===false));});
test('no invented campaign IDs or paid orders',()=>{const f=ledger.funnel;assert.deepEqual(f.grok_asset_ids,[]);assert.ok(f.proposed_topics.every(x=>x.grok_asset_id===null&&x.grok_post_url===null));assert.equal(f.confirmed_orders,null);assert.equal(f.net_revenue_per_1000_qualified_humans,null);});
test('original Thatcher investigation cites five primary scholarly references',()=>{for(const id of ['10.1068/p090483','8354050','9274755','25102929','0956797613501521'])assert.ok(article.includes(id));assert.ok(article.includes('not a validated experiment'));assert.ok(!article.includes('awin1.com'));});
test('two Zen12 variants share EXACT underlying guide',()=>{const begin=B.indexOf('<aside class="fvmo-panel" aria-labelledby="fvmo-film">');const end=B.indexOf('</aside>',begin);assert.ok(begin>0&&end>begin);const aside=B.slice(begin,end+8);assert.equal(aside.length,1917);assert.equal(B.slice(0,begin)+B.slice(end+8),A);});
test('both variants keep merchant links absent and action disabled',()=>{for(const h of [A,B]){assert.equal((h.match(/<button/g)||[]).length,1);assert.ok(h.includes('disabled'));assert.ok(h.includes('may earn a commission'));assert.ok(!h.includes('<iframe'));assert.ok(!h.includes('<script'));assert.ok(!h.includes('awin1.com'));assert.ok(!h.includes('href="https://zen12.com'));}});
test('free lead is not a paid sale',()=>{assert.equal(ledger.funnel.free_resource_url,'https://finalvestige.com/focus/');assert.equal(ledger.ab_test.live,false);assert.equal(ledger.ab_test.winner,'NOT_ESTABLISHED');assert.ok(memo.includes('NOT COMPUTABLE'));});
test('buyer privacy, FTC and release protections are explicit',()=>{for(const x of ['inspire3.com/privacy','ftc.gov','HARD HOLD','no duplicate Jetpack form','PR #172'])assert.ok(memo.toLowerCase().includes(x.toLowerCase()));});

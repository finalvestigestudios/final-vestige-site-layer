"use strict";
/* Run from repo root: node --test mind/r126-commerce-tests.cjs
 * All fixtures are SYNTHETIC. Passing these tests does not prove a real customer, payable commission, authorization or browser accessibility.
 */
const test=require("node:test"), assert=require("node:assert/strict"), fs=require("node:fs"), path=require("node:path");
const read=(name)=>fs.readFileSync(path.join(__dirname,name),"utf8");
const guide=read("r126-zen12-source-checked-decision-insert.html");
const article=read("r126-mcgurk-audiovisual-speech-investigation.md");
const memo=read("r126-one-offer-conversion-acceptance.md");
const register=JSON.parse(read("r126-merchant-claims-and-release-gates.json"));
const {measure,validateInput}=require("./r126-revenue-aggregate-contract.cjs");
const clone=(x)=>({...x});
const fixture={
 cohort_days:7,utm_campaign:"mind_pilot_2026_11",qualified_human_sessions:50,
 sessions_source:"first_party_verified",human_qualification_verified:true,
 merchant_ledger_source:"approved_merchant_reconciliation",settlement_coverage_verified:true,
 verified_paid_orders:2,gross_revenue_cents:10000,refunds_cents:2000,fees_cents:500,chargebacks_cents:0,
 currency:"USD",affiliate_outbound_clicks:12,confirmed_leads:5,lead_count_verified:true,synthetic_fixture:true
};
test("independent article cites primary original and modern replication studies",()=> {
 for(const source of ["10.1038/264746a0","10.1371/journal.pone.0207160","2024","2025"]) assert.ok(article.includes(source),source);
});
test("investigation does not present commercial sales CTA",()=>{
 assert.doesNotMatch(article,/href=.*zen12|buy now|affiliate (link|commission)/i);
});
test("evidence ledger has traceable real URLs",()=>{
 assert.ok(register.sources.length>=18);
 const ids=new Set(register.sources.map(s=>s.id));
 assert.equal(ids.size,register.sources.length);
 for(const c of register.claims) assert.ok(ids.has(c.source_id),c.id);
 for(const s of register.sources) assert.match(s.url,/^https:\/\//);
});
test("no earning link or merchant authorization set",()=>{
 assert.equal(register.commercial_activation,false);
 assert.equal(register.affiliate_approval,null);
 assert.equal(register.tracking_affiliate_url,null);
 assert.equal(register.offer_url,null);
});
test("all commercial and release gates remain closed",()=>{
 assert.ok(register.gates.length>=18);
 assert.ok(register.gates.every(g=>g.state==="CLOSED"));
});
test("no active seller site offer links appear in buyer component",()=>{
 const links=[...guide.matchAll(/<a\s+[^>]*href\s*=\s*["']([^"']+)["']/gi)].map(x=>x[1]);
 assert.ok(!links.some(x=>/zen12\.com|affiliates\.inspire3\.com|payhip\.com/.test(x)));
});
test("all purchase controls are truly disabled",()=>{
 assert.match(guide,/<button\b[^>]*\sdisabled\b/i);
 assert.doesNotMatch(guide,/<a\b[^>]*class=["'][^"']*buy/i);
});
test("FTC earning disclosure directly precedes native-disabled purchase control",()=>{
 const disclosure=guide.indexOf('class="disclosure"');
 const button=guide.indexOf("<button");
 assert.ok(disclosure>0 && button>disclosure && button-disclosure<700);
 assert.match(guide,/may earn a commission/i);
});
test("free resource remains existing sole signup destination",()=>{
 assert.match(guide,/https:\/\/finalvestige.com\/focus\//);
 assert.doesNotMatch(guide,/<form\b|<input\b/i);
});
test("no JS script, remote embed, forced video or network tags",()=>{
 assert.doesNotMatch(guide,/<script\b|<iframe\b|<video\b|autoplay\s*=|onload\s*=/i);
});
test("accessible no-JS storyboard and transcript provided",()=>{
 assert.match(guide,/<details>/);
 assert.match(guide,/<summary>/);
 assert.match(guide,/complete 40-second film transcript/i);
 assert.match(guide,/prefers-reduced-motion/);
 assert.match(guide,/:focus-visible/);
 assert.match(guide,/aria-labelledby/);
});
test("no loss of Focus/Jetpack or protected PR ownership",()=>{
 for(const s of ["PR #49","Issue #150","PR #172","Issue #174","single Jetpack"]) assert.ok(memo.includes(s),s);
});
test("a click alone cannot produce merchant revenue",()=>{
 const a={cohort_days:7,utm_campaign:"mind_pilot_2026_11",currency:"USD",affiliate_outbound_clicks:40};
 const result=measure(a); assert.equal(result.status,"NOT_COMPUTABLE");assert.equal(result.net_revenue_cents,null);
});
test("verified synthetic settlement computes cents net correctly",()=>{
 const r=measure(fixture);assert.equal(r.status,"COMPUTED_FROM_VERIFIED_INPUT_ONLY");
 assert.equal(r.net_revenue_cents,7500);assert.equal(r.net_revenue_per_1000_qualified_sessions_cents,150000);
 assert.equal(r.paid_conversion_rate,0.04);assert.equal(r.lead_to_paid_order_rate,0.4);
 assert.equal(r.sample_caution,"TINY_SAMPLE");assert.equal(r.synthetic_fixture,true);
});
test("incomplete merchant export remains missing, not zero",()=>{
 const r=measure({...fixture,settlement_coverage_verified:false});
 assert.equal(r.status,"NOT_COMPUTABLE");assert.equal(r.net_revenue_cents,null);
});
test("session qualification is required",()=>{
 const r=measure({...fixture,human_qualification_verified:false});
 assert.equal(r.status,"NOT_COMPUTABLE");
});
test("explicit asset attribution demands proof of merchant join",()=>{
 const r=measure({...fixture,asset_id:"grok-mind-001"});
 assert.equal(r.status,"NOT_COMPUTABLE");
 assert.ok(r.reasons.includes("asset_level_merchant_attribution"));
});
test("unknown nested customer record blocked by whitelist",()=>{
 assert.throws(()=>measure({...fixture,customer_email:"fake@example.com"}),/non_whitelisted_field/);
 assert.throws(()=>measure({...fixture,merchant_customer_record:{email:"bad@example.com"}}),/non_whitelisted_field/);
});
test("bad types and impossible monetary input fail closed",()=>{
 assert.throws(()=>measure({...fixture,refunds_cents:-1}),/invalid_measure/);
 assert.throws(()=>measure({...fixture,gross_revenue_cents:NaN}),/invalid_measure/);
 assert.throws(()=>measure({...fixture,qualified_human_sessions:"50"}),/invalid_measure/);
 assert.throws(()=>measure({...fixture,verified_paid_orders:51}),/orders_exceed_sessions/);
});
test("unknown session tracking and currency scope fail closed",()=>{
 assert.throws(()=>validateInput({...fixture,utm_campaign:"bad?utm_email=x"}),/invalid_campaign/);
 assert.throws(()=>validateInput({...fixture,currency:"BTC"}),/unsupported_currency/);
 assert.throws(()=>validateInput({...fixture,asset_id:"../../invalid"}),/invalid_asset_id/);
});
test("tests detect live sale button mutation",()=>{
 const mutant=guide.replace(/(<button[^>]*?)\sdisabled\b/,"$1");
 assert.notEqual(mutant,guide);
 assert.doesNotMatch(mutant,/<button\b[^>]*\sdisabled\b/i);
});
test("tests detect absent earning disclosure mutation",()=>{
 const mutant=guide.replace(/may earn a commission/i,"no special relationship");
 assert.doesNotMatch(mutant,/may earn a commission/i);
});
test("tests detect seller offer URL injection mutation",()=>{
 const mutant=guide.replace('href="https://finalvestige.com/focus/"','href="https://zen12.com/hnp"');
 assert.match(mutant,/<a\s+[^>]*href\s*=\s*"https:\/\/zen12\.com/);
});

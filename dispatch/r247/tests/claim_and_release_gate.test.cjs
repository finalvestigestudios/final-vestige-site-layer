"use strict";
const test=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {evaluate}=require("../claim_and_release_gate.cjs");
const root=path.join(__dirname,"..");
const original=()=>JSON.parse(fs.readFileSync(path.join(root,"MERCHANT_AND_RELEASE_EVIDENCE.json"),"utf8"));
const h=()=>fs.readFileSync(path.join(root,"issue05_TOTAL_FOCUS_OPTIONAL_UNSENT.html"),"utf8");
const p=()=>fs.readFileSync(path.join(root,"issue05_TOTAL_FOCUS_OPTIONAL_UNSENT.txt"),"utf8");
test("baseline is a genuine hold with unknown revenue and recipients",()=>{const r=evaluate(original(),h(),p());assert.equal(r.status,"HOLD_UNSENT");assert.deepEqual(r.errors,[]);assert.equal(r.net_revenue_usd,null);assert.equal(r.email_eligible,null);});
const cases=[
 ["canonical identity",x=>{x.origin.canonical_sha="bad";},"CANONICAL_DRIFT"],
 ["original allocation",x=>{x.editorial_mix.commercial_review_pending=3;},"MIX_CHANGED"],
 ["release false",x=>{x.status="APPROVED";},"RELEASE_STATUS_DRIFT"],
 ["auto send",x=>{x.subscriber.auto_new_post_email=true;},"AUTO_SEND_NOT_OFF"],
 ["recipient invented",x=>{x.subscriber.email_eligible=3;},"ELIGIBLE_RECIPIENTS_UNSUPPORTED"],
 ["order invented",x=>{x.revenue.verified_paid_orders=1;},"REVENUE_UNVERIFIED"],
 ["checkout claimed",x=>{x.merchant.pricing_live_checkout_verified=true;},"CLAIM_OR_PRICE_OVERRIDDEN"],
 ["claim claimed",x=>{x.merchant.product_specific_efficacy_verified=true;},"CLAIM_OR_PRICE_OVERRIDDEN"],
 ["approval forged",x=>{x.gates.email_channel_permission=true;},"RELEASE_GATE_FALSELY_CLEARED"]
];
for(const [name,mut,code] of cases){test("reject "+name,()=>{const x=original();mut(x);assert.ok(evaluate(x,h(),p()).errors.includes(code));});}
test("reject clickable merchant link",()=>assert.ok(evaluate(original(),h()+'<a href="https://hypnosislive.com/buy">BUY</a>',p()).errors.includes("MERCHANT_LINK_ACTIVE")));
test("reject tracker image",()=>assert.ok(evaluate(original(),h()+'<img src="https://track.example/pixel">',p()).errors.includes("UNSAFE_EMAIL_MARKUP")));
test("reject price drift",()=>assert.ok(evaluate(original(),h()+' $24.44',p()).errors.includes("VOLATILE_PRICE_IN_EMAIL")));
test("reject efficacy hype",()=>assert.ok(evaluate(original(),h()+' you will focus',p()).errors.includes("UNSUPPORTED_PROMISE")));
test("reject legal deletion",()=>assert.ok(evaluate(original(),h().replaceAll("[[VALID_POSTAL_ADDRESS_REQUIRED]]",""),p()).errors.some(x=>x.includes("MANDATORY_INERT_TOKEN_MISSING"))));
test("reject active CTA",()=>assert.ok(evaluate(original(),h()+'<a href="https://finalvestige.com/guide">Buy now</a>',p()).errors.includes("PRIMARY_CTA_MUST_BE_INERT")));

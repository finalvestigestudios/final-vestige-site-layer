import test from "node:test";
import assert from "node:assert/strict";
import {replay} from "../replay.mjs";
import fixture from "../synthetic-fixture.json" with {type:"json"};
const cp=x=>JSON.parse(JSON.stringify(x));
test("SYNTHETIC ONLY: full 7 and 30 day cohort with settled net and refund",()=>{const d=replay(fixture);assert.equal(d.send_authorized,false);for(const k of ["d7","d30"]){assert.equal(d.cohorts[k].qualified_human_sessions,2);assert.equal(d.cohorts[k].confirmed_signups,1);assert.equal(d.cohorts[k].settled_orders,1);assert.equal(d.cohorts[k].net_cents,1180);assert.equal(d.cohorts[k].net_per_1000_qualified_sessions_cents,590000);}});
test("duplicate proof cannot double count",()=>assert.equal(replay(fixture).rejection_counts.duplicate_confirmed_signup,1));
test("no provider confirmation means no signup even with form/PDF",()=>{const x=cp(fixture);x.events=x.events.filter(e=>e.type!=="provider_subscribed");assert.equal(replay(x).cohorts.d7.confirmed_signups,0)});
test("Reader-only, unverified WP account, suppression rejected",()=>{for(const change of [{status:"Not subscribed"},{provider_account_verified:false},{suppressed:true}]){const x=cp(fixture);x.events.filter(e=>e.type==="provider_subscribed").forEach(e=>Object.assign(e,change));assert.equal(replay(x).cohorts.d7.confirmed_signups,0)}});
test("existing verified WP account OR confirmed email pathway",()=>{const x=cp(fixture);x.events.filter(e=>e.type==="provider_subscribed").forEach(e=>{e.path="confirmed_email";e.email_confirmation_verified=true;delete e.provider_account_verified});assert.equal(replay(x).cohorts.d7.confirmed_signups,1)});
test("no paid order: clicks do not imply sales or computable net",()=>{const x=cp(fixture);x.events=x.events.filter(e=>e.type!=="merchant_settled_order"&&e.type!=="merchant_refund");assert.equal(replay(x).cohorts.d7.net_cents,null)});
test("pending orders are rejected",()=>{const x=cp(fixture);x.events.find(e=>e.type==="merchant_settled_order").status="pending";assert.equal(replay(x).cohorts.d7.settled_orders,0)});
test("unverified refund rejected instead of net-deducted",()=>{const x=cp(fixture);x.events.find(e=>e.type==="merchant_refund").partner_refund_verified=false;assert.equal(replay(x).cohorts.d7.net_cents,1480)});
test("bot not counted as qualified human",()=>assert.equal(replay(fixture).cohorts.d7.qualified_human_sessions,2));
test("PII input blocked and public aggregate contains no individual keys",()=>{const x=cp(fixture);x.events[0].email="private@example.com";assert.throws(()=>replay(x),/PII prohibited/);assert.doesNotMatch(JSON.stringify(replay(fixture)),/demo_s1|PROOF-SYNTHETIC-01|@/)});
test("hard holds remain, independently of synthetic positive fixture",()=>{const d=replay(fixture);assert.equal(d.send_authorized,false);assert.ok(d.holds.some(h=>h.includes("postal")));assert.ok(d.holds.some(h=>h.includes("founder")))});

test("multiple orders per one customer do not inflate customer conversion rates",()=>{
 const x=cp(fixture);x.events.push({type:"merchant_settled_order",session:"demo_s1",at:"2026-11-10T11:12:00Z",status:"settled",independent_partner_report:true,verified_attribution:true,order_ref:"ORDER-SYNTHETIC-02",gross_cents:900,fees_cents:50,customer_ref:"CUSTOMER-SYNTHETIC-01",customer_ref_verified:true});
 const d=replay(x).cohorts.d7;assert.equal(d.settled_orders,2);assert.equal(d.verified_paying_customers,1);assert.equal(d.paid_conversion_rate,0.5);assert.equal(d.lead_to_customer_rate,1);
});

test("customer conversion withheld when partner does not provide independently verified customer reference",()=>{const x=cp(fixture);const o=x.events.find(e=>e.type==="merchant_settled_order");delete o.customer_ref_verified;const d=replay(x).cohorts.d7;assert.equal(d.settled_orders,1);assert.equal(d.net_cents,1180);assert.equal(d.verified_paying_customers,null);assert.equal(d.paid_conversion_rate,null)});

test("backdated events cannot retroactively manufacture paid conversion",()=>{const x=cp(fixture);x.events.find(e=>e.type==="merchant_settled_order").at="2026-11-10T11:03:20Z";assert.equal(replay(x).cohorts.d7.settled_orders,0);assert.ok(replay(x).rejection_counts.out_of_order>0)});

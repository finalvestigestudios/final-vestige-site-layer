"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const {SHARED,COMMERCIAL,reviewEdition,confirmedSignup,summarizeProofs}=require("./evidence_gate.cjs");
const key="a".repeat(64),orderKey="b".repeat(64);
const accepted={event:"confirmed_signup",provider:"jetpack",email_subscription:"Subscribed",
provider_status_verified:true,confirmed_at:"2026-11-15T07:30:00Z",opaque_key:key,provider_evidence_ref:"proof:jetpack_check"};
const settlement={status:"settled",source:"merchant_settlement",opaque_order_id:orderKey,
settlement_evidence_ref:"proof:merchant_statement",gross:40,refunds:5,fees:3};
test("all six fail closed without attestations",()=>{for(let i=1;i<=6;i++)assert.equal(reviewEdition(i).send_authorized,false)});
test("original two commercial lanes are 03 and 05",()=>assert.deepEqual([1,2,3,4,5,6].filter(i=>reviewEdition(i).lane==="commercial"),[3,5]));
test("editorial merchant permissions isolated",()=>{assert.equal(reviewEdition(1).missing.length,SHARED.length);assert.equal(reviewEdition(3).missing.length,SHARED.length+COMMERCIAL.length)});
test("string truthiness is not evidence",()=>assert.notEqual(reviewEdition(3,{founder_final_send_approval:"true"}).state,"REVIEW_CANDIDATE_ONLY"));
test("all true can only become review candidate, not send",()=>{const p=Object.fromEntries([...SHARED,...COMMERCIAL].map(k=>[k,true]));assert.equal(reviewEdition(3,p).state,"REVIEW_CANDIDATE_ONLY");assert.equal(reviewEdition(3,p).send_authorized,false)});
test("invalid edition raises",()=>assert.throws(()=>reviewEdition(7)));
test("query/CSS success is not a provider signup",()=>assert.equal(confirmedSignup({event:"confirmed_signup",url:"?subscribe=success",css:"is-subscriber"}),false));
test("Reader follower is not email subscribed",()=>assert.equal(confirmedSignup({...accepted,email_subscription:"Not subscribed"}),false));
test("unconfirmed cannot count",()=>assert.equal(confirmedSignup({...accepted,email_subscription:"Not confirmed"}),false));
test("source-of-truth and receipt required",()=>{assert.equal(confirmedSignup({...accepted,provider_status_verified:false}),false);assert.equal(confirmedSignup({...accepted,provider_evidence_ref:"screenshot"}),false)});
test("raw email is not an opaque key",()=>assert.equal(confirmedSignup({...accepted,opaque_key:"person@example.com"}),false));
test("confirmed signup deduplicated",()=>assert.equal(summarizeProofs({signups:[accepted,accepted]}).confirmed_signup_count,1));
test("no actual sales means unknown revenue not zero",()=>{let s=summarizeProofs({signups:[accepted]});assert.equal(s.net_revenue,null);assert.equal(s.net_revenue_per_1000_qualified_human_sessions,null)});
test("click is not settlement",()=>assert.equal(summarizeProofs({orders:[{...settlement,status:"clicked"}]}).settled_order_count,null));
test("duplicate settlement counts once",()=>assert.equal(summarizeProofs({orders:[settlement,settlement]}).settled_order_count,1));
test("synthetic verified math includes refunds and fees",()=>{let s=summarizeProofs({orders:[settlement],sessions:{source:"audited_human_sessions",filter_reviewed:true,count:100,evidence_ref:"proof:human_review"}});assert.equal(s.net_revenue,32);assert.equal(s.net_revenue_per_1000_qualified_human_sessions,320)});
test("zero or unaudited denominator is null",()=>{const b={source:"audited_human_sessions",filter_reviewed:true,count:0,evidence_ref:"proof:human_review"};assert.equal(summarizeProofs({orders:[settlement],sessions:b}).net_revenue_per_1000_qualified_human_sessions,null);assert.equal(summarizeProofs({orders:[settlement],sessions:{...b,count:5,filter_reviewed:false}}).net_revenue_per_1000_qualified_human_sessions,null)});
test("invalid refund cannot count",()=>assert.equal(summarizeProofs({orders:[{...settlement,refunds:41}]}).settled_order_count,null));
test("aggregate output contains no raw receipt ids",()=>{let r=JSON.stringify(summarizeProofs({signups:[accepted],orders:[settlement]}));assert.equal(r.includes("opaque_order_id"),false);assert.equal(r.includes("opaque_key"),false)});

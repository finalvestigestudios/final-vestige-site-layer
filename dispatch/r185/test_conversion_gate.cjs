"use strict";
const assert=require("node:assert/strict");
const g=require("./conversion_gate.cjs");
let n=0;
function t(desc,fn){fn();n++;}
const candidate=()=>({kind:"provider_subscription_status",provider:"jetpack",
 email_subscription:"Subscribed",confirmed_by_provider:true,consent_source_verified:true,
 private_evidence_ref:"ev_private_12A",provider_event_id:"jetpack_evt_12A"});
const settled=()=>({opaque_settlement_ref:"payhip_ord_ABC1",type:"first_party_paid",
 independently_reported:true,refund_checked:true,fees_checked:true,gross:20,refund:2,fees:1});
const good=()=>({qualified_human_sessions:100,qualified_human_sessions_verified:true,
 settlement_dataset_complete:true,attribution_reconciled:true,settlements:[settled()]});
t("no provider event rejects",()=>assert.equal(g.classifyProviderEvent().state,"REJECT"));
t("download panel rejects",()=>assert.equal(g.classifyProviderEvent({kind:"download_panel"}).state,"REJECT"));
t("query param rejects",()=>assert.equal(g.classifyProviderEvent({kind:"query_parameter"}).state,"REJECT"));
t("aggregate count rejects",()=>assert.equal(g.classifyProviderEvent({kind:"aggregate_delta"}).state,"REJECT"));
t("client success rejects",()=>assert.equal(g.classifyProviderEvent({kind:"client_success"}).state,"REJECT"));
t("provider event still only review candidate",()=>assert.equal(g.classifyProviderEvent(candidate()).state,"REVIEW_CANDIDATE"));
t("confirmation missing holds",()=>assert.equal(g.classifyProviderEvent({...candidate(),confirmed_by_provider:false}).state,"HOLD"));
t("consent missing holds",()=>assert.equal(g.classifyProviderEvent({...candidate(),consent_source_verified:false}).state,"HOLD"));
t("provider mismatch holds",()=>assert.equal(g.classifyProviderEvent({...candidate(),provider:"other"}).state,"HOLD"));
t("recipient email forbidden",()=>assert.equal(g.classifyProviderEvent({...candidate(),email:"x@x.com"}).state,"REJECT"));
t("PII in proof reference forbidden",()=>assert.equal(g.classifyProviderEvent({...candidate(),private_evidence_ref:"a@b.com"}).state,"HOLD"));
t("provider signals dedup",()=>assert.deepEqual(g.summarizeConfirmedCandidates([candidate(),candidate()]).duplicate_provider_refs,1));
t("never emits a confirmed event",()=>assert.equal(g.summarizeConfirmedCandidates([candidate()]).confirmed_signup_events_emitted,0));
t("no release ever",()=>assert.equal(g.releaseGate({},false).can_send,false));
t("full send evidence still no send",()=>assert.equal(g.releaseGate(Object.fromEntries(g.REQUIRED_SEND.map(x=>[x,true])),false).can_send,false));
t("commercial missing rights",()=>assert.ok(g.releaseGate({},true).missing.includes("email_channel_permission")));
t("even all rights cannot authorize send",()=>assert.equal(g.releaseGate(Object.fromEntries([...g.REQUIRED_SEND,...g.REQUIRED_PARTNER].map(x=>[x,true])),true).can_send,false));
t("missing revenue uncomputable",()=>assert.equal(g.safeRevenueScorecard({}).status,"NOT_COMPUTABLE"));
t("click is not sale",()=>assert.equal(g.safeRevenueScorecard({affiliate_outbound_clicks:900}).status,"NOT_COMPUTABLE"));
t("missing settlement completeness unknown",()=>assert.equal(g.safeRevenueScorecard({...good(),settlement_dataset_complete:false}).status,"NOT_COMPUTABLE"));
t("missing attribution unknown",()=>assert.equal(g.safeRevenueScorecard({...good(),attribution_reconciled:false}).status,"NOT_COMPUTABLE"));
t("no human denominator unknown",()=>assert.equal(g.safeRevenueScorecard({...good(),qualified_human_sessions:0}).status,"NOT_COMPUTABLE"));
t("negative gross invalid",()=>assert.equal(g.validateRevenueRecord({...settled(),gross:-2}),false));
t("unverified report invalid",()=>assert.equal(g.validateRevenueRecord({...settled(),independently_reported:false}),false));
t("unreconciled refund invalid",()=>assert.equal(g.validateRevenueRecord({...settled(),refund_checked:false}),false));
t("no PII in sales",()=>assert.equal(g.validateRevenueRecord({...settled(),customer_email:"x@x.com"}),false));
t("duplicate settlements fail",()=>assert.equal(g.safeRevenueScorecard({...good(),settlements:[settled(),settled()]}).status,"NOT_COMPUTABLE"));
t("valid synthetic accounting example",()=>assert.equal(g.safeRevenueScorecard(good()).net_revenue_per_1000_qualified_humans,170));
t("invalid social source",()=>assert.equal(g.safeUtm({utm_source:"email",utm_medium:"organic_social",utm_campaign:"mind_pilot_2026_11",utm_content:"grokasset001"}),false));
t("valid social tuple",()=>assert.equal(g.safeUtm({utm_source:"tiktok",utm_medium:"organic_social",utm_campaign:"mind_pilot_2026_11",utm_content:"realasset001"}),true));
t("guess asset disallowed",()=>assert.equal(g.safeUtm({utm_source:"tiktok",utm_medium:"organic_social",utm_campaign:"mind_pilot_2026_11",utm_content:"sample"}),false));
t("source email parameter blocked",()=>assert.equal(g.safeUtm({utm_source:"tiktok",utm_medium:"organic_social",utm_campaign:"mind_pilot_2026_11",utm_content:"email=a@b.com"}),false));
console.log("Dispatch R185 source contract: "+n+"/"+n+" PASS (synthetic fixtures; NO provider attestation)");
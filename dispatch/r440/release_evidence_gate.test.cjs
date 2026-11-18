"use strict";
/* Synthetic tests; zero live addresses or real orders. */
const assert=require("node:assert/strict");
const {assess}=require("./release_evidence_gate.cjs");
let n=0;
function t(label,fn){fn();n++;}
function fixture(){return {
 schema_version:"1.0",
 provider_counts:{dashboard_total:3,confirmed:3,unconfirmed:2,email_filter_total:3,reader_only_total:0},
 provider_proof:{authoritative_filter_read:true,email_rows_all_subscribed:true,email_rows_all_email_subscriber:true,provider_event_join_validated:false,received_welcome_with_fieldbook:false,native_non_sending_preview_witnessed:false},
 wordpress:{new_post_default_off:true,dispatch_copy_matches_manual_cadence:false,final_vestige_valid_postal_witnessed:false,working_unsubscribe_witnessed:false,founder_selected_corrected_editorial_copy:false,final_founder_release_approval:false},
 merchant:{issue03:"Zen12",issue05:"Hypnosis Live",by_issue:{"03":{},"05":{}}},
 receipts:{independent_merchant_settlements_verified:false,cohort_mature_and_refunds_fees_complete:false,realized_net_cents:null},
 attribution:{qualified_human_sessions_audited:false,qualified_human_sessions:null}
};}
const base=assess(fixture());
t("observed email-subscribed aggregate",()=>assert.equal(base.observed_email_eligible_rows,3));
t("none sent",()=>assert.equal(base.release_authorized,false));
t("not editor-ready",()=>assert.equal(base.editorial_reviewable,false));
t("not merchant-ready",()=>assert.equal(base.merchant_issues_ready,false));
t("no net revenue without merchant evidence",()=>assert.equal(base.realized_net_per_1000_human_sessions,null));
t("observed count excludes 2 unconfirmed",()=>assert.equal(fixture().provider_counts.dashboard_total,3));
t("missing confirmation event blocks",()=>assert(base.holds.some(z=>z.id==="confirmed_signup_event")));
t("missing actual welcome blocks",()=>assert(base.holds.some(z=>z.id==="welcome_delivery")));
t("missing Jetpack native preview blocks",()=>assert(base.holds.some(z=>z.id==="native_jetpack_preview")));
t("missing postal and unsubscribe block",()=>assert(base.holds.some(z=>z.id==="publisher_postal")&&base.holds.some(z=>z.id==="working_unsubscribe")));
t("issue05 pinned to Hypnosis Live",()=>assert(!base.holds.some(z=>z.id==="canonical_offer_05")));
for(const [label,mutate] of [
 ["wrong total",x=>x.provider_counts.dashboard_total=4],
 ["wrong confirmed",x=>x.provider_counts.confirmed=2],
 ["wrong email filter",x=>x.provider_counts.email_filter_total=2],
 ["reader-only nonzero",x=>x.provider_counts.reader_only_total=3],
 ["unconfirmed not integral",x=>x.provider_counts.unconfirmed=-1],
 ["missing authoritative filter",x=>x.provider_proof.authoritative_filter_read=false],
 ["not all rows subscribed",x=>x.provider_proof.email_rows_all_subscribed=false],
 ["not all rows email true",x=>x.provider_proof.email_rows_all_email_subscriber=false]
]){t(label+" rejected",()=>{let x=fixture();mutate(x);assert.equal(assess(x).observed_email_eligible_rows,null);});}
t("Total Focus substitution rejected",()=>{let x=fixture();x.merchant.issue05="Total Focus";assert(assess(x).holds.some(h=>h.id==="canonical_offer_05"));});
t("wrong issue03 rejected",()=>{let x=fixture();x.merchant.issue03="Subliminal Guru";assert(assess(x).holds.some(h=>h.id==="canonical_offer_03"));});
t("PII key refused",()=>{let x=fixture();x.provider_proof.email_address="private@example.com";assert(assess(x).errors.some(e=>e.includes("private")));});
t("PII nested key refused",()=>{let x=fixture();x.merchant.by_issue["05"].ip_address="redacted";assert(assess(x).errors.some(e=>e.includes("private")));});
t("all synthetic approvals still no send",()=>{let x=fixture();x.provider_proof.provider_event_join_validated=true;x.provider_proof.received_welcome_with_fieldbook=true;x.provider_proof.native_non_sending_preview_witnessed=true;x.wordpress.dispatch_copy_matches_manual_cadence=true;x.wordpress.final_vestige_valid_postal_witnessed=true;x.wordpress.working_unsubscribe_witnessed=true;x.wordpress.founder_selected_corrected_editorial_copy=true;x.wordpress.final_founder_release_approval=true;for(const k of ["03","05"]) x.merchant.by_issue[k]={named_partner_email_permission:true,vetted_live_guide:true,exact_merchant_sku_and_earning_url:true,live_checkout_refund_claims_verified:true,adjacent_offer_disclosure_verified:true};assert.equal(assess(x).release_authorized,false);});
t("fake 100 clicks do not count as sales",()=>{let x=fixture();x.attribution.cta_clicks=100;assert.equal(assess(x).realized_net_per_1000_human_sessions,null);});
t("immature sales don't compute",()=>{let x=fixture();x.receipts.independent_merchant_settlements_verified=true;x.receipts.realized_net_cents=10000;x.attribution.qualified_human_sessions_audited=true;x.attribution.qualified_human_sessions=100;x.receipts.cohort_mature_and_refunds_fees_complete=false;assert.equal(assess(x).realized_net_per_1000_human_sessions,null);});
t("mature synthetic revenue computes only with audited denominator",()=>{let x=fixture();x.receipts.independent_merchant_settlements_verified=true;x.receipts.realized_net_cents=4567;x.receipts.cohort_mature_and_refunds_fees_complete=true;x.attribution.qualified_human_sessions_audited=true;x.attribution.qualified_human_sessions=100;assert.equal(assess(x).realized_net_per_1000_human_sessions,456.7);});
t("unknown zero denominator is not zero revenue",()=>{let x=fixture();x.receipts.independent_merchant_settlements_verified=true;x.receipts.realized_net_cents=0;x.receipts.cohort_mature_and_refunds_fees_complete=true;x.attribution.qualified_human_sessions_audited=true;x.attribution.qualified_human_sessions=0;assert.equal(assess(x).realized_net_per_1000_human_sessions,null);});
t("missing snapshot fail closed",()=>assert.equal(assess(null).release_authorized,false));
t("no mutation of input",()=>{let x=fixture(),before=JSON.stringify(x);assess(x);assert.equal(JSON.stringify(x),before);});
process.stdout.write(n+"/"+n+" synthetic CommonJS checks passed; NO EMAIL OR LIVE WRITE\n");

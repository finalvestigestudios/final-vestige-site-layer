"use strict";
const assert=require("node:assert/strict");
const {audit,taggedEditorialCta,inspectTransport,releaseDecision,MISSING}=require("./consent_to_settlement_gate.cjs");
let passes=0;
function check(condition,message){assert.ok(condition,message);passes++}
function same(actual,expected,message){assert.equal(actual,expected,message);passes++}
function rejects(fn,message){assert.throws(fn,undefined,message);passes++}
function input(){
 return {as_of_utc:"2026-11-17T20:00:00Z",cohort_days:7,
 proofs:{qualified_human_sessions_complete:true,source_campaign_join_audited:true,merchant_reporting_complete:true,
 refunds_and_fees_complete:true,settlement_and_referral_verified:true,provider_consent_ledger_complete:true},
 sessions:[
 {session_id:"s_one",asset_id:"grok_a1",at_utc:"2026-11-16T12:00:00Z",human_verified:true,qualified:true,utm_source:"youtube",utm_campaign:"fv_mind_pilot"},
 {session_id:"s_two",asset_id:"grok_a2",at_utc:"2026-11-16T12:01:00Z",human_verified:true,qualified:true,utm_source:"tiktok",utm_campaign:"fv_mind_pilot"},
 {session_id:"s_bot",asset_id:"grok_a3",at_utc:"2026-11-16T12:02:00Z",human_verified:false,qualified:true,utm_source:"youtube",utm_campaign:"fv_mind_pilot"}],
 leads:[{provider_id:"p_alpha",session_id:"s_one",at_utc:"2026-11-16T13:00:00Z",provider_confirmed:true,consent_eligible:true,opted_out:false,suppressed:false}],
 orders:[{order_id:"order_xyz",session_id:"s_one",at_utc:"2026-11-16T14:00:00Z",status:"settled",
 merchant_confirmed:true,settlement_confirmed:true,revenue_type:"affiliate_commission",amount_cents:1900,refund_cents:100,fee_cents:200}]};
}
let s=audit(input());
same(s.status,"HOLD_UNSENT","never authorizes send");
same(s.qualified_human_sessions,2,"bot excluded");
same(s.deduplicated_provider_confirmed_leads,1,"real provider count");
same(s.matched_settled_orders,1,"merchant settlement count");
same(s.attributed_net_cents,1600,"net after refunds and fees");
same(s.net_revenue_per_1000_human_sessions,8000,"verified cohort synthetic KPI only");
same(s.paid_conversion_rate,50,"one paying visitor of two");
same(s.lead_to_customer_rate,100,"lead crosswalk");
same(s.missing_evidence.length,0,"no synthetic missing evidence");
let v=input();v.proofs.merchant_reporting_complete=false;s=audit(v);
same(s.net_revenue_per_1000_human_sessions,MISSING,"unknown merchant reporting is not zero");
same(s.attributed_net_cents,null,"no inferred money");
check(s.missing_evidence.includes("merchant_reporting_complete"),"missing source flagged");
v=input();v.orders=[];s=audit(v);same(s.attributed_net_cents,0,"verified complete zero is zero");
same(s.net_revenue_per_1000_human_sessions,0,"verified zero cohort");
v=input();v.sessions.push({...v.sessions[0]});s=audit(v);same(s.qualified_human_sessions,2,"identical session deduplicated");
v=input();v.sessions.push({...v.sessions[0],utm_campaign:"wrong"});rejects(()=>audit(v),"conflicting duplicate blocked");
v=input();v.orders.push({...v.orders[0]});s=audit(v);same(s.matched_settled_orders,1,"identical order deduplicated");
v=input();v.orders.push({...v.orders[0],amount_cents:3000});rejects(()=>audit(v),"conflicting orders blocked");
v=input();v.orders[0].merchant_confirmed=false;s=audit(v);same(s.net_revenue_per_1000_human_sessions,MISSING,"unconfirmed paid event not silently omitted");
v=input();v.orders[0].session_id="s_missing";s=audit(v);same(s.net_revenue_per_1000_human_sessions,MISSING,"unattributed settlement not zero");
v=input();v.orders[0].status="pending";s=audit(v);same(s.matched_settled_orders,0,"pending order is not paid");
v=input();v.orders[0].refund_cents=2200;s=audit(v);same(s.attributed_net_cents,-500,"negative net remains negative");
v=input();v.orders[0].fee_cents=-1;rejects(()=>audit(v),"negative fees rejected");
v=input();v.orders[0].amount_cents=1.2;rejects(()=>audit(v),"fractional cents rejected");
v=input();v.cohort_days=14;rejects(()=>audit(v),"only 7/30-day cohorts");
v=input();v.leads[0].opted_out=true;s=audit(v);same(s.deduplicated_provider_confirmed_leads,0,"opt-out is not lead eligible");
same(s.lead_to_customer_rate,MISSING,"no inferred lead-customer rate");
v=input();v.leads[0].provider_confirmed=false;s=audit(v);same(s.deduplicated_provider_confirmed_leads,0,"client state not provider consent");
v=input();v.leads.push({...v.leads[0]});s=audit(v);same(s.deduplicated_provider_confirmed_leads,1,"provider leads deduplicated");
v=input();v.proofs.provider_consent_ledger_complete=false;s=audit(v);same(s.deduplicated_provider_confirmed_leads,null,"unknown eligible list not count");
same(s.lead_to_customer_rate,MISSING,"lead-to-sale needs consent ledger");
v=input();v.sessions[0].at_utc="2026-10-01T00:00:00Z";s=audit(v);
same(s.net_revenue_per_1000_human_sessions,MISSING,"unmatched historical order attribution blocked");
v=input();v.sessions[0].utm_campaign="";s=audit(v);same(s.net_revenue_per_1000_human_sessions,MISSING,"missing campaign invalidates paid crosswalk");
v=input();v.sessions[0].email="nobody@example.com";rejects(()=>audit(v),"no email PII to GitHub");
v=input();v.sessions[0].ip="127.0.0.1";rejects(()=>audit(v),"no IP PII");
v=input();v.sessions[0].session_id="jane@example.com";rejects(()=>audit(v),"no address in IDs");
v=input();v.proofs.qualified_human_sessions_complete=false;s=audit(v);
same(s.qualified_human_sessions,null,"no invented human denominator");
let c=taggedEditorialCta(1,"https://finalvestige.com/2026/11/02/change-blindness/");
same(c.status,"CANDIDATE_URL_NOT_LIVE","not deployed");
check(c.url.includes("utm_source=dispatch"),"source UTM");
check(c.url.includes("utm_medium=email"),"medium UTM");
check(c.url.includes("utm_content=issue_01"),"edition UTM");
check(c.url.startsWith("https://finalvestige.com/"),"first-party");
for(const k of [2,4,6]){c=taggedEditorialCta(k,"https://finalvestige.com/focus/");
check(c.url.includes("utm_content=issue_0"+k),"edition "+k)}
for(const k of [3,5]){c=taggedEditorialCta(k,"[[APPROVED_GUIDE_REQUIRED]]");
same(c.url,null,"commercial "+k+" remains inert");
same(c.status,"HOLD_COMMERCIAL_GUIDE_NOT_APPROVED","commercial "+k+" hold")}
rejects(()=>taggedEditorialCta(1,"http://finalvestige.com/focus/"),"no plain HTTP");
rejects(()=>taggedEditorialCta(1,"https://inspire3.com/"),"no external merchant");
rejects(()=>taggedEditorialCta(1,"https://finalvestige.com/focus/?email=x"),"no email parameter");
rejects(()=>taggedEditorialCta(1,"https://finalvestige.com/focus/?ref=x"),"no affiliate ref");
rejects(()=>taggedEditorialCta(1,"https://evil.com@finalvestige.com/focus/"),"username rejected");
rejects(()=>taggedEditorialCta(1,"[[URL_REQUIRED]]"),"not a real CTA");
const p=inspectTransport(1,"The mind is not a camera","An old record shows the difference.","<p>EDITORIAL HOLD — DO NOT PUBLISH</p><p>Body</p>");
same(p.actual_email_preheader,"UNVERIFIED_JETPACK_RENDER","no fabricated inbox header");
same(p.first_editor_paragraph_has_hold_banner,true,"transport warning identified");
same(p.status,"HOLD_NATIVE_PREVIEW_UNWITNESSED","source != inbox");
same(p.valid_postal_and_unsubscribe_witness,false,"no synthetic legal pass");
same(inspectTransport(2,"A real title","A real preheader","<p>Body</p>").false_preheader_risk,"MAPPING_UNKNOWN","no false preview certainty");
rejects(()=>inspectTransport(0,"title","pre","<p>test</p>"),"invalid issue rejected");
const release=releaseDecision({commercial:true});
same(release.status,"HOLD_UNSENT","absolute send veto");
check(release.missing.includes("named_merchant_email_promotion_permission"),"merchant permission required");
check(release.missing.includes("publisher_postal_verified"),"FV physical address required");
check(release.missing.includes("unsubscribe_render_and_function_witness"),"tested opt-out required");
check(release.missing.includes("actual_native_jetpack_preview_witness"),"real preview required");
const all={commercial:true};
for(const k of release.missing)all[k]=true;
const ready=releaseDecision(all);same(ready.ready_for_review,true,"all synthetic evidence can enter founder review");
same(ready.status,"HOLD_UNSENT","even full simulated evidence cannot send");
same(ready.founder_release_required,true,"human release still needed");
console.log("PASS "+passes+"/"+passes+" exact-source assertions (runtime verified separately); all live channel actions remain HOLD_UNSENT");
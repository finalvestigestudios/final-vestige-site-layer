import assert from "node:assert/strict";
import {classifyGuest,reconcileSubscribers,countConfirmedSignup,attributeTouch,revenueKpi,releaseDecision} from "./gate.mjs";
// Only synthetic fixtures here; no real recipients, merchant sales, or measured conversions.
const tests=[]; const t=(name,fn)=>tests.push([name,fn]);
t("guest public form remains untested",()=>assert.deepEqual(classifyGuest({public_form_email_input:true,wp_view_self_link:true}),{status:"VISIBLE_FORM_STRUCTURE_ONLY",can_submit:null,source_disagreement:true}));
t("self-link alone cannot prove broken",()=>assert.equal(classifyGuest({wp_view_self_link:true}).can_submit,null));
t("provider aggregates overlap",()=>assert.equal(reconcileSubscribers({total:3,confirmed:3,unconfirmed:2,wp_followers:3,direct_email_followers:0}).eligible_recipients,null));
t("even additive totals cannot establish reachable recipients",()=>assert.equal(reconcileSubscribers({total:3,confirmed:2,unconfirmed:1,wp_followers:3,direct_email_followers:0}).eligible_recipients,null));
t("invalid totals refused",()=>assert.equal(reconcileSubscribers({total:-1,confirmed:2,unconfirmed:1,wp_followers:0,direct_email_followers:0}).state,"INVALID_SNAPSHOT"));
const ev={provider:"jetpack",status:"confirmed",marketing_permission_verified:true,provider_confirmation_event_id:"synthetic:1",confirmed_at:"2026-11-14",consent_provenance:"synthetic"};
t("real confirmation transition once",()=>{const s=new Set();assert.equal(countConfirmedSignup(ev,s),true);assert.equal(countConfirmedSignup(ev,s),false)});
for(const bad of [{status:"unconfirmed"},{marketing_permission_verified:false},{provider_confirmation_event_id:""},{confirmed_at:""},{consent_provenance:""},{provider:"other"}])t("invalid consent fixture "+JSON.stringify(bad),()=>assert.equal(countConfirmedSignup({...ev,...bad},new Set()),false));
t("preserve Grok first-touch",()=>assert.equal(attributeTouch({verified_first_touch:"social-id",verified_email_touch:"email-id"}).first_touch,"social-id"));
t("missing qualified sessions are unknown",()=>assert.equal(revenueKpi(null).net_revenue_per_1000,null));
t("no confirmed paid order without ledger",()=>assert.equal(revenueKpi({owner_reconciled:false,qualified_human_sessions:100,orders:[]}).net_revenue_per_1000,null));
const order={order_id:"synthetic-order",payment_status:"settled",independent_settlement_verified:true,currency:"USD",gross_minor:1000,fees_minor:100,refund_minor:200};
t("synthetic deduped revenue",()=>{const r=revenueKpi({owner_reconciled:true,qualified_human_sessions:100,orders:[order,order]});assert.equal(r.net_revenue_per_1000,70);assert.equal(r.verified_orders,1)});
for(const bad of [{payment_status:"pending"},{independent_settlement_verified:false},{currency:"GBP"},{fees_minor:-1},{order_id:""}])t("reject unauthenticated purchase "+JSON.stringify(bad),()=>assert.equal(revenueKpi({owner_reconciled:true,qualified_human_sessions:100,orders:[{...order,...bad}]}).net_revenue_per_1000,null));
t("editorial issue hold",()=>assert.equal(releaseDecision(1,{}).missing_evidence.length,6));
t("commercial issue hold",()=>assert.equal(releaseDecision(3,{}).missing_evidence.length,11));
t("issue05 merchant hold",()=>assert.equal(releaseDecision(5,{}).commercial_status,"HOLD_MERCHANT"));
t("no automatic release even when evidence booleans are filled",()=>{const keys=releaseDecision(3,{}).missing_evidence;const data=Object.fromEntries(keys.map(k=>[k,{verified:true,source:"synthetic",reviewer:"synthetic"}]));assert.equal(releaseDecision(3,data).status,"HOLD_UNSENT")});
let failed=0;for(const [name,fn] of tests){try{fn();console.log("PASS",name)}catch(e){failed++;console.error("FAIL",name,e.message)}}
console.log(tests.length-failed+"/"+tests.length+" synthetic gate tests passed");if(failed)process.exitCode=1;

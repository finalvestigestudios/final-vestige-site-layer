"use strict";
const assert=require("node:assert/strict");
const test=require("node:test");
const {REQUIRED_COMMON,REQUIRED_MERCHANT,releaseAssessment,confirmedSignup,revenuePerThousand}=require("../release_gate.cjs");
const BASE={founder:{},consent:{},delivery:{},render:{},merchant:{}};
const evidence=(paths)=>{const x=JSON.parse(JSON.stringify(BASE));for(const id of paths){const [a,b]=id.split(".");x[a][b]={verified:true,source:"https://example.org/verified-evidence/record",checked_at:"2026-11-07T16:45:00-08:00"};}return x;};
test("4 editorial / 2 commercial; ALL remain hold without attestations",()=>{
  assert.equal(Array.from({length:6},(_,i)=>releaseAssessment(BASE,i+1).kind).filter(k=>k==="editorial").length,4);
  for(let i=1;i<=6;i++)assert.equal(releaseAssessment(BASE,i).status,"HOLD_UNSENT");
});
test("no commercial status ready without seven separate merchant attestations",()=>{
  const x=evidence(REQUIRED_COMMON);
  for(const i of [3,5]) {const a=releaseAssessment(x,i);assert.equal(a.status,"HOLD_UNSENT");assert.equal(a.missing.length,REQUIRED_MERCHANT.length);}
});
test("false sources or string true are not authentic evidence",()=>{
  const x=evidence(REQUIRED_COMMON);
  x.render.unsubscribe_action_verified={verified:"true",source:"",checked_at:"today"};
  assert.equal(releaseAssessment(x,1).status,"HOLD_UNSENT");
});
test("even full synthetic attestations do not authorize a send",()=>{
  const x=evidence([...REQUIRED_COMMON,...REQUIRED_MERCHANT]);
  assert.equal(releaseAssessment(x,3).status,"READY_FOR_FOUNDER_RECHECK_NOT_AUTHORIZATION");
  assert.equal(releaseAssessment(x,3).mail_sent,false);
});
test("provider confirmation is required; URL params, CSS and gift are irrelevant",()=>{
  const s=new Set();
  for(const o of [{provider_status:"PENDING"},{provider_status:"READER"},{provider_status:"SUBSCRIBED",confirmation_method:"browser_query"}]){
    assert.equal(confirmedSignup({...o,private_dedup_key:"x",provider_confirmation_at:"2026-11-07"},s),false);
  }
  assert.equal(s.size,0);
});
test("private confirmation deduplicates and rejects suppressed",()=>{
  const s=new Set();
  const r={provider_status:"SUBSCRIBED",confirmation_method:"provider_double_opt_in",provider_confirmation_at:"2026-11-07",private_dedup_key:"private:1"};
  assert.equal(confirmedSignup(r,s),true);
  assert.equal(confirmedSignup(r,s),false);
  assert.equal(confirmedSignup({...r,private_dedup_key:"private:2",suppressed:true},s),false);
  assert.equal(s.size,1);
});
test("empty sales cannot be silently reported as zero",()=>{
  assert.equal(revenuePerThousand({orders:[],qualified_human_sessions:10,qualified_human_sessions_verified:true,order_ledger_reconciled:true,refunds_fees_reconciled:true}),null);
});
test("verified zero and verified nonzero revenue remain distinct",()=>{
  const ok={orders:[],qualified_human_sessions:100,qualified_human_sessions_verified:true,order_ledger_reconciled:true,refunds_fees_reconciled:true,zero_orders_independently_verified:true,zero_orders_source:"merchant_report:no_settlements_vetted",reconciliation_source:"merchant_report:reconciled_qhs_refunds",cohort_days:7};
  assert.equal(revenuePerThousand(ok).net_revenue_usd,0);
  assert.equal(revenuePerThousand({...ok,orders:[{settled_net_usd:12,independently_verified:true,merchant_report_ref:"merchant-report-order-001"}],zero_orders_independently_verified:false}).revenue_per_1000_qualified_human_sessions_usd,120);
});
test("clicks and revenue data gaps cannot fill checkout ledger",()=>{
  assert.equal(revenuePerThousand({affiliate_clicks:15,email_clicks:3,qualified_human_sessions:100}),null);
  assert.equal(revenuePerThousand({orders:[{settled_net_usd:12,independently_verified:false}],qualified_human_sessions:100,qualified_human_sessions_verified:true,order_ledger_reconciled:true,refunds_fees_reconciled:true,reconciliation_source:"merchant_report:reconciled"}),null);
});
test("invalid issue numbers fail closed",()=>{for(const i of [0,7,null])assert.throws(()=>releaseAssessment(BASE,i));});

test("cohort and statement proof cannot be omitted",()=>{
 const base={orders:[],qualified_human_sessions:100,qualified_human_sessions_verified:true,order_ledger_reconciled:true,refunds_fees_reconciled:true,zero_orders_independently_verified:true,zero_orders_source:"merch_report:zero",reconciliation_source:"merch_report:reconciled",cohort_days:7};
 assert.equal(revenuePerThousand({...base,cohort_days:null}),null);
 assert.equal(revenuePerThousand({...base,reconciliation_source:""}),null);
 assert.equal(revenuePerThousand({...base,zero_orders_source:""}),null);
 assert.equal(revenuePerThousand({...base,orders:[{settled_net_usd:10,independently_verified:true}]}),null);
});

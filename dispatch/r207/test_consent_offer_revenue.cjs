'use strict';
const lib = require('./consent_offer_revenue.cjs');
function assert(ok, why) { if (!ok) throw new Error(why); }
function eq(a,b,msg){assert(JSON.stringify(a)===JSON.stringify(b),msg+': '+JSON.stringify(a)+' != '+JSON.stringify(b));}
const FIX={status:'VERIFIED',evidence_ref:'WP_ORIGINAL_12345',reviewed_at:'2026-11-08T10:35:00Z'};
let passes=0;
function run(name,fn){fn();passes++;process.stdout?.write?.('PASS '+name+'\n');}
run('Canonical allocation is 4 editorial and 2 commercial',()=>{
  eq(Object.values(lib.ISSUE_TYPES).filter(x=>x==='merchant').length,2,'merchant count');
  eq(Object.keys(lib.ISSUE_TYPES).length,6,'total');
});
run('All unverified issues held',()=>Object.keys(lib.ISSUE_TYPES).forEach(id=>{
  assert(lib.gate(id).status.startsWith('HOLD_'),id);
  assert(!lib.gate(id).is_send_authorized,id);
}));
run('Unknown issue rejected',()=>{
  let ok=false;try{lib.gate('07')}catch(e){ok=true}assert(ok,'unknown');
});
run('Synthetic empty evidence is not proof',()=>{
  assert(!lib.verified({status:'VERIFIED',source_class:'partner_account',evidence_ref:'pending',reviewed_at:FIX.reviewed_at},'partner_account'),'placeholder');
});
run('Public seller page cannot stand in for account approval',()=>{
  assert(!lib.verified({...FIX,source_class:'merchant_page_and_checkout'},'partner_account'),'wrong class');
});
run('Editor screenshot cannot stand in for received email',()=>{
  assert(!lib.verified({...FIX,source_class:'authenticated_cms'},'received_message'),'wrong class');
});
run('Audience counters do not become eligible count',()=>{
  const r=lib.reconcileSubscribers({total:3,confirmed:3,unconfirmed:2,wpcom_followers:3,email_only_followers:0});
  assert(r.authoritative_eligible===null,'eligible unknown');
  assert(r.counted_total===3,'total retained');
});
run('Nonadditive counters do not compute 3+2',()=>{
  const r=lib.reconcileSubscribers({total:3,confirmed:3,unconfirmed:2,wpcom_followers:3,email_only_followers:0});
  assert(r.counted_total!==5,'not five');
});
run('Malformed source counts rejected',()=>{
  let ok=false;try{lib.reconcileSubscribers({total:-1,confirmed:3,unconfirmed:2,wpcom_followers:3,email_only_followers:0})}catch(e){ok=true}assert(ok,'invalid');
});
run('Even complete synthetic proof cannot trigger a send',()=>{
  const both={...lib.REQUIRED_SHARED,...lib.REQUIRED_MERCHANT};
  const p=Object.fromEntries(Object.entries(both).map(([k,v])=>[k,{...FIX,source_class:v}]));
  assert(lib.gate('03',p).status==='FOUNDER_REVIEW_ONLY','review only');
  assert(lib.gate('03',p).is_send_authorized===false,'no send');
  assert(lib.gate('01',p).status==='FOUNDER_REVIEW_ONLY','editorial review');
});
run('Missing affiliate EMAIL channel permission blocks merchant only',()=>{
  const keys={...lib.REQUIRED_SHARED,...lib.REQUIRED_MERCHANT};
  const p=Object.fromEntries(Object.entries(keys).map(([k,v])=>[k,{...FIX,source_class:v}]));
  delete p.email_channel_permission;
  assert(lib.gate('03',p).missing.includes('email_channel_permission'),'merchant permission required');
  assert(!lib.gate('01',p).missing.includes('email_channel_permission'),'editorial independent');
});
run('Absent report never means zero sales',()=>assert(lib.cohortRevenue({})===null,'missing'));
run('Clicks or visits alone never count as revenue',()=>assert(lib.cohortRevenue({outbound_clicks:1000,unique_qualified_human_sessions:1000})===null,'clicks'));
run('No denominator means not computable',()=>assert(lib.cohortRevenue({reconciled:true,source_class:'merchant_settlement_or_owned_checkout',complete_order_population:true,refunds_complete:true,fees_complete:true,confirmed_paid_orders:1,gross:10,refunds:0,fees:1,cohort:'7_day'})===null,'denominator'));
run('Reconciled zero is possible with a closed population',()=>{
  const v=lib.cohortRevenue({reconciled:true,source_class:'merchant_settlement_or_owned_checkout',complete_order_population:true,refunds_complete:true,fees_complete:true,confirmed_paid_orders:0,gross:0,refunds:0,fees:0,cohort:'7_day',unique_qualified_human_sessions:100});
  assert(v.net_per_1000_qualified_sessions===0,'actual zero');
});
run('Refunds and fees reduce settled net, separate from clicks',()=>{
  const v=lib.cohortRevenue({reconciled:true,source_class:'merchant_settlement_or_owned_checkout',complete_order_population:true,refunds_complete:true,fees_complete:true,confirmed_paid_orders:2,gross:50,refunds:10,fees:5,cohort:'30_day',unique_qualified_human_sessions:100});
  assert(v.net_revenue===35 && v.net_per_1000_qualified_sessions===350,'net');
});
process.stdout?.write?.('TOTAL '+passes+'/'+passes+' PASS (synthetic)\n');
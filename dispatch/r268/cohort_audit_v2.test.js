'use strict';
const assert=require('node:assert/strict');
const {inspect,SCHEMA}=require('./cohort_audit_v2');
const b=()=>({schema:SCHEMA,mode:'synthetic',as_of_day:'2026-11-10',
 attestations:{complete_qualified_sessions:true,jetpack_confirmations_verified:true,merchant_settlements_reconciled:true,cohort_attribution_verified:true,publisher_postal_and_unsubscribe_verified:false,partner_email_permission_verified:false,founder_campaign_approval:false},
 sessions:[{day:'2026-11-09',utm_source:'youtube',utm_medium:'organic_social',utm_campaign:'mind_pilot_2026_11',utm_content:'yt_001',attribution_class:'tagged_asset',qualified_human_sessions:100}],
 confirmations:[{day:'2026-11-09',provider:'jetpack',event_ref:'ev_001',status:'confirmed',consent_scope:'fv_dispatch'}],
 settlements:[{acquisition_day:'2026-11-09',settled_day:'2026-11-10',merchant:'inspire3',order_ref:'order_001',utm_source:'youtube',utm_medium:'organic_social',utm_campaign:'mind_pilot_2026_11',utm_content:'yt_001',attribution_class:'tagged_asset',status:'settled',gross_cents:100,refund_cents:100,fee_cents:5}]});
const tests=[];function t(name,fn){tests.push([name,fn]);}
const mutate=fn=>{const x=b();fn(x);return inspect(x)};
t('canonical Grok UTM accepted',()=>assert(inspect(b()).pass));
t('net reflects genuine loss after full refund and nonrefundable fee',()=>assert.equal(inspect(b()).cohorts['7d'].net_cents,-5));
t('net per thousand can be negative',()=>assert.equal(inspect(b()).cohorts['7d'].net_cents_per_1000_qualified_tagged_sessions,-50));
t('only synthetic evidence classification',()=>assert.equal(inspect(b()).evidence_class,'SYNTHETIC_EXAMPLE'));
t('external aggregate remains unverified',()=>assert.equal(mutate(x=>x.mode='external_aggregate').evidence_class,'UNVERIFIED_EXTERNAL_ATTESTATION'));
t('no automated send authorization',()=>assert.equal(inspect(b()).send_authorized,false));
t('no affiliate activation',()=>assert.equal(inspect(b()).affiliate_activation_authorized,false));
t('7d cohort begins Nov 4',()=>assert.equal(inspect(b()).cohorts['7d'].start_day,'2026-11-04'));
t('30d cohort begins Oct 12',()=>assert.equal(inspect(b()).cohorts['30d'].start_day,'2026-10-12'));
t('confirmed lead only counted once',()=>{const r=mutate(x=>x.confirmations.push({...x.confirmations[0]}));assert(r.pass);assert.equal(r.cohorts['7d'].confirmed_signups_unjoined,1)});
t('pending then confirmed same ID fails',()=>assert(!mutate(x=>x.confirmations.push({...x.confirmations[0],status:'pending'})).pass));
t('suppressed then confirmed same ID fails',()=>assert(!mutate(x=>x.confirmations.push({...x.confirmations[0],status:'suppressed'})).pass));
t('same event ID different day fails',()=>assert(!mutate(x=>x.confirmations.push({...x.confirmations[0],day:'2026-11-10'})).pass));
t('seller signup is not FV signup',()=>assert(!mutate(x=>x.confirmations[0].provider='zen12').pass));
t('pinterest is valid source',()=>assert(mutate(x=>{x.sessions[0].utm_source='pinterest';x.settlements[0].utm_source='pinterest'}).pass));
t('bluesky is valid source',()=>assert(mutate(x=>{x.sessions[0].utm_source='bluesky';x.settlements[0].utm_source='bluesky'}).pass));
t('unsupported platform denied',()=>assert(!mutate(x=>x.sessions[0].utm_source='reddit').pass));
t('placeholder cluster is not allowed UTM',()=>assert(!mutate(x=>x.sessions[0].utm_campaign='cluster_pilot_2026_11').pass));
t('valid history campaign',()=>assert(mutate(x=>{x.sessions[0].utm_campaign='history_pilot_2026_11';x.settlements[0].utm_campaign='history_pilot_2026_11'}).pass));
t('wrong medium denied',()=>assert(!mutate(x=>x.sessions[0].utm_medium='paid_social').pass));
t('pii in asset denied',()=>assert(!mutate(x=>x.sessions[0].utm_content='user@example.com').pass));
t('profile traffic cannot claim asset',()=>assert(!mutate(x=>{x.sessions[0].attribution_class='profile_unresolved'}).pass));
t('profile traffic can be observed but not attributed',()=>{const r=mutate(x=>x.sessions.push({day:'2026-11-10',utm_source:'tiktok',utm_medium:'organic_social',utm_campaign:'mind_pilot_2026_11',utm_content:null,attribution_class:'profile_unresolved',qualified_human_sessions:30}));assert(r.pass);assert.equal(r.cohorts['7d'].qualified_profile_sessions_without_asset,30);assert.equal(r.cohorts['7d'].qualified_tagged_asset_sessions,100)});
t('unmatched purchase excluded from attributed money',()=>{const r=mutate(x=>x.settlements[0].utm_content='another_asset');assert(r.pass);assert.equal(r.cohorts['7d'].matched_reported_orders,0);assert.equal(r.cohorts['7d'].unmatched_reported_orders,1)});
t('same asset on wrong day excluded',()=>{const r=mutate(x=>x.settlements[0].acquisition_day='2026-11-08');assert(r.pass);assert.equal(r.cohorts['7d'].matched_reported_orders,0)});
t('zero session route excludes order',()=>{const r=mutate(x=>x.sessions[0].qualified_human_sessions=0);assert(r.pass);assert.equal(r.cohorts['7d'].matched_reported_orders,0)});
t('duplicate daily session rejected',()=>assert(!mutate(x=>x.sessions.push({...x.sessions[0]})).pass));
t('duplicate order rejected',()=>assert(!mutate(x=>x.settlements.push({...x.settlements[0]})).pass));
t('refunded record subtracts commission',()=>{const r=mutate(x=>x.settlements[0].status='refunded');assert(r.pass);assert.equal(r.cohorts['7d'].net_cents,-5)});
t('pending order does not count',()=>{const r=mutate(x=>x.settlements[0].status='pending');assert(r.pass);assert.equal(r.cohorts['7d'].matched_reported_orders,0)});
t('refund cannot exceed gross',()=>assert(!mutate(x=>x.settlements[0].refund_cents=101).pass));
t('fee may exceed gross resulting in negative net',()=>{const r=mutate(x=>{x.settlements[0].refund_cents=0;x.settlements[0].fee_cents=200});assert(r.pass);assert.equal(r.cohorts['7d'].net_cents,-100)});
t('large unsafe integer rejected',()=>assert(!mutate(x=>x.sessions[0].qualified_human_sessions=Number.MAX_SAFE_INTEGER+1).pass));
t('null receipt counts as unknown not zero',()=>{const r=mutate(x=>x.attestations.merchant_settlements_reconciled=false);assert(r.pass);assert.equal(r.cohorts['7d'].net_cents,null);assert.equal(r.cohorts['7d'].net_cents_per_1000_qualified_tagged_sessions,null)});
t('incomplete signup evidence yields null',()=>{const r=mutate(x=>x.attestations.jetpack_confirmations_verified=false);assert(r.pass);assert.equal(r.cohorts['7d'].confirmed_signups_unjoined,null)});
t('all release attestations must remain false',()=>assert(!mutate(x=>x.attestations.founder_campaign_approval=true).pass));
t('missing release field rejected',()=>assert(!mutate(x=>delete x.attestations.partner_email_permission_verified).pass));
t('unauthorized PII field rejected',()=>assert(!mutate(x=>x.confirmations[0].email='private@example.com').pass));
t('malformed calendar day rejected',()=>assert(!mutate(x=>x.as_of_day='2026-11-31').pass));
t('future settlement rejected',()=>assert(!mutate(x=>x.settlements[0].settled_day='2026-11-11').pass));
t('lead-to-customer rate never fabricated',()=>assert.equal(inspect(b()).cohorts['7d'].lead_to_customer_rate,null));
t('buyer evidence never implied by route match',()=>assert.equal(inspect(b()).cohorts['7d'].independently_attributable_sales,'NOT_VERIFIED_BY_THIS_TOOL'));
let pass=0;for(const [name,fn] of tests){try{fn();console.log('PASS '+name);pass++}catch(e){console.error('FAIL '+name+': '+e.message);process.exitCode=1}}console.log(`SUMMARY ${pass}/${tests.length}`);

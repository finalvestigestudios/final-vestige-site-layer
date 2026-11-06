'use strict';
/* R166 offline cohort and confirmed-lead revenue truth contract.
 * NO WordPress/merchant calls, no email sends, no PII storage, no live instrumentation.
 * Values are integer cents of FV's ACTUAL revenue, not gross merchant checkout value.
 */
const OPAQUE=/^proof:[A-Za-z0-9][A-Za-z0-9._-]{5,95}$/;
const ID=/^asset:[A-Za-z0-9][A-Za-z0-9_-]{4,63}$/;
const CAMPAIGN=/^[a-z][a-z0-9_]{3,80}$/;
const PLATFORMS=new Set(['youtube','tiktok','instagram','facebook','pinterest','snapchat','x','bluesky']);
const pii=/(?:[\w.+-]+)@(?:[\w-]+\.)+[\w-]+|(?:subscriber_email|email_address|confirmation_token|session_cookie|access_token|full_name|ip_address)\s*["':=]/i;
const count=x=>Number.isSafeInteger(x)&&x>=0;
function safe(x){if(x===null||typeof x!=='object'||pii.test(JSON.stringify(x)))throw Error('Missing evidence or disallowed personal data');}
function sourceCheck(s){
 safe(s);
 if(s.origin!=='grok_verified_asset_inventory'||!PLATFORMS.has(s.utm_source)||s.utm_medium!=='organic_social'||!CAMPAIGN.test(s.utm_campaign||'')||!ID.test(s.utm_content||'')||!OPAQUE.test(s.asset_inventory_proof||''))throw Error('Unverified creator source or malformed attribution');
 return {source_checked:true,not_a_sale:true};
}
function confirmSignupCandidate(e){
 safe(e);
 if(e.source!=='Jetpack Subscriber Email subscription column'||e.before==='Subscribed'||e.after!=='Subscribed'||e.observed_via!=='provider_status_change'||!OPAQUE.test(e.proof_ref||''))throw Error('No provider-confirmed transition');
 // A status transition is not enough to infer a unique person without private provider dedup.
 return Object.freeze({event:'confirmed_signup_candidate',provider_transition_attested:true,unique_person_count:null,delivery_verified:false,paid_sale:false});
}
function snapshot(a){
 safe(a);
 const labels=['reported_total','reported_confirmed','reported_unconfirmed','reported_suppressed'];
 if(labels.some(k=>!count(a[k])))throw Error('Invalid provider count');
 if(a.reported_confirmed>a.reported_total)throw Error('Confirmed exceeds reported total');
 return Object.freeze({reported_total:a.reported_total,reported_confirmed:a.reported_confirmed,reported_unconfirmed:a.reported_unconfirmed,nonadditive:true,verified_reachable:null});
}
function cohort(c){
 safe(c);
 if(![7,30].includes(c.window_days))throw Error('Only 7/30 day cohorts permitted');
 const day=/^\\d{4}-\\d{2}-\\d{2}$/;
 if(!day.test(c.start_date_utc||'')||!day.test(c.end_date_utc||''))throw Error('Missing UTC cohort boundaries');
 const start=Date.parse(c.start_date_utc),end=Date.parse(c.end_date_utc);
 if(!Number.isFinite(start)||!Number.isFinite(end)||new Date(start).toISOString().slice(0,10)!==c.start_date_utc||new Date(end).toISOString().slice(0,10)!==c.end_date_utc||end-start!==c.window_days*86400000)throw Error('Cohort time bounds mismatch');
 if(!sourceCheck(c.source).source_checked)throw Error('Source absent');
 const checks=['qualified_human_sessions_verified','paid_source_verified','settlement_verified','refunds_fees_reconciled','attribution_reconciled'];
 if(checks.some(k=>c[k]!==true))return Object.freeze({window_days:c.window_days,net_cents:null,net_per_1000:null,status:'NOT_COMPUTABLE',missing:checks.filter(k=>c[k]!==true)});
 if(!OPAQUE.test(c.session_proof||'')||!OPAQUE.test(c.settlement_proof||'')||!OPAQUE.test(c.refund_proof||'')||!count(c.qualified_human_sessions)||!c.qualified_human_sessions)throw Error('Missing independent settlement or human-session proof');
 for(const k of ['fv_settled_receipts_cents','refunds_cents','fees_cents','verified_paid_orders'])if(!count(c[k]))throw Error('Noninteger or invalid source-backed financial input: '+k);
 // Negative net is a legitimate observed outcome and MUST NOT be censored.
 const net=c.fv_settled_receipts_cents-c.refunds_cents-c.fees_cents;
 if(!Number.isSafeInteger(net))throw Error('Unsafe arithmetic');
 const per1000=Math.round(net*1000*100/c.qualified_human_sessions)/100;
 if(!Number.isFinite(per1000))throw Error('Overflow');
 return Object.freeze({window_days:c.window_days,net_cents:net,net_per_1000:per1000,net_per_1000_unit:'USD cents',status:'SOURCE_ATTESTED_INPUT_ONLY',verified_paid_orders:c.verified_paid_orders,small_sample:c.qualified_human_sessions<1000||c.verified_paid_orders<30});
}
function release(){return Object.freeze({send_authorized:false,publish_authorized:false,merchant_activation_authorized:false,emails_sent:0});}
module.exports={sourceCheck,confirmSignupCandidate,snapshot,cohort,release};
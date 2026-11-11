'use strict';
/** Offline *non-deployable* guard for R268 cohort examples.
 * A caller-controlled boolean cannot authenticate a merchant payout or Jetpack signup.
 * No I/O, sends, emails, subscriber records, provider API, or network access.
 */
const {inspect: inspectV2} = require('../r268/cohort_audit_v2.js');
const PRIVATE_FIELDS = ['order_ref','event_ref','to','cc','bcc','email','subscriber','ip','name','recipient'];
const MASKED_FIELDS = [
 'confirmed_signups_unjoined','matched_reported_orders','unmatched_reported_orders',
 'gross_cents','refund_cents','fees_cents','net_cents',
 'net_cents_per_1000_qualified_tagged_sessions'
];
function resultBase(){return {
 schema:'FV-DISPATCH-REVENUE-PROOF-GATE-V3',
 release:'HOLD_UNSENT', send_authorized:false, merchant_link_authorized:false,
 campaign_approved:false, authenticated_merchant_sale:false,
 confirmed_signup_verified:false, realized_net_revenue_verified:false,
 external_metrics:'NOT_COMPUTABLE',
 affiliate_consent:'NOT_VERIFIED', eligible_recipient_count:null,
 jetpack_rendering:'NOT_VERIFIED', publisher_postal:'NOT_VERIFIED',
 unsubscribe_function:'NOT_VERIFIED', welcome_receipt:'NOT_VERIFIED'
};}
function review(input) {
 const base=resultBase();
 if(!input || typeof input!=='object' || Array.isArray(input))
  return {...base,valid:false,reason:'INPUT_REQUIRED',demonstration:null};
 // No upstream claim can turn this offline QA into an authenticated transaction.
 const checked=inspectV2(input);
 if(!checked.pass)return {...base,valid:false,reason:'UNDERLYING_SCHEMA_REJECTED',
  error_codes:checked.errors,demonstration:null};
 if(input.mode!=='synthetic' && input.mode!=='external_aggregate')
  return {...base,valid:false,reason:'MODE_REJECTED',demonstration:null};
 if(input.mode==='external_aggregate')return {...base,valid:true,
  evidence_type:'CALLER_SUPPLIED_EXTERNAL_DATA_NOT_AUTHENTICATED',
  reason:'PROVIDER_AUTHENTICATED_CONFIRMATIONS_AND_SETTLEMENTS_UNAVAILABLE',
  demonstrated_cohorts:null,demonstration:null,
  cohort_windows:['7d','30d'],
  note:'All financial and lead aggregates suppressed, including when every caller-supplied attestation is true.'};
 const cohorts={};
 for(const period of ['7d','30d']){
   const src=checked.cohorts[period];
   const sample={window:period,start_day:src.start_day,end_day:src.end_day,
    all_values_hypothetical:true,
    // For demonstrations only; never release as published metrics.
    example_sessions:input.sessions.filter(x=>{
     const dt=Date.parse(x.day+'T00:00:00Z');
     return dt>=Date.parse(src.start_day+'T00:00:00Z') && dt<=Date.parse(src.end_day+'T00:00:00Z') && x.attribution_class==='tagged_asset';
    }).reduce((s,x)=>s+x.qualified_human_sessions,0),
    example_net_cents:null,example_net_cents_per_1000:null
   };
   // V2 computes demonstration math only if its four input attestations are true.
   if(Number.isSafeInteger(src.net_cents)) {
    sample.example_net_cents=src.net_cents;
    sample.example_net_cents_per_1000=src.net_cents_per_1000_qualified_tagged_sessions;
   }
   cohorts[period]=sample;
 }
 return {...base,valid:true,reason:'SYNTHETIC_EXAMPLE_ONLY',evidence_type:'SYNTHETIC',
  demonstration:cohorts, note:'Never treat example money, signups or session counts as Final Vestige outcomes.'};
}
module.exports={review, resultBase, MASKED_FIELDS, PRIVATE_FIELDS};

'use strict';
/** Offline evidence contract, not a WordPress subscriber API, sender or analytics script. */
const SITE_ID=256784396;
const METHODS=new Set(['email_link_confirmed','verified_wpcom_account']);
const STATES=new Set(['Not confirmed','Not subscribed','Requested']);
const safeToken=x=>typeof x==='string'&&/^[A-Za-z0-9_-]{8,64}$/.test(x);
const epoch=x=>typeof x==='string'&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z$/.test(x)&&Number.isFinite(Date.parse(x))?Date.parse(x):NaN;
function checkProviderTransition(input,nowIso){
 const faults=[];const x=input||{};const at=epoch(x.observed_at),now=epoch(nowIso);
 if(x.origin!=='authenticated_jetpack_subscribers_tab'||x.site_id!==SITE_ID)faults.push('provider_provenance');
 if(!safeToken(x.private_subject_key))faults.push('opaque_subject_key');
 if(!STATES.has(x.previous_email_subscription)||x.current_email_subscription!=='Subscribed')faults.push('not_new_subscribed_transition');
 if(x.email_eligible!==true||x.suppressed!==false||x.bounced!==false||x.paused!==false||x.not_sending!==false)faults.push('email_eligibility');
 if(!METHODS.has(x.confirmation_method))faults.push('confirmation_method');
 if(x.confirmation_method==='email_link_confirmed'&&x.provider_link_confirmation!==true)faults.push('confirmation_link_evidence');
 if(x.confirmation_method==='verified_wpcom_account'&&x.provider_account_verified!==true)faults.push('account_verification_evidence');
 if(!Number.isFinite(at)||!Number.isFinite(now)||at>now||now-at>86400000)faults.push('stale_or_invalid_record');
 if(x.same_list!==true||x.observer_attested!==true)faults.push('list_scope_or_attestation');
 return {status:faults.length?'HOLD_NO_CONFIRMED_SIGNUP':'PROVIDER_TRANSITION_CANDIDATE',faults};
}
/** Keep seen private, created by authorized operator; do not send keys to analytics. */
function issueConfirmedSignup(input,nowIso,seen){
 const evaluated=checkProviderTransition(input,nowIso);
 if(evaluated.faults.length)return {...evaluated,emitted:false};
 if(!(seen instanceof Set))return {status:'HOLD_NO_CONFIRMED_SIGNUP',faults:['missing_private_dedupe'],emitted:false};
 const key=SITE_ID+'|'+input.private_subject_key;
 if(seen.has(key))return {status:'ALREADY_COUNTED',faults:[],emitted:false};
 seen.add(key);
 // No email address, subject key, IP, token, cookie or personal URL in event.
 return {status:'ELIGIBLE_FOR_AUTHORIZED_ANALYTICS_REVIEW_ONLY',faults:[],emitted:true,
  event:{name:'confirmed_signup',site_id:SITE_ID,proof:'authenticated_provider_transition',attribution:'unverified_until_source_join'}};
}
function reconcilePublicCounts(snapshot){
 const s=snapshot||{};
 return {dashboard_total:s.dashboard_total??null,dashboard_confirmed:s.dashboard_confirmed??null,
  dashboard_unconfirmed:s.dashboard_unconfirmed??null,stats_email_followers:s.stats_email_followers??null,
  stats_wpcom_followers:s.stats_wpcom_followers??null,
  confirmed_email_eligible:null,provider_subscription_transitions:null,
  status:'UNRECONCILED_DIFFERENT_POPULATIONS',additive:false};
}
function campaignRelease(){return {state:'HOLD_UNSENT',issues:{'01':'HOLD','02':'HOLD','03':'HOLD_MERCHANT','04':'HOLD','05':'HOLD_MERCHANT','06':'HOLD'},send_authorized:false};}
module.exports={checkProviderTransition,issueConfirmedSignup,reconcilePublicCounts,campaignRelease};

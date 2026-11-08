'use strict';
/**
 * Dispatch R153: OFFLINE classification of native WordPress evidence.
 * No network, browser, DOM, disk, cookie, email, or send APIs.
 * Inputs must come from a separately inspected provider. Local classification
 * cannot independently prove a real signup or create an analytics event.
 *
 * Existing verified WordPress.com accounts may not receive a new confirmation
 * email; new nonverified email addresses can remain Not confirmed.
 * "Confirmed" aggregates are NOT the "Email subscription: Subscribed" field.
 */
const VALID_STATUS=new Set(['Subscribed','Not confirmed','Not subscribed','Bounced','Emails paused','Not sending']);
const ROUTE=new Set(['email_confirmation_completed','preverified_wpcom_account']);
const KEYS=new Set(['provider','email_subscription_status','provider_subscriber_ref',
 'consent_scope','consent_observed','provider_event_ref','provider_transition',
 'verification_route','provider_transition_at','confirmation_result',
 'existing_account_preverified']);
const EMAIL_RE=/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/i;
const OPAQUE=/^[a-zA-Z0-9_-]{8,80}$/;
const ISO=/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?Z$/;
function piiFree(record){
  return !!(record&&typeof record==='object'&&!Array.isArray(record)&&
     Object.entries(record).every(([k,v])=>KEYS.has(k)&&
      (v===null||typeof v==='boolean'||
       (typeof v==='string'&&v.length<=160&&!EMAIL_RE.test(v)))));
}
function utc(x){
  return typeof x==='string'&&ISO.test(x)&&
   !Number.isNaN(Date.parse(x))&&
   new Date(x).toISOString().replace('.000Z','Z')===x.replace('.000Z','Z');
}
function opaque(x){return typeof x==='string'&&OPAQUE.test(x);}
function classify(record){
  if(!record||typeof record!=='object'||Array.isArray(record))
    return {classification:'REJECTED',reason:'INVALID_RECORD'};
  if(!piiFree(record))return {classification:'REJECTED',reason:'PII_OR_UNSAFE_FIELD'};
  if(record.provider!=='jetpack_native')
    return {classification:'REJECTED',reason:'WRONG_PROVIDER'};
  if(!VALID_STATUS.has(record.email_subscription_status))
    return {classification:'REJECTED',reason:'INVALID_STATUS'};
  if(record.email_subscription_status!=='Subscribed')
    return {classification:'NOT_EMAIL_ELIGIBLE',reason:record.email_subscription_status};
  if(!opaque(record.provider_subscriber_ref))
    return {classification:'SNAPSHOT_ONLY',reason:'NO_OPAQUE_PROVIDER_REF'};
  if(record.consent_scope!=='finalvestige_dispatch_editorial'||record.consent_observed!==true)
    return {classification:'SNAPSHOT_ONLY',reason:'NO_EDITORIAL_CONSENT_EVIDENCE'};
  if(!opaque(record.provider_event_ref)||record.provider_transition!=='new_subscription')
    return {classification:'ELIGIBLE_SNAPSHOT_CANDIDATE',reason:'NO_NEW_PROVIDER_TRANSITION'};
  if(!ROUTE.has(record.verification_route)||!utc(record.provider_transition_at))
    return {classification:'ELIGIBLE_SNAPSHOT_CANDIDATE',reason:'UNVERIFIED_ROUTE_OR_TIME'};
  if(record.verification_route==='email_confirmation_completed'&&record.confirmation_result!=='completed')
    return {classification:'ELIGIBLE_SNAPSHOT_CANDIDATE',reason:'CONFIRMATION_NOT_COMPLETED'};
  if(record.verification_route==='preverified_wpcom_account'&&record.existing_account_preverified!==true)
    return {classification:'ELIGIBLE_SNAPSHOT_CANDIDATE',reason:'PREVERIFIED_NOT_EVIDENCED'};
  return {
    classification:'CONFIRMED_SIGNUP_CANDIDATE_ONLY',
    reason:'REQUIRES_INDEPENDENT_NATIVE_PROVIDER_AUDIT',
    dedup_key:record.provider_event_ref,
    subscriber_ref:record.provider_subscriber_ref,
    time:record.provider_transition_at
  };
}
function aggregate(records){
  if(!Array.isArray(records)||records.length>10000)
    throw Error('bounded input array required');
  const events=new Set(),people=new Set();
  let candidates=0,duplicates=0,rejections=0,snapshots=0,ineligible=0;
  const classes=[];
  for(const r of records){
    const c=classify(r); classes.push({classification:c.classification,reason:c.reason});
    if(c.classification==='CONFIRMED_SIGNUP_CANDIDATE_ONLY'){
      if(events.has(c.dedup_key)||people.has(c.subscriber_ref)){duplicates++;continue;}
      events.add(c.dedup_key);people.add(c.subscriber_ref);candidates++;
    } else if(c.classification==='REJECTED')rejections++;
    else if(c.classification==='NOT_EMAIL_ELIGIBLE')ineligible++;
    else snapshots++;
  }
  return {
    verified_confirmed_signup_count:null,
    independently_eligible_recipient_count:null,
    candidate_count:candidates,duplicate_candidates:duplicates,
    rejected_records:rejections,ineligible_records:ineligible,snapshot_only_records:snapshots,
    event_contract:'confirmed_signup requires independent provider-confirmed transition and eligible email status',
    received_welcome_count:null,net_revenue_per_1000_qualified_sessions:null,
    classes
  };
}
module.exports={VALID_STATUS,ROUTE,piiFree,classify,aggregate};

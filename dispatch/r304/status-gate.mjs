/** Pure, offline-only Jetpack aggregate diagnostics. No subscriber lookup, email or event emission. */

function validInt(n){return Number.isInteger(n)&&n>=0;}

function countSnapshot(s){
  const a=s?.newsletter,b=s?.followers;
  if(!a||!b||![a.total,a.confirmed,a.unconfirmed,b.email,b.wpcom].every(validInt)) return {status:"INVALID_SNAPSHOT",eligible_email_recipients:null};
  return {status:"AGGREGATE_ONLY",total:a.total,confirmed:a.confirmed,unconfirmed_not_in_total:a.unconfirmed,wpcom_followers:b.wpcom,email_followers:b.email,eligible_email_recipients:null,confirmation_note:"Unconfirmed entries are not included in the WordPress subscriber total; email eligibility requires the per-subscriber Email subscription status."};
}

function eligibleFromStatuses(d){
  const fields=["subscribed","not_subscribed","bounced","emails_paused","not_sending"];
  if(d?.source!=="jetpack_email_subscription_status_mutually_exclusive_aggregate"||d?.contains_pii!==false||typeof d?.observed_at!=="string"||!/^20\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(d.observed_at)||!validInt(d.total)||!validInt(d.not_confirmed)||!fields.every(k=>validInt(d[k]))) return {status:"INSUFFICIENT_PROVIDER_PROOF",eligible_email_recipients:null};
  if(fields.reduce((n,k)=>n+d[k],0)!==d.total) return {status:"NON_RECONCILING_ROWS",eligible_email_recipients:null};
  return {status:"COUNT_ESTIMATE_FROM_PROVIDER_STATUS_ROWS",eligible_email_recipients:d.subscribed,immediate_deliveries:null,confirmed_signup_events:null,notes:"Instant/daily/weekly delivery preferences and prior-versus-new transitions are not captured by this aggregate."};
}

function classifyProgression(e){
  if(!e||typeof e!=="object"||e.provider!=="jetpack"||e.email_subscription!=="subscribed"||!["verified_wp_account","confirmed_email_link"].includes(e.confirmation)||e.is_new_transition!==true||e.durable_dedup_applied!==true||e.suppressed===true||e.bounced===true) return "NOT_VERIFIED_NEW_SIGNUP";
  if(Object.keys(e).some(k=>/^(email|name|ip|address|user_id|subscriber_id)$/i.test(k))) return "PII_PRESENT_REJECT";
  return "ELIGIBLE_EVENT_CANDIDATE_NOT_EMITTED";
}

export {countSnapshot,eligibleFromStatuses,classifyProgression};


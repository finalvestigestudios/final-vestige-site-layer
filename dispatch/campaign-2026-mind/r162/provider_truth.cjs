'use strict';
// Dispatch R162: offline, read-only evidence checks. NEVER contacts an API or sends mail.
const STATUSES = Object.freeze(['Subscribed','Not subscribed','Not confirmed','Bounced','Emails paused','Not sending']);
const OPAQUE = /^proof:[a-zA-Z0-9][a-zA-Z0-9._-]{5,95}$/;
const KEY = /^anon:[a-zA-Z0-9_-]{16,96}$/;
const isCount = n => Number.isSafeInteger(n) && n >= 0;
const zeroPII = value => {
  const s = JSON.stringify(value);
  if (/(?:[\w.+-]+)@(?:[\w-]+\.)+[\w-]+|(?:email_address|first_name|last_name|subscriber_email|tokenized_link|access_token)\s*["':=]/i.test(s)) throw Error('Personal data not permitted');
};
function reconcile(snapshot) {
  zeroPII(snapshot);
  if (!snapshot || !snapshot.newsletter || !snapshot.followers) throw Error('Missing separate provider surfaces');
  const {newsletter:n, followers:f} = snapshot;
  for (const k of ['total','confirmed','unconfirmed']) if (!isCount(n[k])) throw Error('Invalid newsletter count: '+k);
  for (const k of ['email','wpcom']) if (!isCount(f[k])) throw Error('Invalid follower count: '+k);
  if (n.confirmed > n.total) throw Error('Confirmed exceeds newsletter total');
  // Never sum newsletter unconfirmed + total or follower cohorts. Statuses can overlap.
  const result = {reported_newsletter_total:n.total, reported_confirmed:n.confirmed, reported_unconfirmed:n.unconfirmed,
    reported_wpcom_followers:f.wpcom, reported_legacy_email_followers:f.email,
    verified_email_eligible:null, verified_confirmed_signups:null,
    reported_population_additive:false, source_truth:'AGGREGATE_SNAPSHOT_ONLY', release:'HOLD_UNSENT'};
  const statuses=snapshot.email_subscription_statuses;
  if (statuses !== undefined) {
    if (!statuses || statuses.source !== 'Jetpack Subscriber Email subscription column' || !OPAQUE.test(statuses.proof_ref || '')) throw Error('Missing individual-status provenance');
    if (!statuses.counts || Object.keys(statuses.counts).some(k=>!STATUSES.includes(k))) throw Error('Invalid provider status labels');
    for (const k of STATUSES) if (!isCount(statuses.counts[k] ?? 0)) throw Error('Invalid status count '+k);
    if ((statuses.counts['Subscribed'] || 0) > n.total) throw Error('Eligible count exceeds reported total');
    result.verified_email_eligible=statuses.counts['Subscribed'] || 0;
    result.source_truth='PROVIDER_STATUS_ATTESTED_NOT_DELIVERY_TESTED';
  }
  return result;
}
function confirmedSignup(transitions) {
  if (!Array.isArray(transitions)) throw Error('Transitions must be an array');
  zeroPII(transitions);
  const seen=new Set();let events=0;
  for(const t of transitions){
    if(!t || !KEY.test(t.anonymous_key || '') || !OPAQUE.test(t.proof_ref || '')) throw Error('Missing anonymous identity or evidence');
    if(t.source!=='Jetpack Subscriber Email subscription column' || !STATUSES.includes(t.before) || !STATUSES.includes(t.after)) throw Error('Unknown transition');
    if(t.after!=='Subscribed' || t.before==='Subscribed') continue;
    if(seen.has(t.anonymous_key)) continue;
    if(t.observed_via!=='provider_status_change') continue;
    // Already-verified WordPress.com users may go Reader-only -> Subscribed, without a confirmation email.
    seen.add(t.anonymous_key);events++;
  }
  return {attested_newly_eligible:events, source:'provider_status_change_only', actual_live_events:'NOT_VERIFIED_BY_OFFLINE_TEST', release:'HOLD_UNSENT'};
}
function revenueKpi(input) {
  zeroPII(input);
  if(!input || !input.provider_settled || !input.attribution_reconciled || !input.qualified_human_sessions_verified) return {net_revenue_per_1000:null,reason:'NOT_COMPUTABLE'};
  const {sessions,gross,refunds,fees} = input;
  for(const k of [sessions,gross,refunds,fees]) if(typeof k!=='number' || !Number.isFinite(k) || k<0) throw Error('Invalid metric input');
  if(sessions===0 || refunds+fees>gross) return {net_revenue_per_1000:null,reason:'NOT_COMPUTABLE'};
  return {net_revenue_per_1000:Number((((gross-refunds-fees)/sessions)*1000).toFixed(2)),reason:'SETTLED_AND_ATTRIBUTED'};
}
module.exports={reconcile,confirmedSignup,revenueKpi};

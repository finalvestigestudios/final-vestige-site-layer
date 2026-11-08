'use strict';
// Pure functions; no network, no WordPress, no email, no persistent identifiers.
const ISSUE_TYPES = Object.freeze({ '01':'editorial','02':'editorial','03':'commercial','04':'editorial','05':'commercial','06':'editorial' });
const TOKEN = /^[a-z][a-z0-9_]{1,71}$/;
const EXACT = Object.freeze({source:'dispatch',medium:'email',campaign:'dispatch_pilot_2026_11'});
function campaignLink(issue, destination) {
  if (!Object.hasOwn(ISSUE_TYPES,issue)) throw Error('unknown issue');
  const u = new URL(destination);
  if (u.protocol!=='https:' || u.hostname!=='finalvestige.com' || u.username || u.password || u.hash) throw Error('unapproved destination');
  if (u.search || /\/(?:wp-admin|wp-login|subscribe)(?:\/|$)/i.test(u.pathname)) throw Error('unknown/subscribe destination');
  for (const [key,val] of Object.entries({utm_source:EXACT.source,utm_medium:EXACT.medium,utm_campaign:EXACT.campaign,utm_content:'issue_'+issue})) u.searchParams.set(key,val);
  return u.toString();
}
function classifyNewsletter(snapshot) {
  const {total,confirmed,unconfirmed,suppressed,paid}=snapshot;
  if (![total,confirmed,unconfirmed,suppressed,paid].every(x=>Number.isInteger(x)&&x>=0)) throw Error('invalid provider counters');
  return {nonadditive:true, dashboard:{total,confirmed,unconfirmed,suppressed,paid}, emailEligible:'UNKNOWN', knownConfirmedNotDeliveryProof:confirmed, reason:'Counts and follower totals do not establish per-recipient email eligibility; verify provider email subscription status privately.'};
}
function confirmedSignup({provider_confirmed, email_subscription_active, suppressed, pending, repeat, reader_only}) {
  // Caller/provider must deduplicate privately before any *aggregate* event is emitted.
  return provider_confirmed===true&&email_subscription_active===true&&suppressed===false&&pending===false&&repeat===false&&reader_only===false ? 1 : 0;
}
function evaluateRevenue({qualified_human_sessions,settled_paid_orders,verified_gross,verified_fees,verified_refunds,verified_chargebacks,partner_attribution_verified}) {
  const missing=(why)=>({status:'NOT_COMPUTABLE',reason:why,net_per_1000:null});
  if (!Number.isInteger(qualified_human_sessions)||qualified_human_sessions<=0) return missing('qualified-human denominator unavailable/zero');
  if (!Number.isInteger(settled_paid_orders)||settled_paid_orders<0 || partner_attribution_verified!==true) return missing('independently verified order and attribution evidence missing');
  if (![verified_gross,verified_fees,verified_refunds,verified_chargebacks].every(v=>typeof v==='number'&&Number.isFinite(v)&&v>=0)) return missing('unreconciled gross/fee/refund/chargeback evidence');
  if (settled_paid_orders===0&&verified_gross!==0) return missing('paid-order/gross contradiction');
  const net=verified_gross-verified_fees-verified_refunds-verified_chargebacks;
  return {status:'COMPUTABLE',net_revenue:Math.round(net*100)/100,net_per_1000:Math.round(100000*net/qualified_human_sessions)/100,qualified_human_sessions,settled_paid_orders};
}
function editionGate(issue,evidence={}) {
  if (!Object.hasOwn(ISSUE_TYPES,issue)) throw Error('unknown issue');
  const core=['founder_final_send_approval','provider_eligible_audience_verified','received_email_verified','publisher_postal_verified','unsubscribe_function_verified','consent_scope_verified'];
  const merchant=['named_partner_acceptance','email_channel_permission','issued_earning_url','published_vetted_guide','checkout_terms_verified'];
  const missing=core.filter(k=>evidence[k]!==true);
  if (ISSUE_TYPES[issue]==='commercial') missing.push(...merchant.filter(k=>evidence[k]!==true));
  return {issue,type:ISSUE_TYPES[issue],status:missing.length?'HOLD':'CANDIDATE_FOR_FINAL_HUMAN_REVIEW',not_authorization:true,missing};
}
module.exports={ISSUE_TYPES,campaignLink,classifyNewsletter,confirmedSignup,evaluateRevenue,editionGate};

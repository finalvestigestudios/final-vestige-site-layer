'use strict';
/* Final Vestige Dispatch: non-sending, aggregate-only evidence audit. NO network/writes. */
const FORBIDDEN = new Set(['email_address', 'raw_email', 'recipient_email', 'phone', 'ip', 'ip_address', 'full_name', 'first_name', 'last_name', 'contact', 'subscriber_address', 'recipient', 'cookie', 'user_agent', 'subscriber_id', 'user_id']);
const own = (o,k) => Object.prototype.hasOwnProperty.call(o,k);
function requireObject(v, label) {
  if (!v || typeof v !== 'object' || Array.isArray(v)) throw new TypeError(`${label} must be an object`);
  return v;
}
function rejectPII(value, path='root') {
  if (Array.isArray(value)) return value.forEach((item,i) => rejectPII(item,`${path}[${i}]`));
  if (value && typeof value === 'object') for (const [key,item] of Object.entries(value)) {
    if (FORBIDDEN.has(key.toLowerCase())) throw new Error(`personal-data field prohibited at ${path}.${key}`);
    rejectPII(item, `${path}.${key}`);
  }
}
function count(v, label) {
  if (!Number.isSafeInteger(v) || v < 0) throw new TypeError(`${label} must be non-negative integer`);
  return v;
}
function snapshotReport(snapshot) {
  requireObject(snapshot,'snapshot'); rejectPII(snapshot);
  const n=requireObject(snapshot.newsletter,'newsletter');
  const delivery=requireObject(snapshot.dispatch001,'dispatch001');
  const sub=requireObject(snapshot.stats_subscribers,'stats_subscribers');
  const followers=requireObject(snapshot.stats_followers,'stats_followers');
  const email=requireObject(snapshot.stats_emails,'stats_emails');
  for(const [key,v] of Object.entries({total:n.total,confirmed:n.confirmed,unconfirmed:n.unconfirmed,delivered:delivery.sent,bounces:delivery.bounced,stat_total:sub.total,stat_email:sub.email,stat_reader:sub.reader,follower_email:followers.email,follower_reader:followers.reader,email_sent:email.sent,opens:email.unique_opens,clicks:email.unique_clicks})) count(v,key);
  if(n.confirmed>n.total) throw new Error('confirmed exceeds total');
  if(delivery.status!=='delivered' || delivery.post_id!==2928) throw new Error('historical live Dispatch send not established');
  if(delivery.sent!==email.sent) throw new Error('delivery and Stats sent totals disagree');
  const conflict=sub.email!==followers.email || sub.reader!==followers.reader;
  return {
    delivery: {post_id:2928, provider_status:'delivered',sent:delivery.sent,bounced:delivery.bounced},
    engagement: {recorded_unique_opens:email.unique_opens,recorded_unique_clicks:email.unique_clicks,actual_readers:'UNVERIFIED',actual_email_link_clickers:email.unique_clicks===0?'NO_RECORDED_CLICKS':'PROVIDER_RECORDED_ONLY'},
    audience: {newsletter_total:n.total,newsletter_confirmed:n.confirmed,additional_unconfirmed:n.unconfirmed,stats_subscribers_email:sub.email,stats_subscribers_reader:sub.reader,stats_followers_email:followers.email,stats_followers_reader:followers.reader,classification_conflict:conflict,independent_new_confirmed_signups:null},
    fields_not_supported:['received_welcome','actual_pdf_download','human_visitor_attribution','verified_affiliate_sale','realized_net_revenue_per_1000']
  };
}
function confirmedSignupSummary(events, complete=false) {
  if (!Array.isArray(events) || typeof complete!=='boolean') throw new TypeError('events array and completeness flag required');
  rejectPII(events);
  const verified=new Set(), attributed=new Set();
  for (const ev of events) {
    requireObject(ev,'event');
    if (ev.kind==='form_start' || ev.kind==='signup_submit') continue;
    if (ev.kind!=='provider_transition') throw new Error('unrecognized event kind');
    if(ev.from!=='pending' || ev.to!=='confirmed' || ev.proof!=='provider_confirmation_receipt') continue;
    if (typeof ev.ephemeral_key!=='string'||!/^synthetic-or-transient-[A-Za-z0-9_-]{1,64}$/.test(ev.ephemeral_key)) throw new Error('ephemeral in-memory dedup key required');
    verified.add(ev.ephemeral_key);
    if(typeof ev.asset_id==='string' && /^[A-Za-z0-9_-]{4,80}$/.test(ev.asset_id) && ev.utm_source && ev.utm_campaign) attributed.add(ev.ephemeral_key);
  }
  return {confirmed_signup:complete?verified.size:null,confirmed_signup_source_attributed:complete?attributed.size:null,missing_observation:!complete,method:'single provider pending→confirmed transition per ephemeral key, never form submissions'};
}
function commercialRelease(attestations) {
  requireObject(attestations,'attestations'); rejectPII(attestations);
  const required=['founder_final_send_approval','received_native_jetpack_preview','publisher_postal_address_verified','rendered_unsubscribe_verified','verified_partner_acceptance','explicit_email_channel_permission','approved_earning_link_and_terms','live_vetted_guide','current_merchant_checkout_and_refunds'];
  const missing=required.filter(k=>attestations[k]!==true);
  return {eligible:false,reason:missing.length?'HOLD_MISSING_ATTESTATIONS':'HOLD_MANUAL_RELEASE_REQUIRED',missing};
}
function revenuePerThousand(input) {
  requireObject(input,'revenue'); rejectPII(input);
  if (input.sessions_verified!==true || input.ledger_complete!==true || !Number.isSafeInteger(input.qualified_human_sessions) || input.qualified_human_sessions<=0 || !Array.isArray(input.settlements)) return {value:null,reason:'NOT_COMPUTABLE_INCOMPLETE_ATTRIBUTION_OR_SETTLEMENT'};
  let net=0;const seen=new Set();
  for(const t of input.settlements){requireObject(t,'settlement');
    if(t.independently_verified!==true || t.status!=='settled' || typeof t.order_key!=='string' || !/^aggregate-[A-Za-z0-9_-]{3,80}$/.test(t.order_key)) return {value:null,reason:'NOT_COMPUTABLE_UNVERIFIED_ORDER'};
    if (seen.has(t.order_key)) continue; seen.add(t.order_key);
    for(const k of ['gross','refunds','fees']) if(!Number.isFinite(t[k]) || t[k]<0) return {value:null,reason:'NOT_COMPUTABLE_INVALID_MONEY'};
    net += t.gross - t.refunds - t.fees;
  }
  return {value:Number((1000*net/input.qualified_human_sessions).toFixed(2)),net:Number(net.toFixed(2)),orders:seen.size,reason:'VERIFIED_COMPLETE_COHORT_ONLY'};
}
module.exports={snapshotReport,confirmedSignupSummary,commercialRelease,revenuePerThousand,rejectPII};

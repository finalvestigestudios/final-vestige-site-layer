"use strict";
/* R433: pure offline evaluator, never sends/visits/changes anything.
 * No raw email, IP, phone, URI tokens or subscriber identities are accepted.
 * Real integration must be implemented by Claude with consent and privacy review.
 */
const ALLOWED_TYPES = new Set(["qualified_visit","signup_attempt","provider_confirmed_subscribed","welcome_receipt","editorial_cta_click","merchant_outbound","settled_order","refund","fee"]);
const PII = /(email|e_mail|phone|ip_address|user_agent|full_name|address|subscriber_name|cookie|auth|token|raw_url)/i;
const FINITE = n => typeof n==="number"&&Number.isFinite(n)&&n>=0;
const REF = s => typeof s==="string" && /^[a-z0-9][a-z0-9._-]{2,80}$/i.test(s);
const DAY = 86400000;
function noPII(input) {
  function visit(v){
    if(!v || typeof v!=="object")return;
    for(const [k,x] of Object.entries(v)){
      if(PII.test(k))throw Error("PII_FIELD_FORBIDDEN:"+k);
      if(typeof x==="string" && /@/.test(x))throw Error("PII_VALUE_FORBIDDEN");
      visit(x);
    }
  } visit(input);
}
function inspect(witness,events=[],opts={}) {
  noPII({witness,events,opts});
  if(!witness || !Array.isArray(events)) throw Error("INVALID_ARGUMENTS");
  const j=witness.jetpack||{},s=witness.subscribers||{},c=witness.compliance||{};
  const blocked=[];
  if(j.subscriptions!==true)blocked.push("NEWSLETTER_DISABLED");
  if(j.email_new_posts_by_default!==false)blocked.push("AUTO_SEND_DEFAULT_DRIFT");
  if(j.newsletter_categories_enabled!==false)blocked.push("CATEGORY_TARGETING_DRIFT");
  if(s.provider_email_subscription_subscribed_aggregate===null||s.distinct_eligible_inboxes===null)blocked.push("RECIPIENT_ELIGIBILITY_UNKNOWN");
  for(const [key,code] of [["received_unsubscribe_verified","UNSUBSCRIBE_UNWITNESSED"],["sender_postal_verified","PUBLISHER_POSTAL_UNWITNESSED"],["actual_jetpack_email_preview_verified","NATIVE_PREVIEW_UNWITNESSED"]]){
    if(c[key]!==true)blocked.push(code);
  }
  if(c.affiliate_email_permission_verified!==true)blocked.push("MERCHANT_EMAIL_RIGHTS_UNVERIFIED");
  const ids=new Set(),confirmed=new Set(),attempts=new Set(),visits=new Map(),orders=new Map(),refunds=new Map(),fees=new Map();
  for(const e of events) {
    if(!e||!ALLOWED_TYPES.has(e.type)||!REF(e.event_id))throw Error("EVENT_SCHEMA");
    if(ids.has(e.event_id)) continue; ids.add(e.event_id);
    if(!Number.isFinite(Date.parse(e.at)))throw Error("EVENT_DATE");
    if(e.type==="signup_attempt"){if(!REF(e.subscription_key))throw Error("OPAQUE_SUBSCRIPTION_KEY");attempts.add(e.subscription_key);}
    else if(e.type==="provider_confirmed_subscribed"){
      if(!REF(e.subscription_key)||e.provider_evidence!==true)throw Error("CONFIRMED_NEEDS_PROVIDER_PROOF");
      confirmed.add(e.subscription_key);
    } else if(e.type==="qualified_visit"){
      if(!REF(e.session_id)||e.human_verified!==true||!REF(e.asset_id)||!REF(e.utm_campaign))throw Error("SESSION_REQUIRES_VERIFIED_HUMAN_AND_SOURCE");
      if(visits.has(e.session_id))throw Error("DUPLICATE_SESSION_ID");
      visits.set(e.session_id,e);
    } else if(e.type==="settled_order"){
      if(!REF(e.order_id)||e.merchant_evidence!==true||e.payment_state!=="settled"||!FINITE(e.gross_usd)||!REF(e.session_id))throw Error("UNVERIFIED_SETTLEMENT");
      if(orders.has(e.order_id))throw Error("DUPLICATE_ORDER");
      orders.set(e.order_id,e);
    } else if(e.type==="refund"||e.type==="fee"){
      if(!REF(e.order_id)||!FINITE(e.amount_usd)||e.provider_evidence!==true)throw Error("UNVERIFIED_DEDUCTION");
      const bucket=e.type==="refund"?refunds:fees; bucket.set(e.order_id,(bucket.get(e.order_id)||0)+e.amount_usd);
    } else if(e.type==="welcome_receipt"){
      if(!REF(e.subscription_key)||e.receipt_evidence!==true)throw Error("WELCOME_NOT_PROVEN");
    } else if(e.type==="editorial_cta_click"||e.type==="merchant_outbound"){
      if(!REF(e.session_id))throw Error("CTA_MISSING_SOURCE_SESSION");
    }
  }
  const sessions=[...visits.values()];
  const asOf=Date.parse(opts.as_of||"2026-11-17T22:40:00Z");
  if(!Number.isFinite(asOf))throw Error("AS_OF_DATE");
  const cohorts={};
  for(const duration of [7,30]){
    const mature=sessions.filter(s=>asOf-Date.parse(s.at)>=duration*DAY && Date.parse(s.at)<=asOf);
    const eligibleOrders=[...orders.values()].filter(o=>{
      const v=visits.get(o.session_id); if(!v) return false;
      const gap=Date.parse(o.at)-Date.parse(v.at);
      return gap>=0&&gap<=duration*DAY&&asOf-Date.parse(v.at)>=duration*DAY;
    });
    const net=eligibleOrders.reduce((sum,o)=>sum+o.gross_usd-(refunds.get(o.order_id)||0)-(fees.get(o.order_id)||0),0);
    const denomVerified=opts.qualified_human_reporting_complete===true;
    const settlementsComplete=opts.merchant_reporting_complete===true && opts.refund_reporting_complete===true && opts.fee_reporting_complete===true;
    cohorts[duration+"d"]={status:denomVerified&&settlementsComplete&&mature.length>0?"EVIDENCE_READY_SYNTHETIC_ONLY":"NOT_COMPUTABLE",
      mature_sessions:mature.length,confirmed_orders:eligibleOrders.length,
      net_revenue_usd:denomVerified&&settlementsComplete&&mature.length>0?Math.round(net*100)/100:null,
      net_per_1000:denomVerified&&settlementsComplete&&mature.length>0?Math.round((net/mature.length*1000)*100)/100:null};
  }
  return {status:"HOLD_UNSENT",sendAuthorized:false,mailActionAllowed:false,newsletterCategoriesEnabled:j.newsletter_categories_enabled===true,
    observed:{dashboard_total:s.dashboard_total??null,confirmed:s.confirmed??null,unconfirmed:s.unconfirmed??null,eligible_inboxes:s.distinct_eligible_inboxes??null},
    unique_attempts:attempts.size,unique_confirmed_signups:confirmed.size,qualified_sessions:visits.size,order_record_count:orders.size,
    blocked:[...new Set(blocked)],cohorts};
}
module.exports={inspect};

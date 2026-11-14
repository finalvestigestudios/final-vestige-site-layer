"use strict";
/** R349: offline, non-sending, no-network evidence validators. Never returns SEND. */
function inspectOffer(o) {
  const required=["named_account_acceptance","email_channel_permission","issued_earning_url","approved_live_first_party_guide","exact_checkout_terms","refund_terms_review","claim_review"];
  const missing=required.filter(k=>o.proofs?.[k]?.status!=="verified"||!o.proofs[k].reference);
  const prices=(o.public_observations||[]).filter(x=>x.type==="promotional_display"&&typeof x.amount==="number").map(x=>x.amount);
  const unique=[...new Set(prices)];
  const publicPriceConflict=unique.length>1;
  const prohibited=(o.public_observations||[]).some(x=>x.verified_checkout===true);
  return {offer:o.id||"unknown",status:"HOLD_MERCHANT",missing_proofs:missing,public_price_conflict:publicPriceConflict,observed_promotional_prices:unique,do_not_quote_price:true,do_not_activate_link:true, invalid_public_proof:prohibited, note:"Public seller pages and coupon variants are not authenticated affiliate approval or checkout."};
}
function inspectNewsletter(n) {
  const reasons=[];
  if(n.subscription_enabled!==true)reasons.push("NEWSLETTER_DISABLED");
  if(n.auto_post_enabled!==false)reasons.push("AUTO_POST_FLAG_NOT_OFF");
  if(n.provider_eligible_recipients_verified!==true)reasons.push("ELIGIBLE_RECIPIENTS_UNKNOWN");
  if(n.welcome_actual_inbox_verified!==true)reasons.push("WELCOME_RECEIPT_NOT_VERIFIED");
  if(n.native_inbox_preview_verified!==true)reasons.push("NATIVE_RECEIVED_RENDER_NOT_VERIFIED");
  if(n.publisher_postal_address_verified!==true)reasons.push("PUBLISHER_ADDRESS_NOT_VERIFIED");
  if(n.functional_unsubscribe_verified!==true)reasons.push("UNSUBSCRIBE_NOT_VERIFIED");
  if(n.founder_final_campaign_approval!==true)reasons.push("FOUNDER_FINAL_APPROVAL_MISSING");
  const c=n.subscriber_counts||{},f=n.follower_counts||{};
  const countsNonadditive=Number.isInteger(c.total)&&Number.isInteger(c.confirmed)&&Number.isInteger(c.unconfirmed)&&c.confirmed+c.unconfirmed>c.total;
  return {status:"HOLD_UNSENT",reasons,counts_are_nonadditive:countsNonadditive,provider_subscribers:c,followers_reported_separately:f,actual_eligible_inbox_count:null,note:"A provider count or PDF download never proves an individual confirmed email recipient. This tool cannot authorize sending."};
}
function inspectCohort(c){
  if(!c||c.provider_verified!==true||!Number.isSafeInteger(c.qualified_human_sessions)||c.qualified_human_sessions<1||c.orders_complete_verified!==true||!Array.isArray(c.orders))return {status:"NOT_COMPUTABLE",net_per_1000:null,reason:"Missing audited denominator or complete, independent merchant/owned-order settlement."};
  const seen=new Set();let net=0;
  for(const o of c.orders){
    if(!o||typeof o.id!=="string"||seen.has(o.id)||o.settled!==true||o.refunds_final!==true||o.fees_final!==true||o.currency!=="USD"||!["owned","affiliate"].includes(o.type)||![o.gross,o.refunds,o.fees].every(x=>typeof x==="number"&&Number.isFinite(x)&&x>=0))return {status:"NOT_COMPUTABLE",net_per_1000:null,reason:"Unverified, duplicate, incomplete, or malformed order settlement evidence."};
    seen.add(o.id);net+=o.gross-o.refunds-o.fees;
  }
  return {status:"VERIFIED_LEDGER_ONLY",net_usd:Number(net.toFixed(2)),net_per_1000:Number((net*1000/c.qualified_human_sessions).toFixed(2)),verified_orders:seen.size,tiny_sample:c.qualified_human_sessions<1000,reason:"These calculations only validate evidence that the input provider/merchant has independently authenticated; not sales verified by the tool itself."};
}
module.exports={inspectOffer,inspectNewsletter,inspectCohort};

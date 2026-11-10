"use strict";
/* Read-only, pure validator. No network, no analytics, no email send or subscriber operations. */
function review(snapshot) {
  const issues=[];
  const d=snapshot.dispatch||{}, f=snapshot.focus||{}, n=snapshot.newsletter||{}, a=snapshot.affiliate||{}, c=snapshot.campaign||{};
  const diag=n.subscriber_diagnostics||{}, followers=n.separate_followers||{};
  if(d.published!==true || f.published!==true) issues.push("SOURCE_NOT_PUBLISHED");
  if(!/investigations.*archive finds/i.test(d.promise||"")) issues.push("DISPATCH_PROMISE_MISMATCH");
  if(!/commission/i.test(f.promise||"")) issues.push("FOCUS_DISCLOSURE_MISSING");
  if(d.commercial_earning_disclosure_present!==true) issues.push("DISPATCH_PROMO_NOTICE_GAP");
  if(!/unsubscribe/i.test(d.optout||"") || !/unsubscribe/i.test(f.promise||"")) issues.push("OPT_OUT_PROMISE_GAP");
  if(/commission|offer|tool/i.test(n.welcome_promise||"")===false) issues.push("WELCOME_EXPECTATION_GAP");
  if(n.actual_email_eligible_count===null || n.actual_email_eligible_count===undefined) issues.push("EMAIL_ELIGIBILITY_UNVERIFIED");
  if(Number.isInteger(diag.total)&&Number.isInteger(diag.confirmed)&&Number.isInteger(diag.unconfirmed) && diag.total<diag.confirmed+diag.unconfirmed) issues.push("COUNTERS_NONADDITIVE");
  if(followers.email===0 && followers.wpcom>0 && diag.confirmed>0) issues.push("FOLLOWER_SCOPE_DISAGREEMENT");
  if(n.new_post_automatic_email!==false) issues.push("AUTO_SEND_NOT_DISABLED");
  if(!n.welcome_actual_receipt_verified) issues.push("WELCOME_RECEIPT_UNVERIFIED");
  if(!n.actual_business_postal_verified) issues.push("PUBLISHER_ADDRESS_UNVERIFIED");
  if(!n.delivered_unsubscribe_verified) issues.push("DELIVERED_UNSUBSCRIBE_UNVERIFIED");
  if(!a.named_final_vestige_acceptance || !a.email_promotion_rights || !a.issued_earning_url) issues.push("MERCHANT_EMAIL_RIGHTS_UNVERIFIED");
  if(!a.approved_guide_for_zen12 || !a.approved_guide_for_hypnosis_live || !a.live_affiliate_cart_and_refund_checked) issues.push("OFFER_GUIDE_AND_CART_UNVERIFIED");
  if(!c.all_six_held || c.founder_final_send_approval!==false) issues.push("FOUNDERSHIP_HOLD_NOT_RECORDED");
  if(c.editorial_count!==4 || JSON.stringify(c.commercial_slots)!=="[3,5]") issues.push("CAMPAIGN_ALLOCATION_DRIFT");
  return Object.freeze({
    status:"HOLD_UNSENT", commercial_slots:Object.freeze({3:"HOLD_MERCHANT",5:"HOLD_MERCHANT"}),
    email_eligible_recipients:null, confirmed_paid_sales:null, net_revenue_per_1000:null,
    observations:Object.freeze([...new Set(issues)]),
    legal_conclusion:"UNDETERMINED — copy mismatch alone does not establish illegal consent",
    can_send:false, can_import_subscribers:false, can_activate_affiliate:false
  });
}
function qualifiedConversion({humanSessions,realizedNetRevenue,settlementAuthenticated}={}) {
  if(!settlementAuthenticated || !Number.isFinite(humanSessions) || humanSessions<=0 ||
     !Number.isFinite(realizedNetRevenue))return {status:"NOT_COMPUTABLE",value:null};
  return {status:"CALCULABLE_WITH_VERIFIED_INPUTS",value:1000*realizedNetRevenue/humanSessions};
}
module.exports={review,qualifiedConversion};

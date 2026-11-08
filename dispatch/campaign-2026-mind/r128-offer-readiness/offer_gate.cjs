"use strict";
const assert=(x,msg)=>{if(!x)throw Error(msg)};
function audit(x){
 assert(x&&typeof x==="object","document");
 assert(x.schema==="FV_DISPATCH_R128_INERT","schema");
 assert(x.status==="HOLD_ALL_UNSENT","status");
 assert(JSON.stringify(x.allocation?.editorial)==="[1,2,4,6]","editorial allocation");
 assert(JSON.stringify(x.allocation?.commercial)==="[3,5]","commercial allocation");
 assert(Array.isArray(x.offers)&&x.offers.length===2,"offer count");
 assert(x.offers[0].issue===3&&x.offers[1].issue===5,"slot order");
 assert(x.wordpress.auto_new_post_emails===false&&x.wordpress.email_content_format==="excerpt","WordPress settings");
 assert(x.wordpress.actual_email_eligibility_verified===false,"unverified subscriber reachability");
 assert(x.wordpress.welcome_received_verified===false,"unverified welcome");
 assert(x.wordpress.actual_preview_received_verified===false,"unverified received preview");
 assert(x.legal.publisher_address_verified===false&&x.legal.rendered_opt_out_verified===false&&x.legal.founder_approval===false,"legal/approval proof");
 assert(x.actual_paid_orders===null&&x.net_revenue_per_1000_qualified_sessions===null,"unverified orders/revenue");
 assert(!/subscriber_email|recipient_email|customer_address|phone_number/i.test(JSON.stringify(x)),"PII prohibited");
 for(const o of x.offers){
   assert(o.guide_url===null&&o.merchant_affiliate_url===null,"active commercial link");
   for(const f of ["guide_live_verified","named_partner_approved","email_marketing_allowed","approved_creative_verified","tracking_format_verified","refund_at_checkout_verified","independent_product_efficacy_verified","merchant_paid_sale_verified"]) assert(o[f]===false,"unsupported evidence: "+f);
   assert(o.price_classification==="merchant_display_only_checkout_unverified","price claim");
   assert(/^https:\/\//.test(o.source)&&/^https:\/\//.test(o.research),"primary source");
   assert(o.one_guide_cta.includes("INERT UNPUBLISHED"),"CTA activated");
   assert(o.near_offer_disclosure.includes("may earn a commission"),"near-offer disclosure");
   assert(Array.isArray(o.unsupported_claims)&&o.unsupported_claims.length>=2,"claims audit");
 }
 return {state:"HOLD_ALL_UNSENT",commercial:"HOLD_MERCHANT",offer_count:2,publish_approved:false,send_approved:false};
}
function evidenceRequired(proofs={}){
 const keys=["native_email_reachability","actual_received_welcome","actual_jetpack_email_render","physical_postal_address","operational_unsubscribe","named_partner_email_permission","approved_live_guide","merchant_settled_order_reporting","founder_final_send_approval"];
 return {missing:keys.filter(k=>proofs[k]!==true),send_approved:false};
}
module.exports={audit,evidenceRequired};

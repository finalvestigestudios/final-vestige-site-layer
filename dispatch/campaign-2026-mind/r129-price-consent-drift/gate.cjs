"use strict";
function evaluate(x){
 const errs=[];
 if(!x||x.schema!=="FV_DISPATCH_R129_INERT")return {release:"HOLD_ALL_UNSENT",errors:["INVALID_EVIDENCE_PACKET"]};
 const p=x.merchant||[],h=p.find(a=>a.product==="Total Focus"),z=p.find(a=>a.product==="Zen12 Premium"),w=x.wordpress||{};
 if(!h||!z)errs.push("SPECIFIC_MERCHANT_MISSING");
 if(h&&h.latest_seller_display!==h.prior_seller_display)errs.push("DISPLAY_PRICE_DISCREPANCY_NOT_CHECKOUT_PROOF");
 for(const product of p){if(product.checkout_verified!==true)errs.push("CHECKOUT_UNVERIFIED_"+product.product);if(product.refund_at_checkout_verified!==true)errs.push("REFUND_TERMS_UNVERIFIED_"+product.product);if(product.product_specific_effectiveness_verified!==true)errs.push("PRODUCT_OUTCOME_UNVERIFIED_"+product.product);}
 if(z&&!String(z.merchant_opt_in_warning||"").includes("seller list"))errs.push("MERCHANT_NEWSLETTER_OPTIN_BOUNDARY_MISSING");
 if(x.merchant_permissions_verified!==true||x.email_promotion_permission_verified!==true)errs.push("AFFILIATE_EMAIL_RIGHTS_UNVERIFIED");
 if(x.first_party_guide_live!==true||x.live_affiliate_url!==null)errs.push("FIRST_PARTY_GUIDE_LINK_HOLD");
 if(x.release_all_approved!==false||x.founder_send_approval!==false)errs.push("UNAUTHORIZED_RELEASE_ATTEMPT");
 if(w.post_auto_email!==false)errs.push("POST_AUTO_EMAIL_NOT_DISABLED");
 if(w.individually_reachable_count_verified==null)errs.push("EMAIL_ELIGIBILITY_UNVERIFIED");
 if(w.welcome_inbox_verified!==true)errs.push("WELCOME_RECEIPT_UNVERIFIED");
 if(w.physical_postal_verified!==true||w.real_unsubscribe_verified!==true)errs.push("COMMERCIAL_EMAIL_FOOTER_UNVERIFIED");
 if(x.actual_paid_orders==null||x.net_revenue_per_1000_qualified_human_sessions==null||x.qualified_human_sessions==null)errs.push("REALIZED_PAID_REVENUE_UNOBSERVABLE");
 if(/@[A-Za-z0-9]/.test(JSON.stringify(x)))errs.push("PERSONAL_EMAIL_POSSIBLE");
 if(!x.campaign_mix||x.campaign_mix.editorial.join(",")!=="1,2,4,6"||x.campaign_mix.commercial_reserved.join(",")!=="3,5")errs.push("CAMPAIGN_MIX_CHANGED");
 return {release:"HOLD_ALL_UNSENT",review:errs.length?"HOLD_MISSING_EVIDENCE":"HUMAN_REVIEW_ONLY",has_public_price_variance:!!(h&&h.latest_seller_display!==h.prior_seller_display),errors:errs};
}
module.exports={evaluate};

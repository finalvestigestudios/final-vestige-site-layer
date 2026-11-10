"use strict";
const HOLD="HOLD_UNSENT";
function evaluate(packet, html, plain) {
 const errs=[]; const fail=(x)=>errs.push(x);
 if(!packet||typeof packet!=="object"||Array.isArray(packet)) throw Error("PACKET_REQUIRED");
 if(packet.origin?.canonical_sha!=="d57ccdba3aee8f065e143e101c2945f4f3d01647") fail("CANONICAL_DRIFT");
 if(packet.editorial_mix?.editorial!==4||packet.editorial_mix?.commercial_review_pending!==2) fail("MIX_CHANGED");
 if(packet.status!==HOLD) fail("RELEASE_STATUS_DRIFT");
 if(packet.subscriber?.auto_new_post_email!==false) fail("AUTO_SEND_NOT_OFF");
 if(packet.subscriber?.email_eligible!==null) fail("ELIGIBLE_RECIPIENTS_UNSUPPORTED");
 if(packet.revenue?.verified_paid_orders!==null||packet.revenue?.verified_net_revenue_usd!==null) fail("REVENUE_UNVERIFIED");
 if(packet.merchant?.pricing_live_checkout_verified!==false||packet.merchant?.product_specific_efficacy_verified!==false) fail("CLAIM_OR_PRICE_OVERRIDDEN");
 const gates=Object.values(packet.gates||{});
 if(!gates.length||gates.some(x=>x!==false&&x!==null)) fail("RELEASE_GATE_FALSELY_CLEARED");
 if(!html.includes("UNSENT REVIEW ONLY")||!plain.includes("UNSENT REVIEW COPY")) fail("REVIEW_LABEL_MISSING");
 for(const s of ["[[VALID_POSTAL_ADDRESS_REQUIRED]]","[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]","[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]"]){
  if(!html.includes(s)||!plain.includes(s)) fail("MANDATORY_INERT_TOKEN_MISSING:"+s);
 }
 for(const s of ["Commercial disclosure","may receive a commission","not been independently demonstrated"]){
   if(!html.toLowerCase().includes(s.toLowerCase())) fail("COPY_INTEGRITY:"+s);
 }
 if(/<\s*(script|form|iframe|img|video)\b/i.test(html)) fail("UNSAFE_EMAIL_MARKUP");
 if(/\b(href|src)\s*=\s*["'][^"']*(hypnosislive\.com|zen12\.com|affiliates\.inspire3\.com)/i.test(html)) fail("MERCHANT_LINK_ACTIVE");
 if(/<a\b[^>]*>\s*(?:buy|shop|order|claim|read the guide)\b/i.test(html)) fail("PRIMARY_CTA_MUST_BE_INERT");
 if(!/lang="en"/i.test(html)||!/role="presentation"/i.test(html)||!/<h1\b/i.test(html)) fail("ACCESSIBILITY_SCAFFOLD");
 if(/100% razor-sharp|reprogram your brain|guaranteed (?:focus|concentration|results)|you will (?:focus|concentrate)/i.test(html)) fail("UNSUPPORTED_PROMISE");
 if(/\$24\.44|\$29\.95|\$22\.95|\$39\.90/.test(html)) fail("VOLATILE_PRICE_IN_EMAIL");
 if(/(?:https?:\/\/)?(?:hypnosislive\.com|zen12\.com)\//.test(html.replace(/<[^>]*>/g,"").toLowerCase())===false) fail("SELLER_SOURCE_MISSING");
 // Document review has no authority to unlock distribution, even if all tests pass.
 return Object.freeze({status:HOLD,commercial_issues:[3,5],errors:errs,
  email_eligible:null,paid_orders:null,net_revenue_usd:null,
  net_revenue_per_1000_human_sessions:null,real_jetpack_preview:false});
}
module.exports={evaluate};

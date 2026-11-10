"use strict";
/* R246 documentary decision aid. Inputs are NOT authenticated by this module.
   A passing record cannot authorize an email, affiliate promotion or paid-revenue claim. */
const SAFE_STATES = Object.freeze(["unverified","pending","verified"]);
function evaluateEvidence(packet) {
  if (!packet || typeof packet !== "object" || Array.isArray(packet)) throw Error("PACKET_OBJECT_REQUIRED");
  const fail = new Set();
  const add = code => fail.add(code);
  const docs = packet.documents || {};
  function proof(name, requiredIssuer) {
    const p=docs[name];
    if (!p || p.state!=="verified" || typeof p.ref!=="string" || p.ref.length<8 ||
      typeof p.observed_utc!=="string" || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(p.observed_utc) ||
      !Number.isFinite(Date.parse(p.observed_utc)) ||
      !SAFE_STATES.includes(p.state) || p.issuer!==requiredIssuer) add("EVIDENCE_MISSING_OR_UNVERIFIED:"+name);
  }
  if(packet.pilot_mix?.editorial!==4 || packet.pilot_mix?.commercial!==2)
    add("PILOT_4_2_CHANGED");
  if(packet.original_campaign_ref!=="d57ccdba3aee8f065e143e101c2945f4f3d01647")
    add("ORIGINAL_SOURCE_IDENTITY_NOT_LOCKED");
  if(packet.current_state?.all_sends_hold!==true) add("SEND_HOLD_NOT_ASSERTED");
  if(packet.current_state?.wp_new_post_auto_send_off!==true) add("POST_AUTO_SEND_NOT_CONFIRMED_OFF");
  const scopes=[
    ["partner_named_acceptance","merchant_account"],
    ["partner_email_channel_permission","merchant_account"],
    ["issued_earning_link","merchant_account"],
    ["specific_seller_checkout_price","merchant_checkout"],
    ["specific_seller_refund_terms","merchant_checkout"],
    ["approved_live_warmup_guide","site_owner"],
    ["provider_eligible_status_aggregate","wp_subscriber_status"],
    ["welcome_received_independently","received_inbox"],
    ["publisher_postal_address","publisher"],
    ["real_jetpack_preview","wp_native_preview"],
    ["unsubscribe_in_received_email","received_inbox"],
    ["founder_campaign_release","founder"]
  ];
  for(const [k,issuer] of scopes) proof(k,issuer);
  const offers=packet.seller_pages || [];
  const z=offers.filter(p=>p.product==="Zen12");
  if(z.length<2 || !z.every(p=>typeof p.page_url==="string" && /^https:\/\/zen12\.com\//.test(p.page_url) &&
    typeof p.price_usd==="number" && Number.isFinite(p.price_usd) && p.price_usd>0))
    add("SELLER_PAGE_DIFFERENCE_NOT_DOCUMENTED");
  if(z.length>=2 && new Set(z.map(p=>p.price_usd)).size>1)
    add("ZEN12_PAGE_PRICE_VARIANCE_REQUIRES_EXACT_CHECKOUT_MATCH");
  if(packet.authorized_earning_destination_verified!==true) add("EARNING_DESTINATION_UNKNOWN");
  if(packet.consent?.confirmed_signup_provider_transition_verified!==true) add("CONFIRMED_SIGNUP_NOT_PROVIDER_VERIFIED");
  if(packet.revenue?.independent_settled_orders_verified!==true) add("PAID_REVENUE_NOT_VERIFIED");
  // Deliberately cannot make a release decision from submitted attestation booleans.
  add("NON_SENDING_DOC_REVIEW_ONLY");
  return Object.freeze({
    status:"HOLD_UNSENT", merchant_issues:[3,5],
    blockers:[...fail].sort(), verified_paid_orders:null,
    verified_net_revenue_usd:null, realized_net_revenue_per_1000_human_sessions:null,
    note:"Data and references require independent authentication; this function cannot release a campaign."
  });
}
module.exports={evaluateEvidence};

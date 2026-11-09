'use strict';
// R225 is a research-only, fail-closed review aid. NOT a sender or checkout integration.
const ALLOWED_OFFERS = Object.freeze({
  zen12: 'https://zen12.com/hnp',
  total_focus: 'https://hypnosislive.com/mental-skills/total-focus'
});
const GATES = Object.freeze([
  'named_fv_partner_acceptance', 'explicit_jetpack_email_marketing_permission',
  'account_issued_earning_link', 'offer_specific_deep_link_permission',
  'approved_creative_and_claim_rules', 'approved_live_independent_guide',
  'price_and_currency_at_checkout', 'current_refund_terms_at_checkout',
  'real_received_jetpack_html_and_plaintext', 'publisher_postal_address_in_real_email',
  'working_unsubscribe_in_real_email', 'provider_confirmed_recipient_eligibility',
  'founder_creative_audience_date_and_send_authorization'
]);
const SAFE_RECEIPTS = /^[a-z0-9][a-z0-9._:-]{5,119}$/i;
function validateRegistry(data) {
  const errors=[];
  if (!data || typeof data !== 'object' || Array.isArray(data)) return ['registry_object_required'];
  if (data.status !== 'HOLD_UNSENT') errors.push('status_must_be_hold_unsent');
  if (data.editorial_count !== 4 || data.commercial_count !== 2) errors.push('four_to_two_campaign_required');
  if (!Array.isArray(data.offers) || data.offers.length !== 2) return [...errors,'exactly_two_offers_required'];
  const seen=new Set();
  for (const offer of data.offers) {
    if (!offer || !Object.hasOwn(ALLOWED_OFFERS,offer.id) || seen.has(offer.id)) {errors.push('unknown_or_duplicate_offer');continue;}
    seen.add(offer.id);
    if (offer.official_sales_page !== ALLOWED_OFFERS[offer.id]) errors.push(offer.id+':sales_page_not_exact');
    if (offer.partner_acceptance_verified !== false || offer.email_permission_verified !== false ||
        offer.checkout_verified !== false || offer.live_guide_verified !== false ||
        offer.issued_earning_url !== null || offer.affiliate_clicks !== null ||
        offer.confirmed_sales !== null || offer.realized_net_revenue !== null)
      errors.push(offer.id+':unproven_commerce_or_metrics');
    if (!Array.isArray(offer.seller_assertions) || !offer.seller_assertions.length ||
        !offer.seller_assertions.every(c=>c.provenance==='merchant_claim_not_independently_verified'))
      errors.push(offer.id+':seller_claims_need_label');
    if (!Array.isArray(offer.sources) || !offer.sources.every(u=>typeof u==='string' && /^https:\/\//.test(u)))
      errors.push(offer.id+':source_links_required');
    if (offer.id==='zen12' && offer.merchant_free_audio_optin !== 'MERCHANT_NEWSLETTER_NOT_FV_LEAD')
      errors.push('zen12:merchant_signup_must_be_separate');
  }
  for(const g of GATES) {
    const e=data.release_proofs?.[g];
    if(!e || e.verified !== false || e.reference !== null) errors.push('release_proof_invalid:'+g);
  }
  if(Object.keys(data.release_proofs||{}).length!==GATES.length) errors.push('release_proof_exact_set_required');
  return errors;
}
function summarize(data){
  const errors=validateRegistry(data);
  return Object.freeze({
    status:'HOLD_UNSENT',
    commercial_status:'HOLD_MERCHANT',
    safe_to_send:false,
    candidate_sale_attribution:'NOT_COMPUTABLE',
    failures:errors,
    missing_proofs:[...GATES]
  });
}
function validateExternalAttestation(item){
  // Structural hygiene ONLY: even a plausible reference is NOT authenticated by this function.
  if(!item||typeof item!=='object'||!GATES.includes(item.gate)||item.verified!==true||
      typeof item.reference!=='string'||!SAFE_RECEIPTS.test(item.reference)||
      /@|https?:|\?|\/|=/.test(item.reference)) return false;
  return true;
}
module.exports={ALLOWED_OFFERS,GATES,validateRegistry,summarize,validateExternalAttestation};

// R396 SOURCE-ONLY campaign/product identity gate. NO SEND PATH.
export const SEND_ENABLED = false;
export const PILOT = Object.freeze({
  3: Object.freeze({family:'Zen12', token:'[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]'}),
  5: Object.freeze({family:'Hypnosis Live', token:'[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]'})
});
export const PROOF_KEYS = Object.freeze([
  'founder_scope_approval','named_partner_acceptance','email_channel_permission',
  'exact_sku_permission','issued_earning_link','published_mind_owned_guide',
  'current_offer_terms','claim_substantiation_review','adjacent_commission_disclosure',
  'filtered_eligible_recipients','welcome_receipt','native_jetpack_preview',
  'publisher_postal_footer','functional_unsubscribe','final_campaign_approval'
]);
function isProof(x) {return Boolean(x && x.verified === true && typeof x.evidence_ref === 'string' && x.evidence_ref.trim().length >= 8 && x.source_type !== 'seller_catalog');}
export function checkOfferScope(manifest, issueNo, selection = {}, proofs = {}) {
  const errors=[];
  const ids=(manifest?.issues||[]).map(x=>x.number);
  const kinds=(manifest?.issues||[]).map(x=>x.kind);
  if (JSON.stringify(ids)!=='[1,2,3,4,5,6]' || kinds.filter(k=>k==='editorial').length!==4 || kinds.filter(k=>k==='commercial-review-pending').length!==2) errors.push('CANONICAL_SIX_ISSUE_4_TO_2_MIX_CHANGED');
  if (JSON.stringify((manifest?.issues||[]).filter(x=>x.kind==='commercial-review-pending').map(x=>x.number)) !== '[3,5]') errors.push('COMMERCIAL_SLOT_REASSIGNED');
  const canonical=PILOT[issueNo];
  if (!canonical) errors.push('NOT_A_COMMERCIAL_SLOT');
  const original=(manifest?.issues||[]).find(x=>x.number===issueNo);
  if (canonical && (original?.editorial_cta!==canonical.token || original?.merchant_affiliate_url!==null || original?.publish_state!=='hold')) errors.push('CANONICAL_UNSENT_DESTINATION_CHANGED');
  if (canonical && selection.family!==canonical.family) errors.push('WRONG_MERCHANT_PRODUCT_FAMILY');
  if (!selection.sku || typeof selection.sku!=='string') errors.push('EXACT_SKU_UNIDENTIFIED');
  if (issueNo===5 && selection.sku && selection.sku!=='Hypnosis Live catalog') {
    if(selection.scope!=='specific_child_sku') errors.push('CHILD_SKU_IS_NOT_EQUIVALENT_TO_CATALOG');
    if(!isProof(proofs.founder_scope_approval)) errors.push('CHILD_SKU_REQUIRES_FOUNDER_APPROVAL');
  }
  if (selection.active_merchant_link || selection.active_guide_link) errors.push('LIVE_LINKS_NOT_AUTHORIZED_IN_SOURCE_DRAFT');
  if (selection.price_to_publish!==undefined || selection.refund_to_publish!==undefined) errors.push('UNAPPROVED_PUBLIC_PRICE_OR_REFUND');
  for(const k of PROOF_KEYS) if(!isProof(proofs[k])) errors.push('MISSING_PROOF_'+k.toUpperCase());
  return Object.freeze({status:'HOLD_UNSENT',review_ready:errors.length===0,send_enabled:false,issues:errors});
}

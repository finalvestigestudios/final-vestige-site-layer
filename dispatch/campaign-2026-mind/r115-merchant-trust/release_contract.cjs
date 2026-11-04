'use strict';
/* Read-only pure decision logic. Never send, publish, update, or import. */
const COMMERCIAL = new Set([3,5]);
function assess(issue, proof) {
  if (![1,2,3,4,5,6].includes(issue)) throw new RangeError('Unknown edition');
  if (!proof || proof.no_live_actions !== true) return {status:'HOLD_INVALID_EVIDENCE',allowed_to_send:false};
  const base = proof.compliance || {};
  const readyShared = [
    base.physical_fv_postal_address_verified,
    base.received_unsubscribe_verified,
    base.confirmed_eligible_recipient_count !== null && Number.isInteger(base.confirmed_eligible_recipient_count) && base.confirmed_eligible_recipient_count > 0,
    base.received_email_preview_verified,
    base.precise_native_subject_preheader_verified,
    base.founder_final_send_approval
  ].every(v=>v===true);
  if (COMMERCIAL.has(issue)) {
    const id = issue===3 ? 'zen12' : 'total_focus',m = proof.merchant?.[id] || {};
    const merchantReady = m.affiliate_accepted===true && m.email_marketing_permission===true &&
      typeof m.exact_tracking_link==='string' && m.exact_tracking_link.startsWith('https://') &&
      m.independent_guide_live===true && m.checkout_price_verified===true &&
      m.refund_at_checkout_verified===true && m.purchaser_data_reporting_approved===true;
    return {status:merchantReady && readyShared?'FOUNDER_REVIEW_ONLY':'HOLD_MERCHANT',allowed_to_send:false,issue};
  }
  return {status:readyShared?'FOUNDER_REVIEW_ONLY':'HOLD_UNSENT',allowed_to_send:false,issue};
}
function aggregate(ledger) {
  const w=ledger.wp_readonly||{},a=ledger.attribution||{};
  const eligible = w.reachable_email_recipients===null ? null : w.reachable_email_recipients;
  const netPer1000 = Number.isFinite(a.realized_net_per_1000_qualified_humans) ? a.realized_net_per_1000_qualified_humans : null;
  return {reported_total:w.reported_total,reported_confirmed:w.reported_confirmed,reported_unconfirmed:w.reported_unconfirmed,followers_email:w.followers_email,followers_wpcom:w.followers_wpcom,eligible_email_recipients:eligible,confirmed_paid_orders:Number.isInteger(a.paid_orders)?a.paid_orders:null,net_per_1000_qualified_sessions:netPer1000};
}
module.exports={assess,aggregate};

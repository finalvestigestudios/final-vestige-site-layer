// Read-only, dependency-free metric contract. NOT an analytics runtime or data collector.
// Never treat an outbound click or checkout-start event as a confirmed sale.
const EVENT_TYPES = new Set(["campaign_landing","article_to_resource_click","confirmed_signup","affiliate_click","verified_checkout_start","merchant_confirmed_order","merchant_confirmed_commission","merchant_confirmed_refund"]);
const ID = /^[a-z0-9][a-z0-9_-]{2,79}$/;
export function validateCampaign(candidate) {
  if (!candidate || typeof candidate !== "object") return false;
  return ["utm_source","utm_medium","utm_campaign","asset_id"].every(k=> typeof candidate[k]==="string" && ID.test(candidate[k]))
    && candidate.utm_medium === "organic_social"
    && ["tiktok","youtube","instagram","facebook"].includes(candidate.utm_source)
    && !("email" in candidate) && !("ip" in candidate) && !("fingerprint" in candidate);
}
export function validateEvent(event) {
  if (!event || !EVENT_TYPES.has(event.type)) return false;
  if (typeof event.date !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(event.date)) return false;
  if (event.type === "affiliate_click") return typeof event.asset_id === "string" && ID.test(event.asset_id) && !("revenue" in event);
  if (["merchant_confirmed_order","merchant_confirmed_commission","merchant_confirmed_refund"].includes(event.type))
    return event.provider_verified === true && typeof event.provider_id === "string" && event.provider_id.length > 0;
  return true;
}
export function computeNetRevenue({ qualifiedHumanSessions, grossPaid, refunds, fees, commissions, settledOnly=true }) {
  const values=[qualifiedHumanSessions,grossPaid,refunds,fees,commissions];
  if (!settledOnly || values.some(v=>typeof v!=="number" || !Number.isFinite(v) || v<0))
    return {status:"NOT_COMPUTABLE", reason:"Missing, unsettled or invalid provider-verified inputs"};
  if (!Number.isInteger(qualifiedHumanSessions) || qualifiedHumanSessions < 1)
    return {status:"NOT_COMPUTABLE", reason:"No verified qualified-human denominator"};
  const realizedNet = grossPaid + commissions - refunds - fees;
  return {status:"COMPUTABLE_FROM_VERIFIED_INPUTS_ONLY", netRevenue:realizedNet, per1000:1000*realizedNet/qualifiedHumanSessions, tinySample:qualifiedHumanSessions < 100, formula:"1000*(gross_paid+settled_commissions-refunds-fees)/qualified_human_sessions"};
}
export function paidConversionRate({orders,qualifiedHumanSessions}) {
  if (!Number.isInteger(orders)||orders<0||!Number.isInteger(qualifiedHumanSessions)||qualifiedHumanSessions<1) return null;
  return orders/qualifiedHumanSessions;
}
// Cohort analytics must be run only on pseudonymous, consent-appropriate, provider-verified aggregates.
// No store, network, document, cookie, localStorage, device ID, PII or runtime hooks.

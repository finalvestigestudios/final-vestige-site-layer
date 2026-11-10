"use strict";
// Dispatch R244: read-only *review* of evidence quality; intentionally produces no revenue totals.
// It is NOT the commerce backend and makes no WordPress or merchant calls.
function reviewLedgerCausality(ledger) {
  const blockers = new Set();
  const add = key => blockers.add(key);
  const validRef = s => typeof s === "string" && /^[A-Za-z0-9._:-]{6,120}$/.test(s);
  const time = s => typeof s === "string" && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(s) && Number.isFinite(Date.parse(s));
  if (!ledger || typeof ledger !== "object" || Array.isArray(ledger)) throw Error("object_required");
  for (const key of ["sessions", "confirmations", "actions", "orders"])
    if (!Array.isArray(ledger[key])) throw Error("array_required:" + key);
  const raw = JSON.stringify(ledger);
  if (/"(?:email|email_address|phone|ip_address|full_name|first_name|last_name|street_address|recipient_address)"\s*:/.test(raw) ||
      /[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/.test(raw)) throw Error("PII_FORBIDDEN");
  const seen = new Map();
  const checkUnique = (kind, rows, key) => {
    for (const row of rows) {
      if (!row || !validRef(row[key])) { add(kind + "_ID_INVALID"); continue; }
      const id = kind + ":" + row[key], signature = JSON.stringify(row);
      if (seen.has(id) && seen.get(id) !== signature) add(kind + "_DUPLICATE_CONFLICT");
      else seen.set(id, signature);
    }
  };
  checkUnique("SESSION", ledger.sessions, "session_id");
  checkUnique("CONFIRMATION", ledger.confirmations, "provider_transition_ref");
  checkUnique("ORDER", ledger.orders, "transaction_ref");
  const sessions = new Map(ledger.sessions.filter(s => s && validRef(s.session_id)).map(s => [s.session_id, s]));
  const asOf = ledger.as_of_utc;
  if (!time(asOf)) add("AS_OF_NOT_UTC");
  for (const session of ledger.sessions) {
    if (!time(session.at_utc) || (time(asOf) && Date.parse(session.at_utc) > Date.parse(asOf)))
      add("SESSION_TIME_INVALID");
    if (session.human_review !== "verified_qualified_human") add("SESSION_NOT_QUALIFIED");
    if (!validRef(session.asset_id) || session.utm_content !== session.asset_id ||
        session.utm_medium !== "organic_social") add("SOURCE_TAG_NOT_RECONCILED");
  }
  for (const c of ledger.confirmations) {
    const s = sessions.get(c.attributed_session_id);
    if (!s || !time(c.at_utc) || !time(s.at_utc) || Date.parse(c.at_utc) < Date.parse(s.at_utc))
      add("CONFIRMATION_BEFORE_OR_WITHOUT_SESSION");
    if (c.provider !== "jetpack" || c.status !== "Subscribed" ||
        c.transition !== "confirmed" || c.verification !== "provider_verified")
      add("EMAIL_STATUS_NOT_PROVIDER_CONFIRMED");
  }
  for (const order of ledger.orders) {
    const session = sessions.get(order.attributed_session_id);
    if (!session || !time(order.at_utc) || !time(session.at_utc) ||
        Date.parse(order.at_utc) < Date.parse(session.at_utc))
      add("ORDER_BEFORE_OR_WITHOUT_SESSION");
    if (order.status !== "settled" || order.provider !== "affiliate_network" ||
        order.verification !== "independently_reported_paid" ||
        !validRef(order.proof_reference) || !validRef(order.attribution_proof))
      add("SETTLEMENT_OR_SOURCE_NOT_VERIFIED");
    if (order.currency !== "USD") add("CURRENCY_NOT_ATTESTED_USD");
    if (order.offer_id !== "zen12_premium") add("OFFER_NOT_ONE_AUTHORIZED_CANDIDATE");
    if (!validRef(order.affiliate_click_ref)) { add("CLICK_JOIN_MISSING"); continue; }
    const matches = ledger.actions.filter(a => a && a.type === "affiliate_outbound" &&
      a.attributed_session_id === order.attributed_session_id &&
      a.click_ref === order.affiliate_click_ref && a.offer_id === order.offer_id);
    if (matches.length !== 1) { add("CLICK_JOIN_MISSING_OR_AMBIGUOUS"); continue; }
    const action = matches[0];
    if (!time(action.at_utc) || !session || !time(session.at_utc) ||
        Date.parse(action.at_utc) < Date.parse(session.at_utc) ||
        Date.parse(action.at_utc) > Date.parse(order.at_utc))
      add("CLICK_CAUSAL_ORDER_INVALID");
    for (const k of ["commission_minor", "fees_minor", "refunds_minor"])
      if (!Number.isSafeInteger(order[k]) || order[k] < 0) add("SETTLEMENT_AMOUNT_INVALID");
  }
  // The API cannot authenticate private partner account approval or provider receipts.
  // A synthetic fixture or self-attested boolean is NEVER evidence of real money.
  add("NAMED_AFFILIATE_EMAIL_PERMISSION_NOT_ATTESTED");
  add("EXTERNAL_PAID_SOURCE_AND_SESSION_AUDIT_REQUIRED");
  add("LEGAL_FOOTER_AND_RECIPIENT_PROOF_REQUIRED");
  return Object.freeze({
    status: "REVIEW_ONLY_HOLD_UNSENT",
    commercial_issue_03: "HOLD_MERCHANT",
    audited_7d_net_revenue_per_1000: null,
    audited_30d_net_revenue_per_1000: null,
    independent_verified_paid_orders: null,
    blockers: [...blockers].sort()
  });
}
module.exports = { reviewLedgerCausality };

"use strict";
// R245: supplementary temporal/identity reviewer for synthetic or redacted records.
// This is NOT revenue verification, partner approval, email consent, or a release switch.
function auditTemporalTruth(ledger) {
  if (!ledger || typeof ledger !== "object" || Array.isArray(ledger)) throw Error("LEDGER_OBJECT_REQUIRED");
  for (const key of ["sessions", "confirmations", "actions", "orders"])
    if (!Array.isArray(ledger[key])) throw Error("ARRAY_REQUIRED:" + key);
  const findings = new Set();
  const add = code => findings.add(code);
  const validTime = t => typeof t === "string" && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(t) &&
    Number.isFinite(Date.parse(t)) && new Date(t).toISOString() === t.replace(/Z$/, ".000Z");
  const validId = id => typeof id === "string" && /^[A-Za-z0-9:_-]{6,100}$/.test(id);
  const cutoff = ledger.as_of_utc;
  if (!validTime(cutoff)) add("AS_OF_INVALID_UTC_INSTANT");
  const seen = new Set();
  const record = (kind, row, idField) => {
    if (!row || typeof row !== "object" || Array.isArray(row)) { add(kind + "_ROW_INVALID"); return; }
    const id = row[idField];
    if (!validId(id)) add(kind + "_ID_MISSING_OR_INVALID");
    else if (seen.has(kind + ":" + id)) add(kind + "_DUPLICATE_ID_EVEN_IF_IDENTICAL");
    else seen.add(kind + ":" + id);
    if (!validTime(row.at_utc)) add(kind + "_TIMESTAMP_INVALID_CIVIL_DATE");
    else if (validTime(cutoff) && Date.parse(row.at_utc) > Date.parse(cutoff)) add(kind + "_AFTER_REPORT_CUTOFF");
  };
  for (const s of ledger.sessions) record("SESSION", s, "session_id");
  for (const c of ledger.confirmations) record("CONFIRMATION", c, "provider_transition_ref");
  for (const o of ledger.orders) record("ORDER", o, "transaction_ref");
  for (const a of ledger.actions) if (a?.type === "affiliate_outbound") {
    record("CLICK", a, "click_ref");
  } else add("ACTION_TYPE_NOT_REVIEWED");
  const sessions = new Map(ledger.sessions.filter(s => s && validId(s.session_id)).map(s => [s.session_id, s]));
  const joins = [...ledger.confirmations.map(c => ["CONFIRMATION", c]), ...ledger.orders.map(o => ["ORDER", o]), ...ledger.actions.map(a => ["CLICK", a])];
  for (const [kind, row] of joins) {
    if (!row || typeof row !== "object") continue;
    const origin = sessions.get(row.attributed_session_id);
    if (!origin) { add(kind + "_SOURCE_SESSION_MISSING"); continue; }
    if (validTime(origin.at_utc) && validTime(row.at_utc) && Date.parse(row.at_utc) < Date.parse(origin.at_utc))
      add(kind + "_BEFORE_SOURCE_SESSION");
  }
  for (const o of ledger.orders) {
    if (!o || typeof o !== "object") continue;
    if (o.affiliate_click_ref == null) { add("ORDER_CLICK_REF_NOT_VERIFIED"); continue; }
    const matches = ledger.actions.filter(a => a?.type === "affiliate_outbound" && a.click_ref === o.affiliate_click_ref &&
      a.offer_id === o.offer_id && a.attributed_session_id === o.attributed_session_id);
    if (matches.length !== 1) { add("ORDER_CLICK_JOIN_AMBIGUOUS_OR_ABSENT"); continue; }
    if (validTime(o.at_utc) && validTime(matches[0].at_utc) && Date.parse(matches[0].at_utc) > Date.parse(o.at_utc))
      add("CLICK_AFTER_PAID_ORDER");
  }
  // Other teams own evidence authentication; none of these data alone certify sales or email rights.
  add("NAMED_PARTNER_EMAIL_RIGHTS_UNVERIFIED");
  add("PROVIDER_CONFIRMED_ELIGIBLE_AUDIENCE_UNVERIFIED");
  add("RECEIVED_EMAIL_POSTAL_AND_OPTOUT_UNVERIFIED");
  add("EXTERNAL_TRANSACTION_AND_SESSION_AUDIT_REQUIRED");
  return Object.freeze({status:"REVIEW_ONLY_HOLD_UNSENT", affected_commercial_issues:[3,5],
    verified_paid_orders:null, net_revenue_per_1000_qualified_humans:null,
    blockers:[...findings].sort()});
}
module.exports = {auditTemporalTruth};

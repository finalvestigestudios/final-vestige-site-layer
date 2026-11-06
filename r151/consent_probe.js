/* Final Vestige Dispatch R151. Offline only. No subscriber API, network, send, CMS write, or analytics calls. */
(function (factory) {
  const api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else globalThis.FVConsent = api;
})(function () {
  "use strict";
  const ALLOWED = new Set(["Subscribed","Not subscribed","Not confirmed","Bounced","Emails paused","Not sending","Suppressed"]);
  const OWN = Object.prototype.hasOwnProperty;
  function integer(n) { return Number.isSafeInteger(n) && n >= 0; }
  function redactedError() { return new Error("INVALID_OR_PRIVATE_EVIDENCE"); }
  function assertSafe(record) {
    if (!record || typeof record !== "object" || Array.isArray(record)) throw redactedError();
    const keys = Object.keys(record);
    const allowed = new Set(["opaque_key","email_subscription","confirmation_proof","consent_proof","confirmed_at_utc","source_asset_id","utm_campaign"]);
    if (keys.some(k => !allowed.has(k))) throw redactedError();
    for (const [k,v] of Object.entries(record)) {
      if (typeof v === "string" && (v.includes("@") || /https?:\/\//i.test(v) || v.length > 180)) throw redactedError();
    }
    if (typeof record.opaque_key !== "string" || !/^[a-f0-9]{32,64}$/.test(record.opaque_key)) throw redactedError();
    if (!ALLOWED.has(record.email_subscription)) throw redactedError();
    if (![true,false,null,undefined].includes(record.confirmation_proof)) throw redactedError();
    if (![true,false,null,undefined].includes(record.consent_proof)) throw redactedError();
    if (record.confirmed_at_utc != null) {
      if (typeof record.confirmed_at_utc !== "string" || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(record.confirmed_at_utc) ||
          Number.isNaN(Date.parse(record.confirmed_at_utc))) throw redactedError();
    }
    for (const f of ["source_asset_id","utm_campaign"]) {
      if (record[f] != null && (typeof record[f] !== "string" || !/^[a-z0-9][a-z0-9_-]{0,79}$/.test(record[f]))) throw redactedError();
    }
  }
  function snapshotValid(s) {
    if (!s || typeof s !== "object" || Array.isArray(s)) return false;
    for (const k of ["total","confirmed","unconfirmed","suppressed","paid","imported_last_24h","follower_wpcom","follower_email"]) {
      if (!integer(s[k])) return false;
    }
    if (typeof s.newsletter_enabled !== "boolean" || typeof s.new_posts_auto_send !== "boolean" ||
        !["full","excerpt"].includes(s.format)) return false;
    if (typeof s.as_of !== "string" || Number.isNaN(Date.parse(s.as_of))) return false;
    return true;
  }
  function audit(snapshot, providerRows, completeProviderExport) {
    if (!snapshotValid(snapshot)) throw new Error("INVALID_AGGREGATE_SNAPSHOT");
    if (providerRows !== null && !Array.isArray(providerRows)) throw redactedError();
    if (typeof completeProviderExport !== "boolean") throw redactedError();
    if (providerRows === null && completeProviderExport) throw redactedError();
    const out = {
      release: "HOLD_UNSENT", commercial_release: "HOLD_MERCHANT",
      email_new_posts_by_default: snapshot.new_posts_auto_send,
      dashboard: {total:snapshot.total, confirmed:snapshot.confirmed, unconfirmed:snapshot.unconfirmed},
      follower_breakdown: {wpcom:snapshot.follower_wpcom,email_only:snapshot.follower_email},
      dashboard_count_additive: false,
      email_only_zero_proves_zero_eligible: false,
      exact_email_eligible_count: null,
      provider_reviewed_count: providerRows === null ? null : 0,
      confirmed_signup_count: null,
      test_scope: providerRows === null ? "aggregate_only" : (completeProviderExport ? "complete_private_export_attested" : "partial_private_export"),
      reasons: []
    };
    if (snapshot.confirmed + snapshot.unconfirmed > snapshot.total) out.reasons.push("DASHBOARD_CATEGORIES_OVERLAP_OR_DIFFERENT_DENOMINATORS");
    if (!snapshot.newsletter_enabled) out.reasons.push("NEWSLETTER_DISABLED");
    if (snapshot.new_posts_auto_send) out.reasons.push("AUTO_SEND_ENABLED_RELEASE_STOP");
    if (providerRows === null) {out.reasons.push("NO_AUTHORITATIVE_PER_SUBSCRIBER_EMAIL_STATUS");return out;}
    const seen = new Set(); let candidates=0,signup=0;
    for(const r of providerRows) {
      assertSafe(r);
      if(seen.has(r.opaque_key)) throw new Error("DUPLICATE_OPAQUE_KEY_REQUIRES_PROVIDER_RESOLUTION");
      seen.add(r.opaque_key);
      const eligible = r.email_subscription === "Subscribed" && r.confirmation_proof === true && r.consent_proof === true;
      if(eligible) candidates++;
      if(eligible && r.confirmed_at_utc) signup++;
    }
    out.provider_reviewed_count = seen.size;
    if(!completeProviderExport) {
      out.reasons.push("PARTIAL_PROVIDER_ROWS_CANNOT_ESTABLISH_TOTAL_ELIGIBLE");
      return out;
    }
    out.exact_email_eligible_count = candidates;
    out.confirmed_signup_count = signup;
    out.reasons.push("PRIVATE_PROVIDER_ROWS_REVIEWED_NOT_AN_EMAIL_SEND_OR_PAID_ORDER");
    return out;
  }
  return {audit, snapshotValid, assertSafe};
});
